__all__ = ["Cursor", "Page", "Entry", "ChoicesItem", "ReadOnlyModel"]

from dataclasses import dataclass
from typing import Generic, TypedDict, TypeVar, get_args

from api.esm.utils import get_choices_label
from django.db.models import Manager
from pydantic import BaseModel, ConfigDict, field_validator
from typing_extensions import NotRequired

T = TypeVar("T")


@dataclass
class Cursor:
    offset: int
    reverse: int
    position: str | None


class Page(BaseModel, Generic[T]):
    next: str | None
    previous: str | None
    results: list[T]


class Entry(BaseModel, Generic[T]):
    title: str | None
    results: T


class ChoicesItem(BaseModel, Generic[T]):
    id: T
    name: str | None


class ReadOnlyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int

    @field_validator("*", mode="before")
    def render_complex_fields(cls, value, info):
        for type_ in get_args(cls.model_fields[info.field_name].annotation):
            if metadata := getattr(type_, "__pydantic_generic_metadata__", None):
                if value is not None and metadata["origin"] is ChoicesItem:
                    return {"id": value, "name": get_choices_label(metadata["args"][0], value)}

        if isinstance(value, Manager):
            return value.all()
        return value


class Multiselect(ReadOnlyModel):
    id: int
    name: str | None


class ActionClasses(TypedDict):
    list: NotRequired[type[BaseModel]]
    retrieve: NotRequired[type[BaseModel]]
    update: NotRequired[type[BaseModel]]
    delete: NotRequired[type[BaseModel]]
