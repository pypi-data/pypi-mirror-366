from __future__ import annotations
import os
import sys
import importlib.util
import logging
from typing_extensions import Annotated
from typing import Optional
import warnings

from fastapi import Depends


from .models import AppSettings, EwoksSettings

try:
    from ewoksweb.serverutils import get_test_config
except ImportError:
    get_test_config = None

logger = logging.getLogger(__name__)

_APP_SETTINGS = None

_EWOKS_SETTINGS = None


def _resolve_ewoks_execution_settings(
    ewoks_execution: dict | None, ewoks: dict | None
) -> dict:
    if ewoks is None:
        return ewoks_execution if ewoks_execution else dict()

    if ewoks_execution is None:
        warnings.warn(
            "EWOKS configuration field has been renamed EWOKS_EXECUTION",
            DeprecationWarning,
        )
        return ewoks

    logger.warning(
        "Both EWOKS_EXECUTION and EWOKS fields were specified but EWOKS field is deprecated. EWOKS field will be ignored."
    )
    return ewoks_execution


def _resolve_ewoks_discovery_settings(
    ewoks_discovery: dict | None, discover_timeout: float | None
) -> dict:

    if discover_timeout is None:
        return ewoks_discovery if ewoks_discovery else dict()

    if ewoks_discovery is None:
        warnings.warn(
            "DISCOVER_TIMEOUT is deprecated. The timeout should be specified via the `timeout` field of EWOKS_DISCOVERY",
            DeprecationWarning,
        )
        return {"timeout": discover_timeout}

    logger.warning(
        "Both EWOKS_DISCOVERY and DISCOVER_TIMEOUT fields were specified but DISCOVER_TIMEOUT field is deprecated. DISCOVER_TIMEOUT field will be ignored."
    )
    return ewoks_discovery


def _resolve_ewoks_scheduling_settings(celery: dict | None) -> dict:
    if celery is None:
        return {"type": "local"}

    return {"type": "celery", "configuration": celery}


def create_ewoks_settings(
    config: Optional[str] = None,
    dir: Optional[str] = None,
    without_events: bool = False,
    frontend_tests: bool = False,
    no_discovery_at_launch: bool = False,
) -> EwoksSettings:
    global _EWOKS_SETTINGS

    # Get configuration file
    filename = os.environ.get("EWOKSSERVER_SETTINGS")
    if config:
        filename = config
    if frontend_tests:
        if get_test_config is None:
            raise RuntimeError("ewoksweb is not installed")
        filename = get_test_config()

    # Extract settings from configuration file
    resource_directory = None
    ewoks = None
    ewoks_execution = None
    ewoks_discovery = None
    celery = None
    discover_timeout = None
    if filename:
        spec = importlib.util.spec_from_file_location("ewoksserverconfig", filename)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ewoksserverconfig"] = mod
        spec.loader.exec_module(mod)
        resource_directory = getattr(mod, "RESOURCE_DIRECTORY", resource_directory)
        celery = getattr(mod, "CELERY", celery)
        ewoks_execution = getattr(mod, "EWOKS_EXECUTION", None)
        ewoks_discovery = getattr(mod, "EWOKS_DISCOVERY", None)
        # DEPRECATED
        ewoks = getattr(mod, "EWOKS", ewoks)
        discover_timeout = getattr(mod, "DISCOVER_TIMEOUT", discover_timeout)

    # Overwrite resource directory
    if dir:
        resource_directory = dir
    if not resource_directory:
        resource_directory = "."

    ewoks_discovery = _resolve_ewoks_discovery_settings(
        ewoks_discovery, discover_timeout
    )
    ewoks_execution = _resolve_ewoks_execution_settings(ewoks_execution, ewoks)
    ewoks_scheduling = _resolve_ewoks_scheduling_settings(celery)

    # Overwrite on_start_up if asked
    if no_discovery_at_launch:
        ewoks_discovery["on_start_up"] = False

    configured = bool(filename) or bool(dir)

    _EWOKS_SETTINGS = EwoksSettings(
        configured=configured,
        resource_directory=resource_directory,
        without_events=without_events,
        ewoks_execution=ewoks_execution,
        ewoks_discovery=ewoks_discovery,
        ewoks_scheduling=ewoks_scheduling,
    )
    return _EWOKS_SETTINGS


def create_app_settings(no_older_versions: bool = False) -> AppSettings:
    global _APP_SETTINGS
    _APP_SETTINGS = AppSettings(no_older_versions=no_older_versions)
    return _APP_SETTINGS


def get_ewoks_settings():
    if _EWOKS_SETTINGS is not None:
        return _EWOKS_SETTINGS
    return create_ewoks_settings()


def get_app_settings():
    if _APP_SETTINGS is not None:
        return _APP_SETTINGS
    return create_app_settings()


EwoksSettingsType = Annotated[EwoksSettings, Depends(get_ewoks_settings)]
