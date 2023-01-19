# encoding: utf-8
import time

from pydantic import BaseModel
from sqlalchemy import select
from fastapi import Request

from dbsession import async_session
from models.Block import Block
from server import app, kaspad_client, limiter

MAXHASH_CACHE = (0, 0)


class BlockHeader(BaseModel):
    hash: str = "e6641454e16cff4f232b899564eeaa6e480b66069d87bee6a2b2476e63fcd887"
    timestamp: str = "1656450648874"
    difficulty: int = 1212312312
    daaScore: str = "19984482"
    blueScore: str = "18483232"


class HashrateResponse(BaseModel):
    hashrate: float = 12000132


class MaxHashrateResponse(BaseModel):
    hashrate: float = 12000132
    blockheader: BlockHeader


@app.get("/info/hashrate", response_model=HashrateResponse | str, tags=["Kaspa network info"])
@limiter.limit("2/second")
async def get_hashrate(request: Request, stringOnly: bool = False):
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


@app.get("/info/hashrate/max", response_model=MaxHashrateResponse, tags=["Kaspa network info"])
# TODO: Apply limiter here after setting up tests
#@limiter.limit("2/second")
async def get_max_hashrate(request: Request):
    """
    Returns the current hashrate for Kaspa network in TH/s.
    """
    global MAXHASH_CACHE

    if time.time() - MAXHASH_CACHE[0] < 60 * 5:
        return MAXHASH_CACHE[1]

    async with async_session() as s:
        tx = await s.execute(select(Block)
                             .order_by(Block.difficulty.desc()).limit(1))

        tx = tx.first()

    hashrate = tx[0].difficulty * 2
    hashrate_in_th = hashrate / 1_000_000_000_000

    response = {"hashrate": hashrate_in_th,
                "blockheader":
                    {
                        "hash": tx[0].hash,
                        "timestamp": tx[0].timestamp.isoformat(),
                        "difficulty": tx[0].difficulty,
                        "daaScore": tx[0].daa_score,
                        "blueScore": tx[0].blue_score
                    }
                }

    MAXHASH_CACHE = (time.time(), response)

    return response
