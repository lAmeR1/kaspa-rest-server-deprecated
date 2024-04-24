from sqlalchemy import Column

from dbsession import Base
from models.type_decorators.HexColumn import HexColumn


class ChainBlock(Base):
    __tablename__ = 'chain_blocks'
    block_hash = Column(HexColumn, primary_key=True)
