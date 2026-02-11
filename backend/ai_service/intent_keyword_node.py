# backend/ai_service/intent_keyword_node.py
"""
Pipeline Node 1: Intent & Keyword
- Step 1: Intent Gate (Y/N) — 응대 필요 여부 판별
- Step 2: NLU Analysis — intent, slots, needs_clarification
- Step 3: Keyword Expansion — 검색 키워드 확장

Architecture: Supervisor → [Intent & Keyword] → Hybrid Searcher → LLM Re-ranker
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional

from .config import get_genai, MODEL_NAME, log_debug
from .schemas import PipelineState, Intent, NLUSlots, NLUResponse
from .prompts import (
    INTENT_GATE_PROMPT,
    NLU_SYSTEM_PROMPT,
    KEYWORD_EXPANSION_PROMPT,
    AUX_PROMPT_KEYWORDS,
)


# ─── Intent Gate ─────────────────────────────────────────────

async def _classify_intent(text: str) -> str:
    """
    Classify user utterance as Y (assistance needed) or N (ignore).
    Uses Gemini 2.0 Flash with temperature=0.0 for deterministic output.
    """
    genai = get_genai()
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 5,
        },
    )

    prompt = f"{INTENT_GATE_PROMPT}\n\nUser Utterance: \"{text}\"\nOutput (Y or N):"

    try:
        response = await model.generate_content_async(prompt)
        raw = response.text.strip().upper()
        result = "Y" if raw.startswith("Y") else "N"
        log_debug(f"[Intent Gate] '{text}' → {result}")
        return result
    except Exception as e:
        log_debug(f"[Intent Gate] Error: {e} → defaulting to Y")
        return "Y"  # Fail-open: assume assistance needed


# ─── NLU Analysis ────────────────────────────────────────────

def _robust_json_parse(text: str) -> dict:
    """
    Parse JSON with repair for common Gemini issues:
    - Truncated strings (Unterminated string)
    - Missing closing braces
    - Trailing commas
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Attempt repairs
    repaired = text.strip()

    # Remove trailing commas before } or ]
    import re
    repaired = re.sub(r',\s*([}\]])', r'\1', repaired)

    # Close unclosed strings (find odd number of unescaped quotes)
    if repaired.count('"') % 2 != 0:
        repaired += '"'

    # Close unclosed braces/brackets
    open_braces = repaired.count('{') - repaired.count('}')
    open_brackets = repaired.count('[') - repaired.count(']')
    repaired += ']' * max(0, open_brackets)
    repaired += '}' * max(0, open_braces)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Last resort: extract the first JSON-like object
    match = re.search(r'\{.*', repaired, re.DOTALL)
    if match:
        fragment = match.group()
        # Aggressively close it
        if '"' in fragment and fragment.count('"') % 2 != 0:
            fragment += '"'
        fragment += '}' * (fragment.count('{') - fragment.count('}'))
        try:
            return json.loads(fragment)
        except json.JSONDecodeError:
            pass

    raise json.JSONDecodeError("Cannot repair JSON", text, 0)


async def _analyze_text(text: str, history: List[Dict] = None, max_retries: int = 2) -> NLUResponse:
    """
    Analyze text using Gemini with response_schema for structured JSON output.
    Includes retry logic for intermittent JSON parse failures.
    """
    genai = get_genai()

    response_schema = {
        "type": "object",
        "properties": {
            "intent": {"type": "string", "enum": ["PRODUCT_LOCATION", "OTHER_INQUIRY", "UNSUPPORTED"]},
            "slots": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "nullable": True},
                    "attrs": {"type": "array", "items": {"type": "string"}},
                    "category_hint": {"type": "string", "nullable": True},
                    "query_rewrite": {"type": "string", "nullable": True},
                    "min_price": {"type": "integer", "nullable": True},
                    "max_price": {"type": "integer", "nullable": True},
                },
            },
            "needs_clarification": {"type": "boolean"},
        },
        "required": ["intent", "slots", "needs_clarification"],
    }

    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": response_schema,
            "temperature": 0.0,
            "max_output_tokens": 256,
        },
    )

    # Build conversation context
    messages = [{"role": "user", "parts": [NLU_SYSTEM_PROMPT]}]
    messages.append({"role": "model", "parts": ["Understood. Send me the user query."]})

    if history:
        history_text = "\n".join(
            [f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['text']}" for h in history[-6:]]
        )
        messages.append({"role": "user", "parts": [f"Conversation History:\n{history_text}"]})
        messages.append({"role": "model", "parts": ["Context noted."]})

    messages.append({"role": "user", "parts": [text]})

    request_id = str(uuid.uuid4())[:8]

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            response = await model.generate_content_async(messages)
            latency_ms = int((time.time() - start_time) * 1000)

            # Robust JSON parsing with repair
            parsed = _robust_json_parse(response.text)
            log_debug(f"[NLU] '{text}' → {parsed.get('intent')} | latency={latency_ms}ms" +
                      (f" (retry {attempt})" if attempt > 0 else ""))

            # Extract token usage
            token_usage = {}
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                um = response.usage_metadata
                token_usage = {
                    "prompt_tokens": getattr(um, "prompt_token_count", 0),
                    "completion_tokens": getattr(um, "candidates_token_count", 0),
                    "total_tokens": getattr(um, "total_token_count", 0),
                }

            slots_data = parsed.get("slots", {})

            # Safety: truncate query_rewrite to prevent hallucination bloat
            qr = slots_data.get("query_rewrite")
            if qr and len(qr) > 50:
                qr = qr[:50].strip()
                slots_data["query_rewrite"] = qr
                log_debug(f"[NLU] query_rewrite truncated to 50 chars")

            return NLUResponse(
                request_id=request_id,
                intent=Intent(parsed["intent"]),
                slots=NLUSlots(
                    item=slots_data.get("item"),
                    attrs=slots_data.get("attrs", []),
                    category_hint=slots_data.get("category_hint"),
                    query_rewrite=slots_data.get("query_rewrite"),
                    min_price=slots_data.get("min_price"),
                    max_price=slots_data.get("max_price"),
                ),
                needs_clarification=parsed.get("needs_clarification", False),
                model_name=MODEL_NAME,
                latency_ms=latency_ms,
                token_usage=token_usage,
            )

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                log_debug(f"[NLU] Attempt {attempt + 1} failed: {e} → retrying...")
                import asyncio
                await asyncio.sleep(0.5)  # Brief pause before retry
            else:
                log_debug(f"[NLU] All {max_retries + 1} attempts failed: {e}")

    # All retries exhausted — return safe fallback
    return NLUResponse(
        request_id=request_id,
        intent=Intent.UNSUPPORTED,
        slots=NLUSlots(),
        needs_clarification=False,
    )


# ─── Keyword Expansion ──────────────────────────────────────

async def _expand_search_keywords(product_name: str) -> List[str]:
    """
    Expand a product name into a list of search keywords.
    Returns: ["욕실매트", "욕실", "매트", "욕실용품", "미끄럼방지"]
    """
    if not product_name:
        return []

    genai = get_genai()
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = KEYWORD_EXPANSION_PROMPT.replace("{product_name}", f'"{product_name}"')

    try:
        response = await model.generate_content_async(prompt)
        keywords = json.loads(response.text)
        if isinstance(keywords, list):
            log_debug(f"[Keyword Expand] '{product_name}' → {keywords}")
            return keywords
        return [product_name]
    except Exception as e:
        log_debug(f"[Keyword Expand] Error: {e}")
        return [product_name]


# ─── Keyword Inference (Problem → Product) ───────────────────

async def _infer_product_keywords(text: str) -> List[str]:
    """
    Infer probable product keywords from a problem/usage description.
    e.g., "욕실이 미끄러워" → ["미끄럼방지 매트", "논슬립 패드"]
    """
    genai = get_genai()
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = AUX_PROMPT_KEYWORDS.replace("{text}", text)

    try:
        response = await model.generate_content_async(prompt)
        keywords = json.loads(response.text)
        if isinstance(keywords, list):
            log_debug(f"[Keyword Infer] '{text}' → {keywords}")
            return keywords
        return []
    except Exception as e:
        log_debug(f"[Keyword Infer] Error: {e}")
        return []


# ─── LangGraph Node Function ────────────────────────────────

async def intent_keyword_node(state: PipelineState) -> dict:
    """
    LangGraph node: Intent & Keyword
    Performs Intent Gate → NLU Analysis → Keyword Expansion
    """
    input_text = state["input_text"]
    history = state.get("history", [])
    log_debug(f"--- [Node: Intent & Keyword] Input: '{input_text}' ---")

    # Step 1: Intent Gate (Y/N)
    intent_valid = await _classify_intent(input_text)

    if intent_valid == "N":
        log_debug("[Node: Intent & Keyword] → N (무관한 발화). Skipping NLU.")
        return {
            "intent_valid": "N",
            "intent": Intent.UNSUPPORTED,
            "slots": {},
            "expanded_keywords": [],
            "final_response": NLUResponse(
                request_id=str(uuid.uuid4())[:8],
                intent=Intent.UNSUPPORTED,
                needs_clarification=True,
                generated_question="죄송합니다. 상품 찾기와 관련된 질문을 해주세요. 예: '볼펜 어디 있어?'",
            ),
        }

    # Step 2: NLU Analysis (Y인 경우)
    nlu_result = await _analyze_text(input_text, history=history)

    # Step 3: Keyword Expansion (PRODUCT_LOCATION인 경우)
    # ... existing logging ...
    log_debug(f"--- [Node: Intent] Intent={nlu_result.intent}, Item='{nlu_result.slots.item}' ---")
    
    from .config import log_pipeline
    log_pipeline("Intent & Keyword", {"input_text": state["input_text"]}, {
        "intent": nlu_result.intent,
        "item": nlu_result.slots.item,
        "category_hint": nlu_result.slots.category_hint,
        "query_rewrite": nlu_result.slots.query_rewrite
    })

    expanded_keywords = []
    if nlu_result.intent == Intent.PRODUCT_LOCATION:
        item_name = nlu_result.slots.item or nlu_result.slots.query_rewrite
        if item_name:
            expanded_keywords = await _expand_search_keywords(item_name)

    return {
        "intent_valid": "Y",  # Assume valid if parsing succeeded
        "intent": nlu_result.intent,
        "slots": {
            "item": nlu_result.slots.item,
            "category_hint": nlu_result.slots.category_hint,
            "query_rewrite": nlu_result.slots.query_rewrite,
            "attrs": nlu_result.slots.attrs,
            "min_price": nlu_result.slots.min_price,
            "max_price": nlu_result.slots.max_price,
        },
        "expanded_keywords": expanded_keywords,
        "final_response": nlu_result,
    }
