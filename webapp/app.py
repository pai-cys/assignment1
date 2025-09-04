"""FastAPI 애플리케이션 - 메인 앱 설정 및 라우터 등록"""
import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from webapp.middleware.streaming import StreamingMiddleware
from webapp.container import create_container
from webapp.logger import initialize_logger

from webapp.routers import health, chat

# 환경변수 로드
load_dotenv()

# 로깅 설정
logger = initialize_logger()


# 모델들은 각 라우터 파일로 이동됨


def check_environment():
    """환경 설정 체크"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OpenAI API 키가 설정되지 않았습니다!")
        logger.info("📝 .env 파일에 OPENAI_API_KEY=your_api_key_here 추가")
        sys.exit(1)
    logger.info("✅ 환경 설정 완료")


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""
    # 환경 체크
    check_environment()
    
    # 컨테이너 생성
    container = create_container()
    
    # FastAPI 앱 생성
    app = FastAPI(
        title="Stock Analysis Chatbot API",
        description="Layered Architecture를 적용한 주가 분석 챗봇 API",
        version="2.0.0"
    )
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 스트리밍 미들웨어 추가
    app.add_middleware(StreamingMiddleware)
    
    # 라우터 등록
    app.include_router(health.router)
    app.include_router(chat.router)
    
    # 컨테이너를 앱에 연결
    app.container = container
    
    return app


# FastAPI 앱 인스턴스
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 주가 분석 챗봇 서버 시작 (Layered Architecture)")
    logger.info("🌐 서버 주소: http://localhost:8000")
    logger.info("📚 API 문서: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
