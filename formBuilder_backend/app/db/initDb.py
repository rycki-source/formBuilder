from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base
from app.core.config import settings


async def init_db():
    """Initialiser la base de données"""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured")
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
