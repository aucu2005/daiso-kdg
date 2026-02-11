
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Try getting from standard env var if specific one not found
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY or GOOGLE_API_KEY not found in .env")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash") # Reverted to 2.0-flash for optimized prompt performance


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Project Root
INPUT_JSON_PATH = os.path.join(BASE_DIR, "poc", "data", "intent_output.json")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "poc", "data", "extracted_keywords.json")

def load_data():
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"Error: Input file not found at {INPUT_JSON_PATH}")
        print("Please run 'poc_flash_test.py' (Intent Check) first.")
        return []
    
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

def extract_keyword(query):
    # Improved Prompt: From Extraction to Reasoning/Recommendation
    # Hybrid Prompting Strategy: Top-Down Classification + Specific Rules
    prompt = f"""
    # Role
    당신은 다이소의 **'상품 카테고리 분류 전문가'**입니다.
    고객의 모호한 질문(특징, 상황, 묘사)을 분석하여, 다이소의 **표준 상품군(Standard Category Keyword)** 하나를 도출해야 합니다.

    # [Goal]
    3만 개의 개별 상품명(SKU)을 맞추는 것이 아닙니다.
    검색이 가능한 **'가장 구체적인 카테고리명'**이나 **'대표 상품명'**을 출력하세요.

    # [Thinking Strategy: 2-Step Classification]
    1. **대분류/중분류 판단**: 고객의 의도가 어느 영역인가? (다이소몰 공식 카테고리)
    - [청소/욕실]: 청소용품, 세탁용품, 욕실용품, 변기/배수구용품, 휴지/물티슈, 살충제/제습제, 휴지통/비닐봉투, 주방/청소세제, 세탁세제, 수건/타월, 방충용품
    - [국민득템]: 신상(NEW), 인기상품(BEST), 균일가
    - [뷰티/위생]: 스킨케어, 메이크업, 네일용품, 미용소품, 맨케어, 헤어/바디, 화장지/물티슈, 건강/위생용품, 가정의료용품, 마스크, 칫솔/치약/구강용품
    - [주방용품]: 식기/그릇/트레이, 잔/컵/물병, 밀폐/보관/저장용기, 수저/커트러리, 주방잡화, 주방수납정리, 일회용품, 팬/냄비/뚝배기, 칼/도마/채칼/가위, 조리도구, 베이킹용품, 와인용품, 커피/티용품
    - [수납/정리]: 수납정리함, 바구니류, 사무수납, 행거/후크, 네트망, 옷걸이, 보관커버
    - [문구/팬시]: 다이어리/노트/메모, 폴꾸용품, 스티커류, 문구/사무용품, 필기용품, 편지/봉투, 포장용품, 테이프, 미술용품, 보드/칠판, 파티/이벤트용품
    - [인테리어/원예]: 시계/액자, 아로마/캔들용품, 원예용품, 조화, 안전용품, 다용도매트, 시트지, 커튼용품, 침구/쿠션/방석, 단열/방한용품, 장식소품, 테이블/의자
    - [공구/디지털]: 공구용품, 건전지/콘센트, 조명/전구, 컴퓨터, 휴대폰, 이어폰, 소형가전
    - [식품]: 건강식품, 과자, 음료/커피/차, 사탕/초콜릿/젤리, 견과류/포, 라면/즉석식품, 기타식품
    - [스포츠/레저/취미]: 캠핑/여행, 자동차용품, 홈트레이닝, 구기/라켓운동, 등산/수영/골프, 자전거용품, 스포츠잡화, 취미/기호, 수예용품
    - [패션/잡화]: 의류/언더웨어, 가방, 패션소품, 양말/스타킹, 신발, 슈즈용품, 우천용품
    - [반려동물]: 반려동물완구, 고양이식품, 강아지식품, 위생/미용용품, 외출용품/하우스, 의류/액세서리, 식기/급수기, 관상어/소동물용품
    - [유아/완구]: 역할놀이, 인형, 만들기완구, 로봇/작동완구, 지능개발완구, 어린이도서, 놀이완구, 물놀이완구, 유아용품
    - [시즌/시리즈]: 디즈니, 짱구, 마이멜로디, 피너츠, 모모레이, 다이소굿즈
    - [상품권]: 모바일 상품권

    # [Brainstorming Rules for Accuracy]
    (A) Material Context: "열, 물, 충격"에 따라 소재 구분 (멜라민 vs 실리콘 vs 내열유리)
    (B) Verb Trap: "닦는(Active) 것" vs "닦이는(Passive) 것" 구분 (청소포 vs 시트지)
    (C) Fashion Suppression: "얇은, 튼튼한" 형용사만 있을 때 패션보다 생활/수납 우선

    # [Core Strategy: 4대 행동 패턴]
    1. 문제 해결형 ("냄새나", "더러워") -> 해결책 (탈취제, 배수구망)
    2. 안전/보호형 ("깨질까봐", "다칠까봐") -> 예방 (모서리보호대, 멜라민식기)
    3. 편의/효율성 ("힘 안들이고", "손 안대고") -> 도구 (자동디스펜서, 튜브짜개)
    4. 공간 정리 ("섞이지 않게", "틈새") -> 분할/수납 (칸막이정리함, 꼭꼬핀)

    # Current Query: "{query}"

    # Output Format
    Reasoning: <Category> - <Analysis>
    Primary Keyword: <One Standard Keyword>
    """
    
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        latency = end_time - start_time
        
        response_text = response.text.strip()
        keyword = ""
        
        # Parse "Primary Keyword:"
        for line in response_text.split('\n'):
            if "Primary Keyword:" in line:
                keyword = line.split("Primary Keyword:")[1].strip()
                if "(" in keyword: keyword = keyword.split("(")[0].strip()
                break
        
        if not keyword:
            for line in response_text.split('\n'):
                 if "Keyword:" in line and "Primary" not in line:
                    keyword = line.split("Keyword:")[1].strip()
                    if "(" in keyword: keyword = keyword.split("(")[0].strip()
                    break

        usage = response.usage_metadata
        
        return {
            "keyword": keyword,
            "latency": latency,
            "tokens": {
                "prompt": usage.prompt_token_count,
                "completion": usage.candidates_token_count,
                "total": usage.total_token_count
            }
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    data_list = load_data()
    if not data_list:
        return

    print(f"Loaded {len(data_list)} items from STT output.")
    print("-" * 50)
    
    output_dir = os.path.dirname(OUTPUT_JSON_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Saving extracted keywords to: {OUTPUT_JSON_PATH}")

    processed_data = []

    for i, item in enumerate(data_list):
        query = item.get("utterance", "").strip()
        
        if not query:
            print(f"[{i+1}] Skipping empty utterance.")
            item["extraction"] = {"error": "Empty utterance"}
            processed_data.append(item)
            continue
            
        print(f"[{i+1}/{len(data_list)}] Processing: {query}", end=" -> ")
        
        result = extract_keyword(query)
        
        # Append result to item structure
        item["extraction"] = result
        
        if "error" in result:
             print(f"Error: {result['error']}")
        else:
             print(f"Keyword: {result['keyword']}")
        
        processed_data.append(item)
        
        # Frequent save (optional, but good for long running)
        if (i+1) % 5 == 0:
             with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)

    # Final Save
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"\nAnalysis complete. Results saved to {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()

