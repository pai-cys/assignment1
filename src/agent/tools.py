"""Agent 도구 정의"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class AgentTools:
    """Agent에서 사용할 도구들을 관리합니다."""
    
    def __init__(self):
        """도구 관리자 초기화"""
        self.tools = {}
    
    def register_tool(self, name: str, tool: Any):
        """도구를 등록합니다."""
        self.tools[name] = tool
        logger.info(f"Tool registered: {name}")
    
    def get_tool(self, name: str) -> Any:
        """도구를 가져옵니다."""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[Any]:
        """모든 도구를 반환합니다."""
        return list(self.tools.values())
    
    def list_tool_names(self) -> List[str]:
        """도구 이름 목록을 반환합니다."""
        return list(self.tools.keys())
