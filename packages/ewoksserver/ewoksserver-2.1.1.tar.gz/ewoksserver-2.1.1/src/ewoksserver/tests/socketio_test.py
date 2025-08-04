import asyncio
from typing import List, Any, Dict

from ..app.routes.execution import socketio


class SocketIOTestClient:
    def __init__(self):
        self._manager = socketio._MANAGER
        self._events = list()
        self._org_emit = self._manager._emit

    def __enter__(self) -> "SocketIOTestClient":
        self._manager._emit = self._emit
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()
        self._manager._emit = self._org_emit

    def connect(self) -> None:
        return _run_coroutine(self._manager.connect(None, None, None))

    def disconnect(self) -> None:
        return _run_coroutine(self._manager.disconnect(None))

    def get_events(self) -> List[Dict]:
        events = self._events
        self._events = self._events[len(events) :]
        return events

    def is_running(self) -> bool:
        return _run_coroutine(self._manager.is_running())

    def _emit(self, loop, event) -> None:
        self._events.append(event)


def _run_coroutine(coroutine) -> Any:
    try:
        loop = asyncio.get_event_loop()
    except (DeprecationWarning, RuntimeError):
        loop = asyncio.new_event_loop()
        asyncio.get_event_loop_policy().set_event_loop(loop)
    return loop.run_until_complete(coroutine)
