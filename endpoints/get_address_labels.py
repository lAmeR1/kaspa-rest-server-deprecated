# encoding: utf-8
from fastapi import Path
from sqlalchemy.future import select

from dbsession import async_session
from server import app

from models.AddressLabel import AddressLabel

@app.get("/addresses/{kaspaAddress}/label",
         tags=["Kaspa addresses"])
async def get_address_label(
        kaspaAddress: str = Path(
            description="Kaspa address as string e.g. "
                        "kaspa:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex="^kaspa\:[a-z0-9]{61,63}$")
):
    """
    Return the label of this address if it exists
    """

    async with async_session() as s:
        label = await s.execute(select(AddressLabel.label)
                                                 .filter(AddressLabel.address == kaspaAddress)
                                                )
        label = label.scalar()

    return {"label" : label}
