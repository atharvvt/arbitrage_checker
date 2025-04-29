import os
import time
import ccxt
import random
from dotenv import load_dotenv
from .bybit import buy_order_on_bybit, get_bybit_btc_address, get_bybit_price, sell_order_on_bybit, withdraw_btc_to_address_bybit
from .bitget import buy_order_on_bitget, get_bitget_btc_address, get_bitget_price, sell_order_on_bitget, withdraw_btc_to_address_bitget
# Load environment variables
load_dotenv()

# Constants for fees and tax
bybit_fee = 0.00075  # 0.075%
bitget_fee = 0.0005  # 0.05%
network_fee = 0.0001  # BTC withdrawal fee
tax_rate = 0.0        # Set tax if applicable
 # Amount in USD to simulate arbitrage on
slippage_percentage = 0.001  # 0.1%

# Initialize exchanges
bybit = ccxt.bybit({
    'apiKey': os.getenv('bybit_API_KEY'),
    'secret': os.getenv('bybit_SECRET'),
    'enableRateLimit': True
})

bitget = ccxt.bitget({
    'apiKey': os.getenv('bitget_API_KEY'),
    'secret': os.getenv('bitget_SECRET'),
    'enableRateLimit': True
})

def get_bybit_price(symbol="BTC/USDT"):
    try:
        order_book = bybit.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Bybit error: {e}")
        return None, None

def get_bitget_price(symbol="BTC/USDT"):
    try:
        order_book = bitget.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Bitget error: {e}")
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
    bybit_bid, bybit_ask = get_bybit_price()
    bitget_bid, bitget_ask = get_bitget_price()
    result = {}

    print(f"\n🔍 Prices:")
    print(f"Bybit   - Bid: {bybit_bid}, Ask: {bybit_ask}")
    print(f"Bitget  - Bid: {bitget_bid}, Ask: {bitget_ask}")

    # Arbitrage: Bybit → Bitget
    if bybit_ask and bitget_bid and bybit_ask < bitget_bid:
        result['bybit_to_bitget'] = calculate_arbitrage_profit(
            buy_price=bybit_ask,
            sell_price=bitget_bid,
            buy_fee=bybit_fee,
            sell_fee=bitget_fee,
            trade_amount_usd=usdt_amount,
            from_exchange="Bybit",
            to_exchange="Bitget"
        )

    # Arbitrage: Bitget → Bybit
    if bitget_ask and bybit_bid and bitget_ask < bybit_bid:
        result['bitget_to_bybit'] = calculate_arbitrage_profit(
            buy_price=bitget_ask,
            sell_price=bybit_bid,
            buy_fee=bitget_fee,
            sell_fee=bybit_fee,
            trade_amount_usd=usdt_amount,
            from_exchange="Bitget",
            to_exchange="Bybit"
        )

    return result


def execute_arbitrage_bybit_bitget(usdt_amount=1000):
    result = check_arbitrage_opportunity(usdt_amount)
    response = {
        "status": "No arbitrage opportunity",
        "details": result
    }

    if "bybit_to_bitget" in result and result["bybit_to_bitget"] > 0:
        print("\n🚀 Executing Bybit → Bitget arbitrage")

        btc_bought = buy_order_on_bybit(usdt_amount)["amount"]
        print(f"✅ Bought {btc_bought} BTC on Bybit")

        btc_address = get_bitget_btc_address()
        print(f"📦 Withdrawing {btc_bought} BTC to Bitget address: {btc_address}")
        withdraw_btc_to_address_bitget(btc_bought, btc_address)

        time.sleep(30)

        sell_order_on_bitget(btc_bought)
        print(f"📉 Sold {btc_bought} BTC on Bitget")

        response = {
            "status": "Executed Bybit → Bitget arbitrage",
            "btc_bought": btc_bought,
            "withdraw_address": btc_address,
            "profit_estimate": result["bybit_to_bitget"]
        }

    elif "bitget_to_bybit" in result and result["bitget_to_bybit"] > 0:
        print("\n🚀 Executing Bitget → Bybit arbitrage")

        btc_bought = buy_order_on_bitget(usdt_amount)["amount"]
        print(f"✅ Bought {btc_bought} BTC on Bitget")

        btc_address = get_bybit_btc_address()
        print(f"📦 Withdrawing {btc_bought} BTC to Bybit address: {btc_address}")
        withdraw_btc_to_address_bybit(btc_bought, btc_address)

        time.sleep(30)

        sell_order_on_bybit(btc_bought)
        print(f"📉 Sold {btc_bought} BTC on Bybit")

        response = {
            "status": "Executed Bitget → Bybit arbitrage",
            "btc_bought": btc_bought,
            "withdraw_address": btc_address,
            "profit_estimate": result["bitget_to_bybit"]
        }

    else:
        print("❌ No profitable arbitrage opportunity to execute.")

    final_response = {
        "arbitrage_check": {
            "bybit_to_bitget_profit": result.get("bybit_to_bitget", 0),
            "bitget_to_bybit_profit": result.get("bitget_to_bybit", 0)
        },
        "arbitrage_action": response
    }

    return final_response

# while True:
#     try:
#         result = execute_arbitrage_bybit_bitget(usdt_amount=1000)
#         print(result)
#         print("-" * 50)
#         time.sleep(10)
#     except Exception as e:
#         print(f"Error: {e}")
#         time.sleep(10)