from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Index
from sqlalchemy.dialects.postgresql import ARRAY

from dbsession import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    subnetwork_id = Column(String)  # "0000000000000000000000000000000000000000",
    transaction_id = Column(String, primary_key=True)  # "bedea078...1f73f03061",
    hash = Column(String)  # "a5f99f4dc55693124e7c6b75dc3e56b60db381a74716046dbdcae9210ce1052f",
    mass = Column(String)  # "2036",
    block_hash = Column(ARRAY(String))  # "1b41af8cfe1851243bedf596b7299c039b86b2fef8eb4204b04f954da5d2ab0f",
    block_time = Column(BigInteger)  # "1663286480803"
    is_accepted = Column(Boolean, default=False)
    accepting_block_hash = Column(String, nullable=True)


Index("block_time_idx", Transaction.block_time)
Index("idx_accepting_block", Transaction.accepting_block_hash)
Index("idx_block_hash", Transaction.block_hash)


class TransactionOutput(Base):
    __tablename__ = 'transactions_outputs'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String)
    index = Column(Integer)
    amount = Column(BigInteger)
    script_public_key = Column(String)
    script_public_key_address = Column(String)
    script_public_key_type = Column(String)
    accepting_block_hash = Column(String)


Index("idx_txouts", TransactionOutput.transaction_id)
Index("idx_txouts_addr", TransactionOutput.script_public_key_address)
Index("tx_id_and_index", TransactionOutput.transaction_id, TransactionOutput.index)


class TransactionInput(Base):
    __tablename__ = 'transactions_inputs'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String)
    index = Column(Integer)

    previous_outpoint_hash = Column(String)  # "ebf6da83db96d312a107a2ced19a01823894c9d7072ed0d696a9a152fd81485e"
    previous_outpoint_index = Column(Integer)  # "ebf6da83db96d312a107a2ced19a01823894c9d7072ed0d696a9a152fd81485e"

    signature_script = Column(String)  # "41c903159094....281a1d26f70b0037d600554e01",
    sig_op_count = Column(Integer)


Index("idx_txin_prev", TransactionInput.previous_outpoint_hash)
Index("idx_txin", TransactionInput.transaction_id)
