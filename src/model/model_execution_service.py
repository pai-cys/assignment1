"""Model execution service for LLM model execution."""

import logging
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from src.model.domains import Model, ModelProvider
from src.model.service import ModelService
from src.model.settings import model_settings

logger = logging.getLogger(__name__)

class ModelExecutionService:
    """모델 실행 서비스 - OpenAI GPT-4o만 사용"""
    
    def __init__(self, model_service: ModelService):
        """모델 실행 서비스 초기화"""
        self.settings = model_settings
        self.model_service = model_service
        logger.info("ModelExecution 서비스 초기화 완료")
    
    async def load_llm_model(self, model_id: int) -> BaseChatModel:
        """LLM 모델을 로딩하여 반환"""
        model = await self._get_and_validate_model(model_id, "llm")
        
        # 프로바이더 정보 조회
        provider = await self._get_provider(model.model_provider_id)
        
        # OpenAI 모델 로딩
        if provider.model_vendor == "OpenAI":
            return self._create_openai_model(model)
        else:
            raise ValueError(f"지원하지 않는 벤더: {provider.model_vendor}")
    
    async def _get_and_validate_model(self, model_id: int, expected_type: str) -> Model:
        """모델을 조회하고 타입을 검증"""
        model = await self.model_service.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: model_id={model_id}")
        
        if model.model_type != expected_type:
            raise ValueError(f"model_id={model_id} is not a {expected_type} model.")
        
        return model
    
    async def _get_provider(self, provider_id: int) -> ModelProvider:
        """프로바이더 정보를 조회"""
        provider = await self.model_service.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider not found: provider_id={provider_id}")
        return provider
    
    def _create_openai_model(self, model: Model) -> BaseChatModel:
        """OpenAI 모델 생성"""
        return ChatOpenAI(
            model=model.model_config.get("model", "gpt-4o"),
            api_key=self.settings.openai_api_key,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
            streaming=self.settings.llm_streaming,
        )
    
    # 모델 정보 조회 메서드들
    async def get_model_info(self, model_id: int) -> Optional[dict]:
        """모델 정보를 반환 (실행 없이)"""
        return await self.model_service.get_model_info(model_id)
    
    async def get_available_models(self, model_type: Optional[str] = None) -> List[dict]:
        """사용 가능한 모델 목록을 반환"""
        return await self.model_service.get_available_models(model_type)
