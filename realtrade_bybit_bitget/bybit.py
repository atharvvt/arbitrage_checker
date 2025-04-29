import ccxt
import os
import time

# Initialize Bybit client
bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_API_KEY'),
    'secret': os.getenv('BYBIT_API_SECRET'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True  
    },
    'recvWindow': 10000,
})

def get_bybit_btc_address():
    """Fetch BTC deposit address for Bybit"""
    try:
        address_info = bybit.fetch_deposit_address('BTC')
        print(address_info['address'])
        return address_info['address']
    except Exception as e:
        print(f"❌ Error fetching deposit address: {e}")
        return None

def get_bybit_price(symbol="BTC/USDT"):
    """Fetch current BTC price on Bybit"""
    try:
        ticker = bybit.fetch_ticker(symbol)
        return ticker
    except Exception as e:
        print(f"❌ Error fetching price for {symbol}: {e}")
        return None

def buy_order_on_bybit(usdt_amount):
    """Create a buy order on Bybit"""
    try:
        price = bybit.fetch_ticker('BTC/USDT')['ask']
        amount = round(usdt_amount / price, 6)  # round to 6 decimal places for BTC

        # Create market buy order
        order = bybit.create_market_buy_order('BTC/USDT', amount)
        print("✅ Bought BTC on Bybit:", order)
        return order
    except Exception as e:
        print(f"❌ Error placing buy order: {e}")
        return None

def sell_order_on_bybit(amount_in_btc, symbol="BTC/USDT"):
    """Create a sell order on Bybit"""
    try:
        order = bybit.create_market_sell_order(symbol, amount_in_btc)
        print(f"✅ Market Sell Order placed: {order}")
        return order
    except Exception as e:
        print(f"❌ Error placing sell order: {e}")
        return None

def withdraw_btc_to_address_bybit(btc_amount, btc_address):
    """Withdraw BTC from Bybit to the given address"""
    try:
        tx = bybit.withdraw(
            code='BTC',
            amount=btc_amount,
            address=btc_address
        )
        print("🚀 Withdrew BTC to address:", tx)
        return tx
    except Exception as e:
        print(f"❌ Error withdrawing BTC: {e}")
        return None
