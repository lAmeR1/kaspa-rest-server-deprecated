# encoding: utf-8

from enum import Enum
from typing import List

from fastapi import Path, HTTPException, Query
from pydantic import BaseModel, parse_obj_as
from sqlalchemy import Integer
from sqlalchemy.future import select

from dbsession import async_session
from endpoints import filter_fields, sql_db_only
from models.Block import Block
from models.Transaction import Transaction, TransactionOutput, TransactionInput
from server import app

DESC_RESOLVE_PARAM = "Use this parameter if you want to fetch the TransactionInput previous outpoint details." \
                     " Light fetches only the address and amount. Full fetches the whole TransactionOutput and " \
                     "adds it into each TxInput."


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


class TxInput(BaseModel):
    id: int
    transaction_id: str
    index: int
    previous_outpoint_hash: str
    previous_outpoint_index: str
    previous_outpoint_resolved: TxOutput | None
    previous_outpoint_address: str | None
    previous_outpoint_amount: int | None
    signature_script: str
    sig_op_count: str

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


class PreviousOutpointLookupMode(str, Enum):
    no = "no"
    light = "light"
    full = "full"


@app.get("/transactions/{transactionId}",
         response_model=TxModel,
         tags=["Kaspa transactions"],
         response_model_exclude_unset=True)
@sql_db_only
async def get_transaction(transactionId: str = Path(regex="[a-f0-9]{64}"),
                          inputs: bool = True,
                          outputs: bool = True,
                          resolve_previous_outpoints: PreviousOutpointLookupMode =
                          Query(default=PreviousOutpointLookupMode.no,
                                description=DESC_RESOLVE_PARAM)):
    """
    Get block information for a given block id
    """
    async with async_session() as s:
        tx = await s.execute(select(Transaction, Block.blue_score) \
                             .join(Block, Transaction.accepting_block_hash == Block.hash, isouter=True)
                             .filter(Transaction.transaction_id == transactionId))

        tx = tx.first()

        tx_outputs = None
        tx_inputs = None

        if outputs:
            tx_outputs = await s.execute(select(TransactionOutput) \
                                         .filter(TransactionOutput.transaction_id == transactionId))

            tx_outputs = tx_outputs.scalars().all()

        if inputs:
            if resolve_previous_outpoints in ["light", "full"]:
                tx_inputs = await s.execute(select(TransactionInput, TransactionOutput)
                                            .outerjoin(TransactionOutput,
                                                       (TransactionOutput.transaction_id == TransactionInput.previous_outpoint_hash) &
                                                       (TransactionOutput.index == TransactionInput.previous_outpoint_index, Integer))
                                            .filter(TransactionInput.transaction_id == transactionId))

                tx_inputs = tx_inputs.all()

                if resolve_previous_outpoints in ["light", "full"]:
                    for tx_in, tx_prev_outputs in tx_inputs:
                        # it is possible, that the old tx is not in database. Leave fields empty
                        if not tx_prev_outputs:
                            tx_in.previous_outpoint_amount = None
                            tx_in.previous_outpoint_address = None
                            if resolve_previous_outpoints == "full":
                                tx_in.previous_outpoint_resolved = None
                            continue

                        tx_in.previous_outpoint_amount = tx_prev_outputs.amount
                        tx_in.previous_outpoint_address = tx_prev_outputs.script_public_key_address
                        if resolve_previous_outpoints == "full":
                            tx_in.previous_outpoint_resolved = tx_prev_outputs

                # remove unneeded list
                tx_inputs = [x[0] for x in tx_inputs]

            else:
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
@sql_db_only
async def search_for_transactions(txSearch: TxSearch,
                                  fields: str = "",
                                  resolve_previous_outpoints: PreviousOutpointLookupMode =
                                  Query(default=PreviousOutpointLookupMode.no,
                                        description=DESC_RESOLVE_PARAM)):
    """
    Get block information for a given block id
    """
    if len(txSearch.transactionIds) > 1000:
        raise HTTPException(422, "Too many transaction ids")

    fields = fields.split(",") if fields else []

    async with async_session() as s:
        tx_list = await s.execute(select(Transaction, Block.blue_score)
                                  .join(Block, Transaction.accepting_block_hash == Block.hash, isouter=True)
                                  .filter(Transaction.transaction_id.in_(txSearch.transactionIds))
                                  .order_by(Transaction.block_time.desc()))

        tx_list = tx_list.all()

        if not fields or "inputs" in fields:
            # join TxOutputs if needed
            if resolve_previous_outpoints in ["light", "full"]:
                tx_inputs = await s.execute(select(TransactionInput, TransactionOutput)
                                            .outerjoin(TransactionOutput,
                                                       (TransactionOutput.transaction_id == TransactionInput.previous_outpoint_hash) &
                                                       (TransactionOutput.index == TransactionInput.previous_outpoint_index))
                                            .filter(TransactionInput.transaction_id.in_(txSearch.transactionIds)))

            # without joining previous_tx_outputs
            else:
                tx_inputs = await s.execute(select(TransactionInput)
                                            .filter(TransactionInput.transaction_id.in_(txSearch.transactionIds)))
            tx_inputs = tx_inputs.all()

            if resolve_previous_outpoints in ["light", "full"]:
                for tx_in, tx_prev_outputs in tx_inputs:

                    # it is possible, that the old tx is not in database. Leave fields empty
                    if not tx_prev_outputs:
                        tx_in.previous_outpoint_amount = None
                        tx_in.previous_outpoint_address = None
                        if resolve_previous_outpoints == "full":
                            tx_in.previous_outpoint_resolved = None
                        continue

                    tx_in.previous_outpoint_amount = tx_prev_outputs.amount
                    tx_in.previous_outpoint_address = tx_prev_outputs.script_public_key_address
                    if resolve_previous_outpoints == "full":
                        tx_in.previous_outpoint_resolved = tx_prev_outputs

            # remove unneeded list
            tx_inputs = [x[0] for x in tx_inputs]

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
