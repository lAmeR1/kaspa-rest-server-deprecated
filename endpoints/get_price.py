# encoding: utf-8

from pydantic import BaseModel
from starlette.responses import PlainTextResponse

from helper import get_kas_price, get_kas_market_data
from server import app


class PriceResponse(BaseModel):
    price: float = 0.025235


@app.get("/info/price", response_model=PriceResponse | str, tags=["Kaspa network info"])
async def get_price(stringOnly: bool = False):
    """
    Returns the current price for Kaspa in USD.
    """
    if stringOnly:
        return PlainTextResponse(content=str(await get_kas_price()))

    return {"price": await get_kas_price()}


@app.get("/info/market-data",
         tags=["Kaspa network info"],
         include_in_schema=False)
async def get_market_data():
    """
    Returns market data for kaspa.
    """
    return await get_kas_market_data()
