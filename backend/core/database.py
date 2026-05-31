from backend.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Dependency to inject DB sessions into FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
