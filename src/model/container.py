"""Model domain dependency injection container."""

import logging
from dependency_injector import containers, providers
from src.model.service import ModelService
from src.model.model_execution_service import ModelExecutionService
from src.model.settings import ModelSettings

logger = logging.getLogger(__name__)

class ModelContainer(containers.DeclarativeContainer):
    """Model 도메인 의존성 주입 컨테이너 - dependency_injector 사용"""
    
    # 설정
    settings = providers.Singleton(ModelSettings)
    
    # 서비스들
    model_service = providers.Singleton(ModelService)
    
    execution_service = providers.Singleton(
        ModelExecutionService,
        model_service=model_service,
    )

# 전역 컨테이너 인스턴스
model_container = ModelContainer()
