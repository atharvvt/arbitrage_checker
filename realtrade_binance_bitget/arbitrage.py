import os
import time
import ccxt
import random
from dotenv import load_dotenv
from .binance import buy_order_on_binance, get_binance_btc_address, sell_order_on_binance, withdraw_btc_to_address_binance
from .bybit import buy_order_on_bybit, get_bybit_btc_address, sell_order_on_bybit, withdraw_btc_to_address_bybit

# Load environment variables
load_dotenv()

# Constants for fees and tax
binance_fee = 0.0004   # 0.04% (Binance taker fee)
bybit_fee = 0.00075    # 0.075% (Bybit taker fee)
network_fee = 0.0001   # BTC withdrawal fee
tax_rate = 0.0         # Set tax if applicable
slippage_percentage = 0.001  # 0.1%

# Initialize exchanges
binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True
})
binance.set_sandbox_mode(True)

bybit = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_API_KEY'),
    'secret': os.getenv('BYBIT_API_SECRET'),
    'enableRateLimit': True
})

def get_binance_price(symbol="BTC/USDT"):
    try:
        order_book = binance.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Binance error: {e}")
        return None, None

def get_bybit_price(symbol="BTC/USDT"):
    try:
        order_book = bybit.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Bybit error: {e}")
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
    binance_bid, binance_ask = get_binance_price()
    bybit_bid, bybit_ask = get_bybit_price()
    result = {}

    print(f"\n🔍 Prices:")
    print(f"Binance - Bid: {binance_bid}, Ask: {binance_ask}")
    print(f"Bybit   - Bid: {bybit_bid}, Ask: {bybit_ask}")

    # Arbitrage: Binance → Bybit
    if binance_ask and bybit_bid and binance_ask < bybit_bid:
        result['binance_to_bybit'] = calculate_arbitrage_profit(
            buy_price=binance_ask,
            sell_price=bybit_bid,
            buy_fee=binance_fee,
            sell_fee=bybit_fee,
            trade_amount_usd=usdt_amount,
            from_exchange="Binance",
            to_exchange="Bybit"
        )

    # Arbitrage: Bybit → Binance
    if bybit_ask and binance_bid and bybit_ask < binance_bid:
        result['bybit_to_binance'] = calculate_arbitrage_profit(
            buy_price=bybit_ask,
            sell_price=binance_bid,
            buy_fee=bybit_fee,
            sell_fee=binance_fee,
            trade_amount_usd=usdt_amount,
            from_exchange="Bybit",
            to_exchange="Binance"
        )

    return result

def execute_arbitrage_binance_bybit(usdt_amount=1000):
    result = check_arbitrage_opportunity(usdt_amount)
    response = {
        "status": "No arbitrage opportunity",
        "details": result
    }

    if "binance_to_bybit" in result and result["binance_to_bybit"] > 0:
        print("\n🚀 Executing Binance → Bybit arbitrage")

        btc_bought = buy_order_on_binance(usdt_amount)["amount"]
        print(f"✅ Bought {btc_bought} BTC on Binance")

        btc_address = get_bybit_btc_address()
        print(f"📦 Withdrawing {btc_bought} BTC to Bybit address: {btc_address}")
        withdraw_btc_to_address_bybit(btc_bought, btc_address)

        time.sleep(30)

        sell_order_on_bybit(btc_bought)
        print(f"📉 Sold {btc_bought} BTC on Bybit")

        response = {
            "status": "Executed Binance → Bybit arbitrage",
            "btc_bought": btc_bought,
            "withdraw_address": btc_address,
            "profit_estimate": result["binance_to_bybit"]
        }

    elif "bybit_to_binance" in result and result["bybit_to_binance"] > 0:
        print("\n🚀 Executing Bybit → Binance arbitrage")

        btc_bought = buy_order_on_bybit(usdt_amount)["amount"]
        print(f"✅ Bought {btc_bought} BTC on Bybit")

        btc_address = get_binance_btc_address()
        print(f"📦 Withdrawing {btc_bought} BTC to Binance address: {btc_address}")
        withdraw_btc_to_address_binance(btc_bought, btc_address)

        time.sleep(30)

        sell_order_on_binance(btc_bought)
        print(f"📉 Sold {btc_bought} BTC on Binance")

        response = {
            "status": "Executed Bybit → Binance arbitrage",
            "btc_bought": btc_bought,
            "withdraw_address": btc_address,
            "profit_estimate": result["bybit_to_binance"]
        }

    else:
        print("❌ No profitable arbitrage opportunity to execute.")

    # Now build a final structured output
    final_response = {
        "arbitrage_check": {
            "binance_to_bybit_profit": result.get("binance_to_bybit", 0),
            "bybit_to_binance_profit": result.get("bybit_to_binance", 0)
        },
        "arbitrage_action": response
    }
    
    return final_response


# while True:
#     try:
#         result = execute_arbitrage_binance_bybit(usdt_amount=1000)
#         print(result)
#         print("-" * 50)
#         time.sleep(10)
#     except Exception as e:
#         print(f"Error: {e}")
#         time.sleep(10)
