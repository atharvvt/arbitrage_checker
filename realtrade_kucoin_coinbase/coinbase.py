import ccxt
import os

# Initialize Coinbase client
coinbase = ccxt.coinbase({
    'apiKey': os.getenv('COINBASE_API_KEY'),
    'secret': os.getenv('COINBASE_API_SECRET'),
    'password': os.getenv('COINBASE_PASSWORD'),
    'enableRateLimit': True,
})

def get_coinbase_btc_address():
    """Fetch BTC deposit address for Coinbase"""
    try:
        address_info = coinbase.fetch_deposit_address('BTC')
        print(address_info['address'])
        return address_info['address']
    except Exception as e:
        print(f"❌ Error fetching Coinbase deposit address: {e}")
        return None

def get_coinbase_price(symbol="BTC/USDT"):
    """Fetch current BTC price on Coinbase"""
    try:
        ticker = coinbase.fetch_ticker(symbol)
        return ticker
    except Exception as e:
        print(f"❌ Error fetching Coinbase price for {symbol}: {e}")
        return None

def buy_order_on_coinbase(usdt_amount):
    """Create a buy order on Coinbase"""
    try:
        price = coinbase.fetch_ticker('BTC/USDT')['ask']
        amount = round(usdt_amount / price, 6)

        order = coinbase.create_market_buy_order('BTC/USDT', amount)
        print("✅ Bought BTC on Coinbase:", order)
        return order
    except Exception as e:
        print(f"❌ Error placing buy order on Coinbase: {e}")
        return None

def sell_order_on_coinbase(amount_in_btc, symbol="BTC/USDT"):
    """Create a sell order on Coinbase"""
    try:
        order = coinbase.create_market_sell_order(symbol, amount_in_btc)
        print(f"✅ Market Sell Order placed on Coinbase: {order}")
        return order
    except Exception as e:
        print(f"❌ Error placing sell order on Coinbase: {e}")
        return None

def withdraw_btc_to_address_coinbase(btc_amount, btc_address):
    """Withdraw BTC from Coinbase to a given address"""
    try:
        tx = coinbase.withdraw(
            code='BTC',
            amount=btc_amount,
            address=btc_address
        )
        print("🚀 Withdrew BTC from Coinbase:", tx)
        return tx
    except Exception as e:
        print(f"❌ Error withdrawing BTC from Coinbase: {e}")
        return None
