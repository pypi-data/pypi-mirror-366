import logging
from typing import List, Dict
from typing_extensions import Annotated

from fastapi import APIRouter
from fastapi import Path
from fastapi import Body
from fastapi.responses import JSONResponse
from fastapi import status
from pydantic import ValidationError


from ...backends import json_backend
from ...config import EwoksSettingsType
from ..common import models as common_models
from . import models
from . import discovery

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/task/{identifier}",
    summary="Get ewoks task description",
    response_model=models.EwoksTaskDescription,
    response_model_exclude_none=True,
    response_description="Ewoks task description",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to read task",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Task not found",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def get_task(
    identifier: Annotated[
        str,
        Path(
            title="Task identifier",
            description="Unique identifier in the task database",
        ),
    ],
    settings: EwoksSettingsType,
) -> json_backend.ResourceContentType:
    try:
        return json_backend.load_resource(
            settings.resource_directory / "tasks", identifier
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to read task '{identifier}'.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except FileNotFoundError:
        return JSONResponse(
            {
                "message": f"Task '{identifier}' is not found.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/tasks/descriptions",
    summary="Get all ewoks task descriptions",
    response_model=models.EwoksTaskDescriptions,
    response_description="Ewoks task descriptions",
    status_code=200,
)
def get_tasks(
    settings: EwoksSettingsType,
) -> Dict[str, List[models.EwoksTaskDescription]]:
    tasks = list(json_backend.resources(settings.resource_directory / "tasks"))

    valid_tasks = []
    for task in tasks:
        try:
            valid_task = models.EwoksTaskDescription(**task)
            valid_tasks.append(valid_task)
        except ValidationError as e:
            logger.warning(f"Invalid task description: {e}")

    return {"items": valid_tasks}


@router.get(
    "/tasks",
    summary="Get all ewoks task identifiers",
    response_model=models.EwoksTaskIdentifiers,
    response_description="Ewoks task identifiers",
    status_code=200,
)
def get_task_identifiers(settings: EwoksSettingsType) -> Dict[str, List[str]]:
    task_descriptions = get_tasks(settings)
    identifiers = [task.task_identifier for task in task_descriptions["items"]]
    return {"identifiers": identifiers}


@router.put(
    "/task/{identifier}",
    summary="Update ewoks task description",
    response_model=models.EwoksTaskDescription,
    response_model_exclude_none=True,
    response_description="Ewoks task description",
    status_code=200,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Wrong task identifier",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Task not found",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to edit task",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def update_task(
    identifier: Annotated[
        str,
        Path(
            title="Task identifier",
            description="Unique identifier in the task database",
        ),
    ],
    task: Annotated[models.EwoksTaskDescription, Body(title="Ewoks task description")],
    settings: EwoksSettingsType,
) -> models.EwoksTaskDescription:
    ridentifier = task.task_identifier
    if identifier != ridentifier:
        return JSONResponse(
            {
                "message": f"Resource identifier '{identifier}' is not equal to '{ridentifier}'.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    exists = json_backend.resource_exists(
        settings.resource_directory / "tasks", identifier
    )
    if not exists:
        return JSONResponse(
            {
                "message": f"Task '{identifier}' is not found.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        json_backend.save_resource(
            settings.resource_directory / "tasks", identifier, task.model_dump()
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to edit task '{identifier}'.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return task


@router.post(
    "/tasks",
    summary="Create ewoks task description",
    response_model=models.EwoksTaskDescription,
    response_model_exclude_none=True,
    response_description="Ewoks task description",
    status_code=200,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Task identifier cannot be empty",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_409_CONFLICT: {
            "description": "Task already exists",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to create task",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def create_task(
    task: Annotated[models.EwoksTaskDescription, Body(title="Ewoks task description")],
    settings: EwoksSettingsType,
) -> models.EwoksTaskDescription:
    ridentifier = task.task_identifier

    if ridentifier == "":
        return JSONResponse(
            {
                "message": "Task identifier cannot be empty",
                "type": "task",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    exists = json_backend.resource_exists(
        settings.resource_directory / "tasks", ridentifier
    )
    if exists:
        return JSONResponse(
            {
                "message": f"Task '{ridentifier}' already exists.",
                "type": "task",
                "identifier": ridentifier,
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    try:
        json_backend.save_resource(
            settings.resource_directory / "tasks", ridentifier, task.model_dump()
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to create task '{ridentifier}'.",
                "type": "task",
                "identifier": ridentifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return task


@router.post(
    "/tasks/discover",
    summary="Create ewoks task descriptions from a worker environment",
    response_model=models.EwoksTaskIdentifiers,
    response_description="Discovered ewoks task identifiers",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to create or edit task",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Module not found",
            "model": common_models.ResourceError,
        },
    },
)
def discover_tasks(
    settings: EwoksSettingsType,
    options: Annotated[
        models.EwoksTaskDiscovery, Body(title="Ewoks task discovery options")
    ] = None,
) -> Dict[str, List[str]]:
    if options:
        discover_options = options.model_dump()
    else:
        discover_options = dict()
    try:
        tasks = discovery.discover_tasks(settings, **discover_options)
    except ModuleNotFoundError as e:
        return JSONResponse(
            {
                "message": str(e),
                "type": "task",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    for task in tasks:
        ridentifier = task["task_identifier"]
        try:
            json_backend.save_resource(
                settings.resource_directory / "tasks", ridentifier, task
            )
        except PermissionError:
            return JSONResponse(
                {
                    "message": f"No permission to create task '{ridentifier}'.",
                    "type": "task",
                    "identifier": ridentifier,
                },
                status_code=status.HTTP_403_FORBIDDEN,
            )

    return {"identifiers": [task["task_identifier"] for task in tasks]}


@router.delete(
    "/task/{identifier}",
    summary="Delete ewoks task",
    response_model=common_models.ResourceInfo,
    response_description="Deleted ewoks task",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to read task",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Task not found",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def delete_task(
    identifier: Annotated[
        str,
        Path(
            title="Task identifier",
            description="Unique identifier in the task database",
        ),
    ],
    settings: EwoksSettingsType,
) -> Dict[str, str]:
    try:
        json_backend.delete_resource(settings.resource_directory / "tasks", identifier)
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to delete task '{identifier}'.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except FileNotFoundError:
        return JSONResponse(
            {
                "message": f"Task '{identifier}' is not found.",
                "type": "task",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return {"identifier": identifier, "type": "task"}
