"""LLM 서비스"""
import logging
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel

from .domains import (
    BaseLLM, 
    LLMProvider, 
    CompletionVendor,
    LLMCompletionModel
)
from .entities import LLMConfig
from .settings import llm_settings
from ..utils.exceptions import ModelNotFoundException

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    """OpenAI LLM 구현체"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=config.streaming
        )
        self.config = config
        self._client = None
        self._tool_bound_client = None
    
    @property
    def client(self) -> ChatOpenAI:
        """기본 클라이언트"""
        if self._client is None:
            self._client = ChatOpenAI(
                api_key=self.config.api_key,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=self.config.streaming,
                timeout=self.config.timeout,
                **self.config.extra_params
            )
        return self._client
    
    @property
    def tool_bound_client(self) -> ChatOpenAI:
        """도구가 바인딩된 클라이언트"""
        if self._tool_bound_client is None:
            self._tool_bound_client = self.client
        return self._tool_bound_client
    
    def bind_tools(self, tools: List[Any]) -> 'OpenAILLM':
        """도구 바인딩"""
        self._tool_bound_client = self.client.bind_tools(tools)
        return self
    
    async def generate_response(
        self, 
        messages: List[BaseMessage], 
        tools: Optional[List[Any]] = None
    ) -> Any:
        """응답 생성"""
        try:
            client = self.tool_bound_client if tools else self.client
            if tools and self._tool_bound_client is None:
                client = self.client.bind_tools(tools)
            
            response = await client.ainvoke(messages)
            return response
            
        except Exception as e:
            logger.error(f"OpenAI LLM 응답 생성 실패: {e}")
            raise
    
    async def stream_response(
        self, 
        messages: List[BaseMessage], 
        tools: Optional[List[Any]] = None
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        try:
            client = self.tool_bound_client if tools else self.client
            if tools and self._tool_bound_client is None:
                client = self.client.bind_tools(tools)
            
            async for chunk in client.astream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"OpenAI LLM 스트리밍 응답 실패: {e}")
            yield f"오류가 발생했습니다: {str(e)}"


class LLMFactory:
    """LLM 팩토리 클래스"""
    
    @staticmethod
    def create_llm(config: LLMConfig) -> BaseLLM:
        """설정에 따라 적절한 LLM 인스턴스 생성"""
        provider_mapping = {
            LLMProvider.OPENAI.value: OpenAILLM,
            # 추가 제공자들...
        }
        
        llm_class = provider_mapping.get(config.provider)
        if not llm_class:
            raise ValueError(f"지원하지 않는 LLM 제공자: {config.provider}")
        
        return llm_class(config)


class LLMService:
    """LLM 서비스 - 비즈니스 로직 처리"""
    
    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        self.config: LLMConfig = config or llm_settings.create_config()
        self.llm: BaseLLM = LLMFactory.create_llm(self.config)
    
    async def find_completion_model_list(self) -> List[CompletionVendor]:
        """사용 가능한 완료 모델 목록을 반환합니다."""
        openai_models = CompletionVendor(
            vendor_name="OpenAI",
            model_list=[
                LLMCompletionModel("gpt-4o", "", True),
            ],
        )
        
        return [openai_models]
    
    async def load_chat_model(self, model_name: str) -> BaseChatModel:
        """모델명에 따라 적절한 ChatModel을 로드합니다."""
        if model_name == "gpt-4o":
            return ChatOpenAI(
                model=model_name,
                api_key=llm_settings.openai_api_key,
                stream_usage=True,
            )
        else:
            raise ModelNotFoundException(f"지원하지 않는 모델: {model_name}")
    
    def bind_tools(self, tools: List[Any]) -> 'LLMService':
        """도구 바인딩"""
        self.llm.bind_tools(tools)
        return self
    
    async def generate_response(
        self, 
        messages: List[BaseMessage],
        tools: Optional[List[Any]] = None
    ) -> Any:
        """응답 생성"""
        return await self.llm.generate_response(messages, tools)
    
    async def stream_response(
        self,
        messages: List[BaseMessage],
        tools: Optional[List[Any]] = None
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        async for chunk in self.llm.stream_response(messages, tools):
            yield chunk