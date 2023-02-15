# encoding: utf-8

from typing import List

from pydantic import BaseModel
from starlette.responses import JSONResponse

from server import app, kaspad_client


class SubmitTxOutpoint(BaseModel):
    transactionId: str
    index: int


class SubmitTxInput(BaseModel):
    previousOutpoint: SubmitTxOutpoint
    signatureScript: str
    sequence: int
    sigOpCount: int


class SubmitTxScriptPublicKey(BaseModel):
    version: int
    scriptPublicKey: str


class SubmitTxOutput(BaseModel):
    amount: int
    scriptPublicKey: SubmitTxScriptPublicKey
    # verboseData: TxOutputVerboseData | None


class SubmitTxModel(BaseModel):
    version: int
    inputs: List[SubmitTxInput]
    outputs: List[SubmitTxOutput]
    lockTime: int | None = 0
    subnetworkId: str | None


class SubmitTransactionRequest(BaseModel):
    transaction: SubmitTxModel
    allowOrphan: bool = True


class SubmitTransactionResponse(BaseModel):
    transactionId: str | None
    error: str | None


@app.post("/transactions",
          tags=["Kaspa transactions"],
          response_model_exclude_unset=True,
          responses={200: {"model": SubmitTransactionResponse},
                       400: {"model": SubmitTransactionResponse}})
async def submit_a_new_transaction(body: SubmitTransactionRequest):
    """
    Forwards the body directly to kaspad with the command submitTransactionRequest
    """
    tx_resp = await kaspad_client.request("submitTransactionRequest",
                                          params=body.dict())

    tx_resp = tx_resp["submitTransactionResponse"]

    # if error in response
    if "error" in tx_resp:
        return JSONResponse(status_code=400,
                            content={"error": tx_resp["error"].get("message", "")})

    # if transactionId is in response
    elif "transactionId" in tx_resp:
        return {
            "transactionId": tx_resp["transactionId"]
        }

    # something else went wrong
    else:
        return JSONResponse(status_code=400,
                            content={"error": str(tx_resp)})


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
  }
}
"""
