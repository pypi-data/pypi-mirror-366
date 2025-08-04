import asyncio
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

logger = logging.getLogger("gitops.semaphore")


class AppSemaphoreManager:
    """Manages per-app semaphores to ensure sequential updates per app.

    This ensures that while multiple deployments can run concurrently,
    any given app is only updated by one deployment at a time.
    """

    _instance: "AppSemaphoreManager | None" = None

    def __init__(self) -> None:
        self._app_semaphores: dict[str, asyncio.Semaphore] = {}
        self._semaphore_lock = asyncio.Lock()
        self._initialized: bool = True

    async def get_app_semaphore(self, app_name: str) -> asyncio.Semaphore:
        """Get the semaphore for an app.

        If the semaphore does not exist, create it.
        """
        async with self._semaphore_lock:
            if app_name not in self._app_semaphores:
                logger.debug(f"Creating new semaphore for app: {app_name}")
                self._app_semaphores[app_name] = asyncio.Semaphore(1)
            semaphore = self._app_semaphores[app_name]
        return semaphore

    @asynccontextmanager
    async def app_semaphore(self, app_name: str) -> AsyncGenerator[None, None]:
        """Async context manager to acquire and release a semaphore for the given app.

        Each app gets exactly one semaphore with a limit of 1,
        ensuring sequential updates per app.
        """
        semaphore = await self.get_app_semaphore(app_name)
        async with semaphore:
            yield

    def get_locked_apps(self) -> set[str]:
        """Return a set of apps that currently have active locks."""
        locked_apps = set()
        for app_name, semaphore in self._app_semaphores.items():
            if semaphore.locked():
                locked_apps.add(app_name)
        return locked_apps
