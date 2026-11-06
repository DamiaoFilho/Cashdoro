from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.auth.api.auth_router import router as auth_router
from src.auth.api.users_router import router as users_router
from src.shared.config import get_settings
from src.shared.dependencies import get_db

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)


@api_router.get("/health")
def health(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(get_settings().database_url)
    app.state.session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Cashdoro", lifespan=lifespan)
    app.include_router(api_router)
    return app


app = create_app()
