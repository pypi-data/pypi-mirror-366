import time
from pathlib import Path
from typing import List
from functools import lru_cache
from collections import namedtuple

import pytest
from fastapi.testclient import TestClient

from ewokscore import events
from ewoksjob.tests.conftest import celery_config  # noqa F401
from ewoksjob.tests.conftest import celery_includes  # noqa F401

from .. import app as newserver
from ..app import config as serverconfig
from ..app.backends.binary_backend import _load_url
from ..app.models import (
    EwoksDiscoverySettings,
    EwoksExecutionSettings,
    EwoksJobSettings,
    EwoksSchedulingType,
)
from ..resources import DEFAULT_ROOT
from .socketio_test import SocketIOTestClient

from .api_versions import api_root  # noqa F401
from .api_versions import min_api_version  # noqa F401
from .api_versions import max_api_version  # noqa F401
from .data import resource_filenames


@pytest.fixture
def rest_client(tmpdir):
    """Client to the REST server (no execution)."""
    app = newserver.create_app()

    @lru_cache()
    def get_ewoks_settings_for_tests():
        return serverconfig.EwoksSettings(
            configured=True,
            resource_directory=str(tmpdir),
            # Disable discovery since this client is used to test manual discovery
            ewoks_discovery=EwoksDiscoverySettings(on_start_up=False),
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = (
        get_ewoks_settings_for_tests
    )

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def ewoks_handlers(tmpdir):
    uri = f"file:{tmpdir / 'ewoks_events.db'}"
    yield [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    events.cleanup()


@pytest.fixture
def local_exec_client(tmpdir, ewoks_handlers):
    """Client to the REST server and Socket.IO (execution with process pool)."""
    app = newserver.create_app()

    def get_settings_override():
        return serverconfig.EwoksSettings(
            configured=True,
            resource_directory=str(tmpdir),
            ewoks_execution=EwoksExecutionSettings(handlers=ewoks_handlers),
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = get_settings_override

    with TestClient(app) as client:
        with SocketIOTestClient() as sclient:
            yield client, sclient


@pytest.fixture
def celery_session_registered_worker(celery_session_worker):
    # Some server end-points submit a celery task to all queues.
    # If there are no queue's registered yet, nothing is submitted.
    timeout_seconds = 10
    start_time = time.time()
    while not celery_session_worker.app.control.inspect().active_queues():
        if time.time() - start_time > timeout_seconds:
            pytest.fail(
                f"Celery worker queues were not registered within {timeout_seconds} seconds."
            )
        time.sleep(0.1)


@pytest.fixture
def celery_exec_client(tmpdir, celery_session_registered_worker, ewoks_handlers):
    """Client to the REST server and Socket.IO (execution with celery)."""
    app = newserver.create_app()

    def get_settings_override():
        return serverconfig.EwoksSettings(
            configured=True,
            resource_directory=str(tmpdir),
            ewoks_scheduling=EwoksJobSettings(
                type=EwoksSchedulingType.Celery, configuration=dict()
            ),
            ewoks_execution=EwoksExecutionSettings(handlers=ewoks_handlers),
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = get_settings_override

    with TestClient(app) as client:
        with SocketIOTestClient() as sclient:
            yield client, sclient


@pytest.fixture
def celery_discover_timeout_client(
    tmpdir, celery_session_registered_worker, ewoks_handlers
):
    """Client to the REST server and Socket.IO (with a very small timeout for discovery)"""
    app = newserver.create_app()

    def get_settings_override():
        return serverconfig.EwoksSettings(
            configured=True,
            resource_directory=str(tmpdir),
            ewoks_scheduling=EwoksJobSettings(
                type=EwoksSchedulingType.Celery, configuration=dict()
            ),
            ewoks_execution=EwoksExecutionSettings(handlers=ewoks_handlers),
            # Disable discovery since this client is used to test manual discovery timeout
            ewoks_discovery=EwoksDiscoverySettings(on_start_up=False, timeout=0.1),
        )

    app.dependency_overrides[serverconfig.get_ewoks_settings] = get_settings_override

    with TestClient(app) as client:
        with SocketIOTestClient() as sclient:
            yield client, sclient


@pytest.fixture
def png_icons():
    filenames = resource_filenames()
    return [_load_url(filename) for filename in filenames if filename.endswith(".png")]


@pytest.fixture
def svg_icons():
    filenames = resource_filenames()
    return [_load_url(filename) for filename in filenames if filename.endswith(".svg")]


@pytest.fixture(scope="session")
def default_icon_identifiers() -> List[Path]:
    return [
        url.name
        for url in (DEFAULT_ROOT / "icons").iterdir()
        if not url.name.startswith("__")
    ]


@pytest.fixture(scope="session")
def default_workflow_identifiers() -> List[Path]:
    return [
        url.stem
        for url in (DEFAULT_ROOT / "workflows").iterdir()
        if url.suffix == ".json"
    ]


@pytest.fixture(scope="session")
def default_task_identifiers() -> List[Path]:
    return [
        url.stem for url in (DEFAULT_ROOT / "tasks").iterdir() if url.suffix == ".json"
    ]


@pytest.fixture
def mocked_local_submit(mocker) -> dict:
    submit_local_mock = mocker.patch(
        "ewoksserver.app.routes.execution.utils.submit_local"
    )

    MockFuture = namedtuple("Future", ["uuid"])

    arguments = dict()
    uuid = 0

    def mocked_submit(*args, **kwargs):
        nonlocal uuid
        arguments["args"] = args
        arguments["kwargs"] = kwargs
        uuid += 1
        return MockFuture(uuid=uuid)

    submit_local_mock.side_effect = mocked_submit
    return arguments
