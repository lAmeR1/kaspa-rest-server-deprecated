# encoding: utf-8
from typing import List

from pydantic import BaseModel

from server import app, kaspad_client


class NetworkResponse(BaseModel):
    networkName: str = "kaspa-mainnet"
    blockCount: str = "261357"
    headerCount: str = "23138783"
    tipHashes: List[str] = [
        "efdbe104c6275cf881583fba77834c8528fd1ab059f6b4737c42564d0d9fedbc",
        "6affbe62baef0f1a562f166b9857844b03b51a8ec9b8417ceb308d53fdc239a2"
    ]
    difficulty: float = 3887079905014.09
    pastMedianTime: str = "1656456088196"
    virtualParentHashes: List[str] = [
        "6affbe62baef0f1a562f166b9857844b03b51a8ec9b8417ceb308d53fdc239a2",
        "efdbe104c6275cf881583fba77834c8528fd1ab059f6b4737c42564d0d9fedbc"
    ]
    pruningPointHash: str = "5d32a9403273a34b6551b84340a1459ddde2ae6ba59a47987a6374340ba41d5d"
    virtualDaaScore: str = "19989984"


@app.get("/info/network", response_model=NetworkResponse, tags=["Kaspa network info"])
async def get_network():
    """
    Get some global kaspa network information
    """
    resp = kaspad_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
