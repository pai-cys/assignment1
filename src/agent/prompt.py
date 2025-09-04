"""프롬프트 생성기"""
import logging
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


class PromptGenerator:
    """시스템 프롬프트를 생성합니다."""
    
    def __init__(self):
        """프롬프트 생성기 초기화"""
        self.base_prompt = """당신은 주식 분석 전문가입니다. 사용자의 주식 관련 질문에 정확하고 도움이 되는 답변을 제공해주세요.

사용 가능한 도구:
1. get_stock_price: 특정 주식의 현재 가격과 정보를 조회합니다.
2. calculate: 수학적 계산을 수행합니다.

주식 가격을 조회할 때는 정확한 티커 심볼을 사용하고, 계산이 필요한 경우 calculate 도구를 활용해주세요."""

    def create_prompt_template(self) -> ChatPromptTemplate:
        """기본 프롬프트 템플릿을 생성합니다."""
        return ChatPromptTemplate(
            [
                SystemMessage(content=self.base_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
