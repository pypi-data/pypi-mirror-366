from typing import Dict, List, Mapping, Union, Optional
from collections import OrderedDict
from typing_extensions import Annotated

from fastapi import APIRouter
from fastapi import Body
from fastapi import Path
from fastapi import Depends
from fastapi import status
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from ewoksutils import event_utils
from ewoksjob.client import get_queues


from ...backends import json_backend
from ...config import EwoksSettingsType
from ..common import models as common_models
from ...models import EwoksSchedulingType
from . import models
from . import events
from .utils import (
    WorkflowNotFoundResponse,
    WorkflowNotReadableResponse,
    submit_workflow,
)


v1_0_0_router = APIRouter()
v1_1_0_router = APIRouter()
v2_0_0_router = APIRouter()


@v1_0_0_router.post(
    "/execute/{identifier}",
    summary="Execute workflow",
    response_model=models.EwoksJobInfo,
    response_description="Workflow execution job description",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to read workflow",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def execute_workflow_v1(
    settings: EwoksSettingsType,
    identifier: Annotated[
        str,
        Path(
            title="Workflow identifier",
            description="Unique identifier in the workflow database",
        ),
    ],
    options: Annotated[
        Optional[models.EwoksExecuteOptions_v1], Body(title="Ewoks execute options")
    ] = None,
) -> Union[Mapping[str, Union[int, str, None]], JSONResponse]:
    try:
        graph = json_backend.load_resource(
            settings.resource_directory / "workflows", identifier
        )
    except PermissionError:
        return WorkflowNotReadableResponse(identifier)
    except FileNotFoundError:
        return WorkflowNotFoundResponse(identifier)

    if options is None:
        client_execute_arguments = None
        client_submit_arguments = None
    else:
        client_execute_arguments = options.execute_arguments
        client_submit_arguments = options.worker_options

    graph_execute_arguments = graph["graph"].get("execute_arguments")
    graph_submit_arguments = graph["graph"].get("worker_options")

    future = submit_workflow(
        graph,
        client_execute_arguments,
        client_submit_arguments,
        graph_execute_arguments,
        graph_submit_arguments,
        settings,
    )
    return {"job_id": future.uuid}


@v1_0_0_router.get(
    "/execution/events",
    summary="Get workflow events",
    response_model=models.EwoksEventList_v1,
    response_description="Workflow execution jobs grouped per job ID",
    status_code=200,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Server not configured for ewoks events",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def execute_events_v1(
    settings: EwoksSettingsType,
    filters: Annotated[
        models.EwoksEventFilter, Depends(models.EwoksEventFilter)
    ],  # pydantic model to parse query parameters
) -> Dict[str, List[List[Dict]]]:
    jobs = OrderedDict()
    with events.reader_context(settings) as reader:
        if reader is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Server not configured for ewoks events",
            )
        for event in reader.get_events(**filters.model_dump(exclude_none=True)):
            job_id = event["job_id"]
            if job_id not in jobs:
                jobs[job_id] = list()
            if "engine" in event_utils.FIELD_TYPES:
                event["binding"] = event.pop("engine")
            jobs[job_id].append(event)
    return {"jobs": list(jobs.values())}


v1_1_0_router.include_router(v1_0_0_router)


@v1_1_0_router.get(
    "/execution/workers",
    summary="Get workers",
    response_model=models.EwoksWorkerList,
    response_description="List of available workers",
    status_code=200,
)
def workers(settings: EwoksSettingsType) -> Dict[str, Optional[List[str]]]:
    if settings.ewoks_scheduling.type == EwoksSchedulingType.Local:
        return {"workers": None}

    return {"workers": get_queues()}


@v2_0_0_router.post(
    "/execute/{identifier}",
    summary="Execute workflow",
    response_model=models.EwoksJobInfo,
    response_description="Workflow execution job description",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to read workflow",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def execute_workflow(
    settings: EwoksSettingsType,
    identifier: Annotated[
        str,
        Path(
            title="Workflow identifier",
            description="Unique identifier in the workflow database",
        ),
    ],
    options: Annotated[
        Optional[models.EwoksExecuteOptions_v2], Body(title="Ewoks execute options")
    ] = None,
) -> Union[Mapping[str, Union[int, str, None]], JSONResponse]:
    try:
        graph = json_backend.load_resource(
            settings.resource_directory / "workflows", identifier
        )
    except PermissionError:
        return WorkflowNotReadableResponse(identifier)
    except FileNotFoundError:
        return WorkflowNotFoundResponse(identifier)

    if options is None:
        client_execute_arguments = None
        client_submit_arguments = None
    else:
        client_execute_arguments = options.execute_arguments
        client_submit_arguments = options.submit_arguments

    graph_execute_arguments = graph["graph"].get("execute_arguments")
    graph_submit_arguments = graph["graph"].get("submit_arguments")

    future = submit_workflow(
        graph,
        client_execute_arguments,
        client_submit_arguments,
        graph_execute_arguments,
        graph_submit_arguments,
        settings,
    )
    return {"job_id": future.uuid}


@v2_0_0_router.get(
    "/execution/events",
    summary="Get workflow events",
    response_model=models.EwoksEventList_v2,
    response_description="Workflow execution jobs grouped per job ID",
    status_code=200,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Server not configured for ewoks events",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def execute_events_v2(
    settings: EwoksSettingsType,
    filters: Annotated[
        models.EwoksEventFilter, Depends(models.EwoksEventFilter)
    ],  # pydantic model to parse query parameters
) -> Dict[str, List[List[Dict]]]:
    jobs = OrderedDict()
    with events.reader_context(settings) as reader:
        if reader is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Server not configured for ewoks events",
            )
        for event in reader.get_events(**filters.model_dump(exclude_none=True)):
            job_id = event["job_id"]
            if job_id not in jobs:
                jobs[job_id] = list()
            jobs[job_id].append(event)
    return {"jobs": list(jobs.values())}


@v2_0_0_router.get(
    "/execution/queues",
    summary="Get queues",
    response_model=models.EwoksQueueList,
    response_description="List of available queues",
    status_code=200,
)
def queues(settings: EwoksSettingsType) -> Dict[str, Optional[List[str]]]:
    if settings.ewoks_scheduling.type == EwoksSchedulingType.Local:
        return {"queues": None}

    return {"queues": get_queues()}
