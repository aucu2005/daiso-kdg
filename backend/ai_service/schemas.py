# backend/ai_service/schemas.py
"""
Data models for the AI Agent Pipeline.
- PipelineState: LangGraph graph state
- Domain models: Intent, NLUSlots, NLUResponse, Product
- Result models: IntentGateResult, RerankResult
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ─── Enums ───────────────────────────────────────────────────

class Intent(str, Enum):
    PRODUCT_LOCATION = "PRODUCT_LOCATION"  # 상품 찾기 / 위치 문의
    OTHER_INQUIRY = "OTHER_INQUIRY"        # 운영시간, 주차, 환불 등 일반 문의
    UNSUPPORTED = "UNSUPPORTED"            # 범위 밖 (잡담, 무관한 질문)


# ─── Pydantic Models ─────────────────────────────────────────

class NLUSlots(BaseModel):
    """NLU에서 추출한 슬롯 정보"""
    item: Optional[str] = Field(None, description="핵심 상품명")
    attrs: List[str] = Field(default_factory=list, description="속성 (색상, 용도, 크기)")
    category_hint: Optional[str] = Field(None, description="추론된 카테고리")
    query_rewrite: Optional[str] = Field(None, description="검색 엔진용 최적화 쿼리")
    min_price: Optional[int] = Field(None, description="최소 가격 필터")
    max_price: Optional[int] = Field(None, description="최대 가격 필터")


class Product(BaseModel):
    """상품 정보"""
    id: int
    name: str
    price: int
    image_url: Optional[str] = None
    rank: Optional[int] = None
    category_major: Optional[str] = None
    category_middle: Optional[str] = None
    floor: Optional[str] = None
    location: Optional[str] = None


class NLUResponse(BaseModel):
    """NLU 분석 전체 응답"""
    request_id: str = Field(..., description="추적용 고유 ID")
    intent: Intent = Field(..., description="분류된 의도")
    slots: NLUSlots = Field(default_factory=NLUSlots, description="추출된 슬롯")

    # Clarification
    needs_clarification: bool = Field(False)
    generated_question: Optional[str] = Field(None)

    # Performance Metrics
    model_name: str = Field("gemini-2.0-flash")
    latency_ms: int = Field(0)
    token_usage: Dict[str, int] = Field(default_factory=dict)

    # Search Results (accepts both Product models and raw dicts)
    products: List[Any] = Field(default_factory=list)


class IntentGateResult(BaseModel):
    """Intent Gate Y/N 판별 결과"""
    is_valid: str = Field(..., description="Y (응대 필요) / N (무시)")
    latency_ms: int = Field(0)


class RerankResult(BaseModel):
    """LLM Re-ranker 결과"""
    selected_id: Optional[str] = Field(None, description="선택된 상품 ID (없으면 null)")
    reason: str = Field("", description="선택 사유 (한국어)")
    latency: float = Field(0.0, description="처리 시간 (초)")


# ─── LangGraph State ─────────────────────────────────────────

class PipelineState(TypedDict):
    """LangGraph StateGraph의 전체 상태 정의"""
    request_id: str
    input_text: str               # 정규화된 사용자 입력
    session_id: str               # 세션 ID (대화 컨텍스트용)
    history: List[Dict]           # 대화 이력 [{"role": "user", "text": "..."}]

    # Intent & Keyword 결과
    intent_valid: str             # "Y" / "N"
    intent: Intent
    slots: Dict[str, Any]
    expanded_keywords: List[str]  # 확장된 검색 키워드

    # Hybrid Search 결과
    search_candidates: List[Dict]

    # LLM Re-ranker 결과
    rerank_result: Dict           # {"selected_id": ..., "reason": ..., "latency": ...}

    # Control Flags
    is_ambiguous: bool
    clarification_count: int

    # Final Output
    final_response: NLUResponse
