"""LLM 설정 관리"""
import logging
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)


class LLMSettings(BaseSettings):
    """LLM 설정 관리 클래스 - Pydantic 기반"""
    
    # OpenAI 설정 - .env에서 OPENAI_API_KEY 가져옴
    openai_api_key: str
    
    # 기본 LLM 설정
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: Optional[int] = 1000
    llm_streaming: bool = True
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# 전역 설정 인스턴스
llm_settings = LLMSettings()