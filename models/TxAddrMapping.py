from sqlalchemy import Column, String, BigInteger, Index

from dbsession import Base


class TxAddrMapping(Base):
    __tablename__ = 'tx_id_address_mapping'
    transaction_id = Column(String)
    address = Column(String)
    block_time = Column(BigInteger)
    id = Column(BigInteger, primary_key=True)


Index("idx_address_block_time", TxAddrMapping.address, TxAddrMapping.block_time)
Index("idx_block_time", TxAddrMapping.block_time)
Index("idx_tx_id", TxAddrMapping.transaction_id)
Index("idx_tx_id_address_mapping", TxAddrMapping.transaction_id)
