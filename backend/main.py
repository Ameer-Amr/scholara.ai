from backend.routers import documents
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.core.database import get_db
from fastapi.middleware.cors import CORSMiddleware
from backend.core.middleware import RequestLoggingMiddleware
from backend.routers import auth

app = FastAPI(title="Scholara")

# middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSMiddleware)

# routers
app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/")
def root():
    return "Welcome to scholara"


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "Database is connected successfully!"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
