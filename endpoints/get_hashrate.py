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


def __normalize_hashrate(hashrate: int):
    if hashrate < 1_000:  #
        return f'{round(hashrate, 2)} H/s'  # Hash
    elif hashrate < 1_000_000:
        return f'{round(hashrate / 1_000, 2)} KH/s'  # Kilo
    elif hashrate < 1_000_000_000:
        return f'{round(hashrate / 1_000_000, 2)} MH/s'  # Mega
    elif hashrate < 1_000_000_000_000:
        return f'{round(hashrate / 1_000_000_000, 2)} GH/s'  # Giga
    elif hashrate < 1_000_000_000_000_000:
        return f'{round(hashrate / 1_000_000_000_000, 2)} TH/s'  # Tera
    elif hashrate < 1_000_000_000_000_000_000:
        return f'{round(hashrate / 1_000_000_000_000_000, 2)} PH/s'  # Peta
    elif hashrate < 1_000_000_000_000_000_000_000:
        return f'{round(hashrate / 1_000_000_000_000_000_000, 2)} EH/s'  # Exa
