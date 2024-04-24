# encoding: utf-8
import os
from typing import List

from fastapi import Query, Path, HTTPException
from fastapi import Response
from pydantic import BaseModel
from sqlalchemy import select, case, exists

from dbsession import async_session
from endpoints.get_virtual_chain_blue_score import current_blue_score_data
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
    mergeSetBluesHashes: List[str] = ["580f65c8da9d436480817f6bd7c13eecd9223b37f0d34ae42fb17e1e9fda397e"]
    mergeSetRedsHashes: List[str] = ["580f65c8da9d436480817f6bd7c13eecd9223b37f0d34ae42fb17e1e9fda397e"]
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

    # We found the block, now we guarantee it contains the transactions
    # It's possible that the block from kaspad does not contain transactions
    if 'transactions' not in requested_block or not requested_block['transactions']:
        requested_block['transactions'] = await get_block_transactions(blockId)

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

    blocks_cb = await get_blocks_from_db_by_bluescore(blueScore)

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
            "parents": [{"parentHashes": block.parents}],
            "blueScore": block.blue_score,
            "pruningPoint": block.pruning_point
        },
        "transactions": (txs := (await get_block_transactions(block.hash))) if includeTransactions else None,
        "verboseData": {
            "hash": block.hash,
            "difficulty": block.difficulty,
            "selectedParentHash": block.selected_parent_hash,
            "transactionIds": [tx["verboseData"]["transactionId"] for tx in txs] if includeTransactions else None,
            "blueScore": block.blue_score,
            "childrenHashes": None,
            "mergeSetBluesHashes": block.merge_set_blues_hashes,
            "mergeSetRedsHashes": block.merge_set_reds_hashes,
            "isChainBlock": is_chain_block,
        }
    } for block, is_chain_block in blocks_cb]


async def get_blocks_from_db_by_bluescore(blue_score):
    async with async_session() as s:
        blocks_cb = (await s.execute(
            select(Block,
                   case([(exists().where(ChainBlock.block_hash == Block.hash), True)], else_=False))
            .where(Block.blue_score == blue_score))).all()

    return blocks_cb


async def get_block_from_db(blockId):
    """
    Get the block from the database
    """
    async with async_session() as s:
        blocks_cb = await s.execute(
            select(Block,
                   case([(exists(1).where(ChainBlock.block_hash == Block.hash), True)], else_=False))
            .where(Block.hash == blockId).limit(1))

        block_cb = blocks_cb.first()
        if block_cb is None:
            raise HTTPException(status_code=404, detail="Block not found", headers={"Cache-Control": "public, max-age=3"})
        requested_block, is_chain_block = block_cb

    if requested_block:
        return {
            "header": {
                "version": requested_block.version,
                "hashMerkleRoot": requested_block.hash_merkle_root,
                "acceptedIdMerkleRoot": requested_block.accepted_id_merkle_root,
                "utxoCommitment": requested_block.utxo_commitment,
                "timestamp": requested_block.timestamp,
                "bits": requested_block.bits,
                "nonce": requested_block.nonce,
                "daaScore": requested_block.daa_score,
                "blueWork": requested_block.blue_work,
                "parents": [{"parentHashes": requested_block.parents}],
                "blueScore": requested_block.blue_score,
                "pruningPoint": requested_block.pruning_point
            },
            "transactions": None,  # This will be filled later
            "verboseData": {
                "hash": requested_block.hash,
                "difficulty": requested_block.difficulty,
                "selectedParentHash": requested_block.selected_parent_hash,
                "transactionIds": None,  # information not in database
                "blueScore": requested_block.blue_score,
                "childrenHashes": None,  # information not in database
                "mergeSetBluesHashes": requested_block.merge_set_blues_hashes,
                "mergeSetRedsHashes": requested_block.merge_set_reds_hashes,
                "isChainBlock": is_chain_block,  # information not in database
            }
        }
    return None


"""
Get the transactions associated with a block
"""


async def get_block_transactions(blockId):
    # create tx data
    tx_list = []

    async with async_session() as s:
        transactions = await s.execute(
            select(Transaction, Subnetwork, BlockTransaction)
            .join(Subnetwork,
                  Transaction.subnetwork_id == Subnetwork.id)
            .join(BlockTransaction,
                  Transaction.transaction_id == BlockTransaction.transaction_id)
            .filter(BlockTransaction.block_hash == blockId))

        transactions = transactions.all()

        tx_outputs = await s.execute(select(TransactionOutput)
                                     .where(TransactionOutput.transaction_id
                                            .in_([tx.transaction_id for tx, sub, bt in transactions])))

        tx_outputs = tx_outputs.scalars().all()

        tx_inputs = await s.execute(select(TransactionInput)
                                    .where(TransactionInput.transaction_id
                                           .in_([tx.transaction_id for tx, sub, bt in transactions])))

        tx_inputs = tx_inputs.scalars().all()

    for tx, sub, bt in transactions:
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
                for tx_inp in tx_inputs if tx_inp.transaction_id == tx.transaction_id],
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
                } for tx_out in tx_outputs if tx_out.transaction_id == tx.transaction_id],
            "subnetworkId": sub.subnetwork_id,
            "verboseData": {
                "transactionId": tx.transaction_id,
                "hash": tx.hash,
                "mass": tx.mass,
                "blockHash": bt.block_hash,
                "blockTime": tx.block_time
            }
        })

    return tx_list
