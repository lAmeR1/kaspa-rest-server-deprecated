from sqlalchemy import Column

from dbsession import Base
from models.type_decorators.HexColumn import HexColumn


class TransactionAcceptance(Base):
    __tablename__ = 'transactions_acceptances'
    transaction_id = Column(HexColumn, primary_key=True)
    block_hash = Column(HexColumn)
