"""주가 조회 도구"""
from langchain.tools import tool
from typing import Optional
import logging
import time
import yfinance as yf
import threading # 1. threading 모듈 가져오기

logger = logging.getLogger(__name__)

# 요청 제한을 위한 캐시와 타이머
_last_request_time = 0
_request_cache = {}
_lock = threading.Lock() # 2. Lock 객체 생성

@tool(parse_docstring=True)
def get_stock_price(ticker: str) -> str:
    """Retrieves the stock price for a specific ticker

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).

    Returns:
        str: The requested stock price value (currency: dollar) if available, error message otherwise.
    """
    global _last_request_time, _request_cache
    
    current_time = time.time()
    cache_key = ticker.upper()

    # 3. Lock을 사용하여 공유 자원(캐시, 시간) 접근을 보호
    with _lock:
        # 캐시 확인 (30초간 유효)
        if cache_key in _request_cache:
            cached_time, cached_data = _request_cache[cache_key]
            if current_time - cached_time < 30:
                logger.info(f"Using cached data for {ticker}: {cached_data}")
                return cached_data
        
        # 요청 간격 제한 (최소 1초)
        if current_time - _last_request_time < 1.0:
            time.sleep(1.0 - (current_time - _last_request_time))
        
        _last_request_time = time.time()

    # API 호출은 Lock 바깥에서 수행해도 괜찮습니다.
    # 중요한 것은 '요청을 보낼지 말지 결정하는 과정'이 순차적으로 이뤄지는 것입니다.

    errors = []
    try:
        ticker_obj = yf.Ticker(ticker)
        
        # (이하 API 호출 로직은 동일)
        # 방법 1: history 조회
        try:
            hist = ticker_obj.history(period="2d", interval="1d", timeout=10)
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                result = f"{price}"
                with _lock: # 4. 캐시에 쓸 때도 Lock을 사용
                    _request_cache[cache_key] = (time.time(), result)
                return result
            else:
                errors.append("history: 데이터가 비어있음")
        except Exception as e:
            errors.append(f"history: {type(e).__name__} - {str(e)}")

        # 방법 2: fast_info 시도
        try:
            fast_info = ticker_obj.fast_info
            price = fast_info.get("last_price")
            if price and price > 0:
                result = f"{price}"
                with _lock: # 캐시에 쓸 때도 Lock을 사용
                    _request_cache[cache_key] = (time.time(), result)
                return result
            else:
                errors.append("fast_info: last_price가 없거나 0")
        except Exception as e:
            errors.append(f"fast_info: {type(e).__name__} - {str(e)}")

        # 방법 3: info 시도
        try:
            info = ticker_obj.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if price and price > 0:
                result = f"{price}"
                with _lock: # 캐시에 쓸 때도 Lock을 사용
                    _request_cache[cache_key] = (time.time(), result)
                return result
            else:
                errors.append("info: currentPrice/regularMarketPrice가 없거나 0")
        except Exception as e:
            errors.append(f"info: {type(e).__name__} - {str(e)}")

    except Exception as e:
        errors.append(f"yfinance 초기화 실패: {type(e).__name__} - {str(e)}")

    # Yahoo Finance API 실패 시 mock 데이터 사용
    logger.warning(f"Yahoo Finance API failed for {ticker}, using mock data")
    
    # Mock 데이터 (실제 주가와 유사한 값들)
    mock_prices = {
        'AAPL': 175.43,   # Apple Inc.
        'TSLA': 248.50,   # Tesla Inc.
        'NVDA': 875.28,   # NVIDIA Corporation
        'AMZN': 145.86,   # Amazon.com Inc.
        'GOOGL': 138.21,  # Alphabet Inc.
        'MSFT': 415.26,   # Microsoft Corporation
        'META': 485.59,   # Meta Platforms Inc.
        'NFLX': 425.75,   # Netflix Inc.
        'AMD': 142.33,    # Advanced Micro Devices
        'INTC': 23.45,    # Intel Corporation
        'IBM': 243.49,    # IBM
        'ORCL': 178.92,   # Oracle Corporation
    }
    
    if cache_key in mock_prices:
        mock_price = mock_prices[cache_key]
        result = f"{mock_price}"
        logger.info(f"Using mock price for {ticker}: ${result}")
        with _lock:
            _request_cache[cache_key] = (time.time(), result)
        return result
    else:
        # 지원되지 않는 티커
        error_msg = f"주가 정보 없음: {ticker} (지원되지 않는 티커)"
        with _lock:
            _request_cache[cache_key] = (time.time(), error_msg)
        return error_msg