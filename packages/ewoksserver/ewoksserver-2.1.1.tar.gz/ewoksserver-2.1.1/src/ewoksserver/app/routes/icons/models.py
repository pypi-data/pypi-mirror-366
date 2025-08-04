from typing import List
from pydantic import BaseModel
from pydantic import Field


class EwoksIcon(BaseModel):
    data_url: str = Field(title="Icon data url")


class EwoksIconIdentifiers(BaseModel):
    identifiers: List[str] = Field(title="Icon identifiers")
