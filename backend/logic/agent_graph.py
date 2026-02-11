
import asyncio
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.logic.nlu import analyze_text, generate_tail_question, infer_product_keywords
from backend.database.database import search_products, get_related_products_for_context
from backend.logic.schemas import NLUResponse, Intent, NLUSlots

# --- 1. Graph State Definition ---
class GraphState(TypedDict):
    request_id: str
    input_text: str             # Normalized user input
    session_id: str             # (Added for context handling)
    history: List[Dict]         # Conversation History [{"role": "user", "text": "..."}, ...]
    
    # NLU Result
    intent: Intent              # PRODUCT_LOCATION / OTHER / UNSUPPORTED
    slots: Dict[str, Any]       # {item, attrs, query_rewrite...}
    
    # Search Result
    search_candidates: List[Dict] # DB Search Results
    
    # Control Flags
    is_ambiguous: bool          # Ambiguity Check Result
    clarification_count: int    # Limit max 1 turn
    
    # Final Output
    final_response: NLUResponse # Structured Object for API

# --- 2. Nodes ---

async def nlu_node(state: GraphState):
    """Node 1: Parse User Input"""
    print(f"--- [Node: NLU] Analyzing: {state['input_text']} ---")
    
    # Pass history to NLU for context resolution
    history = state.get("history", [])
    nlu_result = await analyze_text(state['input_text'], history=history)
    
    return {
        "intent": nlu_result.intent,
        "slots": nlu_result.slots.model_dump(),
        # Pass the whole object as partial result
        "final_response": nlu_result 
    }

async def search_node(state: GraphState):
    """Node 2: Search DB"""
    if state["intent"] != Intent.PRODUCT_LOCATION:
        return {"search_candidates": []}
        
    slots = state["slots"]
    query = slots.get("item") or slots.get("query_rewrite") or ""
    print(f"--- [Node: Search] Querying: '{query}' ---")
    
    candidates = []
    if query:
        candidates = search_products(query)
    
    # If no results, try refined search (Rewrite Logic embedded here for robustness)
    if not candidates and query:
         print(f"    -> 0 results. attempting keyword inference...")
         keywords = await infer_product_keywords(state['input_text'])
         for kw in keywords:
             candidates.extend(search_products(kw))
             if candidates: break # stop if found
             
    print(f"    -> Found {len(candidates)} candidates")
    return {"search_candidates": candidates}

async def ambiguity_check_node(state: GraphState):
    """Node 3: Check Context/Ambiguity"""
    candidates = state["search_candidates"]
    intent = state["intent"]
    
    is_ambiguous = False
    
    if intent == Intent.UNSUPPORTED or intent == Intent.OTHER_INQUIRY:
        is_ambiguous = False # Handle in response node
    elif not candidates:
        is_ambiguous = True # Need to explain or ask
    elif len(candidates) > 5: # Too many results
        is_ambiguous = True
    elif state["final_response"].needs_clarification: # NLU flagged it
        is_ambiguous = True
        
    # [LOOP PREVENTION FIX]
    # If the previous turn was an Assistant Question, do NOT ask again. Just show results.
    history = state.get("history", [])
    if history and history[-1]["role"] == "assistant":
        last_msg = history[-1]["text"]
        # Simple heuristic: if last msg ended with ? or was a question
        if "?" in last_msg or "어떤" in last_msg or "입니까" in last_msg:
             print("--- [Node: Ambiguity] Loop Detected (Prev was Question). Forcing Answer. ---")
             is_ambiguous = False
        
    print(f"--- [Node: Ambiguity] Is Ambiguous? {is_ambiguous} ---")
    return {"is_ambiguous": is_ambiguous}

async def clarification_node(state: GraphState):
    """Node 4: Generate Tail Question"""
    print(f"--- [Node: Clarification] Generating Question ---")
    
    candidates = state["search_candidates"]
    slots = state["slots"]
    
    # Build Context with Category Aggregation (Drill-Down Support)
    from backend.database.category_matcher import get_drill_down_context
    db_context = get_drill_down_context(candidates)

    question = await generate_tail_question(
        state["input_text"], 
        slots, 
        db_context=db_context
    )
    
    # Update Final Response
    resp = state["final_response"]
    resp.needs_clarification = True
    resp.generated_question = question
    resp.products = candidates # Show what we found even if asking
    
    return {
        "final_response": resp,
        "clarification_count": state["clarification_count"] + 1
    }

async def response_node(state: GraphState):
    """Node 5: Finalize Answer"""
    print(f"--- [Node: Response] Finalizing ---")
    resp = state["final_response"]
    resp.products = state["search_candidates"]
    
    if state["intent"] == Intent.UNSUPPORTED:
        resp.generated_question = "죄송합니다. 상품 찾기 외의 질문은 아직 답변하기 어렵습니다."
        resp.needs_clarification = True
    elif not resp.generated_question and resp.products:
        # Generate a polite closing if search was successful (and not asking a question)
        query = state['input_text']
        count = len(resp.products)
        # Check if we were forced to answer (Ambiguity = False constraint)
        # We can detect this if 'clarification_count' > 0 -> implies we had a convo? 
        # Actually just a generic nice message is good.
        resp.generated_question = f"요청하신 '{query}' 관련 상품 {count}개를 찾았습니다."
        
    return {"final_response": resp}

# --- 3. Edges ---

def route_after_ambiguity(state: GraphState):
    if state["is_ambiguous"]:
        # Limit Loop: If we already asked once (or purely logic check)
        # Note: current setup runs per request, so count is usually 0 unless we persist state across requests
        # For this PoC, we assume count protects strictly within graph scope
        if state["clarification_count"] >= 1:
            return "final_response"
        return "clarification"
    return "final_response"

# --- 4. Graph Construction ---

workflow = StateGraph(GraphState)

workflow.add_node("nlu", nlu_node)
workflow.add_node("search", search_node)
workflow.add_node("ambiguity_check", ambiguity_check_node)
workflow.add_node("clarification", clarification_node)
workflow.add_node("final_response", response_node)

workflow.set_entry_point("nlu")

workflow.add_edge("nlu", "search")
workflow.add_edge("search", "ambiguity_check")
workflow.add_conditional_edges(
    "ambiguity_check",
    route_after_ambiguity,
    {
        "clarification": "clarification",
        "final_response": "final_response"
    }
)
workflow.add_edge("clarification", END)
workflow.add_edge("final_response", END)

memory = MemorySaver()
agent_app = workflow.compile(checkpointer=memory)
