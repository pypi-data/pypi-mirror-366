"""Pydantic models for Hyperliquid MCP server - Request validation only."""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


# Base Models
class BaseRequestModel(BaseModel):
    """Base model with common validation methods."""

    @classmethod
    def validate_ethereum_address(cls, v: Optional[str]) -> Optional[str]:
        """Reusable Ethereum address validation."""
        if v is not None and (not v.startswith("0x") or len(v) != 42):
            raise ValueError("Invalid Ethereum address format")
        return v


class AssetRequestModel(BaseRequestModel):
    """Base model for requests involving assets."""

    asset: str = Field(..., description="Asset symbol (e.g., 'BTC', 'ETH')")


class UserRequestModel(BaseRequestModel):
    """Base model for requests involving user addresses."""

    user: Optional[str] = Field(None, description="User address to query (optional)")

    @field_validator("user")
    @classmethod
    def validate_user_address(cls, v: Optional[str]) -> Optional[str]:
        return cls.validate_ethereum_address(v)


class AmountRequestModel(BaseRequestModel):
    """Base model for requests involving amounts."""

    amount: float = Field(..., gt=0, description="Amount")


class TimeRangeRequestModel(BaseRequestModel):
    """Base model for requests with time ranges."""

    start_time: int = Field(..., description="Start time in epoch milliseconds")
    end_time: Optional[int] = Field(None, description="End time in epoch milliseconds")

    @model_validator(mode="after")
    def validate_time_range(self):
        """Validate end time is after start time if provided."""
        if self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


class OrderType(str, Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    TRIGGER = "trigger"


class TimeInForce(str, Enum):
    """Time in force enumeration."""

    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate Or Cancel
    ALO = "ALO"  # Add Liquidity Only


class CandleInterval(str, Enum):
    """Candle interval enumeration."""

    ONE_MINUTE = "1m"
    THREE_MINUTES = "3m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    EIGHT_HOURS = "8h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    THREE_DAYS = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


# Request Models - Only for input validation
class PlaceOrderRequest(AssetRequestModel):
    """Request model for placing orders."""

    is_buy: bool = Field(..., description="True for buy order, False for sell order")
    size: float = Field(..., gt=0, description="Order size/quantity")
    order_type: OrderType = Field(default=OrderType.MARKET, description="Order type")
    price: Optional[float] = Field(
        None, gt=0, description="Order price (required for limit/trigger)"
    )
    time_in_force: TimeInForce = Field(
        default=TimeInForce.GTC, description="Time in force"
    )
    reduce_only: bool = Field(
        default=False, description="Whether this is a reduce-only order"
    )
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")

    @model_validator(mode="after")
    def validate_price_for_order_type(self):
        """Validate price is provided for limit/trigger orders."""
        if (
            self.order_type in [OrderType.LIMIT, OrderType.TRIGGER]
            and self.price is None
        ):
            raise ValueError(f"Price is required for {self.order_type} orders")
        return self


class CancelOrderRequest(AssetRequestModel):
    """Request model for canceling orders."""

    order_id: int = Field(..., description="Order ID to cancel")


class ModifyOrderRequest(AssetRequestModel):
    """Request model for modifying orders."""

    order_id: int = Field(..., description="Order ID to modify")
    new_price: Optional[float] = Field(None, gt=0, description="New order price")
    new_size: Optional[float] = Field(None, gt=0, description="New order size")
    new_time_in_force: Optional[TimeInForce] = Field(
        None, description="New time in force"
    )

    @model_validator(mode="after")
    def at_least_one_field(self):
        """Ensure at least one field is provided for modification."""
        if all(
            field is None
            for field in [self.new_price, self.new_size, self.new_time_in_force]
        ):
            raise ValueError(
                "At least one parameter (new_price, new_size, or new_time_in_force) must be provided"
            )
        return self


class BulkCancelRequest(BaseModel):
    """Request model for bulk order cancellation."""

    orders: List[Dict[str, Union[str, int]]] = Field(
        ..., description="List of orders to cancel with 'asset' and 'order_id' fields"
    )

    @field_validator("orders")
    @classmethod
    def validate_orders(
        cls, v: List[Dict[str, Union[str, int]]]
    ) -> List[Dict[str, Union[str, int]]]:
        """Validate order format."""
        for order in v:
            if not isinstance(order, dict):
                raise ValueError("Each order must be a dictionary")
            if "asset" not in order or "order_id" not in order:
                raise ValueError("Each order must have 'asset' and 'order_id' fields")
        return v


class UpdateLeverageRequest(AssetRequestModel):
    """Request model for updating leverage."""

    leverage: float = Field(..., gt=0, le=100, description="New leverage value")
    is_isolated: bool = Field(
        default=True, description="Whether to use isolated margin"
    )


class WithdrawRequest(AmountRequestModel):
    """Request model for withdrawals."""

    destination: str = Field(
        ..., description="Destination wallet address for withdrawal"
    )
    amount: float = Field(
        ...,
        gt=1.0,
        description="Amount of USDC to withdraw (minimum $1.01 due to $1 fee)",
    )

    @field_validator("destination")
    @classmethod
    def validate_destination_address(cls, v: str) -> Optional[str]:
        return cls.validate_ethereum_address(v)


class GetCandleDataRequest(AssetRequestModel, TimeRangeRequestModel):
    """Request model for candle data."""

    interval: CandleInterval = Field(..., description="Time interval")
    end_time: int = Field(..., description="End time in epoch milliseconds")

    @model_validator(mode="after")
    def validate_time_range(self):
        """Validate end time is after start time."""
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


class GetUserFillsRequest(TimeRangeRequestModel, UserRequestModel):
    """Request model for user fills by time."""

    pass


class GetFundingRatesRequest(BaseRequestModel):
    """Request model for funding rates."""

    asset: Optional[str] = Field(None, description="Asset symbol to filter by")
    include_history: bool = Field(
        default=False, description="Include historical funding data"
    )
    start_time: Optional[int] = Field(
        None, description="Start time for historical data"
    )

    @model_validator(mode="after")
    def validate_start_time_for_history(self):
        """Validate start time is provided when including history."""
        if self.include_history and self.start_time is None:
            raise ValueError("start_time is required when include_history is True")
        return self


class GetL2OrderbookRequest(AssetRequestModel):
    """Request model for L2 orderbook."""

    significant_figures: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Number of significant figures for price aggregation",
    )


class GetMarketDataRequest(AssetRequestModel):
    """Request model for market data."""

    pass


class CalculateMinOrderSizeRequest(AssetRequestModel):
    """Request model for minimum order size calculation."""

    min_value_usd: float = Field(
        default=10.0, gt=0, description="Minimum order value in USD"
    )


class UserAddressRequest(UserRequestModel):
    """Request model for operations requiring user address."""

    pass


class AssetFilterRequest(BaseRequestModel):
    """Request model for operations with optional asset filter."""

    asset: Optional[str] = Field(
        None, description="Asset symbol to filter by (optional)"
    )


class OrderStatusRequest(UserRequestModel):
    """Request model for order status."""

    order_id: int = Field(..., description="Order ID to check status for")
