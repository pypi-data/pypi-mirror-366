import logging
import inspect
from functools import lru_cache
from typing import Optional, Dict, Any

from pydantic import validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from .app.config import create_ewoks_settings
from .app.config import create_app_settings


def configure_app(**input_args) -> Dict[str, Any]:
    """Configure the FastAPI application with default parameter
    values from (in order of priority)

    1. :code:`EWOKSAPP_*` environment variables
    2. :code:`.env.prod` file in the current working directory
    3. :code:`.env` file in the current working directory
    4. hard-coded default values
    """
    all_args = _get_env_args()

    if input_args:
        default_args = get_default_args()
        for k, v in input_args.items():
            if k in default_args and v == default_args[k]:
                # The default value should not override the environment value
                continue
            all_args[k] = v

    app_settings = set(inspect.signature(create_app_settings).parameters)
    ewoks_settings = set(inspect.signature(create_ewoks_settings).parameters)
    input_args = set(all_args) - app_settings - ewoks_settings

    app_settings = {k: all_args[k] for k in app_settings}
    ewoks_settings = {k: all_args[k] for k in ewoks_settings}
    input_args = {k: all_args[k] for k in input_args}

    level = logging.getLevelName(input_args["log_level"].upper())
    logging.basicConfig(
        level=level, format="%(levelname)8s(BACKEND %(asctime)s): %(message)s"
    )
    create_app_settings(**app_settings)
    create_ewoks_settings(**ewoks_settings)
    return input_args


@lru_cache
def _get_env_args() -> Dict[str, Any]:
    return _EnvArgs().dict()


@lru_cache
def get_default_args() -> Dict[str, Any]:
    return _DefaultArgs().dict()


class _DefaultArgs(BaseSettings):
    config: Optional[str] = None  # ewoks parameter
    dir: Optional[str] = None  # ewoks parameter
    without_events: bool = False  # ewoks parameter
    frontend_tests: bool = False  # ewoks parameter
    no_discovery_at_launch: bool = False  # ewoks parameter
    no_older_versions: bool = False  # app parameter
    log_level: Optional[str] = None  # uvicorn parameter


class _EnvArgs(_DefaultArgs):
    # env_prefix > .env.prod > .env > pydantic defaults
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_prefix="ewoksapp_",
        extra="ignore",
    )

    @validator("log_level", pre=True, always=True)
    def set_log_level(cls, log_level):
        return log_level or "info"
