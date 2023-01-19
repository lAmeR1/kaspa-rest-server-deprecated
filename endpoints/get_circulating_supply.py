# encoding: utf-8

from pydantic import BaseModel

from server import app, kaspad_client, limiter
from fastapi.responses import PlainTextResponse
from fastapi import Request


class CoinSupplyResponse(BaseModel):
    circulatingSupply: str = "1000900697580640180"
    maxSupply: str = "2900000000000000000"


@app.get("/info/coinsupply", response_model=CoinSupplyResponse, tags=["Kaspa network info"])
@limiter.limit("2/second")
async def get_coinsupply(request: Request):
    """
    Get $KAS coin supply information
    """
    resp = await kaspad_client.request("getCoinSupplyRequest")
    return {
        "circulatingSupply": resp["getCoinSupplyResponse"]["circulatingSompi"],
        "maxSupply": resp["getCoinSupplyResponse"]["maxSompi"]
    }

@app.get("/info/coinsupply/circulating", tags=["Kaspa network info"],
         response_class=PlainTextResponse)
@limiter.limit("2/second")
async def get_circulating_coins(request: Request, in_billion : bool = False):
    """
    Get circulating amount of $KAS token as numerical value
    """
    resp = await kaspad_client.request("getCoinSupplyRequest")
    coins = str(float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 100000000)
    if in_billion:
        return str(round(float(coins) / 1000000000, 2))
    else:
        return coins