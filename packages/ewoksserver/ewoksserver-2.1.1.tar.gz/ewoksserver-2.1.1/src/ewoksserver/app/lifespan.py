import os
import shutil
import logging
from pprint import pformat
from typing import Generator
from contextlib import contextmanager
from contextlib import asynccontextmanager

from fastapi import FastAPI
from ewoksjob.client.local import pool_context
from celery import current_app as current_celery_app

from ewoksserver.app.models import EwoksSchedulingType

from .backends import json_backend
from .. import resources
from . import config
from .routes.execution import socketio
from .routes.tasks.discovery import discover_tasks


logger = logging.getLogger(__name__)


@asynccontextmanager
async def fastapi_lifespan(app: FastAPI) -> Generator[None, None, None]:
    get_ewoks_settings = app.dependency_overrides.get(
        config.get_ewoks_settings, config.get_ewoks_settings
    )
    ewoks_settings = get_ewoks_settings()
    _configure_socketio(ewoks_settings)
    _copy_default_resources(ewoks_settings)
    _enable_execution_events(ewoks_settings)
    with _enable_execution(ewoks_settings):
        _rediscover_tasks(ewoks_settings)
        _print_ewoks_settings(ewoks_settings)
        yield


def _configure_socketio(app_settings: config.EwoksSettings) -> None:
    socketio.configure_socketio(app_settings)


def _copy_default_resources(ewoks_settings: config.EwoksSettings) -> None:
    """Copy the default resources (tasks, workflows and icon) from the
    python package to the resource directory."""
    for resource, resource_ext in {
        "tasks": [".json"],
        "icons": [".png", ".svg"],
        "workflows": [".json"],
    }.items():
        root_url = json_backend.root_url(ewoks_settings.resource_directory, resource)
        os.makedirs(root_url, exist_ok=True)
        for filename in os.listdir(resources.DEFAULT_ROOT / resource):
            _, ext = os.path.splitext(filename)
            if ext not in resource_ext:
                continue

            src = resources.DEFAULT_ROOT / resource / filename
            if not os.path.isfile(src):
                continue

            dest = root_url / filename
            if not os.path.exists(dest):
                shutil.copy(src, dest)


def _rediscover_tasks(ewoks_settings: config.EwoksSettings) -> None:
    if not ewoks_settings.ewoks_discovery.on_start_up:
        return
    try:
        tasks = discover_tasks(ewoks_settings)
    except Exception as ex:
        tasks = []
        logger.exception("Task discovery failed: %s", ex)
    root_url = json_backend.root_url(ewoks_settings.resource_directory, "tasks")
    for resource in tasks:
        json_backend.save_resource(root_url, resource["task_identifier"], resource)


def _enable_execution_events(ewoks_settings: config.EwoksSettings) -> None:
    """Set default ewoks event handler when nothing has been configured"""
    if ewoks_settings.configured:
        return
    if not ewoks_settings.ewoks_execution.handlers:
        ewoks_settings.ewoks_execution.handlers = [
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


@contextmanager
def _enable_execution(
    ewoks_settings: config.EwoksSettings,
) -> Generator[None, None, None]:
    """Ensure workflows can be executed"""
    config = ewoks_settings.ewoks_scheduling
    if config.type == EwoksSchedulingType.Celery:
        current_celery_app.conf.update(config.configuration)
        yield
    else:
        with pool_context():
            yield


def _print_ewoks_settings(ewoks_settings: config.EwoksSettings) -> None:
    """Print summary of all Ewoks settings"""
    resourcedir = ewoks_settings.resource_directory
    if not resourcedir:
        resourcedir = "."

    lines = ["", "", "RESOURCE DIRECTORY:", os.path.abspath(resourcedir)]

    cfg = ewoks_settings.ewoks_scheduling
    if cfg.type is EwoksSchedulingType.Local:
        lines += ["", "EWOKS JOB SCHEDULING", "Local workflow execution"]
    else:
        lines += [
            "",
            "EWOKS JOB SCHEDULING",
            f"Execution using {cfg.type} with the following config:",
            pformat(cfg.configuration),
        ]

    lines += [
        "",
        "EWOKS EXECUTION:",
        pformat(ewoks_settings.ewoks_execution.model_dump()),
    ]

    lines += [
        "",
        "EWOKS DISCOVERY:",
        pformat(ewoks_settings.ewoks_discovery.model_dump()),
    ]

    lines += [""]

    logger.info("\n".join(lines))
