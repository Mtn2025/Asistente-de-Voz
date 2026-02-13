from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app_nuevo.infrastructure.config.settings import settings

print(f"DATABASE_URL: {settings.DATABASE_URL.replace(settings.POSTGRES_PASSWORD, '***')}")
engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI that yields a database session.
    Closes the session automatically after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """
    Initialize database tables safely.
    Uses checkfirst=True to create tables only if they don't exist.
    This prevents errors on subsequent deploys.
    """
    from app_nuevo.infrastructure.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
