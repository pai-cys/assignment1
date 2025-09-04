"""Tools domain dependency injection container."""

import logging
from dependency_injector import containers, providers
from src.tools.service import ToolService

logger = logging.getLogger(__name__)

class ToolsContainer(containers.DeclarativeContainer):
    """Tools 도메인 의존성 주입 컨테이너 - dependency_injector 사용"""
    
    # 서비스들
    service = providers.Singleton(ToolService)

# 전역 컨테이너 인스턴스
tools_container = ToolsContainer()
