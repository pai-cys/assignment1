"""
주가 계산 챗봇 테스트
Multi-turn 대화 및 도구 사용 테스트
"""
import pytest
import asyncio
import os
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent  # test의 상위 디렉토리
sys.path.append(str(project_root))

from ai.agent.stock_agent import StockAgent
from langchain_core.messages import HumanMessage


@pytest.fixture
def agent():
    """StockAgent 인스턴스를 생성합니다."""
    return StockAgent()


@pytest.mark.asyncio
async def test_basic_stock_query(agent):
    """기본 주가 조회 테스트"""
    print("\n=== 기본 주가 조회 테스트 ===")
    
    thread_id = "test_basic"
    config = {'configurable': {'thread_id': thread_id}}
    
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="AAPL 주가 알려줘")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


@pytest.mark.asyncio
async def test_calculation(agent):
    """계산 기능 테스트"""
    print("\n=== 계산 기능 테스트 ===")
    
    thread_id = "test_calc"
    config = {'configurable': {'thread_id': thread_id}}
    
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="100 * 1.5는 얼마야?")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


@pytest.mark.asyncio
async def test_multi_turn_conversation(agent):
    """Multi-turn 대화 테스트 - 사용자가 요청한 시나리오"""
    print("\n=== Multi-turn 대화 테스트 ===")
    
    thread_id = "test_multiturn"
    config = {'configurable': {'thread_id': thread_id}}
    
    # 첫 번째 질문
    print("\n--- 첫 번째 질문: 두명이 돈을 모아서 ---")
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="엔비디아 5주랑 아마존 8주를 두명이 돈을 모아 사려고 하는데, 각자 얼마나 돈 챙겨야 해?")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()
    
    # 두 번째 질문 (같은 thread_id로 연속 대화)
    print("\n--- 두 번째 질문: 3명으로 변경 ---")
    async for state_map in agent.app.astream(input={
        "messages": [HumanMessage(content="아냐 3명이야 어떻게 해야 하지?")]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


@pytest.mark.asyncio
async def test_another_multi_turn_scenario(agent):
    """또 다른 Multi-turn 시나리오"""
    print("\n=== 또 다른 Multi-turn 시나리오 ===")
    
    thread_id = "test_scenario2"
    config = {'configurable': {'thread_id': thread_id}}
    
    # 첫 번째 질문
    print("\n--- 첫 번째: 두명이서 나누기 ---")
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="엔비디아 5주랑 아마존 8주를 두명이 돈을 모아 사려고 하는데, 각자 얼마나 돈 챙겨야 해?")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()
    
    # 두 번째 질문
    print("\n--- 두 번째: 셋이서 나누기로 변경 ---")
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="셋이서 나누기로 했어, 그럼 얼마야?")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


@pytest.mark.asyncio
async def test_streaming_response(agent):
    """스트리밍 응답 테스트"""
    print("\n=== 스트리밍 응답 테스트 ===")
    
    print("User: TSLA 주가 알려줘")
    print("AI: ", end="", flush=True)
    
    async for token in agent.stream_response("TSLA 주가 알려줘", "test_streaming"):
        print(token, end="", flush=True)
    print("\n")


@pytest.mark.asyncio
async def test_complex_calculation(agent):
    """복합 계산 테스트"""
    print("\n=== 복합 계산 테스트 ===")
    
    thread_id = "test_complex"
    config = {'configurable': {'thread_id': thread_id}}
    
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="37593 ** (1/5) 계산해줘")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


@pytest.mark.asyncio
async def test_multiple_stocks(agent):
    """여러 주식 조회 테스트"""
    print("\n=== 여러 주식 조회 테스트 ===")
    
    thread_id = "test_multiple"
    config = {'configurable': {'thread_id': thread_id}}
    
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="NVDA, TSLA, AMZN 주가 모두 알려줘")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


@pytest.mark.asyncio
async def test_conversation_memory(agent):
    """대화 기억 테스트"""
    print("\n=== 대화 기억 테스트 ===")
    
    thread_id = "test_memory"
    config = {'configurable': {'thread_id': thread_id}}
    
    # 첫 번째: 정보 제공
    print("\n--- 정보 설정 ---")
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="내가 AAPL 주식 10주를 가지고 있어")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()
    
    # 두 번째: 이전 정보 참조
    print("\n--- 이전 정보 참조 ---")
    async for state_map in agent.app.astream(input={
        "messages": [
            HumanMessage(content="내 주식의 총 가치는 얼마야?")
        ]
    }, config=config):
        for key, state in state_map.items():
            if 'messages' in state and state['messages']:
                state['messages'][-1].pretty_print()


if __name__ == "__main__":
    # 직접 실행 시 모든 테스트 실행
    async def run_all_tests():
        agent = StockAgent()
        
        print("🚀 주가 계산 챗봇 테스트 시작")
        print("=" * 50)
        
        await test_basic_stock_query(agent)
        await test_calculation(agent)
        await test_multi_turn_conversation(agent)
        await test_another_multi_turn_scenario(agent)
        await test_streaming_response(agent)
        await test_complex_calculation(agent)
        await test_multiple_stocks(agent)
        await test_conversation_memory(agent)
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료!")
    
    asyncio.run(run_all_tests())
