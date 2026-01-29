from ..bot.trade import BinanceFuturesBot
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv('BINANCE_API_KEY')
secret_key=os.getenv('API_SECRET')

base_url="https://testnet.binancefuture.com"

# Initialize bot
bot = BinanceFuturesBot(api_key, secret_key, base_url)

# Get account balance
balance = bot.get_balance()
print(f"Balance: {balance} USDT")

# Get current price
price = bot.get_current_price("BTCUSDT")
print(f"BTC Price: {price}")

# Place market buy order
order = bot.place_market_order("BTCUSDT", "BUY", 0.001)
print(f"Order ID: {order['orderId']}")

# Place limit sell order
order = bot.place_limit_order("BTCUSDT", "SELL", 0.001, 35000.00)
print(f"Order ID: {order['orderId']}")

# Get current position
position = bot.get_position("BTCUSDT")
if position:
    print(f"Position: {position['amount']} BTC")
    print(f"Entry Price: {position['entry_price']}")
    print(f"Unrealized PnL: {position['unrealized_pnl']}")

# Close position
bot.close_position("BTCUSDT")

# Set leverage
bot.set_leverage("BTCUSDT", 10)

# Cancel order
bot.cancel_order("BTCUSDT", order_id=12345678)

# Cancel all orders
bot.cancel_all_orders("BTCUSDT")