"""애플리케이션 의존성 관리"""
from functools import lru_cache
import logging
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ai.agent.stock_agent import StockAgent

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_agent() -> StockAgent:
    """
    StockAgent 인스턴스를 생성하고 캐시하여 앱 전체에서 공유합니다.
    lru_cache 데코레이터를 사용하여 이 함수는 앱 전체에서 단 한 번만 실행됩니다.
    """
    logger.info("Creating a single, shared StockAgent instance...")
    return StockAgent()
