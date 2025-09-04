"""챗봇 서비스 - 가독성 개선"""
import logging

from ..agent.service import AgentService
from ..utils.exceptions import InvalidSessionException, InvalidInputException, ChatbotException
from .entities import ChatbotConfig, ChatResponse, StreamingResponse

logger = logging.getLogger(__name__)


class ChatbotService:
    """간단한 챗봇 서비스"""
    
    def __init__(self, config: ChatbotConfig = None, agent_service=None):
        self.config = config or ChatbotConfig()
        
        # 의존성 주입받은 에이전트 서비스
        self.agent_service = agent_service
    
    def _validate_chat_request(self, session_id: str, user_input: str) -> None:
        """채팅 요청 검증 - 필요시 exception raise"""
        if not session_id:
            raise InvalidSessionException("세션 ID가 필요합니다")
        
        if not user_input or not user_input.strip():
            raise InvalidInputException("사용자 입력이 비어있습니다")
    
    def _create_error_response(self, session_id: str, error: Exception) -> ChatResponse:
        """에러 응답 생성"""
        logger.error(f"채팅 처리 실패 (세션: {session_id}): {error}")
        return ChatResponse(
            content=f"오류가 발생했습니다: {str(error)}",
            session_id=session_id
        )
    
    async def _create_error_streaming_response(self, session_id: str, error: Exception) -> StreamingResponse:
        """에러 스트리밍 응답 생성"""
        logger.error(f"스트리밍 채팅 처리 실패 (세션: {session_id}): {error}")
        
        async def error_generator():
            error_msg = f"오류가 발생했습니다: {str(error)}"
            yield error_msg
        
        return StreamingResponse(
            session_id=session_id,
            generator=error_generator()
        )
    
    async def chat(self, session_id: str, user_input: str) -> ChatResponse:
        """채팅 (일반 응답) - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        self._validate_chat_request(session_id, user_input)
        
        # 비즈니스 로직 실행
        response_content = await self.agent_service.generate_response(user_input, session_id)
        return ChatResponse(
            content=response_content,
            session_id=session_id
        )
    
    async def stream_chat(self, session_id: str, user_input: str) -> StreamingResponse:
        """채팅 (스트리밍 응답) - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        self._validate_chat_request(session_id, user_input)
        
        # 비즈니스 로직 실행
        generator = self.agent_service.stream_response(user_input, session_id)
        return StreamingResponse(
            session_id=session_id,
            generator=generator
        )
    
    def clear_session(self, session_id: str) -> None:
        """세션 초기화"""
        # 간단한 로깅만
        logger.info(f"세션 초기화: {session_id}")
    
    def get_config(self) -> ChatbotConfig:
        """설정 반환"""
        return self.config