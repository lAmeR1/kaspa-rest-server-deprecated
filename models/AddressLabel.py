from sqlalchemy import Column, String

from dbsession import Base

class AddressLabel(Base):
    __tablename__ = 'address_labels'
    address = Column(String, primary_key=True)
    label = Column(String)
