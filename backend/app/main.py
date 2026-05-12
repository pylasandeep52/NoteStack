import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  — register models with Base.metadata
from app.config import BACKEND_DIR, settings
from app.database import Base, engine
from app.middleware import RequestLoggingMiddleware
from app.routers import auth, notes, tags
from app.utils.logging import configure_logging


configure_logging()
logger = logging.getLogger("app")

FRONTEND_DIR = BACKEND_DIR.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info(
        "application starting", extra={"ctx_environment": settings.environment}
    )
    yield
    logger.info("application stopping")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A simple notes application built for learning full-stack development.",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled exception",
        extra={"ctx_method": request.method, "ctx_path": request.url.path},
    )
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error"}
    )


app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(tags.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
