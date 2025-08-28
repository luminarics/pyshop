# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, profile
from app.database import init_db
from app.core.config import GIT_SHA, CORS_ORIGINS
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger

logger.add("logs/api.log", rotation="1 week", serialize=True)


def __init__():
    logger.info("Starting FastAPI application")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("DB schema ensured")

    yield
    logger.info("App shutdown complete")


app = FastAPI(lifespan=lifespan)

# CORS middleware with strict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

instrumentator = Instrumentator()

instrumentator.instrument(app)

instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)


# Routers
app.include_router(products.router)

app.include_router(profile.router)


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/version", include_in_schema=False)
def version():
    return GIT_SHA
