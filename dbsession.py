import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_logger = logging.getLogger(__name__)

engine = create_async_engine(os.getenv("SQL_URI"), pool_pre_ping=True, echo=False)
Base = declarative_base()

session_maker = sessionmaker(engine)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def create_all(drop=False):
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
