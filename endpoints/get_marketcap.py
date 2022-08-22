# encoding: utf-8

import requests
from pydantic import BaseModel

from server import app, kaspad_client


class CoinSupplyResponse(BaseModel):
    marketcap: int = 12000132


@app.get("/info/marketcap", response_model=CoinSupplyResponse | str, tags=["Kaspa network info"])
async def get_marketcap(stringOnly: bool = False):
    """
    Get $KAS price and market cap. Price info is from coingecko.com
    """
    kas_price = _get_kas_price()
    resp = await kaspad_client.request("getCoinSupplyRequest")
    mcap = round(float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 100000000 * kas_price)

    if not stringOnly:
        return {
            "marketcap": mcap
        }
    else:
        if mcap < 1000000000:
            return f"{round(mcap / 1000000,1)}M"
        else:
            return f"{round(mcap / 1000000000,1)}B"


def _get_kas_price():
    resp = requests.get("https://api.coingecko.com/api/v3/simple/price",
                        params={"ids": "kaspa",
                                "vs_currencies": "usd"})
    if resp.status_code == 200:
        return resp.json()["kaspa"]["usd"]
