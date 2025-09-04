"""Dependency injection for webapp."""

import logging
from typing import Annotated, Optional
from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from src.chatbot.service import ChatbotService
from src.agent.service import AgentService
from src.model.model_execution_service import ModelExecutionService
from src.model.service import ModelService
from src.tools.service import ToolService

from webapp.container import ApplicationContainer

logger = logging.getLogger(__name__)

# 의존성 주입 함수들
@inject
def chatbot_service_dependency(
    service: ChatbotService = Depends(
        Provide[ApplicationContainer.chatbot.service]
    ),
) -> ChatbotService:
    """챗봇 서비스 의존성 주입"""
    return service

@inject
def agent_service_dependency(
    service: AgentService = Depends(
        Provide[ApplicationContainer.agent.service]
    ),
) -> AgentService:
    """에이전트 서비스 의존성 주입"""
    return service

@inject
def model_execution_service_dependency(
    service: ModelExecutionService = Depends(
        Provide[ApplicationContainer.model.execution_service]
    ),
) -> ModelExecutionService:
    """모델 실행 서비스 의존성 주입"""
    return service

@inject
def model_service_dependency(
    service: ModelService = Depends(
        Provide[ApplicationContainer.model.model_service]
    ),
) -> ModelService:
    """모델 서비스 의존성 주입"""
    return service

@inject
def tool_service_dependency(
    service: ToolService = Depends(
        Provide[ApplicationContainer.tools.service]
    ),
) -> ToolService:
    """도구 서비스 의존성 주입"""
    return service
