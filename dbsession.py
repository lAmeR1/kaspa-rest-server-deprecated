import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_logger = logging.getLogger(__name__)

engine = create_async_engine(os.getenv("SQL_URI", "postgresql+asyncpg://127.0.0.1:5432"), pool_pre_ping=True, echo=True)
Base = declarative_base()

session_maker = sessionmaker(engine)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_all(drop=False):
    async with engine.begin() as conn:

        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
