"""LLM 엔티티 정의"""
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM 설정"""
    provider: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    streaming: bool = True
    timeout: int = 30
    retry_count: int = 3
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """초기화 후 처리"""
        if self.extra_params is None:
            self.extra_params = {}


@dataclass
class TokenUsage:
    """토큰 사용량"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    timestamp: datetime
    
    @property
    def cost_estimate(self) -> float:
        """비용 추정 (USD)"""
        if "gpt-4" in self.model.lower():
            return (self.prompt_tokens * 0.03 + self.completion_tokens * 0.06) / 1000
        elif "gpt-3.5" in self.model.lower():
            return (self.prompt_tokens * 0.0015 + self.completion_tokens * 0.002) / 1000
        return 0.0