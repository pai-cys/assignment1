"""도구 서비스들 - 가독성 개선"""
import asyncio
import time
import logging
from typing import Dict, Any, Optional
from decimal import Decimal, InvalidOperation

import yfinance as yf
import numexpr as ne

from ..utils.exceptions import InvalidTickerException, InvalidExpressionException, StockPriceException, CalculatorException
from .entities import StockPrice, CalculationResult

logger = logging.getLogger(__name__)


class StockPriceService:
    """주가 조회 서비스 - 순차 처리"""
    
    def __init__(self):
        self._lock = asyncio.Lock()  # 순차 처리를 위한 Lock
        self._cache: Dict[str, tuple] = {}  # (timestamp, data)
        self._cache_ttl = 30  # 30초 캐시
    
    def _validate_ticker(self, ticker: str) -> str:
        """티커 검증 - 필요시 exception raise"""
        if not ticker:
            raise InvalidTickerException("티커 심볼이 필요합니다")
        
        if not ticker.strip():
            raise InvalidTickerException("티커 심볼이 비어있습니다")
        
        return ticker.upper()
    
    def _check_cache(self, ticker: str, current_time: float) -> Optional[str]:
        """캐시 확인"""
        if ticker in self._cache:
            cached_time, cached_data = self._cache[ticker]
            if current_time - cached_time < self._cache_ttl:
                logger.info(f"Using cached data for {ticker}")
                return cached_data
        return None
    
    def _create_stock_result(self, ticker: str, hist) -> str:
        """주가 결과 생성"""
        if hist.empty:
            raise StockPriceException(f"No historical data found for ticker {ticker}")
        
        # 주가 정보 생성
        current_price = hist['Close'].iloc[-1]
        result = f"The current stock price of {ticker} is ${current_price:.2f}"
        
        # 변동률 계산
        if len(hist) > 1:
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100
            change_sign = "+" if change >= 0 else ""
            result += f" ({change_sign}${change:.2f}, {change_sign}{change_percent:.2f}%)"
        
        return result
    
    async def get_stock_price(self, ticker: str) -> str:
        """주가 조회 - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        ticker = self._validate_ticker(ticker)
        
        current_time = time.time()
        
        # 전체 처리를 순차적으로 실행
        async with self._lock:
            # 캐시 확인
            cached_result = self._check_cache(ticker, current_time)
            if cached_result:
                return cached_result
            
            # API 호출
            logger.info(f"Fetching fresh data for {ticker}")
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if hist.empty:
                logger.warning(f"No data found for {ticker}, trying with 5d period")
                hist = stock.history(period="5d")
            
            result = self._create_stock_result(ticker, hist)
            
            # 성공한 경우만 캐시에 저장
            self._cache[ticker] = (current_time, result)
            
            logger.info(f"Successfully processed {ticker}")
            return result


class CalculatorService:
    """계산 서비스"""
    
    def _validate_expression(self, expression: str) -> None:
        """수식 검증 - 필요시 exception raise"""
        if not expression:
            raise InvalidExpressionException("계산식이 필요합니다")
        
        if not expression.strip():
            raise InvalidExpressionException("계산식이 비어있습니다")
        
        # 위험한 문자 체크 (보안)
        dangerous_chars = ['import', 'exec', 'eval', '__', 'open', 'file']
        expression_lower = expression.lower()
        for char in dangerous_chars:
            if char in expression_lower:
                raise InvalidExpressionException(f"보안상 허용되지 않는 문자가 포함되어 있습니다: {char}")
    
    def _create_success_result(self, expression: str, result) -> CalculationResult:
        """성공 결과 생성"""
        decimal_result = Decimal(str(result))
        return CalculationResult(
            expression=expression,
            result=decimal_result,
            is_success=True
        )
    
    def _create_error_result(self, expression: str, error_message: str) -> CalculationResult:
        """에러 결과 생성"""
        logger.error(f"계산 오류 ({expression}): {error_message}")
        return CalculationResult(
            expression=expression,
            result=None,
            is_success=False,
            error_message=error_message
        )
    
    def calculate(self, expression: str) -> CalculationResult:
        """수식 계산 - validate 함수로 깔끔하게 처리"""
        # 입력 검증
        self._validate_expression(expression)
        
        # 계산 실행
        result = ne.evaluate(expression)
        
        if isinstance(result, (int, float)):
            return self._create_success_result(expression, result)
        else:
            return self._create_error_result(
                expression, 
                f"Unsupported result type: {type(result)}"
            )


class ToolService:
    """통합 도구 서비스"""
    
    def __init__(self):
        self.stock_service = StockPriceService()
        self.calculator_service = CalculatorService()
    
    async def get_stock_price(self, ticker: str) -> str:
        """주가 조회 - 순차 처리 보장"""
        return await self.stock_service.get_stock_price(ticker)
    
    def calculate(self, expression: str) -> str:
        """계산"""
        calc_result = self.calculator_service.calculate(expression)
        
        if calc_result.is_success:
            return str(calc_result.result)
        else:
            return f"계산 오류: {calc_result.error_message}"