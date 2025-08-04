# Hyperliquid MCP Server

A [Model Context Protocol (MCP)] server for interacting with [Hyperliquid DEX](https://hyperliquid.xyz/).

## Features

- **Order Management**: Place, modify, and cancel orders with support for both limit and market orders
- **USD-Based Sizing**: Specify order sizes in USD amounts for easier position sizing
- **Leverage Control**: Set and modify leverage for perpetual positions
- **Account Analytics**: Comprehensive P&L tracking, position monitoring, and balance queries
- **Market Data**: Access perpetual and spot market metadata
- **Flexible Authentication**: Separate accounts for trading operations and data queries

## Installation

### From PyPI (Recommended)

```bash
pip install -r requirements.txt
```

### From Source

```bash
git clone https://github.com/OmChillure/hyperliquid
cd hyperliquid_mcp
pip install -e .
```

## Quick Start

### 1. Running with uv/pip

If you prefer to run the server directly:

```json
{
  "mcpServers": {
    "hyperliquid": {
      "command": "python/uvx",
      "args": ["/path/to/your/hyperliquid/server.py"],
      "env": {
        "HYPERLIQUID_MAIN_ACCOUNT_ADDRESS": "",
        "HYPERLIQUID_API_ACCOUNT_ADDRESS": "",
        "HYPERLIQUID_API_ACCOUNT_PRIVATE_KEY": ""
      }
    }
  }
}
```

## Available Tools

### Trading Operations

- **`placeOrder`**: Place limit or market orders with USD-based sizing support
- **`modifyOrder`**: Modify existing orders 
- **`cancelOrder`**: Cancel orders by ID or client order ID

### Account Management  

- **`getAccountState`**: Get comprehensive account information including P&L, positions, and balances
- **`getUserTradeHistory`**: Retrieve trade history and fill data
- **`getUserSpotBalances`**: Query spot token balances

### Market Data

- **`getPerpetualsMeta`**: Get metadata for all perpetual markets
- **`getSpotMeta`**: Get metadata for all spot markets and tokens

## Usage Examples

### Place a Market Order

```python
# Buy $100 worth of ETH at market price
await placeOrder(
    coin="ETH",
    is_buy=True,
    usd_amount=100.0,
    order_type="market"
)
```

### Place a Limit Order with Leverage

```python
# Place a limit buy order with 10x leverage
await placeOrder(
    coin="BTC", 
    is_buy=True,
    size=0.1,
    price=45000.0,
    order_type="limit",
    leverage=10,
    is_cross=False
)
```

### Check Account State

```python
# Get comprehensive account information
account_info = await getAccountState()
print(f"Total PnL: ${account_info['pnl_overview']['total_pnl']}")
print(f"Account Value: ${account_info['pnl_overview']['account_value']}")
```

## Security Architecture

This MCP server uses a dual-account architecture for enhanced security:

- **Main Account**: Your primary trading account that holds funds. Used only for read-only operations.
- **API Account**: A separate account used exclusively for signing transactions. Should have minimal or no funds.

This separation means:
1. Your main trading funds are never directly exposed
2. The API account can be easily rotated if compromised
3. You can grant specific permissions to the API account via Hyperliquid's interface

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HYPERLIQUID_MAIN_ACCOUNT_ADDRESS` | Your main trading account address | Yes |
| `HYPERLIQUID_API_ACCOUNT_ADDRESS` | API account address for signing | Yes |
| `HYPERLIQUID_API_ACCOUNT_PRIVATE_KEY` | Private key for API account | Yes |
| `HYPERLIQUID_BASE_URL` | Hyperliquid API endpoint | No (defaults to mainnet) |

## Development

### Setting up for Development

```bash
git clone https://github.com/yourusername/hyperliquid-mcp
cd hyperliquid-mcp
pip install -e ".[dev]"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
