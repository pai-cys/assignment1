"""Health and system endpoints."""

import logging
from datetime import datetime
from fastapi import APIRouter

from webapp.dtos import HealthResponse

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="", tags=["Health"])

@router.get("/", response_model=dict)
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Stock Analysis Chatbot API v2.0",
        "architecture": "Layered Architecture",
        "docs": "/docs",
        "health": "/health"
    }

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스체크"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0"
    )
