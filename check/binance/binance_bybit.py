import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants for fees and tax
bybit_fee = 0.0003  # 0.03%
binance_fee = 0.001  # 0.1%
network_fee = 0.0001  # BTC withdrawal fee
tax_rate = 0.0  # Set tax if applicable
trade_amount_usd = 50000  # Amount in USD to simulate arbitrage on
slippage_percentage = 0.001  # 0.1%

# Initialize exchanges
binance = ccxt.binance({
    'apiKey': os.getenv('binance_API_KEY'),
    'secret': os.getenv('binance_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

bybit = ccxt.bybit({'enableRateLimit': True})


def get_bybit_price(symbol="BTC/USDT"):
    ticker = bybit.fetch_ticker(symbol)
    return ticker['bid'], ticker['ask']


def get_binance_price(symbol="BTC/USDT"):
    try:
        order_book = binance.fetch_order_book(symbol)
        bid = order_book['bids'][0][0]
        ask = order_book['asks'][0][0]
        return bid, ask
    except Exception as e:
        print(f"⚠️ Binance error: {e}")
        return None, None


def apply_slippage(price, slippage_pct):
    return price * (1 + random.uniform(-slippage_pct, slippage_pct))


def simulate_arbitrage(buy_price, sell_price, buy_fee, sell_fee, trade_amount_usd, from_exchange, to_exchange):
    # Apply slippage
    buy_price = apply_slippage(buy_price, slippage_percentage)
    sell_price = apply_slippage(sell_price, slippage_percentage)

    # Calculate BTC bought
    btc_bought = trade_amount_usd / buy_price

    # Apply network fee (only for cross-exchange arbitrage)
    btc_to_sell = btc_bought - network_fee

    # USD received from selling BTC
    usd_gained = btc_to_sell * sell_price

    # Calculate fees
    buy_cost_fee = trade_amount_usd * buy_fee
    sell_revenue_fee = usd_gained * sell_fee

    # Tax (if any)
    tax = tax_rate * (usd_gained - trade_amount_usd)

    # Final profit
    profit = usd_gained - trade_amount_usd - buy_cost_fee - sell_revenue_fee - tax

    print(f"🧮 {from_exchange} → {to_exchange}")
    print(f"Buy @ ${buy_price:.2f}, Sell @ ${sell_price:.2f}")
    print(f"BTC Bought: {btc_bought:.6f}, After Network Fee: {btc_to_sell:.6f}")
    print(f"USD Gained: ${usd_gained:.2f}")
    print(f"Fees: Buy=${buy_cost_fee:.2f}, Sell=${sell_revenue_fee:.2f}, Tax=${tax:.2f}")
    print(f"💰 Profit: ${profit:.2f}\n")
    return profit


def check_arbitrage_opportunity():
    bybit_bid, bybit_ask = get_bybit_price()
    binance_bid, binance_ask = get_binance_price()

    print(f"\n🔍 Prices:")
    print(f"Bybit  - Bid: {bybit_bid}, Ask: {bybit_ask}")
    print(f"Binance - Bid: {binance_bid}, Ask: {binance_ask}")

    if bybit_ask and binance_bid and bybit_ask < binance_bid:
        simulate_arbitrage(
            buy_price=bybit_ask,
            sell_price=binance_bid,
            buy_fee=bybit_fee,
            sell_fee=binance_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Bybit",
            to_exchange="Binance"
        )

    if binance_ask and bybit_bid and binance_ask < bybit_bid:
        simulate_arbitrage(
            buy_price=binance_ask,
            sell_price=bybit_bid,
            buy_fee=binance_fee,
            sell_fee=bybit_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Binance",
            to_exchange="Bybit"
        )


# Run continuously
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
