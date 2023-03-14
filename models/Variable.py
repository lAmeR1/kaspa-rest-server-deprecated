from sqlalchemy import Column, String, Text

from dbsession import Base


class KeyValueModel(Base):
    __tablename__ = 'vars'
    key = Column(String, primary_key=True)
    value = Column(Text)
