from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone

from app.db import replace_runtime_dataset
from app.services.market_sync_service import MarketSyncError, MarketSyncService


logger = logging.getLogger(__name__)

SyncClock = Callable[[], datetime]
SleepFn = Callable[[float], Awaitable[None]]


class RuntimeSyncController:
    def __init__(
        self,
        *,
        interval_minutes: int,
        enabled_on_start: bool,
        clock: SyncClock | None = None,
        sleep_fn: SleepFn | None = None,
    ) -> None:
        self.interval_minutes = interval_minutes
        self.refresh_interval_hours = round(interval_minutes / 60, 2)
        self.enabled_on_start = enabled_on_start
        self._clock = clock or self._utcnow
        self._sleep = sleep_fn or asyncio.sleep
        self._task: asyncio.Task | None = None
        self._sync_lock = asyncio.Lock()
        self._started_at = self._clock()

    async def start(self) -> None:
        if self.enabled_on_start:
            await self.refresh(reason="startup")
        self._task = asyncio.create_task(self._run_loop(), name="runtime-market-sync")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def refresh(self, *, reason: str) -> dict:
        async with self._sync_lock:
            sync_service = MarketSyncService()
            try:
                payload, snapshots, features, pool_scores = await sync_service.build_runtime_dataset()
                replace_runtime_dataset(payload, snapshots=snapshots, features=features, pool_scores=pool_scores)
                refreshed_at = self._isoformat(self._clock())
                logger.info("runtime market sync completed (%s)", reason)
                return {
                    "ok": True,
                    "reason": reason,
                    "refreshedAt": refreshed_at,
                    "nextRefreshAt": self.next_refresh_at,
                }
            except MarketSyncError as exc:
                logger.warning("runtime market sync skipped (%s): %s", reason, exc)
                return {
                    "ok": False,
                    "reason": reason,
                    "refreshedAt": self._isoformat(self._clock()),
                    "nextRefreshAt": self.next_refresh_at,
                    "error": str(exc),
                }
            except Exception as exc:
                logger.exception("runtime market sync failed (%s)", reason)
                return {
                    "ok": False,
                    "reason": reason,
                    "refreshedAt": self._isoformat(self._clock()),
                    "nextRefreshAt": self.next_refresh_at,
                    "error": str(exc),
                }

    async def _run_loop(self) -> None:
        while True:
            await self._sleep(self.seconds_until_next_refresh())
            await self.refresh(reason="scheduled")

    def seconds_until_next_refresh(self) -> float:
        now = self._clock()
        next_refresh = self._next_refresh_datetime(now)
        return max((next_refresh - now).total_seconds(), 0.0)

    @property
    def next_refresh_at(self) -> str:
        return self._isoformat(self._next_refresh_datetime(self._clock()))

    @property
    def uptime(self) -> str:
        diff = max(self._clock() - self._started_at, timedelta())
        total_minutes = int(diff.total_seconds() // 60)
        days, remaining_minutes = divmod(total_minutes, 60 * 24)
        hours, minutes = divmod(remaining_minutes, 60)

        if days > 0:
            return f"{days}天 {hours}小时"
        if hours > 0:
            return f"{hours}小时 {minutes}分钟"
        return f"{max(minutes, 1)}分钟"

    def _next_refresh_datetime(self, now: datetime) -> datetime:
        minute_bucket = (now.minute // self.interval_minutes) * self.interval_minutes
        current_slot = now.replace(minute=minute_bucket, second=0, microsecond=0)
        if current_slot <= now:
            current_slot += timedelta(minutes=self.interval_minutes)
        return current_slot

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    def _isoformat(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
