# encoding: utf-8

from typing import List

from fastapi import Path
from pydantic import BaseModel

from server import app, kaspad_client


class OutpointModel(BaseModel):
    transactionId: str = "ef62efbc2825d3ef9ec1cf9b80506876ac077b64b11a39c8ef5e028415444dc9"
    index: int = 1


class ScriptPublicKeyModel(BaseModel):
    scriptPublicKey: str = "20c5629ce85f6618cd3ed1ac1c99dc6d3064ed244013555c51385d9efab0d0072fac"


class UtxoModel(BaseModel):
    amount: str = "11501593788",
    scriptPublicKey: ScriptPublicKeyModel
    blockDaaScore: str = "18867232"


class UtxoResponse(BaseModel):
    address: str = "kaspa:qrzk988gtanp3nf76xkpexwud5cxfmfygqf42hz38pwea74s6qrj75jee85nj"
    outpoint: OutpointModel
    utxoEntry: UtxoModel


@app.get("/addresses/{kaspa_address}/utxos", response_model=List[UtxoResponse])
async def get_utxos_for_address(kaspa_address: str = Path(
    description="Kaspa address as string e.g. kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
    regex="^kaspa\:[a-z0-9]{61}$")):
    """
    This endpoint retrieves all open utxo for a given kaspa address
    """
    resp = kaspad_client.request("getUtxosByAddressesRequest",
                                 params={
                                     "addresses": [kaspa_address]
                                 })
    return (utxo for utxo in resp["getUtxosByAddressesResponse"]["entries"] if utxo["address"] == kaspa_address)
