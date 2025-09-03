"""깔끔한 LangGraph 기반 주가 계산 에이전트"""
import os
import json
import logging
from typing import Annotated, Sequence, TypedDict, Literal, AsyncGenerator
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from ai.tools.stock_tools import tools

logger = logging.getLogger(__name__)

# OpenAI API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")


class LangGraphAgentState(TypedDict):
    """에이전트 상태"""
    messages: Annotated[Sequence[BaseMessage], add_messages]


class AgentNode:
    """에이전트 노드"""
    def __init__(self, llm: ChatOpenAI):
        system_prompt = ChatPromptTemplate([
            SystemMessage(content="당신은 주가 계산을 도와주는 AI Agent입니다. 사용자가 주식 심볼을 언급하면 get_stock_price 도구를 사용해서 가격을 조회하고, 계산이 필요하면 calculator 도구를 사용하세요. 한국어로 친근하게 답변해주세요. API 호출이 실패하면 한 번만 재시도하고, 그래도 실패하면 사용자에게 알려주세요."),
            MessagesPlaceholder(variable_name="messages"),
        ])
        self.chain = system_prompt | llm

    async def __call__(self, inputs: LangGraphAgentState) -> LangGraphAgentState:
        messages = inputs['messages']
        output_message = await self.chain.ainvoke({"messages": messages})
        return {"messages": [output_message]}


class BasicToolNode:
    """도구 노드"""
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: LangGraphAgentState) -> LangGraphAgentState:
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        outputs = []        
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result,
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        
        return {"messages": outputs}


def route_tools(state: LangGraphAgentState) -> Literal[END, 'tools']:
    """도구 라우팅"""
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


class StockAgent:
    """주가 계산 에이전트 - 깔끔한 버전"""
    
    def __init__(self):
        # LLM 설정
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.7,
            streaming=True
        )
        
        # 도구 바인딩
        tool_llm = llm.bind_tools(tools)
        
        # 노드 생성
        agent_node = AgentNode(llm=tool_llm)
        tool_node = BasicToolNode(tools=tools)
        
        # 그래프 구성
        graph_builder = StateGraph(LangGraphAgentState)
        graph_builder.add_node("agent", agent_node)
        graph_builder.add_node("tools", tool_node)
        
        graph_builder.add_edge(START, 'agent')
        graph_builder.add_edge('tools', 'agent')
        graph_builder.add_conditional_edges('agent', route_tools, {"tools": "tools", END: END})
        
        # InMemorySaver로 메모리 설정
        memory = InMemorySaver()
        self.app = graph_builder.compile(checkpointer=memory)
    
    async def stream_response(self, user_input: str, thread_id: str = "default") -> AsyncGenerator[str, None]:
        """실제 토큰 단위 스트리밍 응답 생성"""
        import asyncio

        try:
            config = {'configurable': {'thread_id': thread_id}}

            # LangGraph에서 전체 응답 수집
            full_response = ""
            
            async for state_map in self.app.astream(
                input={"messages": [HumanMessage(content=user_input)]},
                config=config
            ):
                for key, state in state_map.items():
                    if 'messages' in state and state['messages']:
                        last_message = state['messages'][-1]

                        # AI 메시지인지 확인 (도구 호출이 없는 최종 응답)
                        if (hasattr(last_message, '__class__') and 'AI' in str(last_message.__class__) and 
                            hasattr(last_message, 'content') and last_message.content and
                            not (hasattr(last_message, 'tool_calls') and last_message.tool_calls)):
                            full_response = last_message.content

            # 토큰 단위 스트리밍 (단어와 구두점 분리)
            if full_response:
                import re
                # 토큰화: 단어, 숫자, 구두점을 분리
                tokens = re.findall(r'\$?\d+\.?\d*|\w+|[^\w\s]', full_response)
                
                for i, token in enumerate(tokens):
                    yield token  # 토큰 그대로 출력
                    await asyncio.sleep(0.03)  # 토큰별 딜레이
                    
                    # 다음 토큰이 단어/숫자이면 공백 추가
                    if i < len(tokens) - 1:
                        next_token = tokens[i + 1]
                        if re.match(r'\w|\$|\d', next_token):
                            yield " "
                            await asyncio.sleep(0.01)
            else:
                # 응답이 없는 경우
                error_msg = "❌ 에이전트 응답 없음"
                for char in error_msg:
                    yield char
                    await asyncio.sleep(0.02)
                                
        except Exception as e:
            logger.error(f"Stream error: {e}")
            error_msg = f"오류가 발생했습니다: {str(e)}"
            for char in error_msg:
                yield char
                await asyncio.sleep(0.02)
    
    async def get_response(self, user_input: str, thread_id: str = "default") -> str:
        """전체 응답 반환 (비스트리밍)"""
        response_parts = []
        async for chunk in self.stream_response(user_input, thread_id):
            response_parts.append(chunk)
        return "".join(response_parts)
    
    def clear_history(self, thread_id: str = "default"):
        """대화 히스토리 초기화"""
        # InMemorySaver는 thread_id별로 자동 관리
        pass