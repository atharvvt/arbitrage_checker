import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants for fees and tax
bybit_fee = 0.00075  # 0.075%
indir_fee = 0.001  # 0.1%
network_fee = 0.0001  # BTC withdrawal fee
tax_rate = 0.0  # Set tax if applicable
trade_amount_usd = 50000  # Amount in USD to simulate arbitrage on
slippage_percentage = 0.001  # 0.1%

# Initialize Bybit
bybit = ccxt.bybit({
    'apiKey': os.getenv('bybit_API_KEY'),
    'secret': os.getenv('bybit_SECRET'),
    'enableRateLimit': True
})

# Initialize Independent Reserve (indir)
indir = ccxt.independentreserve({
    'apiKey': os.getenv('indir_API_KEY'),
    'secret': os.getenv('indir_SECRET'),
    'enableRateLimit': True
})

def get_bybit_price(symbol="BTC/USDT"):
    try:
        order_book = bybit.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Bybit error: {e}")
        return None, None

def get_indir_price(symbol="BTC/USD"):
    try:
        order_book = indir.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Independent Reserve error: {e}")
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
    bybit_bid, bybit_ask = get_bybit_price()
    indir_bid, indir_ask = get_indir_price()

    print(f"\n🔍 Prices:")
    print(f"Bybit             - Bid: {bybit_bid}, Ask: {bybit_ask}")
    print(f"Independent Reserve - Bid: {indir_bid}, Ask: {indir_ask}")

    # Arbitrage: Bybit → Independent Reserve
    if bybit_ask and indir_bid and bybit_ask < indir_bid:
        simulate_arbitrage(
            buy_price=bybit_ask,
            sell_price=indir_bid,
            buy_fee=bybit_fee,
            sell_fee=indir_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Bybit",
            to_exchange="Independent Reserve"
        )

    # Arbitrage: Independent Reserve → Bybit
    if indir_ask and bybit_bid and indir_ask < bybit_bid:
        simulate_arbitrage(
            buy_price=indir_ask,
            sell_price=bybit_bid,
            buy_fee=indir_fee,
            sell_fee=bybit_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Independent Reserve",
            to_exchange="Bybit"
        )

# Main loop
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
