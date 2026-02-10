from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing needed, engine connects lazily
    yield
    # Shutdown: dispose the connection pool
    await engine.dispose()


app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"service": settings.APP_TITLE, "version": settings.APP_VERSION}
