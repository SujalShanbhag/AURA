from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.routes import router

app = FastAPI(
    title="AURA API",
    version="1.0.0",
    description="Next Generation AI Companion Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "app": "AURA",
        "status": "running",
        "version": "1.0.0"
    }