from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field

from ellar.core.schema import Schema


class BlogObjectDTO:
    title: str
    author: str


@dataclass
class NoteSchemaDC:
    id: Union[int, None]
    text: str
    completed: bool


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


class Filter(Schema):
    to_datetime: datetime = Field(alias="to")
    from_datetime: datetime = Field(alias="from")


class CreateCarSchema(Schema):
    name: str
    model: str
    brand: str
    author: User
