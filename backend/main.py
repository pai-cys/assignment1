"""FastAPI 주가 분석 챗봇 서버 - 메인 애플리케이션"""
import os
import sys
from pathlib import Path
import logging
import uvicorn

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from fastapi import FastAPI

# API 라우터 임포트
from backend.api import chat, monitoring

# .env 파일 로드 및 환경 체크
load_dotenv()

def check_environment():
    """환경 설정 체크"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API 키가 설정되지 않았습니다!")
        print("\n📝 설정 방법:")
        print("1. cp env_template .env")
        print("2. .env 파일에서 OPENAI_API_KEY를 실제 키로 교체")
        print("3. python main.py 다시 실행")
        sys.exit(1)
    print("✅ 환경 설정 완료")

# 환경 체크 실행
check_environment()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="Stock Analysis Chatbot", version="1.0.0")

# API 라우터 포함
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(monitoring.router, tags=["Monitoring"])

# 서버 실행
if __name__ == "__main__":
    print("🚀 주가 분석 챗봇 시작...")
    print("🌐 서버 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("\n💡 사용 예시:")
    print("curl -X POST 'http://localhost:8000/chat/stream' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"message\": \"AAPL 주가 알려줘\"}'")
    print("\n🛑 종료: Ctrl+C\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
