# backend/ai_service/__init__.py
"""
AI Agent Layer — LangGraph Supervisor Pipeline

Architecture:
    Supervisor (LangGraph StateGraph)
    └── Pipeline
        ├── Intent & Keyword Node (Gemini 2.0 Flash)
        ├── Hybrid Searcher Node (BM25 + Vector)
        └── LLM Re-ranker Node (Gemini 2.0 Flash)
"""

from .schemas import (
    PipelineState,
    Intent,
    NLUSlots,
    NLUResponse,
    Product,
    IntentGateResult,
    RerankResult,
)

__all__ = [
    "PipelineState",
    "Intent",
    "NLUSlots",
    "NLUResponse",
    "Product",
    "IntentGateResult",
    "RerankResult",
]
