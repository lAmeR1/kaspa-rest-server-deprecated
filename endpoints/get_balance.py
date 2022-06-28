# encoding: utf-8

from fastapi import Path
from pydantic import BaseModel
from server import app, kaspad_client


class BalanceResponse(BaseModel):
    address: str = "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00"
    balance: int = 38240000000

@app.get("/addresses/{kaspa_address}/balance", response_model=BalanceResponse)
async def get_balance_from_kaspa_address(
        kaspa_address: str = Path(
            description="Kaspa address as string e.g. kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex="^kaspa\:[a-z0-9]{61}$")):
    """
    Endpoint for checking the balance of a given kaspa address
    """
    resp = kaspad_client.request("getBalanceByAddressRequest",
                                 params={
                                     "address": kaspa_address
                                 })
    return {
        "address": kaspa_address,
        "balance": int(resp["getBalanceByAddressResponse"]["balance"])
    }