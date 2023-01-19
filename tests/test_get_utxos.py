from tests import validate_rate_limit

import pytest
import endpoints.get_utxos

from server import kaspad_client

test_kaspa_address = "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00"

@pytest.mark.asyncio
async def test_get_utxos_for_address_rate_limit():
    await kaspad_client.initialize_all()

    await validate_rate_limit(f"/addresses/{test_kaspa_address}/utxos")
