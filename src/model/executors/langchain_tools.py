"""LangChain 도구 실행기"""
from langchain.tools import tool
from typing import Any

from ...tools.container import tools_container

# 의존성 주입받은 도구 서비스 인스턴스
tool_service = tools_container.service()


@tool(parse_docstring=True)
def get_stock_price(ticker: str) -> str:
    """Retrieves the stock price for a specific ticker

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        str: The requested stock price value (currency: dollar) if available, error message otherwise.
    """
    return tool_service.get_stock_price(ticker)


@tool(parse_docstring=True)
def calculator(expression: str) -> str:
    """Calculate expression using Python's numexpr library.

    Args:
        expression (str): A single-line mathematical expression to evaluate. For example: "37593 * 67" or "37593**(1/5)".

    Returns:
        str: The result of the evaluated expression.
    """
    return tool_service.calculate(expression)


# 도구 목록
tools = [get_stock_price, calculator]
