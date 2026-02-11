# backend/ai_service/hybrid_searcher_node.py
"""
Pipeline Node 2: Hybrid Searcher (BM25 + Vector)

Strategy: BM25 is primary (exact keyword match), Vector is supplementary (semantic expansion)
BM25: SQLite flexible search (AND → OR → single-term fallback)  
Vector: ChromaDB cosine similarity (supplementary, no distance filter)
Fusion: Reciprocal Rank Fusion (RRF) with k=60

Architecture: Supervisor → Intent & Keyword → [Hybrid Searcher] → LLM Re-ranker
"""

from typing import List, Dict

from .config import log_debug
from .schemas import PipelineState, Intent


# ─── Search Adapters ─────────────────────────────────────────

def _bm25_search(query: str) -> List[Dict]:
    """BM25-like search: SQLite flexible query (AND → OR → single-term)."""
    try:
        from backend.database.database import search_products_flexible
        results = search_products_flexible(query)
        log_debug(f"[BM25] '{query}' → {len(results)} results")
        return results if results else []
    except ImportError:
        log_debug("[BM25] Warning: backend.database.database not available")
        return []


def _vector_search(query: str, top_k: int = 10) -> List[Dict]:
    """Dense vector search: ChromaDB cosine similarity (supplementary)."""
    try:
        from .vector_store import get_vector_store
        store = get_vector_store()
        if store.count() == 0:
            return []
        results = store.search(query, top_k=top_k)
        log_debug(f"[Vector] '{query}' → {len(results)} results")
        return results
    except Exception as e:
        log_debug(f"[Vector] Error: {e}")
        return []


def _hybrid_rrf(bm25_results: List[Dict], vector_results: List[Dict], k: int = 60) -> List[Dict]:
    """Reciprocal Rank Fusion: combine BM25 + vector results."""
    if not bm25_results and not vector_results:
        return []
    if not vector_results:
        return bm25_results
    if not bm25_results:
        return vector_results

    scores: Dict[str, float] = {}
    item_map: Dict[str, Dict] = {}

    # BM25 results get HIGHER weight (×2) since they're more reliable for Korean
    for rank, item in enumerate(bm25_results):
        item_id = str(item.get("id", ""))
        if not item_id:
            continue
        scores[item_id] = scores.get(item_id, 0.0) + 2.0 / (k + rank + 1)
        item_map[item_id] = item

    for rank, item in enumerate(vector_results):
        item_id = str(item.get("id", ""))
        if not item_id:
            continue
        scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
        if item_id not in item_map:
            item_map[item_id] = item

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    fused = [item_map[item_id] for item_id in sorted_ids if item_id in item_map]

    log_debug(f"[RRF] BM25={len(bm25_results)}(×2) + Vector={len(vector_results)} → Fused={len(fused)}")
    return fused


# ─── LangGraph Node Function ────────────────────────────────

async def hybrid_search_node(state: PipelineState) -> dict:
    """
    Search Strategy:
    1) BM25 primary (item name) + Vector supplementary (query_rewrite)
    2) Expanded keywords via BM25
    3) query_rewrite via BM25
    4) LLM keyword inference as last resort
    """
    intent = state.get("intent")

    if intent != Intent.PRODUCT_LOCATION:
        log_debug(f"[Node: Hybrid Search] Intent={intent}, skipping.")
        return {"search_candidates": []}

    slots = state.get("slots", {})
    expanded_keywords = state.get("expanded_keywords", [])
    item_name = slots.get("item") or ""
    query_rewrite = slots.get("query_rewrite") or item_name

    # Safety: truncate query_rewrite to prevent bloated vector queries
    if len(query_rewrite) > 100:
        query_rewrite = query_rewrite[:100].strip()

    log_debug(f"--- [Node: Hybrid Search] item='{item_name}' / rewrite='{query_rewrite[:60]}' ---")

    candidates = []

    # Step 1: BM25 (item name) + Vector (query_rewrite) → RRF
    if item_name:
        bm25_results = _bm25_search(item_name)
        vector_results = _vector_search(query_rewrite, top_k=10)
        candidates = _hybrid_rrf(bm25_results, vector_results)

    # Step 2: Expanded keywords (BM25 only)
    if not candidates and expanded_keywords:
        log_debug(f"    → Trying expanded: {expanded_keywords[:5]}")
        for kw in expanded_keywords:
            kw_results = _bm25_search(kw)
            if kw_results:
                candidates.extend(kw_results)
                break

    # Step 3: query_rewrite in BM25 (flexible OR search)
    if not candidates and query_rewrite and query_rewrite != item_name:
        log_debug(f"    → Trying rewrite in BM25: '{query_rewrite}'")
        candidates = _bm25_search(query_rewrite)

    # Step 4: LLM keyword inference
    if not candidates:
        log_debug(f"    → Last resort: LLM keyword inference...")
        try:
            from .intent_keyword_node import _infer_product_keywords
            inferred = await _infer_product_keywords(state["input_text"])
            log_debug(f"    → Inferred: {inferred}")
            for kw in inferred:
                kw_results = _bm25_search(kw)
                if kw_results:
                    candidates.extend(kw_results)
                    break
        except Exception as e:
            log_debug(f"    → Inference failed: {e}")

    # Deduplicate
    seen_ids = set()
    unique = []
    for c in candidates:
        cid = str(c.get("id", ""))
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            unique.append(c)

    candidate_names = [c.get("name") for c in unique[:5]]
    
    from .config import log_pipeline
    log_pipeline("Hybrid Search", {"item": item_name, "query_rewrite": query_rewrite}, {
        "candidate_count": len(unique),
        "top_5": candidate_names
    })

    log_debug(f"    → Final: {len(unique)} unique candidates")
    return {"search_candidates": unique}
