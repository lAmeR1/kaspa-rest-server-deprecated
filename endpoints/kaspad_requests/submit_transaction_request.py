# encoding: utf-8
import time
from typing import List

from pydantic import BaseModel

from server import app, kaspad_client


class TxOutpoint(BaseModel):
    transactionId: str
    index: int


class TxInput(BaseModel):
    previousOutpoint: TxOutpoint
    signatureScript: str
    sequence: int
    sigOpCount: int


class TxScriptPublicKey(BaseModel):
    version: int
    scriptPublicKey: str


class TxOutputVerboseData(BaseModel):
    scriptPublicKeyType: str
    scriptPublicKeyAddress: str


class TxOutput(BaseModel):
    amount: int
    scriptPublicKey: TxScriptPublicKey
    # verboseData: TxOutputVerboseData | None


class TxVerboseData(BaseModel):
    transactionId: str
    hash: str
    mass: int
    blockHash: str
    blockTime: int


class TxModel(BaseModel):
    version: int
    inputs: List[TxInput]
    outputs: List[TxOutput]
    lockTime: int | None = 0
    subnetworkId: str | None


class SubmitTransactionRequest(BaseModel):
    transaction: TxModel
    allowOrphan: bool = True


class SubmitTransactionResponse(BaseModel):
    transactionId: str | None
    error: str | None


@app.post("/kaspad/submitTransactionRequest",
          response_model=SubmitTransactionResponse,
          tags=["Kaspad direct actions"],
          response_model_exclude_unset=True)
async def submit_a_new_transaction(body: SubmitTransactionRequest):
    """
    Forwards the body directly to kaspad with the command submitTransactionRequest
    """
    tx_resp = await kaspad_client.request("submitTransactionRequest",
                                          params=body.dict())

    tx_resp = tx_resp["submitTransactionResponse"]
    if "error" in tx_resp:
        return {
            "error": tx_resp["error"].get("message", "")
        }

    return {
        "transactionId": tx_resp["transactionId"]
    }


"""
{
  "transaction": {
    "version": 0,
    "inputs": [
      {
        "previousOutpoint": {
          "transactionId": "fa99f98b8e9b0758100d181eccb35a4c053b8265eccb5a89aadd794e087d9820",
          "index": 1
        },
        "signatureScript": "4187173244180496d67a94dc78f3d3651bc645139b636a9c79a4f1d36fdcc718e88e9880eeb0eb208d0c110f31a306556457bc37e1044aeb3fdd303bd1a8c1b84601",
        "sequence": 0,
        "sigOpCount": 1
      }
    ],
    "outputs": [
      {
        "amount": 100000,
        "scriptPublicKey": {
          "scriptPublicKey": "20167f5647a0e88ed3ac7834b5de4a5f0e56a438bcb6c97186a2c935303290ef6fac",
          "version": 0
        }
      },
      {
        "amount": 183448,
        "scriptPublicKey": {
          "scriptPublicKey": "2010352c822bf3c67637c84ea09ff90edc11fa509475ae1884cf5b971e53afd472ac",
          "version": 0
        }
      }
    ],
    "lockTime": 0,
    "subnetworkId": "0000000000000000000000000000000000000000"
  },
  "allowOrphan": true
}
"""
