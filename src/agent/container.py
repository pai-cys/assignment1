"""Agent domain dependency injection container."""

import logging
from dependency_injector import containers, providers
from src.agent.service import AgentService
from src.model.container import ModelContainer

logger = logging.getLogger(__name__)

class AgentContainer(containers.DeclarativeContainer):
    """Agent 도메인 의존성 주입 컨테이너 - dependency_injector 사용"""
    
    # 다른 컨테이너들
    model: ModelContainer = providers.Container(ModelContainer)
    
    # 서비스들
    service = providers.Singleton(
        AgentService,
        model_execution_service=model.execution_service,
    )

# 전역 컨테이너 인스턴스
agent_container = AgentContainer()
