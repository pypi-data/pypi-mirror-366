from dataclasses import dataclass
from typing import Dict, Mapping, Tuple, List, Set, Union, Callable

from fastapi import APIRouter
from fastapi import FastAPI
from starlette.types import ASGIApp

from . import BACKEND_PREFIX

AppGenerator = Callable[[], ASGIApp]
RouterType = Union[APIRouter, AppGenerator]
VersionTuple = Tuple[int, int, int]


@dataclass
class Route:
    router: RouterType
    prefix: str
    tag: str
    versioned: bool


def get_routes(
    tag: str, routers: Dict[VersionTuple, RouterType], suffix: str = ""
) -> Dict[Tuple[int], Route]:
    """Generate routes with versioned paths for all strict and major versions.
    In addition add a route with non-versioned path for the latest version."""
    routes = dict()

    major_routes = dict()
    major_versions = dict()
    for full_version, router in reversed(sorted(routers.items())):
        assert len(full_version) == 3, full_version
        major, minor, patch = full_version
        route_key = major, minor, patch, 0
        path_version = "v" + "_".join(map(str, full_version))
        route_tag = "v" + ".".join(map(str, full_version))
        if suffix:
            prefix = f"{BACKEND_PREFIX}/{path_version}/{suffix}"
        else:
            prefix = f"{BACKEND_PREFIX}/{path_version}"
        routes[route_key] = Route(
            router=router, prefix=prefix, tag=route_tag, versioned=True
        )
        if full_version > major_versions.get(major, (0, 0, 0)):
            major_versions[major] = full_version
            major_routes[major] = router

    for major, router in major_routes.items():
        path_version = route_tag = f"v{major}"
        full_version = major_versions[major]
        _, minor, patch = full_version
        route_key = major, minor, patch, 1
        if suffix:
            prefix = f"{BACKEND_PREFIX}/{path_version}/{suffix}"
        else:
            prefix = f"{BACKEND_PREFIX}/{path_version}"
        routes[route_key] = Route(
            router=router, prefix=prefix, tag=route_tag, versioned=True
        )

    last_major_version = sorted(major_routes)[-1]
    router = major_routes[last_major_version]
    major, minor, patch = major_versions[last_major_version]
    route_key = major, minor, patch, 2
    if suffix:
        prefix = f"{BACKEND_PREFIX}/{suffix}"
    else:
        prefix = f"{BACKEND_PREFIX}"
    routes[route_key] = Route(router=router, prefix=prefix, tag=tag, versioned=False)
    return routes


def assert_route_versions(*all_routes: Mapping[VersionTuple, RouterType]) -> None:
    versions = {tuple(sorted(routes)) for routes in all_routes}
    assert len(versions) == 1, "Not all routes have the same versions"


def extract_version_tags(all_routes: List[Dict[VersionTuple, Route]]) -> Set[str]:
    """Extract all version tags"""
    tags = set()
    for routes in all_routes:
        for route in routes.values():
            if route.versioned:
                tags.add(route.tag)
    return tags


def extract_latest_version(all_routes: List[Dict[VersionTuple, Route]]) -> VersionTuple:
    """Extract the latest version"""
    return max(sorted(routes)[-1][:3] for routes in all_routes)


def add_routes(
    app: FastAPI,
    all_routes: List[Dict[VersionTuple, Route]],
    no_older_versions: bool = False,
) -> None:
    """Add routes to a fastapi app"""
    route_keys = set()
    for keys in all_routes:
        route_keys |= set(keys)

    for route_key in reversed(sorted(route_keys)):
        for routes in all_routes:
            route = routes.get(route_key)
            if route is None:
                continue
            if no_older_versions and route.versioned:
                continue
            if isinstance(route.router, APIRouter):
                app.include_router(
                    route.router,
                    prefix=route.prefix,
                    tags=[route.tag],
                )
            elif isinstance(route.router, Callable):
                subapp = route.router()
                app.mount(route.prefix, subapp)
            else:
                raise TypeError(str(type(route)))
