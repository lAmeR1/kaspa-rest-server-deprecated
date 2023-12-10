# encoding: utf-8
import os
from pydantic import BaseModel
from starlette.responses import PlainTextResponse

from helper import get_kas_price, get_kas_market_data
from server import app

DISABLE_PRICE = os.getenv('DISABLE_PRICE', 'false').lower() == 'true'

class PriceResponse(BaseModel):
    price: float = 0.025235


@app.get("/info/price", response_model=PriceResponse | str, tags=["Kaspa network info"])
async def get_price(stringOnly: bool = False):
    """
    Returns the current price for Kaspa in USD.
    """
    price = await get_kas_price() if not DISABLE_PRICE else 0
    if stringOnly:
        return PlainTextResponse(content=str(price))

    return {"price": price}


@app.get("/info/market-data",
         tags=["Kaspa network info"],
         include_in_schema=False)
async def get_market_data():
    """
    Returns market data for kaspa.
    """
    return await get_kas_market_data() if not DISABLE_PRICE else {}
