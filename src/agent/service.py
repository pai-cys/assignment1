"""Agent 서비스 - 가독성 개선"""
import logging
import asyncio
import re
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

# LLMService import 제거 - model_execution_service 사용
from ..model.executors.langchain_tools import tools
from ..utils.exceptions import AgentException, LLMInvocationException, ToolCallException
from .nodes import AgentNode, ToolNode
from .graph import LangGraphBuilder

logger = logging.getLogger(__name__)


class AgentService:
    """간단한 Agent 서비스 - 스트리밍과 도구 호출만"""

    def __init__(self, model_execution_service):
        """Agent 서비스 초기화 - 의존성 주입"""
        logger.info("Agent 서비스 초기화 중...")
        
        # 의존성 주입받은 서비스들
        self.model_execution_service = model_execution_service
        
        # 시스템 프롬프트
        system_prompt = """당신은 주식 분석 전문가입니다. 사용자의 주식 관련 질문에 정확하고 도움이 되는 답변을 제공해주세요.

사용 가능한 도구:
1. get_stock_price: 특정 주식의 현재 가격과 정보를 조회합니다.
2. calculate: 수학적 계산을 수행합니다.

주식 가격을 조회할 때는 정확한 티커 심볼을 사용하고, 계산이 필요한 경우 calculate 도구를 활용해주세요."""
        
        # 노드 생성
        self.agent_node = AgentNode(self.model_execution_service, system_prompt)
        self.tool_node = ToolNode(tools)
        
        # 그래프 구성
        self.agent = LangGraphBuilder.build_graph(
            self.agent_node,
            self.tool_node,
            use_memory=True
        )
        
        logger.info("Agent 서비스 초기화 완료")

    def _validate_input(self, user_input: str, thread_id: str) -> None:
        """입력 검증 - 필요시 exception raise"""
        if not user_input or not user_input.strip():
            raise AgentException("사용자 입력이 비어있습니다")
        
        if not thread_id or not thread_id.strip():
            raise AgentException("스레드 ID가 비어있습니다")

    async def generate_response(self, user_input: str, thread_id: str = "default") -> str:
        """전체 응답 반환 - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        self._validate_input(user_input, thread_id)
        
        # 비즈니스 로직 실행
        response_parts = []
        async for chunk in self.stream_response(user_input, thread_id):
            response_parts.append(chunk)
        return ''.join(response_parts)

    async def stream_response(self, user_input: str, thread_id: str = "default") -> AsyncGenerator[str, None]:
        """스트리밍 응답 - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        self._validate_input(user_input, thread_id)
        
        # 비즈니스 로직 실행
        config = {"configurable": {"thread_id": thread_id}}
        
        async for chunk in self.agent.astream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        ):
            # AI 메시지 청크 처리
            if "agent" in chunk:
                for message in chunk["agent"]["messages"]:
                    if isinstance(message, (AIMessage, AIMessageChunk)) and message.content:
                        yield message.content
                    
            # 도구 실행 결과 처리
            elif "tools" in chunk:
                for message in chunk["tools"]["messages"]:
                    if isinstance(message, AIMessage) and message.content:
                        yield message.content
            
            # 기타 메시지 (예: 중간 상태)는 무시
            else:
                pass
    
    def clear_history(self, thread_id: str = "default"):
        """대화 히스토리 초기화 (InMemorySaver는 thread_id별로 자동 관리)"""
        logger.info(f"대화 히스토리 초기화 요청: {thread_id}")
        # InMemorySaver는 별도 clear 메서드 없음, 새 thread_id 사용시 자동 초기화 효과
        pass

    def exists_tool_call(self, message: AIMessage) -> bool:
        """AIMessage 객체에 tool_calls가 있는지 확인합니다."""
        if hasattr(message, "tool_calls"):
            return message.tool_calls is not None and len(message.tool_calls) > 0
        return False
