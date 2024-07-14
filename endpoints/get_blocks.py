# encoding: utf-8
import os
from typing import List

from fastapi import Query, Path, HTTPException
from fastapi import Response
from pydantic import BaseModel
from sqlalchemy import select, case, exists, func

from dbsession import async_session
from endpoints.get_virtual_chain_blue_score import current_blue_score_data
from models.BlockParent import BlockParent
from models.Subnetwork import Subnetwork
from models.Block import Block
from models.BlockTransaction import BlockTransaction
from models.ChainBlock import ChainBlock
from models.Transaction import TransactionOutput, TransactionInput, Transaction
from server import app, kaspad_client

IS_SQL_DB_CONFIGURED = os.getenv("SQL_URI") is not None


class VerboseDataModel(BaseModel):
    hash: str = "18c7afdf8f447ca06adb8b4946dc45f5feb1188c7d177da6094dfbc760eca699"
    difficulty: float = 4102204523252.94,
    selectedParentHash: str = "580f65c8da9d436480817f6bd7c13eecd9223b37f0d34ae42fb17e1e9fda397e"
    transactionIds: List[str] | None = ["533f8314bf772259fe517f53507a79ebe61c8c6a11748d93a0835551233b3311"]
    blueScore: str = "18483232"
    childrenHashes: List[str] | None = None
    mergeSetBluesHashes: List[str] = []
    mergeSetRedsHashes: List[str] = []
    isChainBlock: bool | None = None


class ParentHashModel(BaseModel):
    parentHashes: List[str] = ["580f65c8da9d436480817f6bd7c13eecd9223b37f0d34ae42fb17e1e9fda397e"]


class BlockHeader(BaseModel):
    version: int = 1
    hashMerkleRoot: str = "e6641454e16cff4f232b899564eeaa6e480b66069d87bee6a2b2476e63fcd887"
    acceptedIdMerkleRoot: str = "9bab45b027a0b2b47135b6f6f866e5e4040fc1fdf2fe56eb0c90a603ce86092b"
    utxoCommitment: str = "236d5f9ffd19b317a97693322c3e2ae11a44b5df803d71f1ccf6c2393bc6143c"
    timestamp: str = "1656450648874"
    bits: int = 455233226
    nonce: str = "14797571275553019490"
    daaScore: str = "19984482"
    blueWork: str = "2d1b3f04f8a0dcd31"
    parents: List[ParentHashModel]
    blueScore: str = "18483232"
    pruningPoint: str = "5d32a9403273a34b6551b84340a1459ddde2ae6ba59a47987a6374340ba41d5d"


class BlockModel(BaseModel):
    header: BlockHeader
    transactions: list | None
    verboseData: VerboseDataModel


class BlockResponse(BaseModel):
    blockHashes: List[str] = ["44edf9bfd32aa154bfad64485882f184372b64bd60565ba121b42fc3cb1238f3",
                              "18c7afdf8f447ca06adb8b4946dc45f5feb1188c7d177da6094dfbc760eca699",
                              "9a822351cd293a653f6721afec1646bd1690da7124b5fbe87001711406010604",
                              "2fda0dad4ec879b4ad02ebb68c757955cab305558998129a7de111ab852e7dcb"]
    blocks: List[BlockModel] | None


@app.get("/blocks/{blockId}", response_model=BlockModel, tags=["Kaspa blocks"])
async def get_block(response: Response,
                    blockId: str = Path(regex="[a-f0-9]{64}")):
    """
    Get block information for a given block id
    """
    resp = await kaspad_client.request("getBlockRequest",
                                       params={
                                           "hash": blockId,
                                           "includeTransactions": True
                                       })
    requested_block = None

    if "block" in resp["getBlockResponse"]:
        # We found the block in kaspad. Just use it
        requested_block = resp["getBlockResponse"]["block"]
    else:
        if IS_SQL_DB_CONFIGURED:
            # Didn't find the block in kaspad. Try getting it from the DB
            response.headers["X-Data-Source"] = "Database"
            requested_block = await get_block_from_db(blockId)

    if not requested_block:
        # Still did not get the block
        print("hier")
        raise HTTPException(status_code=404, detail="Block not found", headers={
            "Cache-Control": "public, max-age=1"
        })

    if int(requested_block["header"]["blueScore"]) > current_blue_score_data["blue_score"] - 20:
        response.headers["Cache-Control"] = "public, max-age=1"

    elif int(requested_block["header"]["blueScore"]) > current_blue_score_data["blue_score"] - 60:
        response.headers["Cache-Control"] = "public, max-age=10"

    else:
        response.headers["Cache-Control"] = "public, max-age=600"

    return requested_block


@app.get("/blocks", response_model=BlockResponse, tags=["Kaspa blocks"])
async def get_blocks(response: Response,
                     lowHash: str = Query(regex="[a-f0-9]{64}"),
                     includeBlocks: bool = False,
                     includeTransactions: bool = False):
    """
    Lists block beginning from a low hash (block id). Note that this function tries to determine the blocks from
    the kaspad node. If this is not possible, the database is getting queryied as backup. In this case the response
    header contains the key value pair: x-data-source: database.

    Additionally the fields in verboseData: isChainBlock, childrenHashes and transactionIds can't be filled.
    """
    response.headers["Cache-Control"] = "public, max-age=3"

    resp = await kaspad_client.request("getBlocksRequest",
                                       params={
                                           "lowHash": lowHash,
                                           "includeBlocks": includeBlocks,
                                           "includeTransactions": includeTransactions
                                       })

    return resp["getBlocksResponse"]


@app.get("/blocks-from-bluescore", response_model=List[BlockModel], tags=["Kaspa blocks"])
async def get_blocks_from_bluescore(response: Response,
                                    blueScore: int = 43679173,
                                    includeTransactions: bool = False):
    """
    Lists block beginning from a low hash (block id). Note that this function is running on a kaspad and not returning
    data from database.
    """
    response.headers["X-Data-Source"] = "Database"

    if blueScore > current_blue_score_data["blue_score"] - 20:
        response.headers["Cache-Control"] = "no-store"

    async with async_session() as s:
        blocks = (await s.execute(block_join_query().where(Block.blue_score == blueScore))).all()

    return [{
        "header": {
            "version": block.version,
            "hashMerkleRoot": block.hash_merkle_root,
            "acceptedIdMerkleRoot": block.accepted_id_merkle_root,
            "utxoCommitment": block.utxo_commitment,
            "timestamp": block.timestamp,
            "bits": block.bits,
            "nonce": block.nonce,
            "daaScore": block.daa_score,
            "blueWork": block.blue_work,
            "parents": [{"parentHashes": parents}],
            "blueScore": block.blue_score,
            "pruningPoint": block.pruning_point
        },
        "transactions": await get_transactions(block.hash, transaction_ids) if includeTransactions else None,
        "verboseData": {
            "hash": block.hash,
            "difficulty": block.difficulty,
            "selectedParentHash": block.selected_parent_hash,
            "transactionIds": transaction_ids,
            "blueScore": block.blue_score,
            "childrenHashes": children,
            "mergeSetBluesHashes": block.merge_set_blues_hashes or [],
            "mergeSetRedsHashes": block.merge_set_reds_hashes or [],
            "isChainBlock": is_chain_block,
        }
    } for block, is_chain_block, parents, children, transaction_ids in blocks]


async def get_block_from_db(blockId):
    """
    Get the block from the database
    """
    async with async_session() as s:
        block = (await s.execute(block_join_query().where(Block.hash == blockId).limit(1))).first()
        if block is None:
            raise HTTPException(status_code=404, detail="Block not found", headers={"Cache-Control": "public, max-age=3"})
        block, is_chain_block, parents, children, transaction_ids = block

    return {
        "header": {
            "version": block.version,
            "hashMerkleRoot": block.hash_merkle_root,
            "acceptedIdMerkleRoot": block.accepted_id_merkle_root,
            "utxoCommitment": block.utxo_commitment,
            "timestamp": block.timestamp,
            "bits": block.bits,
            "nonce": block.nonce,
            "daaScore": block.daa_score,
            "blueWork": block.blue_work,
            "parents": [{"parentHashes": parents}],
            "blueScore": block.blue_score,
            "pruningPoint": block.pruning_point
        },
        "transactions": await get_transactions(block.hash, transaction_ids),
        "verboseData": {
            "hash": block.hash,
            "difficulty": block.difficulty,
            "selectedParentHash": block.selected_parent_hash,
            "transactionIds": transaction_ids,
            "blueScore": block.blue_score,
            "childrenHashes": children,
            "mergeSetBluesHashes": block.merge_set_blues_hashes or [],
            "mergeSetRedsHashes": block.merge_set_reds_hashes or [],
            "isChainBlock": is_chain_block,
        }
    }


def block_join_query():
    return select(
        Block,
        case([(exists().where(ChainBlock.block_hash == Block.hash), True)], else_=False),
        select(func.array_agg(BlockParent.parent_hash)).where(BlockParent.block_hash == Block.hash).scalar_subquery(),
        select(func.array_agg(BlockParent.block_hash)).where(BlockParent.parent_hash == Block.hash).scalar_subquery(),
        select(func.array_agg(BlockTransaction.transaction_id)).where(BlockTransaction.block_hash == Block.hash).scalar_subquery(),
    )


async def get_transactions(blockId, transactionIds):
    """
    Get the transactions associated with a block
    """
    async with async_session() as s:
        transactions = (await s.execute(
            select(Transaction, Subnetwork)
            .join(Subnetwork, Transaction.subnetwork_id == Subnetwork.id)
            .filter(Transaction.transaction_id.in_(transactionIds))
        )).all()

        tx_outputs = (await s.execute(
            select(TransactionOutput)
            .where(TransactionOutput.transaction_id.in_(transactionIds))
        )).scalars().all()

        tx_inputs = (await s.execute(
            select(TransactionInput)
            .where(TransactionInput.transaction_id.in_(transactionIds))
        )).scalars().all()

    tx_list = []
    for tx, sub in transactions:
        tx_list.append({
            "inputs": [
                {
                    "previousOutpoint": {
                        "transactionId": tx_inp.previous_outpoint_hash,
                        "index": tx_inp.previous_outpoint_index
                    },
                    "signatureScript": tx_inp.signature_script,
                    "sigOpCount": tx_inp.sig_op_count
                }
                for tx_inp in tx_inputs if tx_inp.transaction_id == tx.transaction_id
            ],
            "outputs": [
                {
                    "amount": tx_out.amount,
                    "scriptPublicKey": {
                        "scriptPublicKey": tx_out.script_public_key
                    },
                    "verboseData": {
                        "scriptPublicKeyType": tx_out.script_public_key_type,
                        "scriptPublicKeyAddress": tx_out.script_public_key_address
                    }
                } for tx_out in tx_outputs if tx_out.transaction_id == tx.transaction_id
            ],
            "subnetworkId": sub.subnetwork_id,
            "verboseData": {
                "transactionId": tx.transaction_id,
                "hash": tx.hash,
                "mass": tx.mass,
                "blockHash": blockId,
                "blockTime": tx.block_time
            }
        })
    return tx_list
