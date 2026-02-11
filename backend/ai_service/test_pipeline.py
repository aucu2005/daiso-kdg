# backend/ai_service/test_pipeline.py
"""
E2E Test Script for AI Agent Pipeline

Usage:
    cd c:\\Users\\301\\finalProject\\daiso-category-search-dev-kdg
    set PYTHONIOENCODING=utf-8
    python -m backend.ai_service.test_pipeline

Required:
    - .env with GOOGLE_API_KEY
    - products.db with data
"""

import asyncio
import time
import sys
import os
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


async def test_intent_gate():
    """Test 1: Intent Gate (Y/N)"""
    from backend.ai_service.intent_keyword_node import _classify_intent

    print("=" * 60)
    print("Test 1: Intent Gate (Y/N)")
    print("=" * 60)

    test_cases = [
        ("볼펜 어디 있어?", "Y"),
        ("화장실 어디에요?", "Y"),
        ("충전 케이블 찾아줘", "Y"),
        ("오늘 날씨 어때?", "N"),
        ("욕실이 미끄러워", "Y"),
        ("안녕하세요", "N"),
        ("매트 있어?", "Y"),
        ("수납함 어디야?", "Y"),
    ]

    passed = 0
    for text, expected in test_cases:
        result = await _classify_intent(text)
        ok = result == expected
        passed += int(ok)
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} '{text}' -> {result} (expected: {expected})")

    print(f"\n  Result: {passed}/{len(test_cases)} passed\n")


async def test_nlu_analysis():
    """Test 2: NLU Analysis"""
    from backend.ai_service.intent_keyword_node import _analyze_text

    print("=" * 60)
    print("Test 2: NLU Analysis")
    print("=" * 60)

    test_cases = [
        ("볼펜 어디 있어?", "PRODUCT_LOCATION", "볼펜"),
        ("파란색 볼펜 있어?", "PRODUCT_LOCATION", "볼펜"),
        ("충전 케이블 찾아줘", "PRODUCT_LOCATION", "충전 케이블"),
        ("매트 있어?", "PRODUCT_LOCATION", "매트"),
        ("수납함 어디야?", "PRODUCT_LOCATION", "수납함"),
        ("5000원 이하 생일 선물", "PRODUCT_LOCATION", None),
        ("화장실 바닥 미끄러운 거 방지하는 거", "PRODUCT_LOCATION", None),
        ("배고파", "UNSUPPORTED", None),
    ]

    passed = 0
    for text, expected_intent, expected_item in test_cases:
        result = await _analyze_text(text)
        intent_ok = result.intent.value == expected_intent
        item_ok = expected_item is None or (result.slots.item and expected_item in result.slots.item)
        ok = intent_ok and (expected_item is None or item_ok)
        passed += int(ok)
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} '{text}'")
        print(f"     intent={result.intent.value} (expected: {expected_intent})")
        print(f"     item={result.slots.item}")
        print(f"     query_rewrite={result.slots.query_rewrite}")
        print(f"     latency={result.latency_ms}ms")
        print()

    print(f"  Result: {passed}/{len(test_cases)} passed\n")


async def test_keyword_expansion():
    """Test 3: Keyword Expansion"""
    from backend.ai_service.intent_keyword_node import _expand_search_keywords

    print("=" * 60)
    print("Test 3: Keyword Expansion")
    print("=" * 60)

    test_words = ["볼펜", "충전 케이블", "수납함", "매트"]

    for word in test_words:
        result = await _expand_search_keywords(word)
        print(f"  [KEY] '{word}' -> {result}")

    print()


async def test_search_quality():
    """Test 4: Search Quality (BM25 + Vector + Reranker)"""
    from backend.ai_service.supervisor import agent_app
    from backend.ai_service.schemas import Intent, NLUResponse

    print("=" * 60)
    print("Test 4: Search Quality (Full Pipeline E2E)")
    print("=" * 60)

    # query -> expected product name substring
    test_queries = [
        ("볼펜 어디 있어?", ["볼펜"]),
        ("충전 케이블 찾아줘", ["충전", "케이블", "USB"]),
        ("매트 있어?", ["매트"]),
        ("수납함 어디야?", ["수납"]),
        ("가위 있어?", ["가위"]),
        ("오늘 날씨 어때?", []),  # Should return no products (UNSUPPORTED)
    ]

    passed = 0
    for query, expected_keywords in test_queries:
        print(f"\n  [QUERY] '{query}'")
        start = time.time()

        input_state = {
            "request_id": "test",
            "input_text": query,
            "session_id": "test-session",
            "history": [],
            "intent_valid": "",
            "intent": Intent.UNSUPPORTED,
            "slots": {},
            "expanded_keywords": [],
            "search_candidates": [],
            "rerank_result": {},
            "is_ambiguous": False,
            "clarification_count": 0,
            "final_response": NLUResponse(
                request_id="test",
                intent=Intent.UNSUPPORTED,
            ),
        }

        config = {"configurable": {"thread_id": f"test-{hash(query)}"}}

        try:
            result = await agent_app.ainvoke(input_state, config=config)
            elapsed = int((time.time() - start) * 1000)

            intent = result.get("intent")
            candidates = result.get("search_candidates", [])
            rerank = result.get("rerank_result", {})
            final = result.get("final_response")

            # Check search quality
            if not expected_keywords:
                # Should NOT return products
                ok = len(candidates) == 0
                status = "[PASS]" if ok else "[FAIL]"
                print(f"  {status} intent={intent}, candidates={len(candidates)} (expected: 0)")
            else:
                # Check if top results contain expected keywords
                top_names = [c.get("name", "") for c in candidates[:5]]
                found = any(
                    any(kw in name for kw in expected_keywords)
                    for name in top_names
                )
                selected_name = ""
                if rerank and rerank.get("selected_id"):
                    sid = str(rerank["selected_id"])
                    for c in candidates:
                        if str(c.get("id")) == sid:
                            selected_name = c.get("name", "")
                            break

                rerank_ok = selected_name and any(kw in selected_name for kw in expected_keywords)
                ok = found and (rerank_ok or not selected_name)
                status = "[PASS]" if ok else "[FAIL]"

                print(f"  {status} intent={intent}")
                print(f"     candidates={len(candidates)}, top5={top_names}")
                print(f"     rerank_selected='{selected_name}' (reason: {rerank.get('reason', 'N/A')[:60]})")

            if final:
                q = final.generated_question or ""
                print(f"     response='{q[:80]}'")
            print(f"     time={elapsed}ms")

            passed += int(ok)

        except Exception as e:
            print(f"  [ERROR] {e}")

    print(f"\n  Result: {passed}/{len(test_queries)} passed\n")


async def main():
    print("\n[AI Service Pipeline E2E Test]")
    print("=" * 60)
    print()

    await test_intent_gate()
    await test_nlu_analysis()
    await test_keyword_expansion()
    await test_search_quality()

    print("=" * 60)
    print("[DONE] All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
