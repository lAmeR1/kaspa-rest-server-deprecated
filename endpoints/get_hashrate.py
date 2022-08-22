# encoding: utf-8

from pydantic import BaseModel

from server import app


class HashrateResponse(BaseModel):
    hashrate: float = 12000132


@app.get("/info/hashrate", response_model=HashrateResponse | str, tags=["Kaspa network info"])
async def get_hashrate(stringOnly: bool = False):
    """
    DUMMY! Returns the current hashrate for Kaspa network in TH/s.
    """
    if not stringOnly:
        return {
            "hashrate": 60
        }

    else:
        return "60"
