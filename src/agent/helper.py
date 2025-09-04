"""Agent 헬퍼 유틸리티"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AgentHelper:
    """Agent 관련 헬퍼 클래스"""
    
    def __init__(self):
        """헬퍼 초기화"""
        pass
    
    def get_runnable_config(self, session_id: str, user_id: str = "default") -> Dict[str, Any]:
        """실행 가능한 설정을 반환합니다."""
        return {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }
    
    async def validate_response(self, config: Dict[str, Any], response: str) -> bool:
        """응답 유효성을 검증합니다."""
        # 간단한 검증 로직
        if not response or len(response.strip()) == 0:
            return False
        
        # 부적절한 내용 체크 (예시)
        inappropriate_keywords = ["hate", "violence", "illegal"]
        response_lower = response.lower()
        
        for keyword in inappropriate_keywords:
            if keyword in response_lower:
                logger.warning(f"Inappropriate content detected: {keyword}")
                return False
        
        return True
