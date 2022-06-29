# encoding: utf-8

from pydantic import BaseModel

from server import app, kaspad_client


class CoinSupplyResponse(BaseModel):
    circulatingSupply: str = "1000900697580640180"
    maxSupply: str = "2900000000000000000"


@app.get("/info/coinsupply", response_model=CoinSupplyResponse, tags=["Kaspa network info"])
async def get_coinsupply():
    """
    Get $KAS coin supply information
    """
    resp = kaspad_client.request("getCoinSupplyRequest")
    return {
        "circulatingSupply": resp["getCoinSupplyResponse"]["circulatingSompi"],
        "maxSupply": resp["getCoinSupplyResponse"]["maxSompi"]
    }
