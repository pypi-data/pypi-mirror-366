from functools import wraps
from typing import Optional, Tuple

import pytest

from ..app import routes

_API_VERSIONS = {
    (): (2, 0, 0),
    (2,): (2, 0, 0),
    (2, 0, 0): (2, 0, 0),
    (1,): (1, 1, 0),
    (1, 1, 0): (1, 1, 0),
    (1, 0, 0): (1, 0, 0),
}
# Maps route version to the effective route version used


@pytest.fixture
def min_api_version(request) -> Optional[str]:
    try:
        return request.param
    except AttributeError:
        return None


@pytest.fixture
def max_api_version(request) -> Optional[str]:
    try:
        return request.param
    except AttributeError:
        return None


def _get_api_root(route_version: Tuple[int]) -> str:
    if not route_version:
        return routes.BACKEND_PREFIX
    version_suffix = "_".join(list(map(str, route_version)))
    return f"{routes.BACKEND_PREFIX}/v{version_suffix}"


@pytest.fixture(
    params=list(_API_VERSIONS.items()),
    ids=[_get_api_root(route_version) for route_version in _API_VERSIONS],
)
def api_root(
    request, min_api_version: Optional[str], max_api_version: Optional[str]
) -> str:
    route_version, version_tuple = request.param
    api_root = _get_api_root(route_version)

    if min_api_version:
        min_api_version_tuple = tuple(map(int, min_api_version.split(".")))
        assert (
            len(min_api_version_tuple) == 3
        ), "min_api_version must be of the form 'x.y.z'"
    if max_api_version:
        max_api_version_tuple = tuple(map(int, max_api_version.split(".")))
        assert (
            len(max_api_version_tuple) == 3
        ), "max_api_version must be of the form 'x.y.z'"

    if min_api_version and version_tuple < min_api_version_tuple:
        pytest.skip(f"requires API >= {min_api_version}")
    if max_api_version and version_tuple > max_api_version_tuple:
        pytest.skip(f"requires API <= {max_api_version}")

    return api_root


def api_version_bounds(
    min_version: Optional[str] = None, max_version: Optional[str] = None
):
    def decorator(func):
        parametrize_decorators = []

        if min_version:
            parametrize_decorators.append(
                pytest.mark.parametrize(
                    "min_api_version", [min_version], indirect=True, ids=[""]
                )
            )

        if max_version:
            parametrize_decorators.append(
                pytest.mark.parametrize(
                    "max_api_version", [max_version], indirect=True, ids=[""]
                )
            )

        for decorator in reversed(parametrize_decorators):
            func = decorator(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
