import logging
import asyncio
import threading
from datetime import datetime
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import socketio
from socketio.exceptions import ConnectionRefusedError

from . import events
from ...config import EwoksSettings

logger = logging.getLogger(__name__)


class EwoksEventManager:
    """Asynchronous manager of a Socket.IO application."""

    def __init__(self) -> None:
        # Disable Socket.IO CORS since it is managed by the CORS middleware
        # https://github.com/encode/starlette/issues/1309#issuecomment-953930195
        self._sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
        self._app = socketio.ASGIApp(self._sio, socketio_path="")

        self._sio.on("connect")(self.connect)
        self._sio.on("disconnect")(self.disconnect)

        self._ewoks_settings = None
        self._stop_event = threading.Event()
        self._fetch_events_future: Optional[asyncio.Future] = None
        self._counter = 0
        self._executor = ThreadPoolExecutor(max_workers=1)

    def configure(self, ewoks_settings: EwoksSettings) -> None:
        self._ewoks_settings = ewoks_settings

    async def connect(self, *_) -> None:
        if self._ewoks_settings.without_events:
            raise ConnectionRefusedError("Socket.IO has been disabled")
        self._counter += 1
        await self._start()

    async def disconnect(self, *_) -> None:
        if self._ewoks_settings.without_events:
            return
        self._counter = max(self._counter - 1, 0)
        if self._counter == 0:
            await self._stop(timeout=3)

    async def is_running(self) -> bool:
        return await self._is_running(self._fetch_events_future)

    @staticmethod
    async def _is_running(future: Optional[asyncio.Future] = None) -> bool:
        return future is not None and not future.done()

    async def _start(self) -> None:
        if await self.is_running():
            return

        self._stop_event.clear()
        loop = asyncio.get_running_loop()
        self._fetch_events_future = loop.run_in_executor(
            self._executor, self._fetch_events_main, loop
        )

    async def _stop(self, timeout: Optional[float] = None) -> None:
        future = self._fetch_events_future
        if not await self._is_running(future):
            return
        self._stop_event.set()
        await asyncio.wait_for(future, timeout=timeout)

    def _fetch_events_main(self, loop) -> None:
        try:
            with events.reader_context(self._ewoks_settings) as reader:
                if reader is None:
                    raise RuntimeError("Ewoks event handlers not configured")
                starttime = datetime.now().astimezone()
                for event in reader.wait_events(
                    starttime=starttime, stop_event=self._stop_event
                ):
                    if self._stop_event.is_set():
                        break
                    self._emit(loop, event)
        except Exception as e:
            # TODO: client needs to receive an error
            logger.exception(str(e))
            raise
        finally:
            self._fetch_events_future = None

    def _emit(self, loop, event) -> None:
        coroutine = self._sio.emit("Executing", event)
        future = asyncio.run_coroutine_threadsafe(coroutine, loop)
        future.result()


def create_socketio_app() -> socketio.ASGIApp:
    """Create the ASGI Socket.IO application when needed"""
    global _MANAGER
    if _MANAGER is not None:
        return _MANAGER._app

    _MANAGER = EwoksEventManager()
    return _MANAGER._app


def configure_socketio(ewoks_settings: EwoksSettings) -> None:
    _MANAGER.configure(ewoks_settings)


_MANAGER = None
