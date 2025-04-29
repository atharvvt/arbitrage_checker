import ccxt
import os

# Initialize KuCoin client
kucoin = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_API_SECRET'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),
    'enableRateLimit': True,
})

def get_kucoin_btc_address():
    """Fetch BTC deposit address for KuCoin"""
    try:
        address_info = kucoin.fetch_deposit_address('BTC')
        print(address_info['address'])
        return address_info['address']
    except Exception as e:
        print(f"❌ Error fetching KuCoin deposit address: {e}")
        return None

def get_kucoin_price(symbol="BTC/USDT"):
    """Fetch current BTC price on KuCoin"""
    try:
        ticker = kucoin.fetch_ticker(symbol)
        return ticker
    except Exception as e:
        print(f"❌ Error fetching KuCoin price for {symbol}: {e}")
        return None

def buy_order_on_kucoin(usdt_amount):
    """Create a buy order on KuCoin"""
    try:
        price = kucoin.fetch_ticker('BTC/USDT')['ask']
        amount = round(usdt_amount / price, 6)

        order = kucoin.create_market_buy_order('BTC/USDT', amount)
        print("✅ Bought BTC on KuCoin:", order)
        return order
    except Exception as e:
        print(f"❌ Error placing buy order on KuCoin: {e}")
        return None

def sell_order_on_kucoin(amount_in_btc, symbol="BTC/USDT"):
    """Create a sell order on KuCoin"""
    try:
        order = kucoin.create_market_sell_order(symbol, amount_in_btc)
        print(f"✅ Market Sell Order placed on KuCoin: {order}")
        return order
    except Exception as e:
        print(f"❌ Error placing sell order on KuCoin: {e}")
        return None

def withdraw_btc_to_address_kucoin(btc_amount, btc_address):
    """Withdraw BTC from KuCoin to a given address"""
    try:
        tx = kucoin.withdraw(
            code='BTC',
            amount=btc_amount,
            address=btc_address
        )
        print("🚀 Withdrew BTC from KuCoin:", tx)
        return tx
    except Exception as e:
        print(f"❌ Error withdrawing BTC from KuCoin: {e}")
        return None
