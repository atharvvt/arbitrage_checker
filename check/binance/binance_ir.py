import os
import time
import ccxt
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
binance_fee = 0.001     # 0.1%
ir_fee = 0.005          # 0.5%
network_fee = 0.0001    # BTC withdrawal fee
tax_rate = 0.0
trade_amount_usd = 50000
slippage_percentage = 0.001

# Initialize Binance
binance = ccxt.binance({
    'apiKey': os.getenv('binance_API_KEY'),
    'secret': os.getenv('binance_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

# Initialize Independent Reserve
independent_reserve = ccxt.independentreserve({
    'apiKey': os.getenv('ir_API_KEY'),
    'secret': os.getenv('ir_SECRET'),
    'enableRateLimit': True
})


def get_binance_price(symbol="SOL/USDT"):
    try:
        order_book = binance.fetch_order_book(symbol)
        return order_book['bids'][0][0], order_book['asks'][0][0]
    except Exception as e:
        print(f"⚠️ Binance error: {e}")
        return None, None


def get_ir_price(symbol="SOL/USD"):
    try:
        ticker = independent_reserve.fetch_ticker(symbol)
        return ticker['bid'], ticker['ask']
    except Exception as e:
        print(f"⚠️ Independent Reserve error: {e}")
        return None, None


def apply_slippage(price, slippage_pct):
    return price * (1 + random.uniform(-slippage_pct, slippage_pct))


def simulate_arbitrage(buy_price, sell_price, buy_fee, sell_fee, from_exchange, to_exchange):
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
    binance_bid, binance_ask = get_binance_price()
    ir_bid, ir_ask = get_ir_price()

    print(f"\n🔍 Prices:")
    print(f"Binance             - Bid: {binance_bid}, Ask: {binance_ask}")
    print(f"Independent Reserve - Bid: {ir_bid}, Ask: {ir_ask}")

    if binance_ask and ir_bid and binance_ask < ir_bid:
        simulate_arbitrage(
            buy_price=binance_ask,
            sell_price=ir_bid,
            buy_fee=binance_fee,
            sell_fee=ir_fee,
            from_exchange="Binance",
            to_exchange="Independent Reserve"
        )

    if ir_ask and binance_bid and ir_ask < binance_bid:
        simulate_arbitrage(
            buy_price=ir_ask,
            sell_price=binance_bid,
            buy_fee=ir_fee,
            sell_fee=binance_fee,
            from_exchange="Independent Reserve",
            to_exchange="Binance"
        )
        
    else:
        print("❌ No arbitrage opportunity found right now.")



# Main loop
while True:
    try:
        check_arbitrage_opportunity()
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(20)
