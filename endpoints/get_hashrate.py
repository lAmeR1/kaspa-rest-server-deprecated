# encoding: utf-8

from pydantic import BaseModel

from server import app, kaspad_client


class HashrateResponse(BaseModel):
    hashrate: float = 12000132


@app.get("/info/hashrate", response_model=HashrateResponse | str, tags=["Kaspa network info"])
async def get_hashrate(stringOnly: bool = False):
    """
    Returns the current hashrate for Kaspa network in TH/s.
    """

    resp = await kaspad_client.request("getBlockDagInfoRequest")
    hashrate = resp["getBlockDagInfoResponse"]["difficulty"] * 2
    hashrate_in_th = hashrate / 1_000_000_000_000

    if not stringOnly:
        return {
            "hashrate": hashrate_in_th
        }

    else:
        return f"{hashrate_in_th:.01f}"
