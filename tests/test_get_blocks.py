from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_blocks

test_block_id = "b1662ec333c2ecc024ab33535be7af16b785806ef87318c86bd3a75b695f9855"

@pytest.mark.asyncio
async def test_get_block_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit(f"/blocks/{test_block_id}")

@pytest.mark.asyncio
async def test_get_blocks_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit(f"/blocks?lowHash={test_block_id}")
