from tests import validate_rate_limit

import pytest

import endpoints.get_address_transactions

test_kaspa_address = "kaspa:thisaddressdoesnotexistabcdefghijklmnopqrstuvwxyz1234567890ab"

@pytest.mark.asyncio
async def test_get_address_transaction_rate_limit():
    await validate_rate_limit(f"/addresses/{test_kaspa_address}/transactions")
