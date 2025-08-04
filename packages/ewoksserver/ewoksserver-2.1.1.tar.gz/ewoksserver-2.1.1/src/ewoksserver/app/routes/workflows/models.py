from typing import List, Optional, Dict
from pydantic import BaseModel
from pydantic import Field


class EwoksWorkflow(BaseModel):
    graph: Optional[Dict] = Field(title="Workflow attributes", default=None)
    nodes: Optional[List[Dict]] = Field(title="Node attributes", default=None)
    links: Optional[List[Dict]] = Field(title="Link attributes", default=None)


class EwoksWorkflowDescription(BaseModel):
    id: Optional[str] = Field(
        title="Workflow identifier unique to the server", default=None
    )
    label: Optional[str] = Field(
        title="Workflow label for human consumption", default=None
    )
    category: Optional[str] = Field(title="Workflow category", default=None)
    keywords: Optional[Dict] = Field(title="Workflow search keywords", default=None)
    input_schema: Optional[Dict] = Field(
        title="Workflow execute input schema for the frontend", default=None
    )
    ui_schema: Optional[Dict] = Field(
        title="Workflow execute UI schema for the frontend", default=None
    )


class EwoksWorkflowIdentifiers(BaseModel):
    identifiers: List[str] = Field(title="Workflow identifiers")


class EwoksWorkflowDescriptions(BaseModel):
    items: List[EwoksWorkflowDescription] = Field(title="Workflow descriptions")
