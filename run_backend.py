
import os
import sys
import time

print("="*50)
print("🚀 백엔드 서버를 시작합니다...")
print("초기화에 20~30초 정도 소요될 수 있습니다.")
print("멈춘 것이 아니니 잠시만 기다려 주세요.")
print("="*50)

try:
    import uvicorn
    
    # 직접 uvicorn 실행
    if __name__ == "__main__":
        print("⏳ Uvicorn 서버 준비 중... (로그 레벨: info)")
        uvicorn.run(
            "backend.api:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
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
