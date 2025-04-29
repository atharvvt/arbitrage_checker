import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants for fees and tax
coinbase_fee = 0.001  # 0.1%
coinex_fee = 0.0005   # 0.05%
network_fee = 0.0001  # BTC withdrawal fee
tax_rate = 0.0        # Set tax if applicable
trade_amount_usd = 50000  # Amount in USD to simulate arbitrage on
slippage_percentage = 0.001  # 0.1%

# Initialize Coinbase Pro (Coinbase API)
coinbase = ccxt.coinbase({
    'apiKey': os.getenv('coinbase_API_KEY'),
    'secret': os.getenv('coinbase_SECRET'),
    'password': os.getenv('coinbase_PASSPHRASE'),
    'enableRateLimit': True
})

# Initialize Coinex (using CCXT)
coinex = ccxt.coinex({
    'apiKey': os.getenv('coinex_API_KEY'),
    'secret': os.getenv('coinex_SECRET'),
    'enableRateLimit': True
})

def get_coinbase_price(symbol="BTC-USD"):
    try:
        order_book = coinbase.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Coinbase error: {e}")
        return None, None

def get_coinex_price(symbol="BTC/USDT"):
    try:
        order_book = coinex.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Coinex error: {e}")
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
    coinbase_bid, coinbase_ask = get_coinbase_price()
    coinex_bid, coinex_ask = get_coinex_price()

    print(f"\n🔍 Prices:")
    print(f"Coinbase - Bid: {coinbase_bid}, Ask: {coinbase_ask}")
    print(f"Coinex   - Bid: {coinex_bid}, Ask: {coinex_ask}")

    # Arbitrage: Coinbase → Coinex
    if coinbase_ask and coinex_bid and coinbase_ask < coinex_bid:
        simulate_arbitrage(
            buy_price=coinbase_ask,
            sell_price=coinex_bid,
            buy_fee=coinbase_fee,
            sell_fee=coinex_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Coinbase",
            to_exchange="Coinex"
        )

    # Arbitrage: Coinex → Coinbase
    if coinex_ask and coinbase_bid and coinex_ask < coinbase_bid:
        simulate_arbitrage(
            buy_price=coinex_ask,
            sell_price=coinbase_bid,
            buy_fee=coinex_fee,
            sell_fee=coinbase_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Coinex",
            to_exchange="Coinbase"
        )

# Main loop
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
