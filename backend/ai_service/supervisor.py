# backend/ai_service/supervisor.py
"""
Supervisor: LangGraph StateGraph orchestrating the AI Agent Pipeline.

Flow:
    intent_keyword → route_after_intent → hybrid_search → reranker
                                        → ambiguity_check → route → response / clarification → END
                   (N) → unsupported_response → END

Architecture: [Supervisor (LangGraph)] → Pipeline Nodes
"""

import json
from typing import List, Dict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .schemas import PipelineState, Intent, NLUResponse
from .intent_keyword_node import intent_keyword_node
from .hybrid_searcher_node import hybrid_search_node
from .reranker_node import reranker_node
from .config import log_debug


# ─── Auxiliary Nodes ─────────────────────────────────────────

async def ambiguity_check_node(state: PipelineState) -> dict:
    """Check if the search results are ambiguous and need clarification."""
    candidates = state.get("search_candidates", [])
    intent = state.get("intent")
    rerank = state.get("rerank_result", {})

    is_ambiguous = False

    if intent == Intent.UNSUPPORTED or intent == Intent.OTHER_INQUIRY:
        is_ambiguous = False
    elif not candidates:
        is_ambiguous = True  # No results → need clarification
    elif len(candidates) > 5 and not rerank.get("selected_id"):
        is_ambiguous = True  # Too many results and reranker didn't pick one
    elif state.get("final_response") and state["final_response"].needs_clarification:
        is_ambiguous = True  # NLU flagged as ambiguous

    # Loop prevention: if last history message was a question, don't ask again
    history = state.get("history", [])
    if history and history[-1].get("role") == "assistant":
        last_msg = history[-1].get("text", "")
        if "?" in last_msg or "어떤" in last_msg or "시나요" in last_msg:
            log_debug("[Node: Ambiguity] Loop detected (prev was question). Forcing answer.")
            is_ambiguous = False

    log_debug(f"--- [Node: Ambiguity] Is Ambiguous? {is_ambiguous} ---")
    return {"is_ambiguous": is_ambiguous}


async def clarification_node(state: PipelineState) -> dict:
    """Generate a tail question for ambiguous queries."""
    from .prompts import TAIL_QUESTION_PROMPT
    from .config import get_genai, MODEL_NAME

    log_debug("--- [Node: Clarification] Generating question ---")

    candidates = state.get("search_candidates", [])
    slots = state.get("slots", {})

    # Build DB context from candidates
    db_context = ""
    try:
        from backend.database.category_matcher import get_drill_down_context
        db_context = get_drill_down_context(candidates)
    except ImportError:
        db_context = "\n".join([f"- {c.get('name', '?')}" for c in candidates[:10]])

    # Generate question using LLM
    prompt = TAIL_QUESTION_PROMPT.format(
        context=state["input_text"],
        slots=json.dumps(slots, ensure_ascii=False),
        db_context=db_context,
    )

    question = "어떤 종류의 상품을 찾으시나요?"  # Default

    try:
        genai = get_genai()
        model = genai.GenerativeModel(MODEL_NAME)
        response = await model.generate_content_async(prompt)
        generated = response.text.strip()
        if generated:
            question = generated
        log_debug(f"[Node: Clarification] Question: '{question[:60]}...'")
    except Exception as e:
        log_debug(f"[Node: Clarification] Error: {e}")

    # Update final response
    resp = state.get("final_response")
    if resp:
        resp.needs_clarification = True
        resp.generated_question = question
        resp.products = candidates
    else:
        resp = NLUResponse(
            request_id="clarify",
            intent=Intent.PRODUCT_LOCATION,
            needs_clarification=True,
            generated_question=question,
        )

    return {
        "final_response": resp,
        "clarification_count": state.get("clarification_count", 0) + 1,
    }


async def response_node(state: PipelineState) -> dict:
    """Finalize the response with search results and reranking."""
    log_debug("--- [Node: Response] Finalizing ---")

    resp = state.get("final_response")
    if not resp:
        resp = NLUResponse(request_id="final", intent=state.get("intent", Intent.UNSUPPORTED))

    candidates = state.get("search_candidates", [])
    rerank = state.get("rerank_result", {})

    # Prioritize selected item and limit to Top 3
    final_products = []
    selected_id = rerank.get("selected_id")

    # 1. Add selected item first
    if selected_id:
        for c in candidates:
            if str(c.get("id")) == str(selected_id):
                final_products.append(c)
                break

    # 2. Add remaining candidates (avoid duplicates)
    for c in candidates:
        if len(final_products) >= 3:
            break
        if str(c.get("id")) != str(selected_id):
            final_products.append(c)

    resp.products = final_products

    if state.get("intent") == Intent.UNSUPPORTED:
        resp.generated_question = "죄송합니다. 상품 찾기 외의 질문은 아직 답변하기 어렵습니다."
        resp.needs_clarification = True
    elif state.get("intent") == Intent.OTHER_INQUIRY:
        resp.generated_question = "매장 운영 관련 문의는 직원에게 문의해 주세요."
        resp.needs_clarification = True
    elif rerank.get("selected_id"):
        selected_name = "상품"
        for c in candidates:
            if str(c.get("id")) == str(rerank["selected_id"]):
                selected_name = c.get("name", "상품")
                break
        reason = rerank.get("reason", "")
        resp.generated_question = f"'{selected_name}'을(를) 찾았습니다. {reason}"
    elif candidates:
        resp.generated_question = f"요청하신 상품 관련 {len(final_products)}개의 결과를 찾았습니다."

    from .config import log_pipeline
    log_pipeline("Final Response", {}, {
        "intent": str(state.get("intent")),
        "needs_clarification": resp.needs_clarification,
        "question": resp.generated_question,
        "product_count": len(final_products) if hasattr(resp, 'products') else 0
    })

    return {"final_response": resp}


# ─── Edge Routing Functions ──────────────────────────────────

def route_after_intent(state: PipelineState) -> str:
    """Route based on Intent Gate result (Y/N)."""
    if state.get("intent_valid") == "N":
        return "response"
    if state.get("intent") in (Intent.UNSUPPORTED, Intent.OTHER_INQUIRY):
        return "response"
    return "hybrid_search"


def route_after_ambiguity(state: PipelineState) -> str:
    """Route based on ambiguity check."""
    if state.get("is_ambiguous"):
        if state.get("clarification_count", 0) >= 1:
            return "response"  # Loop limit reached
        return "clarification"
    return "response"


# ─── Graph Construction ─────────────────────────────────────

workflow = StateGraph(PipelineState)

# Register nodes
workflow.add_node("intent_keyword", intent_keyword_node)
workflow.add_node("hybrid_search", hybrid_search_node)
workflow.add_node("reranker", reranker_node)
workflow.add_node("ambiguity_check", ambiguity_check_node)
workflow.add_node("clarification", clarification_node)
workflow.add_node("response", response_node)

# Set entry point
workflow.set_entry_point("intent_keyword")

# Define edges
workflow.add_conditional_edges(
    "intent_keyword",
    route_after_intent,
    {
        "hybrid_search": "hybrid_search",
        "response": "response",
    },
)
workflow.add_edge("hybrid_search", "reranker")
workflow.add_edge("reranker", "ambiguity_check")
workflow.add_conditional_edges(
    "ambiguity_check",
    route_after_ambiguity,
    {
        "clarification": "clarification",
        "response": "response",
    },
)
workflow.add_edge("clarification", END)
workflow.add_edge("response", END)

# Compile with memory checkpointer
memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)
