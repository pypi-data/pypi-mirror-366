import datetime as dt

from pydantic import BaseModel
from pydantic.types import UUID4

# Extras


class DropDownOption(BaseModel):
    id: UUID4
    name: str
    color: str | None
    orderindex: int


class DropDownTypeConfig(BaseModel):
    default: int | None = None
    options: list[DropDownOption]


class Tag(BaseModel):
    name: str


class CustomField(BaseModel):
    name: str
    value: str | float | dt.date | None


class Task(BaseModel):
    id: str
    name: str
    status: str
    update_date: dt.date | None
    creation_date: dt.date | None
    due_date: dt.date | None
    start_date: dt.date | None
    custom_fields: list[CustomField]
    tags: list[Tag]


# Parameters


# Payloads


# Responses
class GetTasksResponse(BaseModel):
    tasks: list[Task]
