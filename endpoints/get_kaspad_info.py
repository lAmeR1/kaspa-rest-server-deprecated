# encoding: utf-8
import hashlib

from pydantic import BaseModel

from server import app, kaspad_client


class KaspadInfoResponse(BaseModel):
    mempoolSize: str = "1"
    serverVersion: str = "0.12.2"
    isUtxoIndexed: bool = True
    isSynced: bool = True
    p2pIdHashed : str = "36a17cd8644eef34fc7fe4719655e06dbdf117008900c46975e66c35acd09b01"


@app.get("/info/kaspad", response_model=KaspadInfoResponse, tags=["Kaspa network info"])
async def get_kaspad_info():
    """
    Get some information for kaspad instance, which is currently connected.
    """
    resp = await kaspad_client.request("getInfoRequest")
    p2p_id = resp["getInfoResponse"].pop("p2pId")
    resp["getInfoResponse"]["p2pIdHashed"] = hashlib.sha256(p2p_id.encode()).hexdigest()
    return resp["getInfoResponse"]
