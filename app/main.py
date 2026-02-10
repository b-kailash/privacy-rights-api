from fastapi import FastAPI

app = FastAPI(
    title="Privacy Rights API",
    description="GDPR/CCPA Data Subject Request Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    return {"service": "Privacy Rights API", "version": "1.0.0"}
