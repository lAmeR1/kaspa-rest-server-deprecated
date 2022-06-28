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

if not kaspad_hosts:
    raise Exception('Please set at least KASPAD_HOST_1 environment variable.')

kaspad_client = KaspadMultiClient(kaspad_hosts)
