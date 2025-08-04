from pydantic import BaseModel
from pydantic import Field


class ResourceInfo(BaseModel):
    identifier: str = Field(title="Resource identifier")


class ResourceError(BaseModel):
    message: str = Field(title="Error message")
    type: str = Field(title="Resource type")


class ResourceIdentifierError(ResourceError):
    identifier: str = Field(title="Resource identifier")
