"""챗봇 엔티티 정의"""
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ChatbotConfig:
    """챗봇 설정"""
    name: str = "Stock Analysis Chatbot"
    system_prompt: str = "당신은 주가 계산을 도와주는 AI Agent입니다. 사용자가 주식 심볼을 언급하면 get_stock_price 도구를 사용해서 가격을 조회하고, 계산이 필요하면 calculator 도구를 사용하세요. 한국어로 친근하게 답변해주세요. API 호출이 실패하면 한 번만 재시도하고, 그래도 실패하면 사용자에게 알려주세요."
    max_history: int = 50
    streaming: bool = True
    tools_enabled: bool = True
    session_timeout: int = 3600  # 1시간


@dataclass
class ChatResponse:
    """채팅 응답"""
    content: str
    session_id: str
    message_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.message_id is None:
            self.message_id = f"msg_{int(self.timestamp.timestamp() * 1000)}"


@dataclass
class StreamingResponse:
    """스트리밍 응답"""
    session_id: str
    generator: AsyncGenerator[str, None]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}