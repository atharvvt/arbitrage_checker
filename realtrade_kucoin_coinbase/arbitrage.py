import os
import time
import ccxt
import random
from dotenv import load_dotenv
from .kucoin import buy_order_on_kucoin, get_kucoin_btc_address, sell_order_on_kucoin, withdraw_btc_to_address_kucoin
from .coinbase import buy_order_on_coinbase, get_coinbase_btc_address, sell_order_on_coinbase, withdraw_btc_to_address_coinbase

# Load environment variables
load_dotenv()

# Constants
kucoin_fee = 0.001  # 0.1% (KuCoin spot fee)
coinbase_fee = 0.006  # 0.6% (Coinbase Advanced Trade fee)
network_fee = 0.0001  # BTC withdrawal network fee
tax_rate = 0.0  # Set your local tax rate if applicable
slippage_percentage = 0.001  # 0.1%

# Initialize exchanges
kucoin = ccxt.kucoin({
    'apiKey': os.getenv('KUCOIN_API_KEY'),
    'secret': os.getenv('KUCOIN_API_SECRET'),
    'password': os.getenv('KUCOIN_PASSPHRASE'),  # KuCoin needs 'password' 
    'enableRateLimit': True
})

coinbase = ccxt.coinbase({
    'apiKey': os.getenv('COINBASE_API_KEY'),
    'secret': os.getenv('COINBASE_API_SECRET'),
    'password': os.getenv('COINBASE_PASSWORD'),
    'enableRateLimit': True
})

def get_kucoin_price(symbol="BTC/USDT"):
    try:
        order_book = kucoin.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ KuCoin error: {e}")
        return None, None

def get_coinbase_price(symbol="BTC/USDT"):
    try:
        order_book = coinbase.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Coinbase error: {e}")
        return None, None

def apply_slippage(price, slippage_pct):
    return price * (1 + random.uniform(-slippage_pct, slippage_pct))

def calculate_arbitrage_profit(buy_price, sell_price, buy_fee, sell_fee, trade_amount_usd, from_exchange, to_exchange):
    buy_price = apply_slippage(buy_price, slippage_percentage)
    sell_price = apply_slippage(sell_price, slippage_percentage)

    btc_bought = trade_amount_usd / buy_price
    btc_to_sell = btc_bought - network_fee
    usd_gained = btc_to_sell * sell_price

    buy_fee_usd = trade_amount_usd * buy_fee
    sell_fee_usd = usd_gained * sell_fee
    tax = tax_rate * (usd_gained - trade_amount_usd)

    profit = usd_gained - trade_amount_usd - buy_fee_usd - sell_fee_usd - tax

    print(f"\n🧮 {from_exchange} → {to_exchange}")
    print(f"Buy @ ${buy_price:.2f}, Sell @ ${sell_price:.2f}")
    print(f"BTC Bought: {btc_bought:.6f}, After Fee: {btc_to_sell:.6f}")
    print(f"USD Gained: ${usd_gained:.2f}")
    print(f"Fees: Buy=${buy_fee_usd:.2f}, Sell=${sell_fee_usd:.2f}, Tax=${tax:.2f}")
    print(f"💰 Profit: ${profit:.2f}")
    return profit

def check_arbitrage_opportunity(usdt_amount):
    kucoin_bid, kucoin_ask = get_kucoin_price()
    coinbase_bid, coinbase_ask = get_coinbase_price()
    result = {}

    print(f"\n🔍 Prices:")
    print(f"KuCoin   - Bid: {kucoin_bid}, Ask: {kucoin_ask}")
    print(f"Coinbase - Bid: {coinbase_bid}, Ask: {coinbase_ask}")

    # Arbitrage: KuCoin → Coinbase
    if kucoin_ask and coinbase_bid and kucoin_ask < coinbase_bid:
        result['kucoin_to_coinbase'] = calculate_arbitrage_profit(
            buy_price=kucoin_ask,
            sell_price=coinbase_bid,
            buy_fee=kucoin_fee,
            sell_fee=coinbase_fee,
            trade_amount_usd=usdt_amount,
            from_exchange="KuCoin",
            to_exchange="Coinbase"
        )

    # Arbitrage: Coinbase → KuCoin
    if coinbase_ask and kucoin_bid and coinbase_ask < kucoin_bid:
        result['coinbase_to_kucoin'] = calculate_arbitrage_profit(
            buy_price=coinbase_ask,
            sell_price=kucoin_bid,
            buy_fee=coinbase_fee,
            sell_fee=kucoin_fee,
            trade_amount_usd=usdt_amount,
            from_exchange="Coinbase",
            to_exchange="KuCoin"
        )

    return result

def execute_arbitrage_kucoin_coinbase(usdt_amount=1000):
    result = check_arbitrage_opportunity(usdt_amount)
    response = {
        "status": "No arbitrage opportunity",
        "details": result
    }

    if "kucoin_to_coinbase" in result and result["kucoin_to_coinbase"] > 0:
        print("\n🚀 Executing Kucoin → Coinbase arbitrage")

        btc_bought = buy_order_on_kucoin(usdt_amount)["amount"]
        print(f"✅ Bought {btc_bought} BTC on Kucoin")

        btc_address = get_coinbase_btc_address()
        print(f"📦 Withdrawing {btc_bought} BTC to Coinbase address: {btc_address}")
        withdraw_btc_to_address_coinbase(btc_bought, btc_address)

        time.sleep(30)

        sell_order_on_coinbase(btc_bought)
        print(f"📉 Sold {btc_bought} BTC on Coinbase")

        response = {
            "status": "Executed Kucoin → Coinbase arbitrage",
            "btc_bought": btc_bought,
            "withdraw_address": btc_address,
            "profit_estimate": result["kucoin_to_coinbase"]
        }

    elif "coinbase_to_kucoin" in result and result["coinbase_to_kucoin"] > 0:
        print("\n🚀 Executing Coinbase → Kucoin arbitrage")

        btc_bought = buy_order_on_coinbase(usdt_amount)["amount"]
        print(f"✅ Bought {btc_bought} BTC on Coinbase")

        btc_address = get_kucoin_btc_address()
        print(f"📦 Withdrawing {btc_bought} BTC to Kucoin address: {btc_address}")
        withdraw_btc_to_address_kucoin(btc_bought, btc_address)

        time.sleep(30)

        sell_order_on_kucoin(btc_bought)
        print(f"📉 Sold {btc_bought} BTC on Kucoin")

        response = {
            "status": "Executed Coinbase → Kucoin arbitrage",
            "btc_bought": btc_bought,
            "withdraw_address": btc_address,
            "profit_estimate": result["coinbase_to_kucoin"]
        }

    else:
        print("❌ No profitable arbitrage opportunity to execute.")

    final_response = {
        "arbitrage_check": {
            "kucoin_to_coinbase_profit": result.get("kucoin_to_coinbase", 0),
            "coinbase_to_kucoin_profit": result.get("coinbase_to_kucoin", 0)
        },
        "arbitrage_action": response
    }

    return final_response


# while True:
#     try:
#         result = execute_arbitrage_kucoin_coinbase(usdt_amount=1000)
#         print(result)
#         print("-" * 50)
#         time.sleep(10)
#     except Exception as e:
#         print(f"Error: {e}")
#         time.sleep(10)
