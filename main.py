from fastapi import FastAPI
import threading
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from realtrade_binance_bitget.arbitrage import execute_arbitrage_binance_bybit
from realtrade_bybit_bitget.arbitrage import execute_arbitrage_bybit_bitget
from realtrade_cryptocom_bitgate.arbitrage import execute_arbitrage_cryptocom_bitget
from realtrade_kucoin_coinbase.arbitrage import execute_arbitrage_kucoin_coinbase
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel

class StartParams(BaseModel):
    usdt_amount: float

app = FastAPI()
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arbitrage")

# State flags for each bot and result containers
running_flags = {
    "binance_bybit": False,
    "bybit_bitget": False,
    "cryptocom_bitget": False,
    "kucoin_coinbase": False,
}

arbitrage_results = {
    "binance_bybit": "",
    "bybit_bitget": "",
    "cryptocom_bitget": "",
    "kucoin_coinbase": ""
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Create a loop to run arbitrage in the background
def create_loop(exchange_pair, arbitrage_func, usdt_amount):
    while running_flags[exchange_pair]:
        try:
            result = arbitrage_func(usdt_amount=usdt_amount)

            if result is not None:
                arbitrage_results[exchange_pair] = json.dumps(result, indent=2)
            else:
                arbitrage_results[exchange_pair] = json.dumps({"error": "No data available"}, indent=2)

        except Exception as e:
            arbitrage_results[exchange_pair] = json.dumps({"error": str(e)}, indent=2)
            logger.error(f"Error in {exchange_pair}: {e}")

        time.sleep(5)



# Routes for Binance <-> Bybit
@app.post("/start/binance-bybit")
def start_binance_bybit(params: StartParams):
    if not running_flags["binance_bybit"]:
        running_flags["binance_bybit"] = True
        threading.Thread(target=create_loop, args=("binance_bybit", execute_arbitrage_binance_bybit, params.usdt_amount)).start()
        return {"status": "Binance ↔️ Bybit arbitrage started"}
    return {"status": "Already running"}

@app.post("/stop/binance-bybit")
def stop_binance_bybit():
    running_flags["binance_bybit"] = False
    return {"status": "Binance ↔️ Bybit arbitrage stopped"}

# Routes for Bybit <-> Bitget
@app.post("/start/bybit-bitget")
def start_bybit_bitget(params: StartParams):
    if not running_flags["bybit_bitget"]:
        running_flags["bybit_bitget"] = True
        threading.Thread(target=create_loop, args=("bybit_bitget", execute_arbitrage_bybit_bitget, params.usdt_amount)).start()
        return {"status": "Bybit ↔️ Bitget arbitrage started"}
    return {"status": "Already running"}

@app.post("/stop/bybit-bitget")
def stop_bybit_bitget():
    running_flags["bybit_bitget"] = False
    return {"status": "Bybit ↔️ Bitget arbitrage stopped"}

# Routes for Crypto.com <-> Bitget
@app.post("/start/cryptocom-bitget")
def start_cryptocom_bitget(params: StartParams):
    if not running_flags["cryptocom_bitget"]:
        running_flags["cryptocom_bitget"] = True
        threading.Thread(target=create_loop, args=("cryptocom_bitget", execute_arbitrage_cryptocom_bitget, params.usdt_amount)).start()
        return {"status": "Crypto.com ↔️ Bitget arbitrage started"}
    return {"status": "Already running"}

@app.post("/stop/cryptocom-bitget")
def stop_cryptocom_bitget():
    running_flags["cryptocom_bitget"] = False
    return {"status": "Crypto.com ↔️ Bitget arbitrage stopped"}

# Routes for KuCoin <-> Coinbase
@app.post("/start/kucoin-coinbase")
def start_kucoin_coinbase(params: StartParams):
    if not running_flags["kucoin_coinbase"]:
        running_flags["kucoin_coinbase"] = True
        threading.Thread(target=create_loop, args=("kucoin_coinbase", execute_arbitrage_kucoin_coinbase,params.usdt_amount)).start()
        return {"status": "KuCoin ↔️ Coinbase arbitrage started"}
    return {"status": "Already running"}

@app.post("/stop/kucoin-coinbase")
def stop_kucoin_coinbase():
    running_flags["kucoin_coinbase"] = False
    return {"status": "KuCoin ↔️ Coinbase arbitrage stopped"}

# Unified status endpoint
@app.get("/status")
def get_status():
    return running_flags


@app.get("/result/{exchange_pair}")
def get_arbitrage_result(exchange_pair: str):
    result = arbitrage_results.get(exchange_pair)
    
    if not result:
        return JSONResponse(content={"error": "Result not ready yet"}, status_code=202)
    
    try:
        return JSONResponse(content=json.loads(result))
    except Exception as e:
        return JSONResponse(content={"error": f"Stored result is invalid: {e}"}, status_code=500)

