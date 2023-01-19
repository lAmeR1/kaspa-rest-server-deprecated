from tests import validate_rate_limit

import pytest
import endpoints.get_virtual_chain_blue_score

from server import kaspad_client

@pytest.mark.asyncio
async def test_get_virtual_selected_parent_blue_score_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit("/info/virtual-chain-blue-score")
