"""LangGraph 그래프 구성"""
import logging
from typing import List

from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver

from .nodes import AgentNode, ToolNode, LangGraphAgentState

logger = logging.getLogger(__name__)


class LangGraphBuilder:
    """LangGraph 빌더 클래스"""
    
    @staticmethod
    def build_graph(
        agent_node: AgentNode,
        tool_node: ToolNode,
        use_memory: bool = True
    ):
        """LangGraph를 구성합니다"""
        logger.info("LangGraph 구성 중...")
        
        # 그래프 생성
        graph = (
            StateGraph(LangGraphAgentState)
            .add_node("agent", agent_node)
            .add_node("tools", tool_node)
            .set_entry_point("agent")
            .add_conditional_edges("agent", tools_condition)
            .add_edge("tools", "agent")
        )
        
        # 메모리 설정
        if use_memory:
            checkpointer = MemorySaver()
            compiled_graph = graph.compile(checkpointer=checkpointer)
        else:
            compiled_graph = graph.compile()
        
        logger.info("LangGraph 구성 완료")
        return compiled_graph
