# backend/api.py
"""
FastAPI STT Pipeline API
Endpoints: /health, /stt/process
v1.2 - Using faster-whisper medium model
"""

import os
import time
import uuid
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager
import json

from .database.database import (
    search_products_flexible, get_all_products, get_related_products_for_context,
    get_map_zones, save_map_zone, delete_map_zone, init_database
)

import yaml
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal

from backend.stt import QualityGate, PolicyGate, WhisperAdapter
from backend.stt.types import STTResult, QualityGateResult, PolicyIntent


# ============== AI Pipeline Request/Response Models ==============

class QueryRequest(BaseModel):
    """Request for /api/query — AI pipeline input"""
    text: str
    session_id: Optional[str] = None
    history: list = []


class SlotData(BaseModel):
    item: Optional[str] = None
    attrs: list = []
    category_hint: Optional[str] = None
    query_rewrite: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None


class RerankData(BaseModel):
    selected_id: Optional[str] = None
    reason: str = ""
    latency: float = 0.0


class QueryResponse(BaseModel):
    """Response for /api/query — AI pipeline output"""
    request_id: str
    intent_valid: str  # "Y" / "N"
    intent: str  # PRODUCT_LOCATION / OTHER_INQUIRY / UNSUPPORTED
    slots: SlotData
    rerank: Optional[RerankData] = None
    products: list = []
    needs_clarification: bool = False
    generated_question: Optional[str] = None
    processing_time_ms: int = 0


# ============== Response Models ==============

class STTResponseData(BaseModel):
    text_raw: Optional[str]
    confidence: Optional[float]
    lang: str
    latency_ms: int
    error: Optional[str]


class QualityGateData(BaseModel):
    status: Literal["OK", "RETRY", "FAIL"]
    is_usable: bool
    reason: str


class PolicyIntentData(BaseModel):
    intent_type: Literal["PRODUCT_SEARCH", "FIXED_LOCATION", "UNSUPPORTED"]
    location_target: Optional[str]
    confidence: float
    reason: str


class STTProcessResponse(BaseModel):
    request_id: str
    stt: STTResponseData
    quality_gate: QualityGateData
    policy_intent: Optional[PolicyIntentData]
    final_response: str
    processing_time_ms: int


# ============== Global State ==============

config: dict = {}
whisper_adapter: Optional[WhisperAdapter] = None
quality_gate: Optional[QualityGate] = None
policy_gate: Optional[PolicyGate] = None


def load_config():
    """Load configuration from YAML"""
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize STT adapter and gates"""
    global config, whisper_adapter, quality_gate, policy_gate
    
    print("🚀 Starting STT Pipeline API...")
    
    # Load config
    config = load_config()
    print(f"✅ Config loaded")
    
    # Initialize Whisper adapter
    stt_config = config.get("stt", {}).get("whisper", {})
    try:
        whisper_adapter = WhisperAdapter(
            model_size=stt_config.get("model", "medium"),
            device=stt_config.get("device", "cuda"),
            compute_type=stt_config.get("compute_type", "float16"),
            fallback_model=stt_config.get("fallback_model", "small"),
            language=stt_config.get("language", "ko")
        )
    except Exception as e:
        print(f"⚠️ Whisper adapter failed to load: {e}")
        print("⚠️ STT endpoint will return simulation results")
        whisper_adapter = None
    
    # Initialize gates
    qg_config = config.get("quality_gate", {})
    quality_gate = QualityGate(
        min_chars=qg_config.get("min_chars", 2),
        min_confidence=qg_config.get("min_confidence", 0.6),
        nonsense_patterns=qg_config.get("nonsense_patterns", [])
    )
    print(f"✅ QualityGate initialized")
    
    pg_config = config.get("policy_gate", {})
    policy_gate = PolicyGate(
        fixed_locations=pg_config.get("fixed_locations", []),
        unsupported_patterns=pg_config.get("unsupported_patterns", [])
    )
    print(f"✅ PolicyGate initialized")
    
    # Initialize Database
    init_database()
    print(f"✅ Database initialized")
    
    print("🎉 STT Pipeline API ready!\n")
    
    yield
    
    print("👋 Shutting down STT Pipeline API...")


# ============== FastAPI App ==============

app = FastAPI(
    title="Daiso STT Pipeline API",
    description="AI Product Location Guide - STT → QualityGate → PolicyGate Pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (프론트엔드 연결용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== WebSocket ==============

from fastapi import WebSocket
from backend.ws_stt import handle_streaming_stt

@app.websocket("/ws/stt")
async def websocket_stt_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming STT"""
    # Accept is handled inside handle_streaming_stt or needs to be done here?
    # backend/main.py just calls the handler. Let's look at main.py again... 
    # It says "Accept the connection first" but calls the handler directly.
    # We will replicate main.py's implementation.
    await handle_streaming_stt(websocket)


# ============== Endpoints ==============

@app.get("/")
def read_root():
    return {"message": "Daiso STT Pipeline API", "status": "running"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "transcription_model": "loaded" if whisper_adapter else "not loaded",
        "llm_model": "gemini-2.0-flash-exp"
    }

@app.get("/api/map/zones")
async def get_zones(floor: Optional[str] = None):
    try:
        zones = get_map_zones(floor)
        # Parse rect JSON string back to dict for response
        for z in zones:
            if 'rect' in z and isinstance(z['rect'], str):
                try:
                    z['rect'] = json.loads(z['rect'])
                except:
                    pass
        return zones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MapZoneCreate(BaseModel):
    floor: str
    name: str
    rect: dict
    color: str

class MapZoneDelete(BaseModel):
    id: int

@app.post("/api/map/zones")
async def create_zone_endpoint(zone: MapZoneCreate):
    try:
        rect_json = json.dumps(zone.rect)
        zone_id = save_map_zone(zone.floor, zone.name, rect_json, zone.color)
        return {"id": zone_id, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/map/zones/{zone_id}")
async def delete_zone_endpoint(zone_id: int):
    try:
        success = delete_map_zone(zone_id)
        if not success:
            raise HTTPException(status_code=404, detail="Zone not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stt/process", response_model=STTProcessResponse)
async def process_stt(
    audio: UploadFile = File(...),
    attempt: int = Form(default=1)
):
    """
    Process audio file through STT pipeline
    
    - **audio**: Audio file (wav, mp3, etc.)
    - **attempt**: Attempt number (1 or 2, for retry logic)
    
    Returns STT result with quality gate and policy gate decisions
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Save uploaded file to temp
    temp_path = None
    try:
        suffix = Path(audio.filename).suffix if audio.filename else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await audio.read()
            tmp.write(content)
            temp_path = tmp.name
        
        # STT Processing
        if whisper_adapter:
            stt_result = whisper_adapter.transcribe(temp_path)
        else:
            # Simulation mode (when whisper not available)
            stt_result = STTResult(
                text_raw="(시뮬레이션 모드 - Whisper 미로드)",
                confidence=0.8,
                lang="ko",
                latency_ms=100,
                error="Whisper adapter not loaded"
            )
        
        # Quality Gate
        quality_result = quality_gate.evaluate(stt_result, attempt=attempt)
        
        # Policy Gate (only if quality OK)
        policy_intent = None
        final_response = ""
        
        if quality_result.status == "OK":
            policy_intent = policy_gate.classify(stt_result.text_raw or "")
            
            pg_config = config.get("policy_gate", {})
            
            if policy_intent.intent_type == "FIXED_LOCATION":
                # Find response for fixed location
                for loc in pg_config.get("fixed_locations", []):
                    if loc["target"] == policy_intent.location_target:
                        final_response = loc["response"]
                        break
                if not final_response:
                    final_response = f"'{policy_intent.location_target}' 위치를 안내해 드립니다."
                    
            elif policy_intent.intent_type == "UNSUPPORTED":
                final_response = pg_config.get(
                    "fallback_message", 
                    "이 서비스는 상품과 매장 내 위치 안내를 도와드리고 있어요."
                )
            else:  # PRODUCT_SEARCH
                final_response = f"[PRODUCT_SEARCH] '{stt_result.text_raw}' 검색 예정"
                
        elif quality_result.status == "RETRY":
            pg_config = config.get("policy_gate", {})
            final_response = pg_config.get(
                "retry_message",
                "말씀을 잘 듣지 못했어요. 다시 말씀해 주세요."
            )
        else:  # FAIL
            final_response = "음성 인식에 실패했습니다. 다시 시도해 주세요."
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return STTProcessResponse(
            request_id=request_id,
            stt=STTResponseData(
                text_raw=stt_result.text_raw,
                confidence=stt_result.confidence,
                lang=stt_result.lang or "ko",
                latency_ms=stt_result.latency_ms,
                error=stt_result.error
            ),
            quality_gate=QualityGateData(
                status=quality_result.status,
                is_usable=quality_result.is_usable,
                reason=quality_result.reason
            ),
            policy_intent=PolicyIntentData(
                intent_type=policy_intent.intent_type,
                location_target=policy_intent.location_target,
                confidence=policy_intent.confidence,
                reason=policy_intent.reason
            ) if policy_intent else None,
            final_response=final_response,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# ============== AI Pipeline Endpoint ==============

@app.post("/api/query")
async def query_ai_pipeline(req: QueryRequest):
    """
    통합 AI 파이프라인 엔드포인트
    
    Intent Gate → NLU 분석 → Hybrid Search → LLM Re-ranking
    
    - **text**: 사용자 입력 텍스트
    - **session_id**: 세션 ID (대화 컨텍스트 유지용, 선택)
    - **history**: 대화 이력 [{"role": "user", "text": "..."}, ...]
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]

    try:
        from backend.ai_service.supervisor import agent_app
        from backend.ai_service.schemas import Intent, NLUResponse

        # Build pipeline input state
        input_state = {
            "request_id": request_id,
            "input_text": req.text,
            "session_id": req.session_id or str(uuid.uuid4())[:8],
            "history": req.history,
            "intent_valid": "",
            "intent": Intent.UNSUPPORTED,
            "slots": {},
            "expanded_keywords": [],
            "search_candidates": [],
            "rerank_result": {},
            "is_ambiguous": False,
            "clarification_count": 0,
            "final_response": NLUResponse(
                request_id=request_id,
                intent=Intent.UNSUPPORTED,
            ),
        }

        from backend.ai_service.config import log_pipeline
        log_pipeline("API Request Received", {"text": req.text, "session_id": req.session_id}, {})

        # Invoke LangGraph pipeline
        config = {"configurable": {"thread_id": req.session_id or request_id}}
        result = await agent_app.ainvoke(input_state, config=config)

        # Extract results
        final = result.get("final_response")
        slots_data = result.get("slots", {})
        rerank_data = result.get("rerank_result", {})
        products = []

        if final and hasattr(final, "products"):
            products = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "category_major": getattr(p, "category_major", ""),
                    "category_middle": getattr(p, "category_middle", ""),
                    "image_url": getattr(p, "image_url", ""),
                }
                if hasattr(p, "id") else p
                for p in (final.products or [])
            ]
        elif result.get("search_candidates"):
            products = result["search_candidates"]

        processing_time_ms = int((time.time() - start_time) * 1000)

        return QueryResponse(
            request_id=request_id,
            intent_valid=result.get("intent_valid", "N"),
            intent=str(result.get("intent", "UNSUPPORTED")),
            slots=SlotData(
                item=slots_data.get("item"),
                attrs=slots_data.get("attrs", []),
                category_hint=slots_data.get("category_hint"),
                query_rewrite=slots_data.get("query_rewrite"),
                min_price=slots_data.get("min_price"),
                max_price=slots_data.get("max_price"),
            ),
            rerank=RerankData(
                selected_id=rerank_data.get("selected_id"),
                reason=rerank_data.get("reason", ""),
                latency=rerank_data.get("latency", 0.0),
            ) if rerank_data else None,
            products=products,
            needs_clarification=final.needs_clarification if final else False,
            generated_question=final.generated_question if final else None,
            processing_time_ms=processing_time_ms,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Pipeline error: {str(e)}")
