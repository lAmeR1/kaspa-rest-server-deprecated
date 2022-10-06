# encoding: utf-8
from typing import List

from fastapi import Path
from pydantic import BaseModel
from sqlalchemy import text

from dbsession import session_maker
from server import app


class TransactionsReceivedAndSpent(BaseModel):
    tx_received: str
    tx_spent: str | None
    # received_amount: int = 38240000000


class TransactionForAddressResponse(BaseModel):
    transactions: List[TransactionsReceivedAndSpent]


@app.get("/addresses/{kaspaAddress}/transactions",
         response_model=TransactionForAddressResponse,
         response_model_exclude_unset=True,
         tags=["Kaspa addresses"],
         include_in_schema=False)
async def get_transactions_for_address(
        kaspaAddress: str = Path(
            description="Kaspa address as string e.g. "
                        "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex="^kaspa\:[a-z0-9]{61}$")):
    """
    Get all transactions for a given address from database
    """
    # SELECT transactions_outputs.transaction_id, transactions_inputs.transaction_id as inp_transaction FROM transactions_outputs
    #
    # LEFT JOIN transactions_inputs ON transactions_inputs.previous_outpoint_hash = transactions_outputs.transaction_id AND transactions_inputs.previous_outpoint_index::int = transactions_outputs.index
    #
    # WHERE "script_public_key_address" = 'kaspa:qp7d7rzrj34s2k3qlxmguuerfh2qmjafc399lj6606fc7s69l84h7mrj49hu6'
    #
    # ORDER by transactions_outputs.transaction_id
    with session_maker() as session:
        resp = session.execute(text(f"""
            SELECT transactions_outputs.transaction_id, transactions_outputs.index, transactions_inputs.transaction_id as inp_transaction, transactions.block_time FROM transactions_outputs
            LEFT JOIN transactions_inputs ON transactions_inputs.previous_outpoint_hash = transactions_outputs.transaction_id AND transactions_inputs.previous_outpoint_index::int = transactions_outputs.index
			LEFT JOIN transactions ON transactions.transaction_id = transactions_outputs.transaction_id
            WHERE "script_public_key_address" = '{kaspaAddress}'
			ORDER by block_time DESC
			 
LIMIT 200""")).all()

    # build response
    tx_list = []
    for x in resp:
        tx_list.append({"tx_received": x[0],
                        "tx_sent": x[1]})
    return {
        "transactions": tx_list
    }
