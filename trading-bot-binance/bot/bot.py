"""
Main trading bot for Binance Futures.

Production-grade bot with validation, logging, and error handling.
"""

import os
from typing import Optional, Dict, Any
from decimal import Decimal
from logger import setup_logger

logger = setup_logger('trading_bot')    

from binance.um_futures import UMFutures

from validation import (
    validate_market_order,
    validate_limit_order,
    validate_cancel_order,
    validate_credentials,
    validate_leverage,
    ValidationError,
    OrderSide
)

class BinanceFuturesBot:
    """
    Trading bot for Binance Futures with validation and logging.
    
    Supports market orders, limit orders, position management, and leverage control.
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: str):
        """
        Initialize trading bot with validated credentials.
        
        Args:
            api_key: Binance API key
            secret_key: Binance secret key
            base_url: API base URL
            
        Raises:
            ValidationError: If credentials are invalid
            RuntimeError: If client initialization fails
        """
        logger.info("Initializing Binance Futures Bot")
        
        # Validate credentials
        try:
            creds = validate_credentials(api_key, secret_key, base_url)
            logger.info("Credentials validated successfully")
        except ValidationError as e:
            logger.error(f"Credential validation failed: {e.message}")
            raise
        
        # Initialize client
        try:
            self.client = UMFutures(
                key=creds.api_key,
                secret=creds.secret_key,
                base_url=creds.base_url
            )
            logger.info("Client initialized successfully")
        except Exception as e:
            logger.error(f"Client initialization failed: {str(e)}")
            raise RuntimeError(f"Failed to initialize client: {str(e)}")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account information dictionary
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            logger.info("Fetching account information")
            account = self.client.account()
            logger.info("Account information retrieved successfully")
            return account
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            raise RuntimeError(f"Failed to get account info: {str(e)}")
    
    def get_balance(self, asset: str = "USDT") -> Decimal:
        """
        Get balance for specific asset.
        
        Args:
            asset: Asset symbol (default: USDT)
            
        Returns:
            Available balance as Decimal
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            logger.info(f"Fetching {asset} balance")
            account = self.get_account_info()   
            
            for asset_info in account['assets']:
                if asset_info['asset'] == asset:
                    balance = Decimal(asset_info['availableBalance'])
                    logger.info(f"{asset} balance: {balance}")
                    return balance
            
            logger.warning(f"Asset {asset} not found in account")
            return Decimal('0')
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise RuntimeError(f"Failed to get balance: {str(e)}")
    
    def get_current_price(self, symbol: str) -> Decimal:
        """
        Get current market price for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price as Decimal
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            logger.info(f"Fetching current price for {symbol}")
            ticker = self.client.ticker_price(symbol=symbol)
            price = Decimal(ticker['price'])
            logger.info(f"{symbol} current price: {price}")
            return price
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {str(e)}")
            raise RuntimeError(f"Failed to get price: {str(e)}")
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Place market order with validation.
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY/SELL)
            quantity: Order quantity
            
        Returns:
            Order response dictionary
            
        Raises:
            ValidationError: If parameters are invalid
            RuntimeError: If order execution fails
        """
        # Validate inputs
        try:
            validated = validate_market_order(symbol, side, quantity)
            logger.info(
                f"Placing market {validated.side} order: "
                f"{validated} {validated.symbol}"
            )
        except ValidationError as e:
            logger.error(f"Market order validation failed: {e.message}")
            raise
        
        # Execute order
        try:
            order = self.client.new_order(
                symbol=validated.symbol,
                side=validated.side,
                type=validated.order_type,
                quantity=float(validated.quantity)
            )
            
            logger.info(
                f"Market order executed successfully: "
                f"Order ID {order['orderId']}, "
                f"Status {order['status']}"
            )
            return order
        except Exception as e:
            logger.error(f"Market order execution failed: {str(e)}")
            raise RuntimeError(f"Order execution failed: {str(e)}")
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place limit order with validation.
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY/SELL)
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force parameter (default: GTC)
            
        Returns:
            Order response dictionary
            
        Raises:
            ValidationError: If parameters are invalid
            RuntimeError: If order execution fails
        """
        # Validate inputs
        try:
            validated = validate_limit_order(
                symbol, side, quantity, price, time_in_force
            )
            logger.info(
                f"Placing limit {validated.side} order: "
                f"{validated.quantity} {validated.symbol} @ {validated.price}, "
                f"TIF: {validated.time_in_force}"
            )
        except ValidationError as e:
            logger.error(f"Limit order validation failed: {e.message}")
            raise
        
        # Execute order
        try:
            order = self.client.new_order(
                symbol=validated.symbol,
                side=validated.side,
                type=validated.order_type,
                timeInForce=validated.time_in_force,
                quantity=float(validated.quantity),
                price=float(validated.price)
            )
            
            logger.info(
                f"Limit order placed successfully: "
                f"Order ID {order['orderId']}, "
                f"Status {order['status']}"
            )
            return order
        except Exception as e:
            logger.error(f"Limit order execution failed: {str(e)}")
            raise RuntimeError(f"Order execution failed: {str(e)}")
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel existing order with validation.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response dictionary
            
        Raises:
            ValidationError: If parameters are invalid
            RuntimeError: If cancellation fails
        """
        # Validate inputs
        try:
            validated = validate_cancel_order(symbol, order_id)
            logger.info(
                f"Cancelling order {validated.order_id} for {validated.symbol}"
            )
        except ValidationError as e:
            logger.error(f"Cancel order validation failed: {e.message}")
            raise
        
        # Cancel order
        try:
            response = self.client.cancel_order(
                symbol=validated.symbol,
                orderId=validated.order_id
            )
            
            logger.info(
                f"Order cancelled successfully: Order ID {response['orderId']}"
            )
            return response
        except Exception as e:
            logger.error(f"Order cancellation failed: {str(e)}")
            raise RuntimeError(f"Order cancellation failed: {str(e)}")
    
    def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """
        Cancel all open orders for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Cancellation response dictionary
            
        Raises:
            RuntimeError: If cancellation fails
        """
        try:
            logger.info(f"Cancelling all orders for {symbol}")
            response = self.client.cancel_open_orders(symbol=symbol)
            logger.info(f"All orders cancelled for {symbol}")
            return response
        except Exception as e:
            logger.error(f"Failed to cancel all orders: {str(e)}")
            raise RuntimeError(f"Failed to cancel all orders: {str(e)}")
    
    def get_open_orders(self, symbol: str) -> list:
        """
        Get all open orders for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            List of open orders
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            logger.info(f"Fetching open orders for {symbol}")
            orders = self.client.get_orders(symbol=symbol)
            logger.info(f"Found {len(orders)} open orders for {symbol}")
            return orders
        except Exception as e:
            logger.error(f"Failed to get open orders: {str(e)}")
            raise RuntimeError(f"Failed to get open orders: {str(e)}")
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current position for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Position information dictionary or None if no position
            
        Raises:
            RuntimeError: If API call fails
        """
        try:
            logger.info(f"Fetching position for {symbol}")
            positions = self.client.get_position_risk(symbol=symbol)
            
            for pos in positions:
                position_amt = Decimal(pos['positionAmt'])
                if position_amt != 0:
                    position_data = {
                        'symbol': pos['symbol'],
                        'amount': position_amt,
                        'entry_price': Decimal(pos['entryPrice']),
                        'mark_price': Decimal(pos['markPrice']),
                        'unrealized_pnl': Decimal(pos['unRealizedProfit']),
                        'leverage': int(pos['leverage'])
                    }
                    logger.info(
                        f"Position found: {position_data['amount']} @ "
                        f"{position_data['entry_price']}, "
                        f"PnL: {position_data['unrealized_pnl']}"
                    )
                    return position_data
            
            logger.info(f"No open position for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Failed to get position: {str(e)}")
            raise RuntimeError(f"Failed to get position: {str(e)}")
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        Set leverage for symbol with validation.
        
        Args:
            symbol: Trading pair symbol
            leverage: Leverage multiplier (1-125)
            
        Returns:
            Leverage change response dictionary
            
        Raises:
            ValidationError: If parameters are invalid
            RuntimeError: If leverage change fails
        """
        # Validate inputs
        try:
            validated = validate_leverage(symbol, leverage)
            logger.info(
                f"Setting leverage to {validated.leverage}x for {validated.symbol}"
            )
        except ValidationError as e:
            logger.error(f"Leverage validation failed: {e.message}")
            raise
        
        # Set leverage
        try:
            response = self.client.change_leverage(
                symbol=validated.symbol,
                leverage=validated.leverage
            )
            
            logger.info(
                f"Leverage set successfully to {response['leverage']}x"
            )
            return response
        except Exception as e:
            logger.error(f"Leverage change failed: {str(e)}")
            raise RuntimeError(f"Leverage change failed: {str(e)}")
    
    def close_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Close current position for symbol using market order.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Order response dictionary or None if no position
            
        Raises:
            RuntimeError: If closing position fails
        """
        try:
            # Get current position
            position = self.get_position(symbol)
            
            if position is None:
                logger.info(f"No position to close for {symbol}")
                return None
            
            # Determine side (opposite of current position)
            amount = position['amount']
            side = OrderSide.SELL.value if amount > 0 else OrderSide.BUY.value
            quantity = abs(float(amount))
            
            logger.info(
                f"Closing position: {side} {quantity} {symbol}"
            )
            
            # Place market order to close position
            order = self.place_market_order(symbol, side, quantity)
            
            logger.info(f"Position closed successfully: Order ID {order['orderId']}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to close position: {str(e)}")
            raise RuntimeError(f"Failed to close position: {str(e)}")