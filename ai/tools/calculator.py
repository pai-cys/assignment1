"""계산기 도구"""
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool(parse_docstring=True)
def calculator(expression: str) -> str:
    """Calculate expression using Python's numexpr library.

    Args:
        expression (str): A single-line mathematical expression to evaluate. For example: "37593 * 67" or "37593**(1/5)".

    Returns:
        str: The result of the evaluated expression.
    """
    import numexpr
    try:
        result = numexpr.evaluate(expression)
        logger.info(f"Calculated {expression} = {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Calculation error for {expression}: {e}")
        return f"계산 오류: {str(e)}"
