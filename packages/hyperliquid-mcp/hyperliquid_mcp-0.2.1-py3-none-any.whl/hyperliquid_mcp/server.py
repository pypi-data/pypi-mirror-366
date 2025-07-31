"""Hyperliquid MCP Server implementation using fastmcp."""

import os
from typing import Any, Dict

from fastmcp import FastMCP

from hyperliquid_mcp.logging_config import get_logger, setup_logging
from hyperliquid_mcp.models import (
    AssetFilterRequest,
    BulkCancelRequest,
    CalculateMinOrderSizeRequest,
    CancelOrderRequest,
    GetCandleDataRequest,
    GetFundingRatesRequest,
    GetL2OrderbookRequest,
    GetMarketDataRequest,
    GetUserFillsRequest,
    ModifyOrderRequest,
    OrderStatusRequest,
    PlaceOrderRequest,
    UpdateLeverageRequest,
    UserAddressRequest,
    WithdrawRequest,
)
from hyperliquid_mcp.tools.account import AccountClient
from hyperliquid_mcp.tools.market import MarketClient
from hyperliquid_mcp.tools.order import OrderClient

logger = get_logger(__name__)

# Initialize MCP server
mcp: FastMCP = FastMCP("Hyperliquid MCP Server")

# Initialize specialized clients
account_client = AccountClient()
market_client = MarketClient()
order_client = OrderClient()


@mcp.tool()
async def get_positions(request: UserAddressRequest) -> Dict[str, Any]:
    """
    Get current positions from Hyperliquid exchange.

    Args:
        request: User address request with optional user field

    Returns:
        Current positions and margin information
    """
    try:
        return await account_client.get_positions(request.user)
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return {"error": str(e)}


@mcp.tool()
async def update_leverage(request: UpdateLeverageRequest) -> Dict[str, Any]:
    """
    Update leverage for a specific asset on Hyperliquid.

    Args:
        request: Leverage update request with asset, leverage, and margin type

    Returns:
        Leverage update result
    """
    try:
        return await account_client.update_leverage(
            request.asset, request.leverage, request.is_isolated
        )
    except Exception as e:
        logger.error(f"Error updating leverage: {e}")
        return {"error": str(e)}


@mcp.tool()
async def withdraw(request: WithdrawRequest) -> Dict[str, Any]:
    """
    Withdraw USDC from Hyperliquid to external wallet.

    Args:
        request: Withdrawal request with destination and amount

    Returns:
        Withdrawal result
    """
    try:
        return await account_client.withdraw(request.destination, request.amount)
    except Exception as e:
        logger.error(f"Error withdrawing: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_spot_user_state(request: UserAddressRequest) -> Dict[str, Any]:
    """
    Get spot account state and balances from Hyperliquid.

    Args:
        request: User address request with optional user field

    Returns:
        Spot account state data
    """
    try:
        return await account_client.get_spot_user_state(request.user)
    except Exception as e:
        logger.error(f"Error getting spot user state: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_user_fees(request: UserAddressRequest) -> Dict[str, Any]:
    """
    Get user's fee information from Hyperliquid exchange.

    Args:
        request: User address request with optional user field

    Returns:
        User fee information
    """
    try:
        return await account_client.get_user_fees(request.user)
    except Exception as e:
        logger.error(f"Error getting user fees: {e}")
        return {"error": str(e)}


# Market Data Tools
@mcp.tool()
async def get_market_data(request: GetMarketDataRequest) -> Dict[str, Any]:
    """
    Get market data for a specific asset from Hyperliquid.

    Args:
        request: Market data request with asset symbol

    Returns:
        Market data
    """
    try:
        return await market_client.get_market_data(request.asset)
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return {"error": str(e)}


@mcp.tool()
async def calculate_min_order_size(
    request: CalculateMinOrderSizeRequest,
) -> Dict[str, Any]:
    """
    Calculate the minimum order size needed to meet Hyperliquid's minimum order value requirement.

    Args:
        request: Min order size calculation request with asset and minimum value

    Returns:
        Minimum order size calculation
    """
    try:
        return await market_client.calculate_min_order_size(
            request.asset, request.min_value_usd
        )
    except Exception as e:
        logger.error(f"Error calculating min order size: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_candle_data(request: GetCandleDataRequest) -> Dict[str, Any]:
    """
    Get historical candle/OHLCV data for a specific asset from Hyperliquid.

    Args:
        request: Candle data request with asset, interval, and time range

    Returns:
        Historical candle data
    """
    try:
        return await market_client.get_candle_data(
            request.asset, request.interval.value, request.start_time, request.end_time
        )
    except Exception as e:
        logger.error(f"Error getting candle data: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_user_fills_by_time(request: GetUserFillsRequest) -> Dict[str, Any]:
    """
    Get user fills/trades within a specific time range from Hyperliquid exchange.

    Args:
        request: User fills request with time range and optional user address

    Returns:
        Time-filtered user fills data
    """
    try:
        return await order_client.get_user_fills_by_time(
            request.start_time, request.end_time, request.user
        )
    except Exception as e:
        logger.error(f"Error getting user fills by time: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_funding_rates(request: GetFundingRatesRequest) -> Dict[str, Any]:
    """
    Get current and historical funding rates for perpetual contracts.

    Args:
        request: Funding rates request with optional asset filter and history options

    Returns:
        Funding rates data
    """
    try:
        return await market_client.get_funding_rates(
            request.asset, request.include_history, request.start_time
        )
    except Exception as e:
        logger.error(f"Error getting funding rates: {e}")
        return {"error": str(e)}


# Order Management Tools
@mcp.tool()
async def place_order(request: PlaceOrderRequest) -> Dict[str, Any]:
    """
    Place an order on Hyperliquid exchange.

    Args:
        request: Order placement request with all order parameters

    Returns:
        Order placement result
    """
    try:
        return await order_client.place_order(
            request.asset,
            request.is_buy,
            request.size,
            request.order_type.value,
            request.price,
            request.time_in_force.value,
            request.reduce_only,
            request.take_profit,
            request.stop_loss,
        )
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return {"error": str(e)}


@mcp.tool()
async def cancel_order(request: CancelOrderRequest) -> Dict[str, Any]:
    """
    Cancel an existing order on Hyperliquid exchange.

    Args:
        request: Order cancellation request with asset and order ID

    Returns:
        Cancellation result
    """
    try:
        return await order_client.cancel_order(request.asset, request.order_id)
    except Exception as e:
        logger.error(f"Error canceling order: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_open_orders(request: UserAddressRequest) -> Dict[str, Any]:
    """
    Get open orders from Hyperliquid exchange.

    Args:
        request: User address request with optional user field

    Returns:
        Open orders data
    """
    try:
        return await order_client.get_open_orders(request.user)
    except Exception as e:
        logger.error(f"Error getting open orders: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_order_status(request: OrderStatusRequest) -> Dict[str, Any]:
    """
    Get the status of a specific order by order ID.

    Args:
        request: Order status request with order ID and optional user address

    Returns:
        Order status information
    """
    try:
        return await order_client.get_order_status(request.order_id, request.user)
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        return {"error": str(e)}


@mcp.tool()
async def modify_order(request: ModifyOrderRequest) -> Dict[str, Any]:
    """
    Modify an existing order on Hyperliquid exchange.

    Args:
        request: Order modification request with asset, order ID, and optional new parameters

    Returns:
        Modification result
    """
    try:
        return await order_client.modify_order(
            request.asset,
            request.order_id,
            request.new_price,
            request.new_size,
            request.new_time_in_force.value if request.new_time_in_force else None,
        )
    except Exception as e:
        logger.error(f"Error modifying order: {e}")
        return {"error": str(e)}


@mcp.tool()
async def bulk_cancel_orders(request: BulkCancelRequest) -> Dict[str, Any]:
    """
    Cancel multiple orders at once on Hyperliquid exchange.

    Args:
        request: Bulk cancellation request with list of orders to cancel

    Returns:
        Bulk cancellation result
    """
    try:
        return await order_client.bulk_cancel_orders(request.orders)
    except Exception as e:
        logger.error(f"Error bulk canceling orders: {e}")
        return {"error": str(e)}


@mcp.tool()
async def cancel_all_orders(request: AssetFilterRequest) -> Dict[str, Any]:
    """
    Cancel all open orders, optionally filtered by asset.

    Args:
        request: Asset filter request with optional asset symbol

    Returns:
        Cancellation result
    """
    try:
        return await order_client.cancel_all_orders(request.asset)
    except Exception as e:
        logger.error(f"Error canceling all orders: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_user_fills(request: UserAddressRequest) -> Dict[str, Any]:
    """
    Get recent user fills/trades from Hyperliquid exchange.

    Args:
        request: User address request with optional user field

    Returns:
        User fills data
    """
    try:
        return await order_client.get_user_fills(request.user)
    except Exception as e:
        logger.error(f"Error getting user fills: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_l2_orderbook(request: GetL2OrderbookRequest) -> Dict[str, Any]:
    """
    Get L2 order book depth for a specific asset from Hyperliquid.

    Args:
        request: L2 orderbook request with asset and optional significant figures

    Returns:
        L2 orderbook data
    """
    try:
        return await market_client.get_l2_orderbook(
            request.asset, request.significant_figures
        )
    except Exception as e:
        logger.error(f"Error getting L2 orderbook: {e}")
        return {"error": str(e)}


def main() -> None:
    """Main entry point for the MCP server."""
    show_logs = os.getenv("HYPERLIQUID_MCP_SHOW_LOGS", "false").lower() == "true"
    setup_logging(include_console=show_logs)

    # Validate environment variables
    required_vars = ["HYPERLIQUID_PRIVATE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some trading operations may not be available")

    logger.info("Starting Hyperliquid MCP Server...")

    # Run the server
    mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
