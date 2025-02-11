from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import settings
from urllib.parse import quote

# Quote the password to ensure special characters are handled
postgres_password = settings.POSTGRES_PASSWORD
quoted_password = quote(postgres_password)

# Manually construct the full database URL
postgres_url = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{quoted_password}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# Create the async engine
engine = create_async_engine(postgres_url)

# Create the session factory
AsyncSessionFactory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)


# Function to get a new session
async def get_session() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session
