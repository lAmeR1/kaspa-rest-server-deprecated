# encoding: utf-8

import os

from fastapi import FastAPI

from kaspad.KaspadMultiClient import KaspadMultiClient

app = FastAPI()

kaspad_hosts = []

for i in range(100):
    try:
        kaspad_hosts.append(os.environ[f"KASPAD_HOST_{i + 1}"].strip())
    except KeyError:
        break

kaspad_client = KaspadMultiClient(kaspad_hosts)


@app.get("/addresses/{address_id}/balance")
def get_balance(address_id: str):
    resp = kaspad_client.request("getBalanceByAddressRequest",
                                 params={
                                     "address": address_id
                                 })
    return {
        "address": address_id,
        "balance": resp["getBalanceByAddressResponse"]["balance"]
    }


@app.get("/addresses/{address_id}/utxos")
def get_utxos_for_address(address_id: str):
    resp = kaspad_client.request("getUtxosByAddressesRequest",
                                 params={
                                     "addresses": [address_id]
                                 })
    return (utxo for utxo in resp["getUtxosByAddressesResponse"]["entries"] if utxo["address"] == address_id)


@app.get("/blocks")
def get_blocks(lowHash: str, includeBlocks: bool = False, includeTransactions: bool = False):
    resp = kaspad_client.request("getBlocksRequest",
                                 params={
                                     "lowHash": lowHash,
                                     "includeBlocks": includeBlocks,
                                     "includeTransactions": includeTransactions
                                 })

    return resp["getBlocksResponse"]


@app.get("/blocks/{block_id}")
def get_block(block_id: str):
    resp = kaspad_client.request("getBlockRequest",
                                 params={
                                     "hash": block_id,
                                     "includeTransactions": True
                                 })

    return resp["getBlockResponse"]


@app.get("/infos/blockdag")
def get_blockdag():
    resp = kaspad_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]


@app.get("/infos/coinsupply")
def get_coinsupply():
    resp = kaspad_client.request("getCoinSupplyRequest")
    return {
        "circulatingSupply": resp["getCoinSupplyResponse"]["circulatingSompi"],
        "maxSupply": resp["getCoinSupplyResponse"]["maxSompi"]
    }


@app.get("/infos/kaspad")
def get_infos():
    resp = kaspad_client.request("getInfoRequest")
    resp["getInfoResponse"].pop("p2pId")
    return resp["getInfoResponse"]


@app.get("/infos/network")
def get_network():
    resp = kaspad_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
