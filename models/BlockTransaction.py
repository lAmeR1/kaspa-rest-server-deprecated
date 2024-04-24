from sqlalchemy import Column

from dbsession import Base
from models.type_decorators.HexColumn import HexColumn


class BlockTransaction(Base):
    __tablename__ = 'blocks_transactions'
    block_hash = Column(HexColumn, primary_key=True)
    transaction_id = Column(HexColumn, primary_key=True)
