"""
CLI interface for Binance Futures trading bot.

Provides both command-line arguments and interactive menu modes.
"""

import os
import sys
import argparse
from typing import Optional
from decimal import Decimal

from dotenv import load_dotenv

from bot import BinanceFuturesBot
from validation import ValidationError, OrderType, OrderSide, Symbol, TimeInForce
from logger import setup_logger


logger = setup_logger('cli')


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='binance-bot',
        description='Binance Futures Trading Bot CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python cli.py
  
  # Place market order
  python cli.py order market -s BTCUSDT -S BUY -q 0.001
  
  # Place limit order
  python cli.py order limit -s BTCUSDT -S SELL -q 0.001 -p 35000 -t GTC
  
  # Check balance
  python cli.py balance
  
  # Get position
  python cli.py position -s BTCUSDT
  
  # Close position
  python cli.py close -s BTCUSDT
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Order command
    order_parser = subparsers.add_parser('order', help='Place an order')
    order_subparsers = order_parser.add_subparsers(dest='order_type', help='Order type')
    
    # Market order
    market_parser = order_subparsers.add_parser('market', help='Place market order')
    market_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                               help='Trading symbol')
    market_parser.add_argument('-S', '--side', required=True, choices=[s.value for s in OrderSide],
                               help='Order side')
    market_parser.add_argument('-q', '--quantity', required=True, type=float,
                               help='Order quantity')
    
    # Limit order
    limit_parser = order_subparsers.add_parser('limit', help='Place limit order')
    limit_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                              help='Trading symbol')
    limit_parser.add_argument('-S', '--side', required=True, choices=[s.value for s in OrderSide],
                              help='Order side')
    limit_parser.add_argument('-q', '--quantity', required=True, type=float,
                              help='Order quantity')
    limit_parser.add_argument('-p', '--price', required=True, type=float,
                              help='Limit price')
    limit_parser.add_argument('-t', '--time-in-force', default='GTC',
                              choices=[t.value for t in TimeInForce],
                              help='Time in force (default: GTC)')
    
    # Balance command
    balance_parser = subparsers.add_parser('balance', help='Check account balance')
    balance_parser.add_argument('-a', '--asset', default='USDT',
                                help='Asset to check (default: USDT)')
    
    # Position command
    position_parser = subparsers.add_parser('position', help='Get current position')
    position_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                                 help='Trading symbol')
    
    # Close position command
    close_parser = subparsers.add_parser('close', help='Close current position')
    close_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                              help='Trading symbol')
    
    # Price command
    price_parser = subparsers.add_parser('price', help='Get current price')
    price_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                              help='Trading symbol')
    
    # Orders command
    orders_parser = subparsers.add_parser('orders', help='Get open orders')
    orders_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                               help='Trading symbol')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel order')
    cancel_subparsers = cancel_parser.add_subparsers(dest='cancel_type', help='Cancel type')
    
    cancel_one_parser = cancel_subparsers.add_parser('one', help='Cancel single order')
    cancel_one_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                                   help='Trading symbol')
    cancel_one_parser.add_argument('-o', '--order-id', required=True, type=int,
                                   help='Order ID to cancel')
    
    cancel_all_parser = cancel_subparsers.add_parser('all', help='Cancel all orders')
    cancel_all_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                                   help='Trading symbol')
    
    # Leverage command
    leverage_parser = subparsers.add_parser('leverage', help='Set leverage')
    leverage_parser.add_argument('-s', '--symbol', required=True, choices=[s.value for s in Symbol],
                                 help='Trading symbol')
    leverage_parser.add_argument('-l', '--leverage', required=True, type=int,
                                 help='Leverage value (1-125)')
    
    return parser


def handle_order_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle order placement commands.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    if args.order_type == 'market':
        logger.info(f"Placing market {args.side} order: {args.quantity} {args.symbol}")
        order = bot.place_market_order(args.symbol, args.side, args.quantity)
        print(f"\nMarket order placed successfully")
        print(f"Order ID: {order['orderId']}")
        print(f"Status: {order['status']}")
        print(f"Executed Quantity: {order.get('executedQty', 'N/A')}")
        
    elif args.order_type == 'limit':
        logger.info(f"Placing limit {args.side} order: {args.quantity} {args.symbol} @ {args.price}")
        order = bot.place_limit_order(
            args.symbol,
            args.side,
            args.quantity,
            args.price,
            args.time_in_force
        )
        print(f"\nLimit order placed successfully")
        print(f"Order ID: {order['orderId']}")
        print(f"Status: {order['status']}")
        print(f"Price: {order.get('price', 'N/A')}")
        print(f"Time in Force: {order.get('timeInForce', 'N/A')}")
    else:
        print("Error: Invalid order type")
        sys.exit(1)


def handle_balance_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle balance check command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    logger.info(f"Checking {args.asset} balance")
    balance = bot.get_balance(args.asset)
    print(f"\n{args.asset} Balance: {balance}")


def handle_position_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle position query command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    logger.info(f"Fetching position for {args.symbol}")
    position = bot.get_position(args.symbol)
    
    if position:
        print(f"\nCurrent Position for {args.symbol}:")
        print(f"Amount: {position['amount']}")
        print(f"Entry Price: {position['entry_price']}")
        print(f"Mark Price: {position['mark_price']}")
        print(f"Unrealized PnL: {position['unrealized_pnl']}")
        print(f"Leverage: {position['leverage']}x")
    else:
        print(f"\nNo open position for {args.symbol}")


def handle_close_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle close position command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    logger.info(f"Closing position for {args.symbol}")
    order = bot.close_position(args.symbol)
    
    if order:
        print(f"\nPosition closed successfully")
        print(f"Order ID: {order['orderId']}")
        print(f"Status: {order['status']}")
    else:
        print(f"\nNo position to close for {args.symbol}")


def handle_price_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle price query command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    logger.info(f"Fetching price for {args.symbol}")
    price = bot.get_current_price(args.symbol)
    print(f"\n{args.symbol} Current Price: {price}")


def handle_orders_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle open orders query command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    logger.info(f"Fetching open orders for {args.symbol}")
    orders = bot.get_open_orders(args.symbol)
    
    if orders:
        print(f"\nOpen Orders for {args.symbol}:")
        for order in orders:
            print(f"\nOrder ID: {order['orderId']}")
            print(f"Type: {order['type']}")
            print(f"Side: {order['side']}")
            print(f"Price: {order.get('price', 'N/A')}")
            print(f"Quantity: {order['origQty']}")
            print(f"Status: {order['status']}")
    else:
        print(f"\nNo open orders for {args.symbol}")


def handle_cancel_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle order cancellation command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    if args.cancel_type == 'one':
        logger.info(f"Cancelling order {args.order_id} for {args.symbol}")
        response = bot.cancel_order(args.symbol, args.order_id)
        print(f"\nOrder cancelled successfully")
        print(f"Order ID: {response['orderId']}")
        
    elif args.cancel_type == 'all':
        logger.info(f"Cancelling all orders for {args.symbol}")
        response = bot.cancel_all_orders(args.symbol)
        print(f"\nAll orders cancelled for {args.symbol}")
    else:
        print("Error: Invalid cancel type")
        sys.exit(1)


def handle_leverage_command(bot: BinanceFuturesBot, args: argparse.Namespace) -> None:
    """
    Handle leverage adjustment command.
    
    Args:
        bot: Trading bot instance
        args: Parsed command arguments
    """
    logger.info(f"Setting leverage to {args.leverage}x for {args.symbol}")
    response = bot.set_leverage(args.symbol, args.leverage)
    print(f"\nLeverage set successfully")
    print(f"Symbol: {response['symbol']}")
    print(f"Leverage: {response['leverage']}x")


def interactive_mode(bot: BinanceFuturesBot) -> None:
    """
    Run bot in interactive menu mode.
    
    Args:
        bot: Trading bot instance
    """
    while True:
        print("\n" + "="*50)
        print("Binance Futures Trading Bot")
        print("="*50)
        print("\n[1] Place Market Order")
        print("[2] Place Limit Order")
        print("[3] Check Balance")
        print("[4] Get Current Price")
        print("[5] View Position")
        print("[6] Close Position")
        print("[7] View Open Orders")
        print("[8] Cancel Order")
        print("[9] Cancel All Orders")
        print("[10] Set Leverage")
        print("[0] Exit")
        print()
        
        try:
            choice = input("Select option: ").strip()
            
            if choice == '0':
                print("\nExiting...")
                break
                
            elif choice == '1':
                # Market order
                print("\n--- Place Market Order ---")
         
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                side = input(f"Side ({', '.join([s.value for s in OrderSide])}): ").strip().upper()
                quantity = float(input("Quantity: ").strip())
                order = bot.place_market_order(symbol, side, quantity)
                print(f"\nOrder placed! Order ID: {order['orderId']}")
                
            elif choice == '2':
                # Limit order
                print("\n--- Place Limit Order ---")
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                side = input(f"Side ({', '.join([s.value for s in OrderSide])}): ").strip().upper()
                quantity = float(input("Quantity: ").strip())
                price = float(input("Price: ").strip())
                tif = input(f"Time in Force (GTC/IOC/FOK, default GTC): ").strip().upper() or "GTC"
                
                order = bot.place_limit_order(symbol, side, quantity, price, tif)
                print(f"\nOrder placed! Order ID: {order['orderId']}")
                
            elif choice == '3':
                # Check balance
                asset = input("Asset (default USDT): ").strip().upper() or "USDT"
                balance = bot.get_balance(asset)
                print(f"\n{asset} Balance: {balance}")
                
            elif choice == '4':
                # Get price
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                price = bot.get_current_price(symbol)
                print(f"\n{symbol} Price: {price}")
                
            elif choice == '5':
                # View position
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                position = bot.get_position(symbol)
                
                if position:
                    print(f"\nPosition:")
                    print(f"Amount: {position['amount']}")
                    print(f"Entry Price: {position['entry_price']}")
                    print(f"Mark Price: {position['mark_price']}")
                    print(f"Unrealized PnL: {position['unrealized_pnl']}")
                    print(f"Leverage: {position['leverage']}x")
                else:
                    print(f"\nNo open position for {symbol}")
                    
            elif choice == '6':
                # Close position
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                confirm = input(f"Confirm close position for {symbol}? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    order = bot.close_position(symbol)
                    if order:
                        print(f"\nPosition closed! Order ID: {order['orderId']}")
                    else:
                        print(f"\nNo position to close")
                else:
                    print("\nCancelled")
                    
            elif choice == '7':
                # View open orders
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                orders = bot.get_open_orders(symbol)
                
                if orders:
                    print(f"\nOpen Orders:")
                    for order in orders:
                        print(f"\nOrder ID: {order['orderId']}")
                        print(f"Type: {order['type']} | Side: {order['side']}")
                        print(f"Quantity: {order['origQty']} | Price: {order.get('price', 'N/A')}")
                else:
                    print(f"\nNo open orders")
                    
            elif choice == '8':
                # Cancel order
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                order_id = int(input("Order ID: ").strip())
                
                bot.cancel_order(symbol, order_id)
                print(f"\nOrder {order_id} cancelled")
                
            elif choice == '9':
                # Cancel all orders
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                confirm = input(f"Confirm cancel all orders for {symbol}? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    bot.cancel_all_orders(symbol)
                    print(f"\nAll orders cancelled for {symbol}")
                else:
                    print("\nCancelled")
                    
            elif choice == '10':
                # Set leverage
                symbol = input(f"Symbol ({', '.join([s.value for s in Symbol])}): ").strip().upper()
                leverage = int(input("Leverage (1-125): ").strip())
                
                bot.set_leverage(symbol, leverage)
                print(f"\nLeverage set to {leverage}x for {symbol}")
                
            else:
                print("\nInvalid option")
                
        except ValidationError as e:
            print(f"\nValidation error: {e.message}")
        except RuntimeError as e:
            print(f"\nRuntime error: {str(e)}")
        except Exception as e:
            print(f"\nError: {str(e)}")
        
        input("\nPress Enter to continue...")


def main():
    """Main entry point for CLI."""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    base_url = os.getenv('BINANCE_BASE_URL', 'https://testnet.binancefuture.com')
    
    # Validate environment variables
    if not api_key or not secret_key:
        print("Error: BINANCE_API_KEY and BINANCE_SECRET_KEY must be set in .env file")
        sys.exit(1)
    
    try:
        # Initialize bot
        bot = BinanceFuturesBot(api_key, secret_key, base_url)
        logger.info("Bot initialized successfully")
        
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # If no command provided, run interactive mode
        if not args.command:
            interactive_mode(bot)
            return
        
        # Handle commands
        if args.command == 'order':
            handle_order_command(bot, args)
        elif args.command == 'balance':
            handle_balance_command(bot, args)
        elif args.command == 'position':
            handle_position_command(bot, args)
        elif args.command == 'close':
            handle_close_command(bot, args)
        elif args.command == 'price':
            handle_price_command(bot, args)
        elif args.command == 'orders':
            handle_orders_command(bot, args)
        elif args.command == 'cancel':
            handle_cancel_command(bot, args)
        elif args.command == 'leverage':
            handle_leverage_command(bot, args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except ValidationError as e:
        logger.error(f"Validation error: {e.message}")
        print(f"\nValidation error: {e.message}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        print(f"\nRuntime error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()