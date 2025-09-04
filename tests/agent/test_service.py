"""Agent service 단위테스트."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agent.service import AgentService
from src.utils.exceptions import AgentException


class TestAgentService:
    """AgentService 테스트"""
    
    @pytest.fixture
    def mock_model_execution_service(self):
        """Mock ModelExecutionService 생성"""
        return AsyncMock()
    
    @pytest.fixture
    def agent_service(self, mock_model_execution_service):
        """AgentService 인스턴스 생성"""
        return AgentService(mock_model_execution_service)
    
    def test_validate_input_valid(self, agent_service):
        """유효한 입력 검증 테스트"""
        # 정상 케이스 - 예외가 발생하지 않아야 함
        agent_service._validate_input("안녕하세요", "session_123")
        agent_service._validate_input("AAPL 주가 알려줘", "default")
    
    def test_validate_input_empty_user_input(self, agent_service):
        """빈 사용자 입력 검증 테스트"""
        with pytest.raises(AgentException, match="사용자 입력이 비어있습니다"):
            agent_service._validate_input("", "session_123")
        
        with pytest.raises(AgentException, match="사용자 입력이 비어있습니다"):
            agent_service._validate_input("   ", "session_123")
        
        with pytest.raises(AgentException, match="사용자 입력이 비어있습니다"):
            agent_service._validate_input(None, "session_123")
    
    def test_validate_input_empty_thread_id(self, agent_service):
        """빈 스레드 ID 검증 테스트"""
        with pytest.raises(AgentException, match="스레드 ID가 비어있습니다"):
            agent_service._validate_input("안녕하세요", "")
        
        with pytest.raises(AgentException, match="스레드 ID가 비어있습니다"):
            agent_service._validate_input("안녕하세요", "   ")
        
        with pytest.raises(AgentException, match="스레드 ID가 비어있습니다"):
            agent_service._validate_input("안녕하세요", None)
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, agent_service, mock_model_execution_service):
        """응답 생성 성공 테스트"""
        # Mock 설정
        mock_agent = AsyncMock()
        mock_agent.astream.return_value = [
            {"messages": [{"content": "안녕하세요! 주식 관련 질문이 있으시면 도와드리겠습니다."}]}
        ]
        agent_service.agent = mock_agent
        
        # 테스트 실행
        result = await agent_service.generate_response("안녕하세요", "session_123")
        
        # 검증
        assert "안녕하세요! 주식 관련 질문이 있으시면 도와드리겠습니다." in result
        mock_agent.astream.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_invalid_input(self, agent_service):
        """잘못된 입력으로 응답 생성 테스트"""
        with pytest.raises(AgentException, match="사용자 입력이 비어있습니다"):
            await agent_service.generate_response("", "session_123")
    
    @pytest.mark.asyncio
    async def test_stream_response_success(self, agent_service, mock_model_execution_service):
        """스트리밍 응답 성공 테스트"""
        # Mock 설정
        mock_agent = AsyncMock()
        mock_agent.astream.return_value = [
            {"messages": [{"content": "안녕하세요!"}]},
            {"messages": [{"content": " 주식 관련 질문이 있으시면"}]},
            {"messages": [{"content": " 도와드리겠습니다."}]}
        ]
        agent_service.agent = mock_agent
        
        # 테스트 실행
        chunks = []
        async for chunk in agent_service.stream_response("안녕하세요", "session_123"):
            chunks.append(chunk)
        
        # 검증
        assert len(chunks) > 0
        assert any("안녕하세요!" in chunk for chunk in chunks)
        mock_agent.astream.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_response_invalid_input(self, agent_service):
        """잘못된 입력으로 스트리밍 응답 테스트"""
        with pytest.raises(AgentException, match="사용자 입력이 비어있습니다"):
            async for chunk in agent_service.stream_response("", "session_123"):
                pass
    
    @pytest.mark.asyncio
    async def test_stream_response_with_tool_calls(self, agent_service, mock_model_execution_service):
        """도구 호출이 포함된 스트리밍 응답 테스트"""
        # Mock 설정
        mock_agent = AsyncMock()
        mock_agent.astream.return_value = [
            {"messages": [{"content": "AAPL 주가를 조회해드리겠습니다.", "tool_calls": [{"name": "get_stock_price", "args": {"ticker": "AAPL"}}]}]},
            {"messages": [{"content": "Apple Inc.의 현재 주가는 $150.0입니다."}]}
        ]
        agent_service.agent = mock_agent
        
        # 테스트 실행
        chunks = []
        async for chunk in agent_service.stream_response("AAPL 주가 알려줘", "session_123"):
            chunks.append(chunk)
        
        # 검증
        assert len(chunks) > 0
        assert any("AAPL 주가를 조회해드리겠습니다." in chunk for chunk in chunks)
        assert any("Apple Inc.의 현재 주가는 $150.0입니다." in chunk for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_stream_response_error_handling(self, agent_service, mock_model_execution_service):
        """스트리밍 응답 에러 처리 테스트"""
        # Mock 설정 - 에러 발생
        mock_agent = AsyncMock()
        mock_agent.astream.side_effect = Exception("모델 호출 실패")
        agent_service.agent = mock_agent
        
        # 테스트 실행
        chunks = []
        async for chunk in agent_service.stream_response("안녕하세요", "session_123"):
            chunks.append(chunk)
        
        # 검증 - 에러 메시지가 포함되어야 함
        assert len(chunks) > 0
        assert any("죄송합니다" in chunk for chunk in chunks)
        assert any("오류가 발생했습니다" in chunk for chunk in chunks)
