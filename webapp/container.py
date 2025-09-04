"""Application container for dependency injection."""

import logging
from dependency_injector import containers, providers
from src.agent.container import AgentContainer
from src.chatbot.container import ChatbotContainer
from src.model.container import ModelContainer
from src.tools.container import ToolsContainer

logger = logging.getLogger(__name__)

class ApplicationContainer(containers.DeclarativeContainer):
    """애플리케이션 컨테이너 - 모든 도메인 컨테이너를 통합"""
    
    wiring_config = containers.WiringConfiguration(packages=["webapp"])
    
    # 도메인 컨테이너들
    model: ModelContainer = providers.Container(ModelContainer)
    tools: ToolsContainer = providers.Container(ToolsContainer)
    agent: AgentContainer = providers.Container(
        AgentContainer,
        model=model,
    )
    chatbot: ChatbotContainer = providers.Container(
        ChatbotContainer,
        agent=agent,
    )

def create_container() -> ApplicationContainer:
    """컨테이너 생성 및 초기화"""
    container = ApplicationContainer()
    
    # 컨테이너 초기화
    container.wire(modules=["webapp"])
    
    logger.info("Application container initialized")
    return container
