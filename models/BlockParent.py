from sqlalchemy import Column

from dbsession import Base
from models.type_decorators.HexColumn import HexColumn


class BlockParent(Base):
    __tablename__ = 'block_parent'
    block_hash = Column(HexColumn, primary_key=True)
    parent_hash = Column(HexColumn, primary_key=True)
