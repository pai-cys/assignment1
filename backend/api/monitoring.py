"""서버 상태 및 정보 API 라우터"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """API 정보"""
    return {
        "message": "Stock Analysis Chatbot API",
        "streamlit_ui": "To run UI: `streamlit run frontend/streamlit_app.py`",
        "docs": "/docs",
        "health": "/health"
    }

@router.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy"}