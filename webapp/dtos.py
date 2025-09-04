"""Data Transfer Objects for webapp."""

import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

logger = logging.getLogger(__name__)

class CamelModel(BaseModel):
    """FastAPI의 모든 Request, Response 모델에 CamelCase를 적용"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

# 요청 모델들
class ChatRequest(CamelModel):
    """채팅 요청 모델"""
    message: str
    session_id: Optional[str] = None

# 응답 모델들
class ChatResponse(CamelModel):
    """채팅 응답 모델"""
    content: str
    session_id: str
    message_id: Optional[str] = None
    timestamp: Optional[datetime] = None

class HealthResponse(CamelModel):
    """헬스체크 응답 모델"""
    status: str
    timestamp: datetime
    version: str

class OkDTO(CamelModel):
    """성공 응답 모델"""
    ok: bool = True
