from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import init_db, replace_runtime_dataset
from app.schemas import (
    CoinDetailResponse,
    CoinHistoryResponse,
    HealthResponse,
    ListResponse,
    StatusResponse,
)
from app.services.market_sync_service import MarketSyncError, MarketSyncService
from app.services.winlong_service import CoinNotFoundError, WinlongService


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if settings.enable_sync_on_start:
        sync_service = MarketSyncService()
        try:
            payload, snapshots, features, pool_scores = await sync_service.build_runtime_dataset()
            replace_runtime_dataset(payload, snapshots=snapshots, features=features, pool_scores=pool_scores)
            logger.info("runtime market sync completed on startup")
        except MarketSyncError as exc:
            logger.warning("runtime market sync skipped: %s", exc)
        except Exception:
            logger.exception("runtime market sync failed, keeping current dataset")
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
service = WinlongService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CoinNotFoundError)
async def handle_coin_not_found(_: Request, exc: CoinNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": f"coin not found: {exc}", "data": None},
    )


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "invalid request", "data": exc.errors()},
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(ok=True, version=settings.app_version)


@app.get("/api/winlong/list", response_model=ListResponse)
async def get_winlong_list(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    min_score: float = Query(0, ge=0, le=100),
    sort_by: str = Query("rank"),
    order: str = Query("asc"),
    q: str | None = Query(default=None, max_length=20),
    tag: str | None = Query(default=None, max_length=32),
):
    return service.list_coins(
        limit=limit,
        offset=offset,
        min_score=min_score,
        sort_by=sort_by,
        order=order,
        q=q,
        tag=tag,
    )


@app.get("/api/winlong/coins/{symbol}", response_model=CoinDetailResponse)
async def get_coin_detail(symbol: str):
    return service.get_coin_detail(symbol)


@app.get("/api/winlong/coins/{symbol}/history", response_model=CoinHistoryResponse)
async def get_coin_history(symbol: str, days: int = Query(30, ge=1, le=180)):
    return service.get_coin_history(symbol, days=days)


@app.get("/api/winlong/status", response_model=StatusResponse)
async def get_status():
    return service.get_status()
