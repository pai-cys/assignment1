"""Model service for LLM model management."""

import logging
from typing import List, Optional
from src.model.domains import Model, ModelProvider, get_default_models
from src.model.settings import model_settings

logger = logging.getLogger(__name__)

class ModelService:
    """모델 서비스 - OpenAI GPT-4o만 사용하는 단순화된 버전"""
    
    def __init__(self):
        """모델 서비스 초기화"""
        self.settings = model_settings
        logger.info("Model 서비스 초기화 완료")
    
    # Model CRUD (단순화된 버전)
    async def get_model(self, model_id: int) -> Optional[Model]:
        """모델 ID로 모델 조회 - 현재는 기본 모델만 반환"""
        if model_id == 1:  # 기본 GPT-4o 모델
            return Model(
                model_id=1,
                model_provider_id=1,
                model_name="gpt-4o",
                model_type="llm",
                model_config={"model": "gpt-4o", "enable_tool_calling": True},
                use_custom=False,
                is_deleted=False,
                created_at=None  # 실제로는 datetime.now()
            )
        return None
    
    async def get_models_by_type(self, model_type: str) -> List[Model]:
        """모델 타입으로 모든 모델 조회"""
        if model_type == "llm":
            return [await self.get_model(1)]
        return []
    
    async def get_all_models(self) -> List[Model]:
        """모든 모델 조회"""
        return [await self.get_model(1)]
    
    # ModelProvider CRUD (단순화된 버전)
    async def get_provider(self, provider_id: int) -> Optional[ModelProvider]:
        """프로바이더 ID로 프로바이더 조회"""
        if provider_id == 1:  # OpenAI 프로바이더
            return ModelProvider(
                model_provider_id=1,
                model_provider_name="OpenAI",
                model_key_id=1,
                model_vendor="OpenAI",
                is_deleted=False,
                created_at=None  # 실제로는 datetime.now()
            )
        return None
    
    async def get_all_providers(self) -> List[ModelProvider]:
        """모든 프로바이더 조회"""
        return [await self.get_provider(1)]
    
    # 모델 정보 조회 메서드들
    async def get_model_info(self, model_id: int) -> Optional[dict]:
        """모델 정보를 반환 (실행 없이)"""
        model = await self.get_model(model_id)
        if not model:
            return None
        
        return {
            "model_id": model.model_id,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "model_config": model.model_config,
            "use_custom": model.use_custom,
        }
    
    async def get_available_models(self, model_type: Optional[str] = None) -> List[dict]:
        """사용 가능한 모델 목록을 반환"""
        if model_type:
            models = await self.get_models_by_type(model_type)
        else:
            models = await self.get_all_models()
        
        return [
            {
                "model_id": model.model_id,
                "model_name": model.model_name,
                "model_type": model.model_type,
                "model_config": model.model_config,
                "use_custom": model.use_custom,
            }
            for model in models if not model.is_deleted
        ]
