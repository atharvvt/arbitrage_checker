import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load API keys
load_dotenv()

# Constants
kucoin_fee = 0.001       # 0.1%
htx_fee = 0.001          # 0.1%
network_fee = 0.0001     # BTC network fee
tax_rate = 0.0
trade_amount_usd = 50000
slippage_percentage = 0.001

# Initialize KuCoin
kucoin = ccxt.kucoin({
    'apiKey': os.getenv('kucoin_API_KEY'),
    'secret': os.getenv('kucoin_SECRET'),
    'password': os.getenv('kucoin_PASSWORD'),
    'enableRateLimit': True
})

# Initialize HTX (Huobi)
htx = ccxt.huobi({
    'apiKey': os.getenv('htx_API_KEY'),
    'secret': os.getenv('htx_SECRET'),
    'enableRateLimit': True
})


def get_kucoin_price(symbol="BTC/USDT"):
    try:
        order_book = kucoin.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ KuCoin error: {e}")
        return None, None


def get_htx_price(symbol="BTC/USDT"):
    try:
        order_book = htx.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ HTX error: {e}")
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
    kucoin_bid, kucoin_ask = get_kucoin_price()
    htx_bid, htx_ask = get_htx_price()

    print(f"\n🔍 Prices:")
    print(f"KuCoin      - Bid: {kucoin_bid}, Ask: {kucoin_ask}")
    print(f"HTX (Huobi) - Bid: {htx_bid}, Ask: {htx_ask}")

    if kucoin_ask and htx_bid and kucoin_ask < htx_bid:
        simulate_arbitrage(
            buy_price=kucoin_ask,
            sell_price=htx_bid,
            buy_fee=kucoin_fee,
            sell_fee=htx_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="KuCoin",
            to_exchange="HTX"
        )

    if htx_ask and kucoin_bid and htx_ask < kucoin_bid:
        simulate_arbitrage(
            buy_price=htx_ask,
            sell_price=kucoin_bid,
            buy_fee=htx_fee,
            sell_fee=kucoin_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="HTX",
            to_exchange="KuCoin"
        )


# Main loop
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
