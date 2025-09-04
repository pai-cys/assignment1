"""Model settings for configuration management."""

import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class ModelSettings(BaseSettings):
    """모델 관련 설정 - OpenAI만 사용"""
    
    # OpenAI 설정 - .env에서 OPENAI_API_KEY 가져옴
    openai_api_key: str
    
    # 기본 LLM 설정
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    llm_streaming: bool = True
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# 전역 설정 인스턴스
model_settings = ModelSettings()
