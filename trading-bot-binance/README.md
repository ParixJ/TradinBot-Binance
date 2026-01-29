# Binance Futures Trading Bot

Production-grade trading bot for Binance Futures with CLI interface, input validation, and structured logging.

## Project Structure

```
binance-futures-bot/
├── bot.py                    # Main trading bot class
├── cli.py                    # CLI interface (interactive + command-line)
├── validation.py             # Input validation with Pydantic
├── logger.py                 # JSON logging configuration
├── config.py                 # Configuration management
├── test_validation.py        # Validation tests
├── pyproject.toml            # Project dependencies
├── .env                      # API credentials (create from .env.example)
├── .env.example              # Environment template
├── .gitignore                # Git exclusions
└── README.md                 # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

This installs:
- `binance-futures-connector` - Binance API client
- `python-dotenv` - Environment variables
- `pydantic` - Input validation
- `python-json-logger` - JSON logging
- `pytest` - Testing framework

### 2. Configure API Keys

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Binance testnet API keys:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_SECRET_KEY=your_testnet_secret_key_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

Get testnet keys: https://testnet.binancefuture.com/

### 3. Run the Bot

**Interactive Mode (Recommended):**
```bash
python cli.py
```

**Command-Line Mode:**
```bash
python cli.py order market -s BTCUSDT -S BUY -q 0.001
```

---

## Usage

### Interactive Mode

Run without arguments to get a menu:

```bash
python cli.py
```

```
==================================================
Binance Futures Trading Bot
==================================================

[1] Place Market Order
[2] Place Limit Order
[3] Check Balance
[4] Get Current Price
[5] View Position
[6] Close Position
[7] View Open Orders
[8] Cancel Order
[9] Cancel All Orders
[10] Set Leverage
[0] Exit

Select option:
```

Simply enter a number and follow the prompts.

---

### Command-Line Mode

Execute commands directly from terminal.

#### Place Orders

**Market Order (Buy/Sell immediately at current price):**
```bash
# Buy 0.001 BTC
python cli.py order market -s BTCUSDT -S BUY -q 0.001

# Sell 0.001 BTC
python cli.py order market -s BTCUSDT -S SELL -q 0.001
```

**Limit Order (Buy/Sell at specific price):**
```bash
# Buy 0.001 BTC at $30,000
python cli.py order limit -s BTCUSDT -S BUY -q 0.001 -p 30000

# Sell 0.001 BTC at $35,000
python cli.py order limit -s BTCUSDT -S SELL -q 0.001 -p 35000

# With custom time in force
python cli.py order limit -s BTCUSDT -S BUY -q 0.001 -p 30000 -t IOC
```

#### Check Account Information

**Balance:**
```bash
# Check USDT balance
python cli.py balance

# Check specific asset
python cli.py balance -a BTC
```

**Current Price:**
```bash
python cli.py price -s BTCUSDT
```

**Position:**
```bash
python cli.py position -s BTCUSDT
```

**Open Orders:**
```bash
python cli.py orders -s BTCUSDT
```

#### Manage Positions

**Close Position:**
```bash
python cli.py close -s BTCUSDT
```

**Set Leverage:**
```bash
# Set 10x leverage
python cli.py leverage -s BTCUSDT -l 10
```

#### Cancel Orders

**Cancel Single Order:**
```bash
python cli.py cancel one -s BTCUSDT -o 12345678
```

**Cancel All Orders:**
```bash
python cli.py cancel all -s BTCUSDT
```

---

## Command Reference

### Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-s, --symbol` | Trading symbol | BTCUSDT, ETHUSDT |
| `-S, --side` | Order side | BUY, SELL |
| `-q, --quantity` | Order quantity | 0.001 |
| `-p, --price` | Limit price | 30000 |
| `-t, --time-in-force` | Time in force | GTC, IOC, FOK |
| `-a, --asset` | Asset symbol | USDT, BTC |
| `-o, --order-id` | Order ID | 12345678 |
| `-l, --leverage` | Leverage value | 1-125 |

### Supported Symbols

- BTCUSDT (Bitcoin)
- ETHUSDT (Ethereum)
- BNBUSDT (Binance Coin)
- ADAUSDT (Cardano)
- DOGEUSDT (Dogecoin)
- SOLUSDT (Solana)

### Time in Force Options

- **GTC** (Good Till Cancel) - Order stays until filled or cancelled
- **IOC** (Immediate or Cancel) - Fill available amount, cancel rest
- **FOK** (Fill or Kill) - Fill entire order or cancel

---

## Getting Help

**General help:**
```bash
python cli.py --help
```

**Command-specific help:**
```bash
python cli.py order --help
python cli.py order market --help
python cli.py order limit --help
python cli.py balance --help
```

---

## Testing

Run validation tests:

```bash
pytest test_validation.py -v
```

Run with coverage:

```bash
pytest test_validation.py --cov=. --cov-report=html
```

---

## Logging

Logs are written to `trading_bot.log` in JSON format and displayed in console.

**Log file (JSON):**
```json
{
  "asctime": "2026-01-29 10:30:45",
  "name": "trading_bot",
  "levelname": "INFO",
  "message": "Market order executed successfully: Order ID 12345678"
}
```

**Console (Human-readable):**
```
2026-01-29 10:30:45 - trading_bot - INFO - Market order executed successfully
```

Configure logging in `.env`:
```env
LOG_LEVEL=INFO
LOG_FILE=trading_bot.log
```

---

## Configuration

All configuration via `.env` file:

```env
# API Configuration
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_BASE_URL=https://testnet.binancefuture.com

# Trading Defaults
DEFAULT_SYMBOL=BTCUSDT
DEFAULT_LEVERAGE=1

# Risk Management
MAX_POSITION_SIZE=0.1
STOP_LOSS_PERCENT=2.0
TAKE_PROFIT_PERCENT=5.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=trading_bot.log
```

---

## Examples

### Example 1: Simple Market Buy

```bash
# Check balance
python cli.py balance

# Check current price
python cli.py price -s BTCUSDT

# Buy 0.001 BTC
python cli.py order market -s BTCUSDT -S BUY -q 0.001

# Check position
python cli.py position -s BTCUSDT
```

### Example 2: Limit Order with Take Profit

```bash
# Buy at $30,000
python cli.py order limit -s BTCUSDT -S BUY -q 0.001 -p 30000

# Wait for fill...

# Set take profit at $31,000
python cli.py order limit -s BTCUSDT -S SELL -q 0.001 -p 31000
```

### Example 3: Check Status and Close

```bash
# View open orders
python cli.py orders -s BTCUSDT

# View current position
python cli.py position -s BTCUSDT

# Close position
python cli.py close -s BTCUSDT
```

### Example 4: Using Interactive Mode

```bash
python cli.py

# Select [1] Place Market Order
# Enter: BTCUSDT
# Enter: BUY
# Enter: 0.001

# Select [5] View Position
# Enter: BTCUSDT

# Select [6] Close Position
# Enter: BTCUSDT
# Enter: yes
```

---

## Error Handling

All operations include validation and error handling:

```bash
# Invalid symbol
python cli.py order market -s INVALID -S BUY -q 0.001
# Error: Validation error

# Invalid quantity
python cli.py order market -s BTCUSDT -S BUY -q -0.001
# Error: Validation error: Quantity must be greater than zero

# Invalid leverage
python cli.py leverage -s BTCUSDT -l 200
# Error: Validation error: Leverage must be between 1 and 125
```

---

## Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Contains API keys

2. **Use testnet for development**
   - Practice with fake money first
   - Get familiar with bot behavior

3. **Enable IP restrictions**
   - On Binance API key settings
   - Restrict to your server IP

4. **Never enable withdrawals**
   - Trading keys should only trade
   - Keep withdrawal keys separate

5. **Use separate API keys**
   - One for testing
   - One for production
   - Delete keys when not needed

---

## Troubleshooting

### "API key not found"
Check `.env` file has correct keys:
```bash
cat .env
```

### "Module not found"
Install dependencies:
```bash
pip install -e .
```

### "Connection error"
Check testnet is accessible:
```bash
curl https://testnet.binancefuture.com
```

### "Invalid symbol"
Use supported symbols only: BTCUSDT, ETHUSDT, etc.

### "Insufficient balance"
Get testnet USDT from faucet at testnet.binancefuture.com

---

## API Rate Limits

Binance Futures limits:
- 1200 requests per minute for orders
- 2400 requests per minute for other endpoints

The bot respects these limits. For high-frequency trading, implement rate limiting.

---

## Support

- **Binance Testnet:** https://testnet.binancefuture.com/
- **API Docs:** https://binance-docs.github.io/apidocs/futures/en/
- **Python Connector:** https://github.com/binance/binance-futures-connector-python

