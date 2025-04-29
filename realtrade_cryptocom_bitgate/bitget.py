import ccxt
import os
import time

# Initialize Bitget client
bitget = ccxt.bitget({
    'apiKey': os.getenv('BITGET_API_KEY'),
    'secret': os.getenv('BITGET_API_SECRET'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True  
    },
    'recvWindow': 10000,
})

def get_bitget_btc_address():
    """Fetch BTC deposit address for Bitget"""
    try:
        address_info = bitget.fetch_deposit_address('BTC')
        print(address_info['address'])
        return address_info['address']
    except Exception as e:
        print(f"❌ Error fetching deposit address: {e}")
        return None

def get_bitget_price(symbol="BTC/USDT"):
    """Fetch current BTC price on Bitget"""
    try:
        ticker = bitget.fetch_ticker(symbol)
        return ticker
    except Exception as e:
        print(f"❌ Error fetching price for {symbol}: {e}")
        return None

def buy_order_on_bitget(usdt_amount):
    """Create a buy order on Bitget"""
    try:
        price = bitget.fetch_ticker('BTC/USDT')['ask']
        amount = round(usdt_amount / price, 6)  # round to 6 decimal places for BTC

        # Create market buy order
        order = bitget.create_market_buy_order('BTC/USDT', amount)
        print("✅ Bought BTC on Bitget:", order)
        return order
    except Exception as e:
        print(f"❌ Error placing buy order: {e}")
        return None

def sell_order_on_bitget(amount_in_btc, symbol="BTC/USDT"):
    """Create a sell order on Bitget"""
    try:
        order = bitget.create_market_sell_order(symbol, amount_in_btc)
        print(f"✅ Market Sell Order placed: {order}")
        return order
    except Exception as e:
        print(f"❌ Error placing sell order: {e}")
        return None

def withdraw_btc_to_address_bitget(btc_amount, btc_address):
    """Withdraw BTC from Bitget to the given address"""
    try:
        tx = bitget.withdraw(
            code='BTC',
            amount=btc_amount,
            address=btc_address
        )
        print("🚀 Withdrew BTC to address:", tx)
        return tx
    except Exception as e:
        print(f"❌ Error withdrawing BTC: {e}")
        return None
