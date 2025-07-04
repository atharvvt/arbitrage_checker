import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
bitget_fee = 0.0005         # 0.05%
cryptocom_fee = 0.00075     # 0.075%
network_fee = 0.0001        # BTC network fee
tax_rate = 0.0              # Change if needed
trade_amount_usd = 50000
slippage_percentage = 0.001  # 0.1%

# Initialize Bitget
bitget = ccxt.bitget({
    'apiKey': os.getenv('bitget_API_KEY'),
    'secret': os.getenv('bitget_SECRET'),
    'enableRateLimit': True
})

# Initialize Crypto.com
cryptocom = ccxt.cryptocom({
    'apiKey': os.getenv('cryptocom_API_KEY'),
    'secret': os.getenv('cryptocom_SECRET'),
    'enableRateLimit': True
})


def get_bitget_price(symbol="SOL/USDT"):
    try:
        order_book = bitget.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Bitget error: {e}")
        return None, None


def get_cryptocom_price(symbol="SOL/USDT"):
    try:
        order_book = cryptocom.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Crypto.com error: {e}")
        return None, None


def apply_slippage(price, slippage_pct):
    return price * (1 + random.uniform(-slippage_pct, slippage_pct))


def simulate_arbitrage(buy_price, sell_price, buy_fee, sell_fee, trade_amount_usd, from_exchange, to_exchange):
    symbol = "SOL/USDT"
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
    print(f"{symbol} Bought: {btc_bought:.6f}, After Fee: {btc_to_sell:.6f}")
    print(f"USD Gained: ${usd_gained:.2f}")
    print(f"Fees: Buy=${buy_fee_usd:.2f}, Sell=${sell_fee_usd:.2f}, Tax=${tax:.2f}")
    print(f"💰 Profit: ${profit:.2f}")
    return profit


def check_arbitrage_opportunity():
    bitget_bid, bitget_ask = get_bitget_price()
    cryptocom_bid, cryptocom_ask = get_cryptocom_price()

    print(f"\n🔍 Prices:")
    print(f"Bitget        - Bid: {bitget_bid}, Ask: {bitget_ask}")
    print(f"Crypto.com    - Bid: {cryptocom_bid}, Ask: {cryptocom_ask}")

    if bitget_ask and cryptocom_bid and bitget_ask < cryptocom_bid:
        simulate_arbitrage(
            buy_price=bitget_ask,
            sell_price=cryptocom_bid,
            buy_fee=bitget_fee,
            sell_fee=cryptocom_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Bitget",
            to_exchange="Crypto.com"
        )

    if cryptocom_ask and bitget_bid and cryptocom_ask < bitget_bid:
        simulate_arbitrage(
            buy_price=cryptocom_ask,
            sell_price=bitget_bid,
            buy_fee=cryptocom_fee,
            sell_fee=bitget_fee,
            trade_amount_usd=trade_amount_usd,
            from_exchange="Crypto.com",
            to_exchange="Bitget"
        )


# Main loop
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
