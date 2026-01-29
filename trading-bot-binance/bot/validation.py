"""
Input validation module for Binance Futures trading operations.

Provides strict type checking and business logic validation for all trading parameters.
"""

from enum import Enum
from typing import Optional, Literal
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class OrderSide(str, Enum):
    """Valid order sides."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Valid order types - restricted to MARKET and LIMIT only."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class TimeInForce(str, Enum):
    """Valid time in force options for limit orders."""
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


class Symbol(str, Enum):
    """Supported trading symbols."""
    BTCUSDT = "BTCUSDT"
    ETHUSDT = "ETHUSDT"
    BNBUSDT = "BNBUSDT"
    ADAUSDT = "ADAUSDT"
    DOGEUSDT = "DOGEUSDT"
    SOLUSDT = "SOLUSDT"


class MarketOrderRequest(BaseModel):
    """Validation schema for market orders."""
    
    symbol: Symbol = Field(
        description="Trading pair symbol"
    )
    side: OrderSide = Field(
        description="Order side - BUY or SELL"
    )
    order_type: OrderType = Field(
        alias="type",
        description="Order type - must be MARKET"
    )
    quantity: Decimal = Field(
        gt=0,
        max_digits=8,
        decimal_places=3,
        description="Order quantity - must be positive"
    )
    
    class Config:
        use_enum_values = True
        populate_by_name = True
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_precision(cls, v: Decimal) -> Decimal:
        """Ensure quantity has appropriate precision."""
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v


class LimitOrderRequest(BaseModel):
    """Validation schema for limit orders."""
    
    symbol: Symbol = Field(
        description="Trading pair symbol"
    )
    side: OrderSide = Field(
        description="Order side - BUY or SELL"
    )
    order_type: Literal[OrderType.LIMIT] = Field(
        alias="type",
        description="Order type - must be LIMIT"
    )
    quantity: Decimal = Field(
        gt=0,
        max_digits=8,
        decimal_places=3,
        description="Order quantity - must be positive"
    )
    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Limit price - must be positive"
    )
    time_in_force: TimeInForce = Field(
        default=TimeInForce.GTC,
        alias="timeInForce",
        description="Time in force parameter"
    )
    
    class Config:
        use_enum_values = True
        populate_by_name = True
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_precision(cls, v: Decimal) -> Decimal:
        """Ensure quantity has appropriate precision."""
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price_precision(cls, v: Decimal) -> Decimal:
        """Ensure price has appropriate precision."""
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v


class CancelOrderRequest(BaseModel):
    """Validation schema for order cancellation."""
    
    symbol: Symbol = Field(
        description="Trading pair symbol"
    )
    order_id: int = Field(
        gt=0,
        alias="orderId",
        description="Order ID to cancel"
    )
    
    class Config:
        use_enum_values = True
        populate_by_name = True


class PositionQueryRequest(BaseModel):
    """Validation schema for position queries."""
    
    symbol: Symbol = Field(
        description="Trading pair symbol"
    )
    
    class Config:
        use_enum_values = True


class APICredentials(BaseModel):
    """Validation schema for API credentials."""
    
    api_key: str = Field(
        min_length=64,
        max_length=64,
        description="Binance API key - must be exactly 64 characters"
    )
    secret_key: str = Field(
        min_length=64,
        max_length=64,
        description="Binance secret key - must be exactly 64 characters"
    )
    base_url: str = Field(
        description="API base URL"
    )
    
    @field_validator('api_key', 'secret_key')
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        """Ensure keys contain only valid characters."""
        if not all(c.isalnum() for c in v):
            raise ValueError("API keys must contain only alphanumeric characters")
        return v
    
    @field_validator('base_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is valid."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        return v


class LeverageRequest(BaseModel):
    """Validation schema for leverage adjustment."""
    
    symbol: Symbol = Field(
        description="Trading pair symbol"
    )
    leverage: int = Field(
        ge=1,
        le=125,
        description="Leverage multiplier - must be between 1 and 125"
    )
    
    class Config:
        use_enum_values = True


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error in '{field}': {message}")


def validate_market_order(
    symbol: str,
    side: str,
    quantity: float
) -> MarketOrderRequest:
    """
    Validate market order parameters.
    
    Args:
        symbol: Trading pair symbol
        side: Order side (BUY/SELL)
        quantity: Order quantity
        
    Returns:
        Validated MarketOrderRequest object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return MarketOrderRequest(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET.value,
            quantity=Decimal(str(quantity))
        )
    except Exception as e:
        raise ValidationError("market_order", str(e))


def validate_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC"
) -> LimitOrderRequest:
    """
    Validate limit order parameters.
    
    Args:
        symbol: Trading pair symbol
        side: Order side (BUY/SELL)
        quantity: Order quantity
        price: Limit price
        time_in_force: Time in force parameter
        
    Returns:
        Validated LimitOrderRequest object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return LimitOrderRequest(
            symbol=symbol,
            side=side,
            type=OrderType.LIMIT.value,
            quantity=Decimal(quantity),
            price=Decimal(price),
            timeInForce=time_in_force
        )
    except Exception as e:
        raise ValidationError("limit_order", str(e))


def validate_cancel_order(
    symbol: str,
    order_id: int
) -> CancelOrderRequest:
    """
    Validate order cancellation parameters.
    
    Args:
        symbol: Trading pair symbol
        order_id: Order ID to cancel
        
    Returns:
        Validated CancelOrderRequest object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return CancelOrderRequest(
            symbol=symbol,
            orderId=order_id
        )
    except Exception as e:
        raise ValidationError("cancel_order", str(e))


def validate_credentials(
    api_key: str,
    secret_key: str,
    base_url: str
) -> APICredentials:
    """
    Validate API credentials.
    
    Args:
        api_key: Binance API key
        secret_key: Binance secret key
        base_url: API base URL
        
    Returns:
        Validated APICredentials object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return APICredentials(
            api_key=api_key,
            secret_key=secret_key,
            base_url=base_url
        )
    except Exception as e:
        raise ValidationError("credentials", str(e))


def validate_leverage(
    symbol: str,
    leverage: int
) -> LeverageRequest:
    """
    Validate leverage adjustment parameters.
    
    Args:
        symbol: Trading pair symbol
        leverage: Leverage multiplier
        
    Returns:
        Validated LeverageRequest object
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        return LeverageRequest(
            symbol=symbol,
            leverage=leverage
        )
    except Exception as e:
        raise ValidationError("leverage", str(e))
    
if __name__=='__main__':
    print(OrderType.LIMIT.value)