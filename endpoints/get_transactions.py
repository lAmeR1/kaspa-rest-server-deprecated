# encoding: utf-8
from typing import List

from fastapi import Path, HTTPException
from pydantic import BaseModel, parse_obj_as
from sqlalchemy.future import select

from dbsession import async_session
from endpoints import filter_fields
from models.Block import Block
from models.Transaction import Transaction, TransactionOutput, TransactionInput
from server import app


class TxInput(BaseModel):
    id: int
    transaction_id: str
    index: int
    previous_outpoint_hash: str
    previous_outpoint_index: str
    signature_script: str
    sig_op_count: str

    class Config:
        orm_mode = True


class TxOutput(BaseModel):
    id: int
    transaction_id: str
    index: int
    amount: int
    script_public_key: str
    script_public_key_address: str
    script_public_key_type: str
    accepting_block_hash: str | None

    class Config:
        orm_mode = True


class TxModel(BaseModel):
    subnetwork_id: str | None
    transaction_id: str | None
    hash: str | None
    mass: str | None
    block_hash: List[str] | None
    block_time: int | None
    is_accepted: bool | None
    accepting_block_hash: str | None
    accepting_block_blue_score: int | None
    inputs: List[TxInput] | None
    outputs: List[TxOutput] | None

    class Config:
        orm_mode = True


class TxSearch(BaseModel):
    transactionIds: List[str]


@app.get("/transactions/{transactionId}",
         response_model=TxModel,
         tags=["Kaspa transactions"],
         response_model_exclude_unset=True)
async def get_transaction(transactionId: str = Path(regex="[a-f0-9]{64}"),
                          inputs: bool = True,
                          outputs: bool = True):
    """
    Get block information for a given block id
    """
    async with async_session() as s:
        tx = await s.execute(select(Transaction, Block.blue_score) \
                             .join(Block, Transaction.accepting_block_hash == Block.hash, isouter=True) \
                             .filter(Transaction.transaction_id == transactionId))

        tx = tx.first()

        tx_outputs = None
        tx_inputs = None

        if outputs:
            tx_outputs = await s.execute(select(TransactionOutput) \
                                         .filter(TransactionOutput.transaction_id == transactionId))

            tx_outputs = tx_outputs.scalars().all()

        if inputs:
            tx_inputs = await s.execute(select(TransactionInput) \
                                        .filter(TransactionInput.transaction_id == transactionId))
            tx_inputs = tx_inputs.scalars().all()

    if tx:
        return {
            "subnetwork_id": tx.Transaction.subnetwork_id,
            "transaction_id": tx.Transaction.transaction_id,
            "hash": tx.Transaction.hash,
            "mass": tx.Transaction.mass,
            "block_hash": tx.Transaction.block_hash,
            "block_time": tx.Transaction.block_time,
            "is_accepted": tx.Transaction.is_accepted,
            "accepting_block_hash": tx.Transaction.accepting_block_hash,
            "accepting_block_blue_score": tx.blue_score,
            "outputs": parse_obj_as(List[TxOutput], tx_outputs) if tx_outputs else None,
            "inputs": parse_obj_as(List[TxInput], tx_inputs) if tx_inputs else None
        }
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")


@app.post("/transactions/search",
          response_model=List[TxModel],
          tags=["Kaspa transactions"],
          response_model_exclude_unset=True)
async def search_for_transactions(txSearch: TxSearch,
                                  fields: str = ""):
    """
    Get block information for a given block id
    """
    fields = fields.split(",") if fields else []

    async with async_session() as s:
        tx_list = await s.execute(select(Transaction, Block.blue_score) \
                                  .join(Block, Transaction.accepting_block_hash == Block.hash) \
                                  .filter(Transaction.transaction_id.in_(txSearch.transactionIds)))

        tx_list = tx_list.all()

        if not fields or "inputs" in fields:
            tx_inputs = await s.execute(select(TransactionInput) \
                                        .filter(TransactionInput.transaction_id.in_(txSearch.transactionIds)))
            tx_inputs = tx_inputs.scalars().all()
        else:
            tx_inputs = None

        if not fields or "outputs" in fields:
            tx_outputs = await s.execute(select(TransactionOutput) \
                                         .filter(TransactionOutput.transaction_id.in_(txSearch.transactionIds)))
            tx_outputs = tx_outputs.scalars().all()
        else:
            tx_outputs = None



    return (filter_fields({
        "subnetwork_id": tx.Transaction.subnetwork_id,
        "transaction_id": tx.Transaction.transaction_id,
        "hash": tx.Transaction.hash,
        "mass": tx.Transaction.mass,
        "block_hash": tx.Transaction.block_hash,
        "block_time": tx.Transaction.block_time,
        "is_accepted": tx.Transaction.is_accepted,
        "accepting_block_hash": tx.Transaction.accepting_block_hash,
        "accepting_block_blue_score": tx.blue_score,
        "outputs": parse_obj_as(List[TxOutput],
                                [x for x in tx_outputs if x.transaction_id == tx.Transaction.transaction_id])
        if tx_outputs else None,  # parse only if needed
        "inputs": parse_obj_as(List[TxInput],
                               [x for x in tx_inputs if x.transaction_id == tx.Transaction.transaction_id])
        if tx_inputs else None  # parse only if needed
    }, fields) for tx in tx_list)
