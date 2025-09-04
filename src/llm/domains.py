"""LLM 도메인 정의"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, Any, Optional, List, Literal
from enum import Enum

logger = logging.getLogger(__name__)


# 타입 정의
CompletionVendorName = Literal["OpenAI"]
CompletionModelName = Literal["gpt-4o"]


class LLMProvider(Enum):
    """지원하는 LLM 제공자"""
    OPENAI = "openai"


class LLMModel(Enum):
    """지원하는 LLM 모델"""
    GPT_4O = "gpt-4o"


@dataclass
class LLMCompletionModel:
    """LLM 완료 모델"""
    model_name: CompletionModelName
    model_url: str
    tool_calling: bool


@dataclass
class CompletionVendor:
    """완료 모델 벤더"""
    vendor_name: CompletionVendorName
    model_list: List[LLMCompletionModel]


class BaseLLM(ABC):
    """LLM 추상 기본 클래스"""
    
    def __init__(
        self,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = True,
        **kwargs
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.extra_params = kwargs
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Any], 
        tools: Optional[List] = None
    ) -> Any:
        """응답 생성"""
        pass
    
    @abstractmethod
    async def stream_response(
        self, 
        messages: List[Any], 
        tools: Optional[List] = None
    ) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        pass
    
    @abstractmethod
    def bind_tools(self, tools: List[Any]):
        """도구 바인딩"""
        pass
