# backend/ai_service/reranker_node.py
"""
Pipeline Node 3: LLM Re-ranker (Gemini 2.0 Flash)

Uses Chain-of-Thought reasoning to select the best product from search candidates.
Ported from: poc/kdg/poc_v5_experiment_phase_1.py

Architecture: Supervisor → Intent & Keyword → Hybrid Searcher → [LLM Re-ranker]
"""

import json
import time
from typing import List, Dict

from .config import get_genai, MODEL_NAME, log_debug
from .schemas import PipelineState, Intent
from .prompts import RERANK_SYSTEM_PROMPT


# ─── Rerank Logic ────────────────────────────────────────────

async def _advanced_rerank(user_query: str, candidates: List[Dict]) -> Dict:
    """
    Rerank candidates using Gemini 2.0 Flash with CoT reasoning.
    Returns: {"selected_id": str|null, "reason": str, "latency": float}
    """
    if not candidates:
        return {"selected_id": None, "reason": "후보 상품이 없습니다.", "latency": 0.0}

    genai = get_genai()
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"},
    )

    # Build candidate text
    candidate_text = ""
    for c in candidates:
        name = c.get("name", "Unknown")
        desc = c.get("desc", "") or c.get("searchable_desc", "") or "No description"
        desc = desc[:100]  # Truncate to save tokens
        cid = c.get("id", "?")
        candidate_text += f"- ID {cid}: {name} (Desc: {desc})\n"

    # Construct prompt
    prompt = f"""
    {RERANK_SYSTEM_PROMPT}

    [Current Task]
    User Query: "{user_query}"

    Candidates:
    {candidate_text}

    Output JSON:
    {{
        "selected_id": "string or null",
        "reason": "string (Korean)"
    }}
    """

    try:
        start_time = time.time()
        response = await model.generate_content_async(prompt)
        latency = time.time() - start_time

        result = json.loads(response.text)
        result["latency"] = round(latency, 3)

        log_debug(
            f"[Reranker] Query='{user_query}' → selected={result.get('selected_id')} "
            f"| reason='{result.get('reason', '')[:50]}...' | latency={latency:.3f}s"
        )
        return result

    except Exception as e:
        log_debug(f"[Reranker] Error: {e}")
        return {"selected_id": None, "reason": f"리랭킹 오류: {str(e)}", "latency": 0.0}


# ─── LangGraph Node Function ────────────────────────────────

async def reranker_node(state: PipelineState) -> dict:
    """
    LangGraph node: LLM Re-ranker
    Selects the best product from search candidates using CoT reasoning.
    """
    intent = state.get("intent")
    candidates = state.get("search_candidates", [])

    # Skip reranking for non-product intents or empty candidates
    if intent != Intent.PRODUCT_LOCATION or not candidates:
        log_debug(f"[Node: Reranker] Skipping (intent={intent}, candidates={len(candidates)})")
        return {"rerank_result": {"selected_id": None, "reason": "", "latency": 0.0}}

    input_text = state["input_text"]
    log_debug(f"--- [Node: Reranker] Query='{input_text}', {len(candidates)} candidates ---")

    # Always use LLM reranking to validate relevance (even for 1 candidate)
    result = await _advanced_rerank(input_text, candidates)
    
    from .config import log_pipeline
    log_pipeline("Reranker", {"input_text": input_text, "candidate_count": len(candidates)}, {
        "selected_id": result.get("selected_id"),
        "reason": result.get("reason"),
        "latency": result.get("latency")
    })
    
    return {"rerank_result": result}
