from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    return {"service": settings.APP_TITLE, "version": settings.APP_VERSION}
