from sqlalchemy import Column, String

from dbsession import Base
from models.AddressColumn import AddressColumn


class AddressKnown(Base):
    __tablename__ = 'addresses_known'
    address = Column(AddressColumn, primary_key=True)
    name = Column(String)
