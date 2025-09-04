"""Agent nodes 단위테스트."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.agent.nodes import AgentNode, ToolNode
from src.utils.exceptions import LLMInvocationException, ToolCallException


class TestAgentNode:
    """AgentNode 테스트"""
    
    @pytest.fixture
    def mock_model_execution_service(self):
        """Mock ModelExecutionService 생성"""
        return AsyncMock()
    
    @pytest.fixture
    def agent_node(self, mock_model_execution_service):
        """AgentNode 인스턴스 생성"""
        system_prompt = "당신은 주식 분석 전문가입니다."
        return AgentNode(mock_model_execution_service, system_prompt)
    
    def test_validate_model_invocation_valid(self, agent_node):
        """유효한 모델 호출 검증 테스트"""
        mock_model = MagicMock()
        messages = [HumanMessage(content="안녕하세요")]
        
        # 정상 케이스 - 예외가 발생하지 않아야 함
        agent_node._validate_model_invocation(mock_model, messages)
    
    def test_validate_model_invocation_no_model(self, agent_node):
        """모델이 없는 경우 검증 테스트"""
        messages = [HumanMessage(content="안녕하세요")]
        
        with pytest.raises(LLMInvocationException, match="모델이 초기화되지 않았습니다"):
            agent_node._validate_model_invocation(None, messages)
    
    def test_validate_model_invocation_no_messages(self, agent_node):
        """메시지가 없는 경우 검증 테스트"""
        mock_model = MagicMock()
        
        with pytest.raises(LLMInvocationException, match="메시지가 비어있습니다"):
            agent_node._validate_model_invocation(mock_model, [])
        
        with pytest.raises(LLMInvocationException, match="메시지가 비어있습니다"):
            agent_node._validate_model_invocation(mock_model, None)
    
    @pytest.mark.asyncio
    async def test_invoke_chain_success(self, agent_node, mock_model_execution_service):
        """체인 호출 성공 테스트"""
        # Mock 설정
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = AIMessage(content="안녕하세요!")
        messages = [HumanMessage(content="안녕하세요")]
        config = {"configurable": {"thread_id": "test"}}
        
        # 테스트 실행
        result = await agent_node.invoke_chain(mock_model, messages, config)
        
        # 검증
        assert result.content == "안녕하세요!"
        mock_model.ainvoke.assert_called_once_with(messages, config=config)
    
    @pytest.mark.asyncio
    async def test_invoke_chain_invalid_model(self, agent_node):
        """잘못된 모델로 체인 호출 테스트"""
        messages = [HumanMessage(content="안녕하세요")]
        config = {"configurable": {"thread_id": "test"}}
        
        with pytest.raises(LLMInvocationException, match="모델이 초기화되지 않았습니다"):
            await agent_node.invoke_chain(None, messages, config)
    
    @pytest.mark.asyncio
    async def test_load_chat_model_success(self, agent_node, mock_model_execution_service):
        """채팅 모델 로딩 성공 테스트"""
        # Mock 설정
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_model_execution_service.load_llm_model.return_value = mock_llm
        
        # 테스트 실행
        result = await agent_node.load_chat_model()
        
        # 검증
        assert result == mock_llm
        mock_model_execution_service.load_llm_model.assert_called_once_with(1)
        mock_llm.bind_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_chat_model_error(self, agent_node, mock_model_execution_service):
        """채팅 모델 로딩 에러 테스트"""
        # Mock 설정 - 에러 발생
        mock_model_execution_service.load_llm_model.side_effect = Exception("모델 로딩 실패")
        
        # 테스트 실행
        result = await agent_node.load_chat_model()
        
        # 검증 - 에러가 발생해도 None을 반환해야 함
        assert result is None


class TestToolNode:
    """ToolNode 테스트"""
    
    @pytest.fixture
    def mock_tools(self):
        """Mock 도구들 생성"""
        mock_tool1 = AsyncMock()
        mock_tool1.ainvoke.return_value = "Apple Inc.의 현재 주가는 $150.0입니다."
        
        mock_tool2 = AsyncMock()
        mock_tool2.ainvoke.return_value = "계산 결과: 42"
        
        return {
            "get_stock_price": mock_tool1,
            "calculate": mock_tool2
        }
    
    @pytest.fixture
    def tool_node(self, mock_tools):
        """ToolNode 인스턴스 생성"""
        return ToolNode(mock_tools)
    
    def test_validate_tool_call_valid(self, tool_node):
        """유효한 도구 호출 검증 테스트"""
        mock_message = MagicMock()
        mock_message.tool_calls = [{"name": "get_stock_price", "args": {"ticker": "AAPL"}}]
        
        # 정상 케이스 - 예외가 발생하지 않아야 함
        tool_node._validate_tool_call(mock_message)
    
    def test_validate_tool_call_no_tool_calls(self, tool_node):
        """도구 호출이 없는 경우 검증 테스트"""
        mock_message = MagicMock()
        mock_message.tool_calls = None
        
        with pytest.raises(ToolCallException, match="도구 호출이 없습니다"):
            tool_node._validate_tool_call(mock_message)
        
        mock_message.tool_calls = []
        
        with pytest.raises(ToolCallException, match="도구 호출이 없습니다"):
            tool_node._validate_tool_call(mock_message)
    
    def test_validate_tool_exists_valid(self, tool_node):
        """존재하는 도구 검증 테스트"""
        # 정상 케이스 - 예외가 발생하지 않아야 함
        tool_node._validate_tool_exists("get_stock_price")
        tool_node._validate_tool_exists("calculate")
    
    def test_validate_tool_exists_invalid(self, tool_node):
        """존재하지 않는 도구 검증 테스트"""
        with pytest.raises(ToolCallException, match="도구를 찾을 수 없습니다: non_existent_tool"):
            tool_node._validate_tool_exists("non_existent_tool")
    
    def test_create_tool_message(self, tool_node):
        """도구 메시지 생성 테스트"""
        result = "Apple Inc.의 현재 주가는 $150.0입니다."
        tool_id = "call_123"
        tool_name = "get_stock_price"
        
        tool_message = tool_node._create_tool_message(result, tool_id, tool_name)
        
        assert isinstance(tool_message, ToolMessage)
        assert tool_message.content == result
        assert tool_message.tool_call_id == tool_id
        assert tool_message.name == tool_name
    
    @pytest.mark.asyncio
    async def test_call_success(self, tool_node, mock_tools):
        """도구 노드 호출 성공 테스트"""
        # Mock 설정
        mock_message = MagicMock()
        mock_message.tool_calls = [
            {
                "name": "get_stock_price",
                "args": {"ticker": "AAPL"},
                "id": "call_123"
            }
        ]
        
        state = {
            "messages": [mock_message]
        }
        
        # 테스트 실행
        result = await tool_node(state)
        
        # 검증
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], ToolMessage)
        assert result["messages"][0].content == "Apple Inc.의 현재 주가는 $150.0입니다."
        mock_tools["get_stock_price"].ainvoke.assert_called_once_with({"ticker": "AAPL"})
    
    @pytest.mark.asyncio
    async def test_call_multiple_tools(self, tool_node, mock_tools):
        """여러 도구 호출 테스트"""
        # Mock 설정
        mock_message = MagicMock()
        mock_message.tool_calls = [
            {
                "name": "get_stock_price",
                "args": {"ticker": "AAPL"},
                "id": "call_123"
            },
            {
                "name": "calculate",
                "args": {"expression": "2 + 3"},
                "id": "call_456"
            }
        ]
        
        state = {
            "messages": [mock_message]
        }
        
        # 테스트 실행
        result = await tool_node(state)
        
        # 검증
        assert "messages" in result
        assert len(result["messages"]) == 2
        assert all(isinstance(msg, ToolMessage) for msg in result["messages"])
        mock_tools["get_stock_price"].ainvoke.assert_called_once()
        mock_tools["calculate"].ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_no_tool_calls(self, tool_node):
        """도구 호출이 없는 경우 테스트"""
        mock_message = MagicMock()
        mock_message.tool_calls = None
        
        state = {
            "messages": [mock_message]
        }
        
        with pytest.raises(ToolCallException, match="도구 호출이 없습니다"):
            await tool_node(state)
    
    @pytest.mark.asyncio
    async def test_call_invalid_tool(self, tool_node):
        """존재하지 않는 도구 호출 테스트"""
        mock_message = MagicMock()
        mock_message.tool_calls = [
            {
                "name": "non_existent_tool",
                "args": {},
                "id": "call_123"
            }
        ]
        
        state = {
            "messages": [mock_message]
        }
        
        with pytest.raises(ToolCallException, match="도구를 찾을 수 없습니다: non_existent_tool"):
            await tool_node(state)
