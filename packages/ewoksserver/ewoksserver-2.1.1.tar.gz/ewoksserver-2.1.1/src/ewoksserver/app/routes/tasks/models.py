from typing import Optional, List, Dict
from pydantic import BaseModel
from pydantic import Field


class EwoksTaskDescription(BaseModel):
    task_type: str = Field(title="One of the Ewoks task types")
    task_identifier: str = Field(title="Task identifier unique to the server")
    category: Optional[str] = Field(title="Task category", default=None)
    icon: Optional[str] = Field(
        title="Task icon identifier unique to the server", default=None
    )
    required_input_names: Optional[List[str]] = Field(
        title="Task required input names", default=None
    )
    optional_input_names: Optional[List[str]] = Field(
        title="Task optional input names", default=None
    )
    output_names: Optional[List[str]] = Field(title="Task output names", default=None)


class EwoksTaskIdentifiers(BaseModel):
    identifiers: List[str] = Field(title="Task identifiers")


class EwoksTaskDescriptions(BaseModel):
    items: List[EwoksTaskDescription] = Field(title="Task descriptions")


class EwoksTaskDiscovery(BaseModel):
    modules: Optional[List[str]] = Field(title="Ewoks task description", default=None)
    task_type: Optional[str] = Field(title="Task type to discover", default=None)
    worker_options: Optional[Dict] = Field(title="Worker options", default=None)
