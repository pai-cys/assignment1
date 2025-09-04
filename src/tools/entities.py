"""도구 엔티티 정의"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


@dataclass
class StockPrice:
    """주가 정보"""
    symbol: str
    price: Decimal
    currency: str = "USD"
    timestamp: datetime = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def formatted_price(self) -> str:
        """포맷된 가격 문자열"""
        return f"${self.price:.2f}"


@dataclass
class CalculationResult:
    """계산 결과"""
    expression: str
    result: Any
    timestamp: datetime = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def is_success(self) -> bool:
        """계산 성공 여부"""
        return self.error is None