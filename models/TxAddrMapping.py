from sqlalchemy import Column, BigInteger

from dbsession import Base
from models.type_decorators.HexColumn import HexColumn
from models.AddressColumn import AddressColumn


class TxAddrMapping(Base):
    __tablename__ = 'addresses_transactions'
    transaction_id = Column(HexColumn, primary_key=True)
    address = Column(AddressColumn, primary_key=True)
    block_time = Column(BigInteger)
