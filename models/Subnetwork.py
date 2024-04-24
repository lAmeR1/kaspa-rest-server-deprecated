from sqlalchemy import Column, SmallInteger, String

from dbsession import Base


class Subnetwork(Base):
    __tablename__ = 'subnetworks'
    id = Column(SmallInteger, primary_key=True)
    subnetwork_id = Column(String)
