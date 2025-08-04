from typing import List, Dict
from typing_extensions import Annotated

from fastapi import APIRouter
from fastapi import Path
from fastapi import Body
from fastapi.responses import JSONResponse
from fastapi import status


from ...backends import binary_backend
from ...config import EwoksSettingsType
from ..common import models as common_models
from . import models

router = APIRouter()


@router.get(
    "/icon/{identifier}",
    summary="Get ewoks icon",
    response_model=models.EwoksIcon,
    response_model_exclude_none=True,
    response_description="Ewoks icon",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to read icon",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Icon not found",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def get_icon(
    identifier: Annotated[
        str,
        Path(
            title="Icon identifier",
            description="Unique identifier in the icon database",
        ),
    ],
    settings: EwoksSettingsType,
) -> binary_backend.ResourceContentType:
    try:
        return binary_backend.load_resource(
            settings.resource_directory / "icons", identifier
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to read icon '{identifier}'.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except FileNotFoundError:
        return JSONResponse(
            {
                "message": f"Icon '{identifier}' is not found.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/icons",
    summary="Get all ewoks icon identifiers",
    response_model=models.EwoksIconIdentifiers,
    response_description="Ewoks icon identifiers",
    status_code=200,
)
def get_icon_identifiers(settings: EwoksSettingsType) -> Dict[str, List[str]]:
    return {
        "identifiers": list(
            binary_backend.resource_identifiers(settings.resource_directory / "icons")
        )
    }


@router.put(
    "/icon/{identifier}",
    summary="Update ewoks icon",
    response_model=models.EwoksIcon,
    response_model_exclude_none=True,
    response_description="Ewoks icon",
    status_code=200,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Icon not found",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to edit icon",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def update_icon(
    identifier: Annotated[
        str,
        Path(
            title="Icon identifier",
            description="Unique identifier in the icon database",
        ),
    ],
    icon: Annotated[models.EwoksIcon, Body(title="Ewoks icon")],
    settings: EwoksSettingsType,
) -> models.EwoksIcon:
    exists = binary_backend.resource_exists(
        settings.resource_directory / "icons", identifier
    )
    if not exists:
        return JSONResponse(
            {
                "message": f"Icon '{identifier}' is not found.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        binary_backend.save_resource(
            settings.resource_directory / "icons", identifier, icon.model_dump()
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to edit icon '{identifier}'.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return icon


@router.post(
    "/icon/{identifier}",
    summary="Create ewoks icon",
    response_model=models.EwoksIcon,
    response_model_exclude_none=True,
    response_description="Ewoks icon",
    status_code=200,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Icon already exists",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to create icon",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def create_icon(
    identifier: Annotated[
        str,
        Path(
            title="Icon identifier",
            description="Unique identifier in the icon database",
        ),
    ],
    icon: Annotated[models.EwoksIcon, Body(title="Ewoks icon")],
    settings: EwoksSettingsType,
) -> models.EwoksIcon:
    exists = binary_backend.resource_exists(
        settings.resource_directory / "icons", identifier
    )
    if exists:
        return JSONResponse(
            {
                "message": f"Icon '{identifier}' already exists.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    try:
        binary_backend.save_resource(
            settings.resource_directory / "icons", identifier, icon.model_dump()
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to create icon '{identifier}'.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return icon


@router.delete(
    "/icon/{identifier}",
    summary="Delete ewoks icon",
    response_model=common_models.ResourceInfo,
    response_description="Deleted ewoks icon identifier",
    status_code=200,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "No permission to read icon",
            "model": common_models.ResourceIdentifierError,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Icon not found",
            "model": common_models.ResourceIdentifierError,
        },
    },
)
def delete_icon(
    identifier: Annotated[
        str,
        Path(
            title="Icon identifier",
            description="Unique identifier in the icon database",
        ),
    ],
    settings: EwoksSettingsType,
) -> Dict[str, str]:
    try:
        binary_backend.delete_resource(
            settings.resource_directory / "icons", identifier
        )
    except PermissionError:
        return JSONResponse(
            {
                "message": f"No permission to delete icon '{identifier}'.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except FileNotFoundError:
        return JSONResponse(
            {
                "message": f"Icon '{identifier}' is not found.",
                "type": "icon",
                "identifier": identifier,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return {"identifier": identifier, "type": "icon"}
