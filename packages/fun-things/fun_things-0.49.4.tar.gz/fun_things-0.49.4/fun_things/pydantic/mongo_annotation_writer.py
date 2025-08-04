from dataclasses import dataclass
from typing import Generic, TypeVar
from .mongo_annotation_field import MongoAnnotationField

T = TypeVar("T")


@dataclass(frozen=True)
class MongoAnnotationWriter(Generic[T]):
    field: MongoAnnotationField
    result: T
