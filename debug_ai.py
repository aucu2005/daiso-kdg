
import sys
import time
import os

print("--- AI Pipeline Debugger ---")

def step(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}...", end="", flush=True)
    start = time.time()
    return start

def done(start):
    print(f" DONE ({time.time() - start:.2f}s)")

try:
    s = step("Importing chromadb")
    import chromadb
    done(s)

    s = step("Importing langchain")
    import langchain
    done(s)

    s = step("Importing langgraph")
    import langgraph
    done(s)
    
    s = step("Importing backend.ai_service.vector_store")
    from backend.ai_service.vector_store import VectorStore
    done(s)

    s = step("Initializing VectorStore (checks chromadb client)")
    vs = VectorStore()
    # Force client initialization
    vs._get_client()
    done(s)

    s = step("Importing backend.ai_service.supervisor")
    from backend.ai_service.supervisor import agent_app
    done(s)

    print("\n✅ AI Pipeline imports successful.")

except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")
