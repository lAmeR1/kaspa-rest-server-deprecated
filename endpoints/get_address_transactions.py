# encoding: utf-8
import re
import time
from enum import Enum
from typing import List

from fastapi import Path, Query
from pydantic import BaseModel
from sqlalchemy import text, func
from sqlalchemy.future import select

from dbsession import async_session
from endpoints import sql_db_only
from endpoints.get_transactions import search_for_transactions, TxSearch, TxModel
from models.TxAddrMapping import TxAddrMapping
from server import app

DESC_RESOLVE_PARAM = "Use this parameter if you want to fetch the TransactionInput previous outpoint details." \
                     " Light fetches only the address and amount. Full fetches the whole TransactionOutput and " \
                     "adds it into each TxInput."

REGEX_KASPA_ADDRESS = "^kaspa(test)?\:[a-z0-9]{61,63}$"

class TransactionsReceivedAndSpent(BaseModel):
    tx_received: str
    tx_spent: str | None
    # received_amount: int = 38240000000


class TransactionForAddressResponse(BaseModel):
    transactions: List[TransactionsReceivedAndSpent]


class TransactionCount(BaseModel):
    total: int


class PreviousOutpointLookupMode(str, Enum):
    no = "no"
    light = "light"
    full = "full"


@app.get("/addresses/{kaspaAddress}/transactions",
         response_model=TransactionForAddressResponse,
         response_model_exclude_unset=True,
         tags=["Kaspa addresses"])
@sql_db_only
async def get_transactions_for_address(
        kaspaAddress: str = Path(
            description="Kaspa address as string e.g. "
                        "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex=REGEX_KASPA_ADDRESS)):
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
    kaspaAddress = re.sub(r"^kaspa(test)?:", "", kaspaAddress)  # Custom query bypasses the TypeDecorator, must handle it manually
    async with async_session() as session:
        resp = await session.execute(
            text(f"""
            SELECT o.transaction_id, i.transaction_id
            FROM transactions t
            LEFT JOIN transactions_outputs o ON t.transaction_id = o.transaction_id
            LEFT JOIN transactions_inputs i ON i.previous_outpoint_hash = t.transaction_id AND i.previous_outpoint_index = o.index
            WHERE o.script_public_key_address = :kaspaAddress
            ORDER by t.block_time DESC
            LIMIT 500"""),
            {'kaspaAddress': kaspaAddress})

        resp = resp.all()

    # build response
    tx_list = []
    for x in resp:
        tx_list.append({"tx_received": x[0].hex() if x[0] is not None else None,
                        "tx_spent": x[1].hex() if x[1] is not None else None})
    return {
        "transactions": tx_list
    }


@app.get("/addresses/{kaspaAddress}/full-transactions",
         response_model=List[TxModel],
         response_model_exclude_unset=True,
         tags=["Kaspa addresses"])
@sql_db_only
async def get_full_transactions_for_address(
        kaspaAddress: str = Path(
            description="Kaspa address as string e.g. "
                        "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex=REGEX_KASPA_ADDRESS),
        limit: int = Query(
            description="The number of records to get",
            ge=1,
            le=500,
            default=50),
        offset: int = Query(
            description="The offset from which to get records",
            ge=0,
            default=0),
        fields: str = "",
        resolve_previous_outpoints: PreviousOutpointLookupMode =
        Query(default="no",
              description=DESC_RESOLVE_PARAM)):
    """
    Get all transactions for a given address from database.
    And then get their related full transaction data
    """

    async with async_session() as s:
        # Doing it this way as opposed to adding it directly in the IN clause
        # so I can re-use the same result in tx_list, TxInput and TxOutput
        tx_within_limit_offset = await s.execute(select(TxAddrMapping.transaction_id)
                                                 .filter(TxAddrMapping.address == kaspaAddress)
                                                 .limit(limit)
                                                 .offset(offset)
                                                 .order_by(TxAddrMapping.block_time.desc())
                                                 )

        tx_ids_in_page = [x[0] for x in tx_within_limit_offset.all()]

    return await search_for_transactions(TxSearch(transactionIds=tx_ids_in_page),
                                         fields,
                                         resolve_previous_outpoints)


@app.get("/addresses/{kaspaAddress}/transactions-count",
         response_model=TransactionCount,
         tags=["Kaspa addresses"])
@sql_db_only
async def get_transaction_count_for_address(
        kaspaAddress: str = Path(
            description="Kaspa address as string e.g. "
                        "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex=REGEX_KASPA_ADDRESS)
):
    """
    Count the number of transactions associated with this address
    """

    async with async_session() as s:
        count_query = select(func.count()).filter(TxAddrMapping.address == kaspaAddress)

        tx_count = await s.execute(count_query)

    return TransactionCount(total=tx_count.scalar())
