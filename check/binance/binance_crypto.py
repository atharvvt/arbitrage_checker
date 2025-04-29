import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
binance_fee = 0.001       # 0.1%
cryptocom_fee = 0.001     # 0.1%
network_fee = 0.0001      # BTC withdrawal fee
tax_rate = 0.0
trade_amount_usd = 50000
slippage_percentage = 0.001  # 0.1%

# Initialize Binance
binance = ccxt.binance({
    'apiKey': os.getenv('binance_API_KEY'),
    'secret': os.getenv('binance_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

# Initialize Crypto.com
cryptocom = ccxt.cryptocom({
    'apiKey': os.getenv('cryptocom_API_KEY'),
    'secret': os.getenv('cryptocom_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})


def get_binance_price(symbol="BTC/USDT"):
    try:
        order_book = binance.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Binance error: {e}")
        return None, None


def get_cryptocom_price(symbol="BTC/USDT"):
    try:
        order_book = cryptocom.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Crypto.com error: {e}")
        return None, None


def apply_slippage(price, slippage_pct):
    return price * (1 + random.uniform(-slippage_pct, slippage_pct))


def simulate_arbitrage(buy_price, sell_price, buy_fee, sell_fee, trade_amount_usd, from_exchange, to_exchange):
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


def check_arbitrage_opportunity():
    binance_bid, binance_ask = get_binance_price()
    crypto_bid, crypto_ask = get_cryptocom_price()

    print(f"\n🔍 Prices:")
    print(f"Binance     - Bid: {binance_bid}, Ask: {binance_ask}")
    print(f"Crypto.com  - Bid: {crypto_bid}, Ask: {crypto_ask}")

    if binance_ask and crypto_bid and binance_ask < crypto_bid:
        simulate_arbitrage(
            buy_price=binance_ask,
            sell_price=crypto_bid,
            buy_fee=binance_fee,
            sell_fee=cryptocom_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Binance",
            to_exchange="Crypto.com"
        )

    if crypto_ask and binance_bid and crypto_ask < binance_bid:
        simulate_arbitrage(
            buy_price=crypto_ask,
            sell_price=binance_bid,
            buy_fee=cryptocom_fee,
            sell_fee=binance_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Crypto.com",
            to_exchange="Binance"
        )


# Main loop
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
