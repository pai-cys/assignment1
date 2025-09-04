"""Model domain models and definitions."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Literal, Optional

logger = logging.getLogger(__name__)

# OpenAI만 사용하므로 단순화
ModelType = Literal["llm"]
ModelVendor = Literal["OpenAI"]

@dataclass
class Model:
    """모델 도메인 모델"""
    model_id: Optional[int]
    model_provider_id: int
    model_name: str
    model_type: ModelType
    model_config: dict
    use_custom: bool
    is_deleted: bool
    created_at: datetime
    
    @staticmethod
    def new(
        model_provider_id: int, 
        model_name: str, 
        model_type: ModelType, 
        model_config: dict, 
        use_custom: bool
    ) -> "Model":
        """새 모델 생성"""
        return Model(
            model_id=None,
            model_provider_id=model_provider_id,
            model_name=model_name,
            model_type=model_type,
            model_config=model_config,
            use_custom=use_custom,
            is_deleted=False,
            created_at=datetime.now()
        )
    
    @staticmethod
    def from_entity(entity) -> "Model":
        """엔티티에서 도메인 모델로 변환"""
        return Model(
            model_id=entity.model_id,
            model_provider_id=entity.model_provider_id,
            model_name=entity.model_name,
            model_type=entity.model_type,
            model_config=entity.model_config,
            use_custom=entity.use_custom,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at
        )

@dataclass
class ModelProvider:
    """모델 프로바이더 도메인 모델"""
    model_provider_id: Optional[int]
    model_provider_name: str
    model_key_id: Optional[int]
    model_vendor: ModelVendor
    created_at: datetime
    is_deleted: bool
    
    @staticmethod
    def new(
        model_provider_name: str, 
        model_vendor: ModelVendor
    ) -> "ModelProvider":
        """새 프로바이더 생성"""
        return ModelProvider(
            model_provider_id=None,
            model_provider_name=model_provider_name,
            model_key_id=None,
            model_vendor=model_vendor,
            created_at=datetime.now(),
            is_deleted=False
        )

@dataclass
class ModelKey:
    """모델 키 도메인 모델"""
    model_key_id: Optional[int]
    key_name: str
    key_value: str

@dataclass
class ProviderModel:
    """프로바이더별 모델 정의"""
    name: str
    type: ModelType
    config: dict
    is_default: bool = False

# OpenAI 모델 정의 (GPT-4o만 사용)
OPENAI_MODELS: Dict[str, ProviderModel] = {
    "gpt-4o": ProviderModel(
        name="gpt-4o",
        type="llm",
        config={"model": "gpt-4o", "enable_tool_calling": True},
        is_default=True
    ),
}

# 프로바이더별 모델 매핑
PROVIDER_MODELS: Dict[ModelVendor, Dict[str, ProviderModel]] = {
    "OpenAI": OPENAI_MODELS,
}

def get_provider_models(provider: ModelVendor) -> Dict[str, ProviderModel]:
    """프로바이더의 모든 모델을 반환"""
    return PROVIDER_MODELS.get(provider, {})

def get_provider_model(provider: ModelVendor, model_name: str) -> Optional[ProviderModel]:
    """프로바이더의 특정 모델을 반환"""
    models = get_provider_models(provider)
    return models.get(model_name)

def get_default_models(provider: ModelVendor) -> List[ProviderModel]:
    """프로바이더의 기본 모델들을 반환"""
    models = get_provider_models(provider)
    return [model for model in models.values() if model.is_default]

def get_models_by_type(provider: ModelVendor, model_type: ModelType) -> List[ProviderModel]:
    """프로바이더의 특정 타입 모델들을 반환"""
    models = get_provider_models(provider)
    return [model for model in models.values() if model.type == model_type]
