
import os
import sys
import time

print("="*50)
print("🚀 백엔드 서버를 시작합니다 (Reload 모드 끔)...")
print("초기화(AI 모델 로딩)에 30초 이상 소요될 수 있습니다.")
print("이 창을 끄지 마시고 기다려 주세요.")
print("="*50)

# 강제 출력 플러시
sys.stdout.flush()

try:
    import uvicorn
    
    if __name__ == "__main__":
        print("⏳ 서버 시작 중...")
        uvicorn.run(
            "backend.api:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=False,  # Reload 끔 (재시작 방지, 속도 향상)
            log_level="info" 
        )

except ImportError:
    print("❌ uvicorn 모듈을 찾을 수 없습니다. 'pip install uvicorn'을 실행해 주세요.")
except KeyboardInterrupt:
    print("\n👋 서버를 종료합니다.")
except Exception as e:
    print(f"\n❌ 서버 실행 중 에러 발생: {e}")
    import traceback
    traceback.print_exc()

input("\n종료하려면 Enter 키를 누르세요...")
