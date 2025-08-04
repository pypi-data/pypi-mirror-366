import json
import pytest
from ewoksserver.app.config import create_ewoks_settings
from ewoksserver.app.models import (
    EwoksDiscoverySettings,
    EwoksExecutionSettings,
    EwoksSchedulingType,
)


_HANDLERS = [
    {
        "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
        "arguments": [
            {
                "name": "uri",
                "value": "file:ewoks_events.db",
            }
        ],
    }
]


def write_config(filename, **fields):
    with open(filename, "w") as _file:
        for k, v in fields.items():
            _file.write(f"{k} = {json.dumps(v) if isinstance(v, str) else str(v)}\n")


def test_ewoks_execution_no_discovery(tmpdir):
    filename = tmpdir / "config.py"
    write_config(
        filename,
        RESOURCE_DIRECTORY=str(tmpdir),
        EWOKS_EXECUTION={"handlers": _HANDLERS},
    )

    settings = create_ewoks_settings(filename)

    assert settings.resource_directory == tmpdir
    assert settings.ewoks_execution.handlers == _HANDLERS
    assert settings.ewoks_discovery == EwoksDiscoverySettings()


def test_ewoks_execution_and_discovery(tmpdir):
    filename = tmpdir / "config.py"
    write_config(
        filename,
        RESOURCE_DIRECTORY=str(tmpdir),
        EWOKS_EXECUTION={"handlers": _HANDLERS},
        EWOKS_DISCOVERY={"on_start_up": True, "timeout": 100},
    )

    settings = create_ewoks_settings(filename)

    assert settings.resource_directory == tmpdir
    assert settings.ewoks_execution.handlers == _HANDLERS
    assert settings.ewoks_discovery.on_start_up is True
    assert settings.ewoks_discovery.timeout == 100


def test_deprecated_ewoks_field(tmpdir):
    filename = tmpdir / "config.py"
    write_config(
        filename,
        RESOURCE_DIRECTORY=str(tmpdir),
        EWOKS={"handlers": _HANDLERS},
    )

    with pytest.deprecated_call():
        settings = create_ewoks_settings(filename)

    assert settings.resource_directory == tmpdir
    assert settings.ewoks_execution.handlers == _HANDLERS
    assert settings.ewoks_discovery == EwoksDiscoverySettings()


def test_ignore_deprecated_ewoks_field(tmpdir):
    filename = tmpdir / "config.py"
    write_config(
        filename,
        RESOURCE_DIRECTORY=str(tmpdir),
        EWOKS_EXECUTION={"handlers": []},
        EWOKS={"handlers": _HANDLERS},
    )

    settings = create_ewoks_settings(filename)

    assert settings.resource_directory == tmpdir
    assert settings.ewoks_execution.handlers == []
    assert settings.ewoks_discovery == EwoksDiscoverySettings()


def test_deprecated_timeout_field(tmpdir):
    filename = tmpdir / "config.py"
    write_config(filename, RESOURCE_DIRECTORY=str(tmpdir), DISCOVER_TIMEOUT=100)

    with pytest.deprecated_call():
        settings = create_ewoks_settings(filename)

    assert settings.resource_directory == tmpdir
    assert settings.ewoks_execution == EwoksExecutionSettings()
    assert settings.ewoks_discovery.timeout == 100


def test_ignore_deprecated_timeout_field(tmpdir):
    filename = tmpdir / "config.py"
    write_config(
        filename,
        RESOURCE_DIRECTORY=str(tmpdir),
        EWOKS_DISCOVERY={"timeout": 50},
        DISCOVER_TIMEOUT=100,
    )

    settings = create_ewoks_settings(filename)

    assert settings.resource_directory == tmpdir
    assert settings.ewoks_execution == EwoksExecutionSettings()
    assert settings.ewoks_discovery.timeout == 50


def test_ewoks_local_scheduling(tmpdir):
    filename = tmpdir / "config.py"
    write_config(filename)

    settings = create_ewoks_settings(filename)

    assert settings.ewoks_scheduling.type == EwoksSchedulingType.Local
    assert settings.ewoks_scheduling.configuration == {}


def test_ewoks_celery_scheduling(tmpdir):
    filename = tmpdir / "config.py"
    celery_config = {
        "broker_url": "redis://localhost:25001/2",
        "result_backend": "redis://localhost:25001/3",
    }
    write_config(filename, CELERY=celery_config)

    settings = create_ewoks_settings(filename)

    assert settings.ewoks_scheduling.type == EwoksSchedulingType.Celery
    assert settings.ewoks_scheduling.configuration == celery_config
