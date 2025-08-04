from typing import Any, Dict, Optional, Mapping
from fastapi.responses import JSONResponse
from fastapi import status

from ewoksjob.client import submit
from ewoksjob.client.local import submit as submit_local

from ...models import EwoksSchedulingType
from ...config import EwoksSettingsType


class WorkflowNotReadableResponse(JSONResponse):
    def __init__(self, identifier: str):
        super().__init__(
            {
                "message": f"No permission to read workflow '{identifier}'.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )


class WorkflowNotFoundResponse(JSONResponse):
    def __init__(self, identifier: str):
        super().__init__(
            {
                "message": f"Workflow '{identifier}' is not found.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )


def submit_workflow(
    workflow,
    client_execute_arguments: Optional[Dict[str, Any]],
    client_submit_arguments: Optional[Dict[str, Any]],
    graph_execute_arguments: Optional[Dict[str, Any]],
    graph_submit_arguments: Optional[Dict[str, Any]],
    settings: EwoksSettingsType,
):
    execute_kwargs = _merge_execute_arguments(
        client_execute_arguments, graph_execute_arguments, settings
    )
    submit_kwargs = _merge_submit_arguments(
        client_submit_arguments, graph_submit_arguments
    )

    # Workflow execution: position arguments
    submit_kwargs["args"] = (workflow,)
    # Workflow execution: named arguments
    submit_kwargs["kwargs"] = execute_kwargs

    if settings.ewoks_scheduling.type == EwoksSchedulingType.Local:
        return submit_local(**submit_kwargs)
    else:
        return submit(**submit_kwargs)


def _merge_execute_arguments(
    client_execute_arguments: Optional[Dict[str, Any]],
    graph_execute_arguments: Optional[Dict[str, Any]],
    settings: EwoksSettingsType,
) -> Dict[str, Any]:
    """Client arguments have precedence over graph arguments in case merging does not apply.
    Server configuration arguments can always be merged.
    """
    if client_execute_arguments is None:
        client_execute_arguments = dict()
    if graph_execute_arguments is None:
        graph_execute_arguments = dict()

    # Handler from the client
    execinfo = client_execute_arguments.get("execinfo", dict())
    handlers = execinfo.pop("handlers", list())

    # Handler from the graph
    execinfo = graph_execute_arguments.get("execinfo", dict())
    extra_handlers = execinfo.pop("handlers", list())

    # Handler from the server configuration
    extra_handlers += settings.ewoks_execution.handlers

    for handler in extra_handlers:
        if handler not in handlers:
            handlers.append(handler)

    if handlers:
        execinfo = client_execute_arguments.setdefault("execinfo", dict())
        execinfo["handlers"] = handlers

    return _merge_mappings(graph_execute_arguments, client_execute_arguments)


def _merge_submit_arguments(
    client_submit_arguments: Optional[Dict[str, Any]],
    graph_submit_arguments: Optional[Dict[str, Any]],
):
    """Client arguments have precedence over graph arguments in case merging does not apply."""
    if client_submit_arguments is None:
        client_submit_arguments = dict()
    if graph_submit_arguments is None:
        graph_submit_arguments = dict()
    return _merge_mappings(graph_submit_arguments, client_submit_arguments)


def _merge_mappings(d1: Optional[Mapping], d2: Optional[Mapping]) -> dict:
    """`d2` has precedence over `d1` in case merging does not apply.
    Merging is done like `{**d1, **d2}` but then recursive.
    """
    if d1 is None:
        merged = dict()
    else:
        merged = dict(d1)
    if not d2:
        return merged
    for key, value2 in d2.items():
        value1 = merged.get(key)
        if isinstance(value1, Mapping) and isinstance(value2, Mapping):
            value2 = _merge_mappings(value1, value2)
        merged[key] = value2
    return merged
