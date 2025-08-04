import json
from typing import List, Dict, Optional
from typing_extensions import Annotated

from fastapi import APIRouter
from fastapi import Path
from fastapi import Body
from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi import status


from ...backends import json_backend
from ...config import EwoksSettingsType
from ..common import models as common_models
from . import models
from . import descriptions

router = APIRouter()


@router.get(
    "/workflow/{identifier}",
    summary="Get ewoks workflow",
    response_model=models.EwoksWorkflow,
    response_model_exclude_none=True,
    response_description="Ewoks workflow",
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
def get_workflow(
    identifier: Annotated[
        str,
        Path(
            title="Workflow identifier",
            description="Unique identifier in the workflow database",
        ),
    ],
    settings: EwoksSettingsType,
) -> json_backend.ResourceContentType:
    try:
        return json_backend.load_resource(
            settings.resource_directory / "workflows", identifier
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to read workflow '{identifier}'.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except FileNotFoundError:
        return JSONResponse(
            {
                "message": f"Workflow '{identifier}' is not found.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/workflows",
    summary="Get all ewoks workflow identifiers",
    response_model=models.EwoksWorkflowIdentifiers,
    response_description="Ewoks workflow identifiers",
    status_code=200,
)
def get_workflow_identifiers(
    settings: EwoksSettingsType, kw: Annotated[Optional[List[str]], Query()] = None
) -> Dict[str, List[str]]:
    keywords = _compile_keywords(kw)
    root = settings.resource_directory / "workflows"
    if keywords:
        identifiers = [
            desc["id"]
            for desc in descriptions.workflow_descriptions(root, keywords=keywords)
        ]
    else:
        identifiers = list(json_backend.resource_identifiers(root))
    return {"identifiers": identifiers}


def _compile_keywords(kw: Optional[List[str]]) -> Optional[Dict]:
    if not kw:
        return
    keywords = dict()
    for s in kw:
        name, _, value = s.partition(":")
        try:
            value = json.loads(value)
        except json.decoder.JSONDecodeError:
            pass
        keywords[name] = value
    return keywords


@router.get(
    "/workflows/descriptions",
    summary="Get all ewoks workflow descriptions",
    response_model=models.EwoksWorkflowDescriptions,
    response_model_exclude_none=True,
    response_description="Ewoks workflow descriptions",
    status_code=200,
)
def get_workflows(
    settings: EwoksSettingsType, kw: Annotated[Optional[List[str]], Query()] = None
) -> Dict[str, List[Dict]]:
    keywords = _compile_keywords(kw)
    return {
        "items": list(
            descriptions.workflow_descriptions(
                settings.resource_directory / "workflows", keywords=keywords
            )
        )
    }


@router.put(
    "/workflow/{identifier}",
    summary="Update ewoks workflow",
    response_model=models.EwoksWorkflow,
    response_model_exclude_none=True,
    response_description="Ewoks workflow",
    status_code=200,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Wrong workflow identifier",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Workflow not found",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to edit workflow",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def update_workflow(
    identifier: Annotated[
        str,
        Path(
            title="Workflow identifier",
            description="Unique identifier in the workflow database",
        ),
    ],
    workflow: Annotated[models.EwoksWorkflow, Body(title="Ewoks workflow")],
    settings: EwoksSettingsType,
) -> models.EwoksWorkflow:
    if workflow.graph:
        ridentifier = workflow.graph.get("id", identifier)
    else:
        ridentifier = None
    if identifier != ridentifier:
        return JSONResponse(
            {
                "message": f"Resource identifier '{identifier}' is not equal to '{ridentifier}'.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    exists = json_backend.resource_exists(
        settings.resource_directory / "workflows", identifier
    )
    if not exists:
        return JSONResponse(
            {
                "message": f"Workflow '{identifier}' is not found.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        json_backend.save_resource(
            settings.resource_directory / "workflows",
            identifier,
            workflow.model_dump(exclude_none=True),
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to edit workflow '{identifier}'.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return workflow


@router.post(
    "/workflows",
    summary="Create ewoks workflow",
    response_model=models.EwoksWorkflow,
    response_model_exclude_none=True,
    response_description="Ewoks workflow",
    status_code=200,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Workflow identifier missing",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Workflow identifier cannot be empty",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_409_CONFLICT: {
            "description": "Workflow already exists",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to create workflow",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def create_workflow(
    workflow: Annotated[models.EwoksWorkflow, Body(title="Ewoks workflow")],
    settings: EwoksSettingsType,
) -> models.EwoksWorkflow:
    if workflow.graph:
        ridentifier = workflow.graph.get("id")
    else:
        ridentifier = None
    if ridentifier is None:
        return JSONResponse(
            {
                "message": "Workflow identifier missing",
                "type": "workflow",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if ridentifier == "":
        return JSONResponse(
            {
                "message": "Workflow identifier cannot be empty",
                "type": "workflow",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    exists = json_backend.resource_exists(
        settings.resource_directory / "workflows", ridentifier
    )
    if exists:
        return JSONResponse(
            {
                "message": f"Workflow '{ridentifier}' already exists.",
                "type": "workflow",
                "identifier": ridentifier,
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    try:
        json_backend.save_resource(
            settings.resource_directory / "workflows",
            ridentifier,
            workflow.model_dump(exclude_none=True),
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to create workflow '{ridentifier}'.",
                "type": "workflow",
                "identifier": ridentifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return workflow


@router.delete(
    "/workflow/{identifier}",
    summary="Delete ewoks workflow",
    response_model=common_models.ResourceInfo,
    response_description="Deleted ewoks workflow",
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
def delete_workflow(
    identifier: Annotated[
        str,
        Path(
            title="Workflow identifier",
            description="Unique identifier in the workflow database",
        ),
    ],
    settings: EwoksSettingsType,
) -> Dict[str, str]:
    try:
        json_backend.delete_resource(
            settings.resource_directory / "workflows", identifier
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to delete workflow '{identifier}'.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except FileNotFoundError:
        return JSONResponse(
            {
                "message": f"Workflow '{identifier}' is not found.",
                "type": "workflow",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return {"identifier": identifier, "type": "workflow"}
