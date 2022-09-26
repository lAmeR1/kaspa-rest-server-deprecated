from sqlalchemy import Column, String, Float, Boolean, ARRAY, Integer, BigInteger, TIMESTAMP

from dbsession import Base


class Block(Base):
    __tablename__ = 'blocks'

    hash = Column(String, primary_key=True)
    accepted_id_merkle_root = Column(String)
    difficulty = Column(Float)
    # childrenHashes = Column(JSONB)
    is_chain_block = Column(Boolean)
    merge_set_blues_hashes = Column(ARRAY(String))
    merge_set_reds_hashes = Column(ARRAY(String))
    selected_parent_hash = Column(String)
    bits = Column(Integer)
    blue_score = Column(BigInteger)
    blue_work = Column(String)
    daa_score = Column(BigInteger)
    hash_merkle_root = Column(String)
    nonce = Column(String)
    parents = Column(ARRAY(String))
    pruning_point = Column(String)
    timestamp = Column(TIMESTAMP(timezone=False))
    utxo_commitment = Column(String)
    version = Column(Integer)

