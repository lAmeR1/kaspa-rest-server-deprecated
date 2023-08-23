from sqlalchemy import Column, String, BigInteger, Boolean, UniqueConstraint, Index

from dbsession import Base


class TxAddrMapping(Base):
    __tablename__ = 'tx_id_address_mapping'
    transaction_id = Column(String)
    address = Column(String)
    block_time = Column(BigInteger)
    is_accepted = Column(Boolean, default=False)
    id = Column(BigInteger, primary_key=True)

    __table_args__ = (UniqueConstraint('transaction_id', 'address',
                                       name='tx_id_address_mapping_transaction_id_address_key'),)


Index("idx_address_block_time", TxAddrMapping.address, TxAddrMapping.block_time)
Index("idx_block_time", TxAddrMapping.block_time)
Index("idx_tx_id", TxAddrMapping.transaction_id)
Index("idx_tx_id_address_mapping", TxAddrMapping.transaction_id)
