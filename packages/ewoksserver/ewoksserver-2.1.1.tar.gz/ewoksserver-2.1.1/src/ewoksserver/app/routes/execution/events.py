import logging
from contextlib import contextmanager
from typing import Generator, Optional

from ewoksjob.events.readers import EwoksEventReader
from ewoksjob.events.readers import instantiate_reader

from ...config import EwoksSettingsType

logger = logging.getLogger(__name__)


@contextmanager
def reader_context(
    ewoks_settings: EwoksSettingsType,
) -> Generator[Optional[EwoksEventReader], None, None]:
    r = _reader(ewoks_settings)
    try:
        yield r
    finally:
        if r is not None:
            r.close()


def _reader(ewoks_settings: EwoksSettingsType) -> Optional[EwoksEventReader]:
    handlers = ewoks_settings.ewoks_execution.handlers
    argmap = {"uri": "url"}
    for name in ("Redis", "Sqlite3", None):
        for handler in handlers:
            if name is None or name in handler["class"]:
                arguments = handler.get("arguments", list())
                arguments = {
                    argmap.get(arg["name"], arg["name"]): arg["value"]
                    for arg in arguments
                }
                return instantiate_reader(**arguments)

    logger.warning("Configure ewoks event handlers")
    return None
