"""Start ewoks server from the command line with the ewoks-server CLI

..code: bash

    ewoks-server --reload
"""

import sys
from typing import Optional, List

import click
from uvicorn.main import main as uvicorn_main

from .config import configure_app
from .config import get_default_args


uvicorn_main = click.option(
    "--config",
    type=str,
    default=get_default_args()["config"],
    help="Path to the config python script (equivalent to the environment variable 'EWOKSSERVER_SETTINGS')",
)(uvicorn_main)

uvicorn_main = click.option(
    "--dir",
    type=str,
    default=get_default_args()["dir"],
    help="Root directory for resources (e.g. workflows, tasks, icons descriptions)",
)(uvicorn_main)

uvicorn_main = click.option(
    "--without-events",
    is_flag=True,
    default=get_default_args()["without_events"],
    help="Disable Socket.IO app for event stream",
)(uvicorn_main)

uvicorn_main = click.option(
    "--frontend-tests",
    is_flag=True,
    default=get_default_args()["frontend_tests"],
    help="Load frontend test configuration",
)(uvicorn_main)

uvicorn_main = click.option(
    "--no-discovery-at-launch",
    is_flag=True,
    default=get_default_args()["no_discovery_at_launch"],
    help="Do not rediscover tasks when launching the server",
)(uvicorn_main)

uvicorn_main = click.option(
    "--no-older-versions",
    is_flag=True,
    default=get_default_args()["no_older_versions"],
    help="Do not provide end-points for older versions of the Ewoks API",
)(uvicorn_main)


def _ewoks_main(**cli_args):
    return _original_callback(**configure_app(**cli_args))


_original_callback = uvicorn_main.callback
uvicorn_main.callback = _ewoks_main


def main(argv: Optional[List[str]] = None) -> None:
    """Exposes the uvicorn CLI with a default APP factory"""
    if argv is None:
        argv = sys.argv[1:]
    if "--factory" not in argv:
        argv += ["--factory", "ewoksserver.app:create_app"]
    uvicorn_main(argv)


if __name__ == "__main__":
    sys.exit(main())
