import base64
import mimetypes
from urllib import request
import logging
from pathlib import Path
from typing import Iterator, Union


ResourceIdentifierType = str
ResourceUrlType = Path
ResourceContentType = dict

_logger = logging.getLogger(__name__)


def root_url(root_url: Union[str, Path, None], category: str) -> ResourceUrlType:
    if not root_url:
        root_url = Path(".")
    elif isinstance(root_url, str):
        root_url = Path(root_url)
    return root_url / category


def resource_identifiers(root: ResourceUrlType) -> Iterator[ResourceIdentifierType]:
    for url in _resource_urls(root):
        yield _url_to_identifier(url)


def resources(root: ResourceUrlType) -> Iterator[ResourceContentType]:
    for url in _resource_urls(root):
        yield _load_url(url)


def resource_exists(root: ResourceUrlType, identifier: ResourceIdentifierType) -> bool:
    return _identifier_to_url(root, identifier).exists()


def _resource_urls(root: ResourceUrlType) -> Iterator[ResourceUrlType]:
    for url in root.iterdir():
        if _is_resource(url):
            yield url


def _is_resource(url: ResourceUrlType) -> bool:
    return (
        url.is_file() and not url.name.startswith(".") and not url.name.endswith(".py")
    )


def save_resource(
    root: ResourceUrlType,
    identifier: ResourceIdentifierType,
    resource: ResourceContentType,
):
    url = _identifier_to_url(root, identifier)
    _save_url(url, resource)


def load_resource(
    root: ResourceUrlType, identifier: ResourceIdentifierType
) -> ResourceContentType:
    url = _identifier_to_url(root, identifier)
    return _load_url(url)


def delete_resource(root: ResourceUrlType, identifier: ResourceIdentifierType) -> None:
    url = _identifier_to_url(root, identifier)
    _delete_url(url)


def _delete_url(url: ResourceUrlType) -> ResourceContentType:
    _logger.debug("Delete file '%s'", url)
    url.unlink()


def _identifier_to_url(root: ResourceUrlType, identifier: ResourceIdentifierType):
    return root / identifier


def _url_to_identifier(url: ResourceUrlType) -> ResourceIdentifierType:
    return url.name


def _load_url(url: ResourceUrlType) -> ResourceContentType:
    mimetype, encoding = mimetypes.guess_type(url, strict=True)
    if mimetype is None:
        raise ValueError(f"Cannot derive mime type from '{url}'")

    try:
        with open(url, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        _logger.error(f"'{url}' not found")
        raise

    if not encoding:
        encoding = "base64"
        data = base64.b64encode(data).decode()

    return {"data_url": f"data:{mimetype};{encoding},{data}"}


def _save_url(url: ResourceUrlType, resource: ResourceContentType) -> None:
    _logger.debug("Save file '%s'", url)
    url.parent.mkdir(parents=True, exist_ok=True)
    with request.urlopen(resource["data_url"]) as f:
        data = f.read()
    with open(url, "wb") as f:
        f.write(data)
