[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/alex2yang97-siya-yahoo-finance-mcp-badge.png)](https://mseep.ai/app/alex2yang97-siya-yahoo-finance-mcp)

# Yahoo Finance MCP Server

<div align="right">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a>
</div>

This is a Model Context Protocol (MCP) server that provides comprehensive financial data from Yahoo Finance. It allows you to retrieve detailed information about stocks, including historical prices, company information, financial statements, options data, and market news.

[![smithery badge](https://smithery.ai/badge/@Alex2Yang97/siya-yahoo-finance-mcp)](https://smithery.ai/server/@Alex2Yang97/siya-yahoo-finance-mcp)

## Demo

![MCP Demo](assets/demo.gif)

## MCP Tools

The server exposes the following tools through the Model Context Protocol:

### Stock Information

| Tool | Description |
|------|-------------|
| `get_historical_stock_prices` | Get historical OHLCV data for a stock with customizable period and interval |
| `get_stock_info` | Get comprehensive stock data including price, metrics, and company details |
| `get_yahoo_finance_news` | Get latest news articles for a stock |
| `get_stock_actions` | Get stock dividends and splits history |

### Financial Statements

| Tool | Description |
|------|-------------|
| `get_financial_statement` | Get income statement, balance sheet, or cash flow statement (annual/quarterly) |
| `get_holder_info` | Get major holders, institutional holders, mutual funds, or insider transactions |

### Options Data

| Tool | Description |
|------|-------------|
| `get_option_expiration_dates` | Get available options expiration dates |
| `get_option_chain` | Get options chain for a specific expiration date and type (calls/puts) |

### Analyst Information

| Tool | Description |
|------|-------------|
| `get_recommendations` | Get analyst recommendations or upgrades/downgrades history |

## Real-World Use Cases

With this MCP server, you can use Claude to:

### Stock Analysis

- **Price Analysis**: "Show me the historical stock prices for AAPL over the last 6 months with daily intervals."
- **Financial Health**: "Get the quarterly balance sheet for Microsoft."
- **Performance Metrics**: "What are the key financial metrics for Tesla from the stock info?"
- **Trend Analysis**: "Compare the quarterly income statements of Amazon and Google."
- **Cash Flow Analysis**: "Show me the annual cash flow statement for NVIDIA."

### Market Research

- **News Analysis**: "Get the latest news articles about Meta Platforms."
- **Institutional Activity**: "Show me the institutional holders of Apple stock."
- **Insider Trading**: "What are the recent insider transactions for Tesla?"
- **Options Analysis**: "Get the options chain for SPY with expiration date 2024-06-21 for calls."
- **Analyst Coverage**: "What are the analyst recommendations for Amazon over the last 3 months?"

### Investment Research

- "Create a comprehensive analysis of Microsoft's financial health using their latest quarterly financial statements."
- "Compare the dividend history and stock splits of Coca-Cola and PepsiCo."
- "Analyze the institutional ownership changes in Tesla over the past year."
- "Generate a report on the options market activity for Apple stock with expiration in 30 days."
- "Summarize the latest analyst upgrades and downgrades in the tech sector over the last 6 months."

## Requirements

- Python 3.11 or higher
- Dependencies as listed in `pyproject.toml`, including:
  - mcp
  - yfinance
  - pandas
  - pydantic
  - and other packages for data processing

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install siya-siya-yahoo-finance-mcp
```

### Option 2: Install from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/Alex2Yang97/siya-yahoo-finance-mcp.git
   cd siya-yahoo-finance-mcp
   ```

2. Create and activate a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## Usage

### Command Line Usage

**Option 1: Run with uvx (Recommended - no installation needed):**
```bash
uvx siya-yahoo-finance-mcp
```

**Option 2: After installation, run directly:**
```bash
siya-yahoo-finance-mcp
```

**Option 3: Run as Python module:**
```bash
python -m siya_yahoo_finance_mcp.server
```

### Integration with Claude for Desktop

To integrate this server with Claude for Desktop:

1. Install Claude for Desktop

2. Edit the Claude for Desktop config file:
   - **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the server configuration:

   **Option 1: Using uvx (Recommended - no installation needed):**
   ```json
   {
     "mcpServers": {
       "yfinance": {
         "command": "uvx",
         "args": ["siya-yahoo-finance-mcp"]
       }
     }
   }
   ```

   **Option 2: Using installed package:**
   ```json
   {
     "mcpServers": {
       "yfinance": {
         "command": "siya-yahoo-finance-mcp"
       }
     }
   }
   ```

   **Option 3: Using Python module:**
   ```json
   {
     "mcpServers": {
       "yfinance": {
         "command": "python",
         "args": ["-m", "siya_yahoo_finance_mcp.server"]
       }
     }
   }
   ```

4. Restart Claude for Desktop

### Development Mode

For development or testing with MCP Inspector:

```bash
# If installed from source
uv run siya_yahoo_finance_mcp/server.py

# If installed via pip
python -c "from siya_yahoo_finance_mcp.server import main; main()"
```

## License

MIT


