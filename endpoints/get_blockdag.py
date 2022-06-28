# encoding: utf-8
from typing import List

from pydantic import BaseModel

from server import app, kaspad_client


class BlockdagResponse(BaseModel):
    networkName: str = "kaspa-mainnet"
    blockCount: str = "260890"
    headerCount: str = "2131312"
    tipHashes: List[str] = ["78273854a739e3e379dfd34a262bbe922400d8e360e30e3f31228519a334350a"]
    difficulty: float = 3870677677777.2
    pastMedianTime: str = "1656455670700"
    virtualParentHashes: List[str] = ["78273854a739e3e379dfd34a262bbe922400d8e360e30e3f31228519a334350a"]
    pruningPointHash: str = "5d32a9403273a34b6551b84340a1459ddde2ae6ba59a47987a6374340ba41d5d",
    virtualDaaScore: str = "19989141"


@app.get("/info/blockdag", response_model=BlockdagResponse)
async def get_blockdag():
    """
    Retrieves some global kaspa BlockDAG information
    """
    resp = kaspad_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
