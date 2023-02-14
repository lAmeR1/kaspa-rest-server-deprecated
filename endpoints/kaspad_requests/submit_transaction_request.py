# encoding: utf-8

from typing import List

from pydantic import BaseModel

from server import app


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
    verboseData: TxOutputVerboseData


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
    lockTime: int
    subnetworkId: str
    gas: int
    payload: str
    verboseData: TxVerboseData


class SubmitTransactionRequest(BaseModel):
    transaction: TxModel
    allowOrphan: bool


class SubmitTransactionResponse(BaseModel):
    transactionId: str
    error: str | None


@app.post("/kaspad/submitTransactionRequest",
          response_model=SubmitTransactionResponse,
          tags=["Kaspad direct actions"],
          response_model_exclude_unset=True)
async def submit_a_new_transaction(body: SubmitTransactionRequest):
    """
    Forwards the body to directly to kaspad with the command submitTransactionRequest
    """
    pass
