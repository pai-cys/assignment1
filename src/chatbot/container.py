"""Chatbot domain dependency injection container."""

import logging
from dependency_injector import containers, providers
from src.chatbot.service import ChatbotService
from src.chatbot.entities import ChatbotConfig
from src.agent.container import AgentContainer

logger = logging.getLogger(__name__)

class ChatbotContainer(containers.DeclarativeContainer):
    """Chatbot 도메인 의존성 주입 컨테이너 - dependency_injector 사용"""
    
    # 다른 컨테이너들
    agent: AgentContainer = providers.Container(AgentContainer)
    
    # 설정
    config = providers.Singleton(
        ChatbotConfig,
        name="Stock Analysis Chatbot v2.0",
        streaming=True,
        tools_enabled=True
    )
    
    # 서비스들
    service = providers.Singleton(
        ChatbotService,
        config=config,
        agent_service=agent.service,
    )

# 전역 컨테이너 인스턴스
chatbot_container = ChatbotContainer()
