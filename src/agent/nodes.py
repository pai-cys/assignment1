"""LangGraph 노드 정의 - 가독성 개선"""
import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, ToolMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.graph.message import add_messages

# LLMService import 제거 - model_execution_service 사용
from ..model.executors.langchain_tools import tools
from ..utils.exceptions import LLMInvocationException, ToolCallException

logger = logging.getLogger(__name__)


class LangGraphAgentState(TypedDict):
    """LangGraph Agent 상태 (참고 코드 기반 간소화)"""
    messages: Annotated[list, add_messages]


class AgentNode:
    """LLM을 통해 응답을 생성하는 노드 (참고 코드 기반)"""

    def __init__(
        self,
        model_execution_service,
        system_prompt: str,
    ):
        self.model_execution_service = model_execution_service
        self.system_prompt = system_prompt

    async def __call__(
        self, state: LangGraphAgentState, config: RunnableConfig = None
    ) -> LangGraphAgentState:
        """노드 실행 - 참고 코드 스타일"""
        
        # 모델 로드 및 도구 바인딩
        model = await self.load_chat_model()
        
        # 시스템 프롬프트 추가
        messages = state["messages"]
        if not messages or messages[0].type != "system":
            messages = [SystemMessage(content=self.system_prompt)] + messages

        # LLM 호출
        message = await self.invoke_chain(model, messages, config)

        # 메시지에 타임스탬프 추가 (참고 코드 스타일)
        if hasattr(message, 'additional_kwargs'):
            if message.additional_kwargs is None:
                message.additional_kwargs = {}
            message.additional_kwargs["timestamp"] = datetime.now().isoformat()
        else:
            message.additional_kwargs = {
                "timestamp": datetime.now().isoformat()
            }

        logger.info(f"Agent response generated: {message.content[:100] if message.content else 'No content'}...")
        
        return {"messages": [message]}

    async def load_chat_model(self) -> BaseChatModel:
        """모델을 로드하고 도구를 바인딩합니다 (참고 코드 기반)"""
        model = await self.model_execution_service.load_llm_model(1)  # 기본 GPT-4o 모델
        
        try:
            return model.bind_tools(tools)
        except Exception as e:
            logger.error(f"Error binding tools: {e}")
            return model

    def _validate_model_invocation(self, model: Runnable, messages: List[AnyMessage]) -> None:
        """모델 호출 검증 - 필요시 exception raise"""
        if not model:
            raise LLMInvocationException("모델이 초기화되지 않았습니다")
        
        if not messages:
            raise LLMInvocationException("메시지가 비어있습니다")

    async def invoke_chain(
        self, model: Runnable, messages: List[AnyMessage], config: RunnableConfig
    ):
        """모델을 호출합니다 - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        self._validate_model_invocation(model, messages)
        
        # 비즈니스 로직 실행
        return await model.ainvoke(messages, config=config)


class ToolNode:
    """도구 노드 - 가독성 개선"""
    
    def __init__(self, tools_list):
        self.tools = {tool.name: tool for tool in tools_list}
    
    def _validate_tool_call(self, last_message: AnyMessage) -> None:
        """도구 호출 검증 - 필요시 exception raise"""
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            raise ToolCallException("도구 호출이 없습니다")
    
    def _validate_tool_exists(self, tool_name: str) -> None:
        """도구 존재 검증 - 필요시 exception raise"""
        if tool_name not in self.tools:
            raise ToolCallException(f"도구를 찾을 수 없습니다: {tool_name}")
    
    def _create_tool_message(self, content: str, tool_id: str, tool_name: str) -> ToolMessage:
        """도구 메시지 생성"""
        tool_message = ToolMessage(
            content=content,
            tool_call_id=tool_id,
            name=tool_name
        )
        
        # 타임스탬프 추가
        tool_message.additional_kwargs = {
            "timestamp": datetime.now().isoformat()
        }
        
        return tool_message
    
    async def __call__(
        self, 
        state: LangGraphAgentState, 
        config: RunnableConfig = None
    ) -> LangGraphAgentState:
        """도구 실행 - validate 함수로 깔끔하게 처리"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # 도구 호출 검증
        self._validate_tool_call(last_message)
        
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            # 도구 존재 검증
            self._validate_tool_exists(tool_name)
            
            # 도구 실행
            tool = self.tools[tool_name]
            result = await tool.ainvoke(tool_args)
            
            tool_message = self._create_tool_message(str(result), tool_id, tool_name)
            tool_messages.append(tool_message)
            logger.info(f"Tool {tool_name} executed successfully")
        
        return {"messages": tool_messages}