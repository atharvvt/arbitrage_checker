import ccxt
import os
import time

# Initialize Crypto.com client
cryptocom = ccxt.cryptocom({
    'apiKey': os.getenv('CRYPTOCOM_API_KEY'),
    'secret': os.getenv('CRYPTOCOM_API_SECRET'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True
    },
    'recvWindow': 10000,
})

def get_cryptocom_btc_address():
    """Fetch BTC deposit address for Crypto.com"""
    try:
        address_info = cryptocom.fetch_deposit_address('BTC')
        print(address_info['address'])
        return address_info['address']
    except Exception as e:
        print(f"❌ Error fetching Crypto.com deposit address: {e}")
        return None

def get_cryptocom_price(symbol="BTC/USDT"):
    """Fetch current BTC price on Crypto.com"""
    try:
        ticker = cryptocom.fetch_ticker(symbol)
        return ticker
    except Exception as e:
        print(f"❌ Error fetching price for {symbol} on Crypto.com: {e}")
        return None

def buy_order_on_cryptocom(usdt_amount):
    """Create a buy order on Crypto.com"""
    try:
        price = cryptocom.fetch_ticker('BTC/USDT')['ask']
        amount = round(usdt_amount / price, 6)  # round to 6 decimal places for BTC

        # Create market buy order
        order = cryptocom.create_market_buy_order('BTC/USDT', amount)
        print("✅ Bought BTC on Crypto.com:", order)
        return order
    except Exception as e:
        print(f"❌ Error placing buy order on Crypto.com: {e}")
        return None

def sell_order_on_cryptocom(amount_in_btc, symbol="BTC/USDT"):
    """Create a sell order on Crypto.com"""
    try:
        order = cryptocom.create_market_sell_order(symbol, amount_in_btc)
        print(f"✅ Market Sell Order placed on Crypto.com: {order}")
        return order
    except Exception as e:
        print(f"❌ Error placing sell order on Crypto.com: {e}")
        return None

def withdraw_btc_to_address_cryptocom(btc_amount, btc_address):
    """Withdraw BTC from Crypto.com to the given address"""
    try:
        tx = cryptocom.withdraw(
            code='BTC',
            amount=btc_amount,
            address=btc_address
        )
        print("🚀 Withdrew BTC to address from Crypto.com:", tx)
        return tx
    except Exception as e:
        print(f"❌ Error withdrawing BTC from Crypto.com: {e}")
        return None
