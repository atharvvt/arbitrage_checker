import ccxt
import os
import time

# Initialize Binance client
binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True
    },
    'recvWindow': 10000,
})

def get_binance_btc_address():
    """Fetch BTC deposit address for Binance"""
    try:
        address_info = binance.fetch_deposit_address('BTC')
        print(address_info['address'])
        return address_info['address']
    except Exception as e:
        print(f"❌ Error fetching Binance deposit address: {e}")
        return None

def get_binance_price(symbol="BTC/USDT"):
    """Fetch current BTC price on Binance"""
    try:
        ticker = binance.fetch_ticker(symbol)
        return ticker
    except Exception as e:
        print(f"❌ Error fetching price for {symbol} on Binance: {e}")
        return None

def buy_order_on_binance(usdt_amount):
    """Create a buy order on Binance"""
    try:
        price = binance.fetch_ticker('BTC/USDT')['ask']
        amount = round(usdt_amount / price, 6)  # round to 6 decimal places for BTC

        # Create market buy order
        order = binance.create_market_buy_order('BTC/USDT', amount)
        print("✅ Bought BTC on Binance:", order)
        return order
    except Exception as e:
        print(f"❌ Error placing buy order on Binance: {e}")
        return None

def sell_order_on_binance(amount_in_btc, symbol="BTC/USDT"):
    """Create a sell order on Binance"""
    try:
        order = binance.create_market_sell_order(symbol, amount_in_btc)
        print(f"✅ Market Sell Order placed on Binance: {order}")
        return order
    except Exception as e:
        print(f"❌ Error placing sell order on Binance: {e}")
        return None

def withdraw_btc_to_address_binance(btc_amount, btc_address):
    """Withdraw BTC from Binance to the given address"""
    try:
        tx = binance.withdraw(
            code='BTC',
            amount=btc_amount,
            address=btc_address
        )
        print("🚀 Withdrew BTC to address from Binance:", tx)
        return tx
    except Exception as e:
        print(f"❌ Error withdrawing BTC from Binance: {e}")
        return None
