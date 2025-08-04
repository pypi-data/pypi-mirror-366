import os
from typing import Dict, Any, Optional

from eth_account import Account
from eth_account.signers.local import LocalAccount
from fastmcp import FastMCP
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.utils.types import Cloid

#instance of FastMCP for Hyperliquid MCP
mcp = FastMCP("hyperliquid-mcp")

def get_base_url() -> str:
    """Get the base URL for Hyperliquid DEX from environment or default to mainnet"""
    return os.environ.get("HYPERLIQUID_BASE_URL", constants.MAINNET_API_URL)


def get_main_account_address() -> str:
    """Get the main account address for Hyperliquid DEX from environment"""
    account_address = os.environ.get("HYPERLIQUID_MAIN_ACCOUNT_ADDRESS")
    if not account_address:
        raise ValueError("HYPERLIQUID_MAIN_ACCOUNT_ADDRESS environment variable not set")
    return account_address


def get_api_account_address() -> str:
    """Get the API account address for Hyperliquid DEX from environment"""
    account_address = os.environ.get("HYPERLIQUID_API_ACCOUNT_ADDRESS")
    if not account_address:
        raise ValueError("HYPERLIQUID_API_ACCOUNT_ADDRESS environment variable not set")
    return account_address


def get_api_private_key() -> str:
    """Get the API account private key for Hyperliquid DEX from environment"""
    private_key = os.environ.get("HYPERLIQUID_API_ACCOUNT_PRIVATE_KEY")
    if not private_key:
        raise ValueError("HYPERLIQUID_API_ACCOUNT_PRIVATE_KEY environment variable not set")
    return private_key


def get_exchange() -> Exchange:
    """Get Exchange instance for transactions"""
    account: LocalAccount = Account.from_key(get_api_private_key())
    return Exchange(account, get_base_url())


def get_info() -> Info:
    """Get Info instance for read-only operations"""
    return Info(get_base_url(), skip_ws=True)


@mcp.tool()
async def placeOrder(
        coin: str,
        is_buy: bool,
        size: Optional[float] = None,
        price: Optional[float] = None,
        order_type: str = "limit",
        reduce_only: bool = False,
        cloid: Optional[str] = None,
        leverage: Optional[int] = None,
        is_cross: bool = False,
        usd_amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Place an order on Hyperliquid DEX with support for USD-based sizing.

    Args:
        coin: The trading pair (e.g., "ETH", "BTC", "PURR/USDC") on Hyperliquid DEX
        is_buy: True for buy order, False for sell order on Hyperliquid DEX
        size: Order size in coin units (optional if usd_amount is provided)
        price: Order price (optional for market orders or when using USD amount)
        order_type: "limit" or "market" order on Hyperliquid DEX
        reduce_only: Whether this is a reduce-only order on Hyperliquid DEX
        cloid: Optional client order ID for Hyperliquid DEX
        leverage: Optional leverage multiplier (e.g., 10 for 10x). If provided, updates leverage before placing order
        is_cross: Whether to use cross margin (True) or isolated margin (False) when leverage is set
        usd_amount: Optional USD amount to convert to coin size (e.g., 50 for $50 worth of ETH)

    Returns:
        Order placement result for Hyperliquid DEX
    """
    try:
        exchange = get_exchange()
        info = get_info()
        cloid_obj = Cloid.from_str(cloid) if cloid else None

        if leverage is not None:
            try:
                leverage_result = exchange.update_leverage(leverage, coin, is_cross)
                if leverage_result.get("status") != "ok":
                    return {
                        "success": False,
                        "error": f"Failed to update leverage: {leverage_result}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to update leverage: {str(e)}"
                }

        if usd_amount is not None:
            if size is not None:
                return {
                    "success": False,
                    "error": "Cannot specify both 'size' and 'usd_amount'. Use one or the other."
                }
            
            try:
                all_mids = info.all_mids()
                if coin not in all_mids:
                    return {
                        "success": False,
                        "error": f"Could not find market price for {coin}"
                    }
                
                current_price = float(all_mids[coin])
                
                calculated_size = usd_amount / current_price

                meta = info.meta()
                sz_decimals = 4
                for asset_info in meta["universe"]:
                    if asset_info["name"] == coin:
                        sz_decimals = asset_info["szDecimals"]
                        break
                
                size = round(calculated_size, sz_decimals)
                
                if order_type == "market" and price is None:
                    price = current_price
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to convert USD amount to size: {str(e)}"
                }

        if size is None:
            return {
                "success": False,
                "error": "Must specify either 'size' or 'usd_amount'"
            }

        if order_type == "market":
            result = exchange.market_open(
                coin,
                is_buy,
                size,
                None,  
                0.01   # 1% slippage
            )
        else:
            if price is None:
                return {
                    "success": False,
                    "error": "Price is required for limit orders"
                }
            
            order_config = {"limit": {"tif": "Gtc"}}
            result = exchange.order(
                coin,
                is_buy,
                size,
                price,
                order_config,
                reduce_only,
                cloid_obj
            )

        return {
            "success": result["status"] == "ok",
            "result": result,
            "leverage_applied": leverage if leverage is not None else None,
            "usd_amount_used": usd_amount if usd_amount is not None else None,
            "calculated_size": size if usd_amount is not None else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
@mcp.tool()
async def modifyOrder(
        oid_or_cloid: str,
        coin: str,
        is_buy: bool,
        size: Optional[float] = None,
        price: Optional[float] = None,
        order_type: str = "limit",
        cloid: Optional[str] = None,
        leverage: Optional[int] = None,
        is_cross: bool = False,
        usd_amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Modify an existing order on Hyperliquid DEX with support for leverage and USD-based sizing.

    Args:
        oid_or_cloid: Order ID or Client Order ID to modify on Hyperliquid DEX
        coin: The trading pair on Hyperliquid DEX
        is_buy: True for buy order, False for sell order on Hyperliquid DEX
        size: New order size in coin units (optional if usd_amount is provided)
        price: New order price (optional for market orders or when using USD amount)
        order_type: "limit" or "market" order on Hyperliquid DEX
        cloid: Optional new client order ID for Hyperliquid DEX
        leverage: Optional leverage multiplier (e.g., 10 for 10x). If provided, updates leverage before modifying order
        is_cross: Whether to use cross margin (True) or isolated margin (False) when leverage is set
        usd_amount: Optional USD amount to convert to coin size (e.g., 50 for $50 worth of ETH)

    Returns:
        Order modification result for Hyperliquid DEX
    """
    try:
        exchange = get_exchange()
        info = get_info()

        if leverage is not None:
            try:
                leverage_result = exchange.update_leverage(leverage, coin, is_cross)
                if leverage_result.get("status") != "ok":
                    return {
                        "success": False,
                        "error": f"Failed to update leverage: {leverage_result}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to update leverage: {str(e)}"
                }

        if usd_amount is not None:
            if size is not None:
                return {
                    "success": False,
                    "error": "Cannot specify both 'size' and 'usd_amount'. Use one or the other."
                }
            
            try:
                all_mids = info.all_mids()
                if coin not in all_mids:
                    return {
                        "success": False,
                        "error": f"Could not find market price for {coin}"
                    }
                
                current_price = float(all_mids[coin])

                calculated_size = usd_amount / current_price
                
                meta = info.meta()
                sz_decimals = 4 
                for asset_info in meta["universe"]:
                    if asset_info["name"] == coin:
                        sz_decimals = asset_info["szDecimals"]
                        break
                
                size = round(calculated_size, sz_decimals)
                
                if order_type == "market" and price is None:
                    price = current_price
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to convert USD amount to size: {str(e)}"
                }


        if size is None:
            return {
                "success": False,
                "error": "Must specify either 'size' or 'usd_amount'"
            }
        
        if order_type == "limit":
            if price is None:
                return {
                    "success": False,
                    "error": "Price is required for limit orders"
                }
            order_config = {"limit": {"tif": "Gtc"}}
        else:
            order_config = {"market": {"slippage": 0.01}}

        try:
            oid = int(oid_or_cloid)
            order_id = oid
        except ValueError:
            order_id = Cloid.from_str(oid_or_cloid)

        cloid_obj = Cloid.from_str(cloid) if cloid else None

        result = exchange.modify_order(
            order_id,
            coin,
            is_buy,
            size,
            price if price is not None else 0, 
            order_config,
            False, 
            cloid_obj
        )

        return {
            "success": result["status"] == "ok",
            "result": result,
            "leverage_applied": leverage if leverage is not None else None,
            "usd_amount_used": usd_amount if usd_amount is not None else None,
            "calculated_size": size if usd_amount is not None else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def cancelOrder(
        coin: str,
        oid_or_cloid: str
) -> Dict[str, Any]:
    """
    Cancel an existing order on Hyperliquid DEX

    Args:
        coin: The trading pair on Hyperliquid DEX
        oid_or_cloid: Order ID or Client Order ID to cancel on Hyperliquid DEX

    Returns:
        Order cancellation result for Hyperliquid DEX
    """
    try:
        exchange = get_exchange()

        try:
            oid = int(oid_or_cloid)
            result = exchange.cancel(coin, oid)
        except ValueError:
            cloid = Cloid.from_str(oid_or_cloid)
            result = exchange.cancel_by_cloid(coin, cloid)

        return {
            "success": result["status"] == "ok",
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def getAccountState(
        user: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get complete account state including balances, positions, and all PnL data on Hyperliquid DEX

    Args:
        user: User address (defaults to main account address) on Hyperliquid DEX

    Returns:
        Complete account state with margin summary, positions, spot balances, and PnL data for Hyperliquid DEX
    """
    try:
        info = get_info()
        user_address = user if user else get_main_account_address()

        user_state = info.user_state(user_address)
        spot_state = info.spot_user_state(user_address)

        try:
            fills = info.user_fills(user_address)
        except Exception:
            fills = []

        total_realized_pnl = 0
        total_fees_paid = 0
        realized_pnl_by_coin = {}
        
        for fill in fills:
            closed_pnl = float(fill.get("closedPnl", 0))
            fee = float(fill.get("fee", 0))
            coin = fill.get("coin")
            
            total_realized_pnl += closed_pnl
            total_fees_paid += fee
            
            if coin not in realized_pnl_by_coin:
                realized_pnl_by_coin[coin] = {
                    "realized_pnl": 0,
                    "fees": 0,
                    "trade_count": 0
                }
            
            realized_pnl_by_coin[coin]["realized_pnl"] += closed_pnl
            realized_pnl_by_coin[coin]["fees"] += fee
            realized_pnl_by_coin[coin]["trade_count"] += 1
            
        positions = []
        total_unrealized_pnl = 0
        
        for pos in user_state.get("assetPositions", []):
            position_data = pos.get("position", {})
            if position_data:
                unrealized_pnl = float(position_data.get("unrealizedPnl", 0))
                total_unrealized_pnl += unrealized_pnl
                positions.append(position_data)

        margin_summary = user_state.get("marginSummary", {})
        
        total_pnl = total_unrealized_pnl + total_realized_pnl
        net_pnl_after_fees = total_pnl - total_fees_paid

        return {
            "success": True,
            "user_address": user_address,
            "pnl_overview": {
                "total_unrealized_pnl": total_unrealized_pnl,
                "total_realized_pnl": total_realized_pnl,
                "total_pnl": total_pnl,
                "total_fees_paid": total_fees_paid,
                "net_pnl_after_fees": net_pnl_after_fees,
                "account_value": float(margin_summary.get("accountValue", 0)),
                "withdrawable": margin_summary.get("withdrawable")
            },
            "realized_pnl_breakdown": {
                "total": total_realized_pnl,
                "by_coin": realized_pnl_by_coin,
                "total_trades": len(fills)
            },
            "perp": {
                "margin_summary": margin_summary,
                "cross_margin_summary": user_state.get("crossMarginSummary"),
                "positions": positions,
                "total_unrealized_pnl": total_unrealized_pnl
            },
            "spot": {
                "balances": spot_state.get("balances", [])
            },
            "trade_history": {
                "recent_fills": fills[-10:] if fills else [], 
                "total_fills_count": len(fills)
            },
            "raw_data": {
                "full_user_state": user_state,
                "full_spot_state": spot_state
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def getUserTradeHistory(
        user: Optional[str] = None,
        start_time: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get trade history for a user on Hyperliquid DEX

    Args:
        user: User address (defaults to main account address) on Hyperliquid DEX
        start_time: Start timestamp in milliseconds (optional) for Hyperliquid DEX

    Returns:
        User's trade history for Hyperliquid DEX
    """
    try:
        info = get_info()
        user_address = user if user else get_main_account_address()

        if start_time is not None:
            fills = info.user_fills(user_address, start_time)
        else:
            fills = info.user_fills(user_address)

        return {
            "success": True,
            "user_address": user_address,
            "fills": fills,
            "count": len(fills) if fills else 0
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def getPerpetualsMeta() -> Dict[str, Any]:
    """
    Get metadata for all perpetual markets on Hyperliquid DEX

    Returns:
        Metadata for all perpetual markets on Hyperliquid DEX
    """
    try:
        info = get_info()
        meta = info.meta()

        perps = []
        for asset in meta.get("universe", []):
            perps.append({
                "name": asset["name"],
                "szDecimals": asset["szDecimals"],
                "maxLeverage": asset.get("maxLeverage"),
                "onlyIsolated": asset.get("onlyIsolated", False)
            })

        return {
            "success": True,
            "perpetuals": perps,
            "count": len(perps)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def getSpotMeta() -> Dict[str, Any]:
    """
    Get metadata for all spot markets and tokens on Hyperliquid DEX

    Returns:
        Metadata for all spot markets on Hyperliquid DEX
    """
    try:
        info = get_info()
        spot_meta = info.spot_meta()

        tokens = []
        for token in spot_meta.get("tokens", []):
            tokens.append({
                "name": token["name"],
                "index": token["index"],
                "tokenId": token.get("tokenId"),
                "szDecimals": token["szDecimals"],
                "weiDecimals": token["weiDecimals"]
            })

        return {
            "success": True,
            "tokens": tokens,
            "universe": spot_meta.get("universe", []),
            "count": len(tokens)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def getUserSpotBalances(
        user: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a user's spot token balances on Hyperliquid DEX

    Args:
        user: User address (defaults to main account address) on Hyperliquid DEX

    Returns:
        User's spot token balances for Hyperliquid DEX
    """
    try:
        info = get_info()
        user_address = user if user else get_main_account_address()

        spot_state = info.spot_user_state(user_address)

        balances = []
        for balance in spot_state.get("balances", []):
            balances.append({
                "coin": balance["coin"],
                "token": balance.get("token"),
                "hold": balance["hold"],
                "total": balance["total"],
                "entryNtl": balance.get("entryNtl")
            })

        return {
            "success": True,
            "user_address": user_address,
            "balances": balances,
            "count": len(balances)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point for the CLI command"""
    print("Starting Hyperliquid MCP Server...")
    mcp.run()

if __name__ == "__main__":
    main()
