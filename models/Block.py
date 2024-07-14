from sqlalchemy import Column, Float, BigInteger, SmallInteger

from dbsession import Base
from models.type_decorators.HexColumn import HexColumn
from models.type_decorators.HexArrayColumn import HexArrayColumn
from models.type_decorators.ByteColumn import ByteColumn


class Block(Base):
    __tablename__ = 'blocks'
    hash = Column(HexColumn, primary_key=True)
    accepted_id_merkle_root = Column(HexColumn)
    difficulty = Column(Float)
    merge_set_blues_hashes = Column(HexArrayColumn)
    merge_set_reds_hashes = Column(HexArrayColumn)
    selected_parent_hash = Column(HexColumn)
    bits = Column(BigInteger)
    blue_score = Column(BigInteger)
    blue_work = Column(HexColumn)
    daa_score = Column(BigInteger)
    hash_merkle_root = Column(HexColumn)
    nonce = Column(ByteColumn)
    pruning_point = Column(HexColumn)
    timestamp = Column(BigInteger)
    utxo_commitment = Column(HexColumn)
    version = Column(SmallInteger)
