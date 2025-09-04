"""Tools service 단위테스트."""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.tools.service import StockPriceService, CalculatorService
from src.utils.exceptions import InvalidTickerException, InvalidExpressionException, StockPriceException


class TestStockPriceService:
    """StockPriceService 테스트"""
    
    @pytest.fixture
    def stock_service(self):
        """StockPriceService 인스턴스 생성"""
        return StockPriceService()
    
    @pytest.mark.asyncio
    async def test_get_stock_price_success(self, stock_service):
        """주식 가격 조회 성공 테스트"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock 설정
            mock_ticker_instance = MagicMock()
            mock_ticker.return_value = mock_ticker_instance
            
            # Mock historical data
            mock_hist = pd.DataFrame({
                'Close': [150.0, 151.0, 152.0]
            })
            mock_ticker_instance.history.return_value = mock_hist
            
            # 테스트 실행
            result = await stock_service.get_stock_price("AAPL")
            
            # 검증
            assert "AAPL" in result
            assert "150.0" in result
            mock_ticker.assert_called_once_with("AAPL")
    
    @pytest.mark.asyncio
    async def test_get_stock_price_invalid_ticker(self, stock_service):
        """잘못된 티커로 주식 가격 조회 테스트"""
        with pytest.raises(StockPriceException, match="No historical data found for ticker INVALID"):
            await stock_service.get_stock_price("INVALID")
    
    @pytest.mark.asyncio
    async def test_get_stock_price_empty_ticker(self, stock_service):
        """빈 티커로 주식 가격 조회 테스트"""
        with pytest.raises(InvalidTickerException, match="티커 심볼이 필요합니다"):
            await stock_service.get_stock_price("")
    
    @pytest.mark.asyncio
    async def test_get_stock_price_none_ticker(self, stock_service):
        """None 티커로 주식 가격 조회 테스트"""
        with pytest.raises(InvalidTickerException, match="티커 심볼이 필요합니다"):
            await stock_service.get_stock_price(None)
    
    @pytest.mark.asyncio
    async def test_get_stock_price_no_price_info(self, stock_service):
        """가격 정보가 없는 경우 테스트"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock 설정 - 빈 DataFrame 반환
            mock_ticker_instance = MagicMock()
            mock_ticker.return_value = mock_ticker_instance
            mock_ticker_instance.history.return_value = pd.DataFrame()
            
            # 테스트 실행 및 예외 검증
            with pytest.raises(StockPriceException, match="No historical data found for ticker AAPL"):
                await stock_service.get_stock_price("AAPL")
    
    def test_validate_ticker_valid(self, stock_service):
        """유효한 티커 검증 테스트"""
        # 정상 케이스 - 예외가 발생하지 않아야 함
        result = stock_service._validate_ticker("AAPL")
        assert result == "AAPL"
        
        result = stock_service._validate_ticker("tsla")
        assert result == "TSLA"  # 대문자로 변환됨
    
    def test_validate_ticker_invalid(self, stock_service):
        """잘못된 티커 검증 테스트"""
        with pytest.raises(InvalidTickerException, match="티커 심볼이 필요합니다"):
            stock_service._validate_ticker("")
        
        with pytest.raises(InvalidTickerException, match="티커 심볼이 필요합니다"):
            stock_service._validate_ticker(None)
        
        with pytest.raises(InvalidTickerException, match="티커 심볼이 비어있습니다"):
            stock_service._validate_ticker("   ")


class TestCalculatorService:
    """CalculatorService 테스트"""
    
    @pytest.fixture
    def calculator_service(self):
        """CalculatorService 인스턴스 생성"""
        return CalculatorService()
    
    @pytest.mark.asyncio
    async def test_calculate_success(self, calculator_service):
        """계산 성공 테스트"""
        # 기본 사칙연산
        result = await calculator_service.calculate("2 + 3")
        assert "5" in result
        
        result = await calculator_service.calculate("10 - 4")
        assert "6" in result
        
        result = await calculator_service.calculate("3 * 4")
        assert "12" in result
        
        result = await calculator_service.calculate("15 / 3")
        assert "5" in result
    
    @pytest.mark.asyncio
    async def test_calculate_complex_expression(self, calculator_service):
        """복잡한 수식 계산 테스트"""
        result = await calculator_service.calculate("(2 + 3) * 4")
        assert "20" in result
        
        result = await calculator_service.calculate("2 ** 3")
        assert "8" in result
    
    @pytest.mark.asyncio
    async def test_calculate_invalid_expression(self, calculator_service):
        """잘못된 수식 계산 테스트"""
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            await calculator_service.calculate("invalid_expression")
    
    @pytest.mark.asyncio
    async def test_calculate_empty_expression(self, calculator_service):
        """빈 수식 계산 테스트"""
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            await calculator_service.calculate("")
    
    @pytest.mark.asyncio
    async def test_calculate_none_expression(self, calculator_service):
        """None 수식 계산 테스트"""
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            await calculator_service.calculate(None)
    
    @pytest.mark.asyncio
    async def test_calculate_division_by_zero(self, calculator_service):
        """0으로 나누기 테스트"""
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            await calculator_service.calculate("5 / 0")
    
    def test_validate_expression_valid(self, calculator_service):
        """유효한 수식 검증 테스트"""
        # 정상 케이스 - 예외가 발생하지 않아야 함
        calculator_service._validate_expression("2 + 3")
        calculator_service._validate_expression("(1 + 2) * 3")
    
    def test_validate_expression_invalid(self, calculator_service):
        """잘못된 수식 검증 테스트"""
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            calculator_service._validate_expression("")
        
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            calculator_service._validate_expression(None)
        
        with pytest.raises(InvalidExpressionException, match="계산식이 필요합니다"):
            calculator_service._validate_expression("   ")
    
    def test_create_success_result(self, calculator_service):
        """성공 결과 생성 테스트"""
        result = calculator_service._create_success_result("2 + 3", 5.0)
        
        assert "5.0" in result
        assert "계산 결과" in result
    
    def test_create_error_result(self, calculator_service):
        """에러 결과 생성 테스트"""
        error_msg = "테스트 에러"
        result = calculator_service._create_error_result("2 + 3", error_msg)
        
        assert error_msg in result
        assert "계산 실패" in result
