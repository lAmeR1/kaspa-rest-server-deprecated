from sqlalchemy import Column, String, BigInteger, Boolean

from dbsession import Base

class TxAddrMapping(Base):
    __tablename__ = 'tx_id_address_mapping'
    transaction_id = Column(String)
    address = Column(String)
    block_time = Column(BigInteger)
    is_accepted = Column(Boolean, default=False)
    id = Column(BigInteger, primary_key=True)