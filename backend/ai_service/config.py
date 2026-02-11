# backend/ai_service/config.py
"""
Shared configuration for AI Service Layer.
- Gemini API initialization (singleton)
- Model constants
- Debug logging utility
"""

import os
import datetime
import warnings
from dotenv import load_dotenv

# Suppress google.generativeai deprecation warning
# TODO: Migrate to google.genai SDK (requires API surface change in all nodes)
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

load_dotenv()

# ─── Constants ───────────────────────────────────────────────
MODEL_NAME = "gemini-2.0-flash"

# ─── Gemini Singleton ────────────────────────────────────────
_genai = None


def get_genai():
    """
    Initialize and return the google.generativeai module (singleton).
    Reads GEMINI_API_KEY or GOOGLE_API_KEY from environment.
    """
    global _genai
    if _genai is None:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required."
            )
        genai.configure(api_key=api_key)
        _genai = genai
    return _genai


# ─── Logging ─────────────────────────────────────────────────
_LOG_FILE = "ai_service_debug.log"


def log_debug(message: str):
    """Simple debug logger with timestamp and file output."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted = f"[{timestamp}] [DEBUG] {message}"
    print(formatted)
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def log_pipeline(step: str, inputs: dict, outputs: dict):
    """
    Structured logger for pipeline steps.
    Prints inputs and outputs in a readable format.
    """
    import json
    print(f"\n{'='*20} [PIPELINE: {step}] {'='*20}")
    print(f"📥 INPUTS: {json.dumps(inputs, ensure_ascii=False, default=str)[:200]}...")
    print(f"📤 OUTPUTS: {json.dumps(outputs, ensure_ascii=False, indent=2, default=str)}")
    print(f"{'='*60}\n")
