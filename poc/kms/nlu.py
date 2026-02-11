
import os
import json
import uuid
import time
import datetime
import asyncio
from typing import List, Dict
from dotenv import load_dotenv
from .schemas import NLUResponse, Intent, NLUSlots
from .prompts import SYSTEM_PROMPT_V1, TAIL_QUESTION_PROMPT, AUX_PROMPT_KEYWORDS, KEYWORD_EXPANSION_PROMPT

load_dotenv()

_genai = None
MODEL_NAME = "gemini-2.0-flash"

def get_genai():
    global _genai
    if _genai is None:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        _genai = genai
    return _genai

def log_debug(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"[{timestamp}] {msg}")
    try:
        with open("nlu_debug.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except:
        pass

async def analyze_text(text: str, history: List[Dict[str, str]] = []) -> NLUResponse:
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    log_debug(f"[{request_id}] Analyzing: {text} | History: {len(history)} turns")

    # Format History
    history_text = ""
    if history:
        history_text = "## Conversation History\n"
        for turn in history:
            role = turn["role"]
            content = turn["text"]
            history_text += f"{role}: {content}\n"
    
    try:
        genai = get_genai()
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_PROMPT_V1, 
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "OBJECT",
                    "properties": {
                        "intent": {"type": "STRING"},
                        "slots": {
                            "type": "OBJECT",
                            "properties": {
                                "item": {"type": "STRING", "nullable": True},
                                "attrs": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "category_hint": {"type": "STRING", "nullable": True},
                                "query_rewrite": {"type": "STRING", "nullable": True},
                                "min_price": {"type": "INTEGER", "nullable": True},
                                "max_price": {"type": "INTEGER", "nullable": True}
                            }
                        },
                        "needs_clarification": {"type": "BOOLEAN"}
                    }
                }
            }
        )
        
        # Combine System Prompt + History + Current Input
        # Note: Gemini system_instruction is set above, but to be safe and explicit with context:
        final_prompt = f"{history_text}\nUser's Current Input: {text}"
        
        # Async call
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, final_prompt),
            timeout=5.0
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0} 
        
        if hasattr(response, "usage_metadata"):
             usage["prompt_tokens"] = response.usage_metadata.prompt_token_count
             usage["completion_tokens"] = response.usage_metadata.candidates_token_count
             usage["total_tokens"] = response.usage_metadata.total_token_count
        
        # Fallback Estimation
        if usage.get("total_tokens", 0) == 0:
             usage["prompt_tokens"] = max(1, len(final_prompt) // 4)
             usage["completion_tokens"] = max(1, len(response.text) // 4)
             usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]

        data = json.loads(response.text)
        
        intent_val = data.get("intent", "UNSUPPORTED")
        if intent_val not in Intent.__members__:
            intent_val = "UNSUPPORTED"
            
        return NLUResponse(
            request_id=request_id,
            intent=Intent[intent_val],
            slots=NLUSlots(**data.get("slots", {})),
            needs_clarification=data.get("needs_clarification", False),
            latency_ms=latency_ms,
            token_usage=usage
        )

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        log_debug(f"[{request_id}] Error: {e}")
        return NLUResponse(
            request_id=request_id,
            intent=Intent.UNSUPPORTED,
            slots=NLUSlots(),
            needs_clarification=False,
            generated_question=f"Error: {str(e)}",
            latency_ms=latency_ms
        )

async def generate_tail_question(context: str, slots: dict, db_context: str = "") -> str:
    try:
        genai = get_genai()
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        
        formatted_prompt = TAIL_QUESTION_PROMPT.format(
            context=context, 
            slots=json.dumps(slots, ensure_ascii=False),
            db_context=db_context
        )
        
        response = await asyncio.to_thread(model.generate_content, formatted_prompt)
        return response.text.strip()
    except Exception:
        return "자세히 말씀해 주시면 찾아드릴게요."

async def infer_product_keywords(text: str, return_usage: bool = False) -> list[str] | tuple[list[str], dict]:
    try:
        genai = get_genai()
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        prompt = AUX_PROMPT_KEYWORDS.format(text=text)
        
        # Capture response object to get usage
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if hasattr(response, "usage_metadata"):
             usage["prompt_tokens"] = response.usage_metadata.prompt_token_count
             usage["completion_tokens"] = response.usage_metadata.candidates_token_count
             usage["total_tokens"] = response.usage_metadata.total_token_count
        
        # Fallback Estimation
        if usage.get("total_tokens", 0) == 0:
             usage["prompt_tokens"] = max(1, len(prompt) // 4)
             usage["completion_tokens"] = max(1, len(response.text) // 4)
             usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        
        keywords = json.loads(response.text)
        if not isinstance(keywords, list): keywords = []
        
        if return_usage:
            return keywords, usage
        return keywords
        
    except Exception as e:
        log_debug(f"Inference error: {e}")
        empty_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if return_usage:
            return [], empty_usage
        return []

async def expand_search_keywords(product_name: str, return_usage: bool = False) -> List[str] | tuple[List[str], dict]:
    try:
        genai = get_genai()
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        prompt = KEYWORD_EXPANSION_PROMPT.format(product_name=product_name)
        
        start_time = time.time()
        response = await asyncio.to_thread(model.generate_content, prompt)
        end_time = time.time()
        latency = end_time - start_time
        
        usage = {
            "prompt_tokens": 0, 
            "completion_tokens": 0, 
            "total_tokens": 0,
            "latency_seconds": latency
        }
        if hasattr(response, "usage_metadata"):
             usage["prompt_tokens"] = response.usage_metadata.prompt_token_count
             usage["completion_tokens"] = response.usage_metadata.candidates_token_count
             usage["total_tokens"] = response.usage_metadata.total_token_count
             
        # Fallback Estimation
        if usage.get("total_tokens", 0) == 0:
             usage["prompt_tokens"] = max(1, len(prompt) // 4)
             usage["completion_tokens"] = max(1, len(response.text) // 4)
             usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
             
        keywords = json.loads(response.text)
        if not isinstance(keywords, list): keywords = [product_name]
        
        if return_usage:
            return keywords, usage
        return keywords

    except Exception as e:
        log_debug(f"Keyword expansion error for {product_name}: {e}")
        empty_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if return_usage:
             return [product_name], empty_usage
        return [product_name]
