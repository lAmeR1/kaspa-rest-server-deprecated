from tests import validate_rate_limit

from server import kaspad_client

import pytest
import endpoints.get_blockdag

@pytest.mark.asyncio
async def test_get_blockdag_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit("/info/blockdag")
