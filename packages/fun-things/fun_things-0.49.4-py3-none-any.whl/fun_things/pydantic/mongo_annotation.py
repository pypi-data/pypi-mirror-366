from dataclasses import dataclass
from typing import Callable, Dict, Optional

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pymongo.collection import Collection

from .mongo_annotation_field import MongoAnnotationField
from .mongo_annotation_writer import MongoAnnotationWriter


def ignore_null(payload: MongoAnnotationField):
    return payload.value is not None


def default_filter_writer(
    writer: MongoAnnotationWriter[dict],
):
    if writer.field.annotation.filter:
        writer.result[writer.field.key] = writer.field.value

    return writer.result


def default_update_writer(
    writer: MongoAnnotationWriter[dict],
):
    result = writer.result
    annotation = writer.field.annotation
    key = writer.field.key
    value = writer.field.value

    if annotation.set:
        if "$set" not in result:
            result["$set"] = {}

        result["$set"][key] = value

    if annotation.set_on_insert:
        if "$setOnInsert" not in result:
            result["$setOnInsert"] = {}

        result["$setOnInsert"][key] = value

    return result


@dataclass(frozen=True)
class MongoAnnotation:
    filter: bool = False
    """
    If `True`,
    the field will be used as a filter when using `query_filter()`.
    """
    set: bool = True
    set_on_insert: bool = False
    filter_condition: Optional[
        Callable[
            [MongoAnnotationField],
            bool,
        ]
    ] = None
    update_condition: Optional[
        Callable[
            [MongoAnnotationField],
            bool,
        ]
    ] = None
    filter_writer: Callable[
        [MongoAnnotationWriter[dict]],
        dict,
    ] = default_filter_writer
    update_writer: Callable[
        [MongoAnnotationWriter[dict]],
        dict,
    ] = default_update_writer

    @classmethod
    def __get_annotation(cls, key, infos: Dict[str, FieldInfo]):
        if key not in infos:
            return cls

        for annotation in infos[key].metadata:
            if isinstance(annotation, MongoAnnotation):
                return annotation

        return cls

    @classmethod
    def get_fields(
        cls,
        model: BaseModel,
        *dump_args,
        **dump_kwargs,
    ):
        dump = model.model_dump(*dump_args, **dump_kwargs)
        infos = model.model_fields

        for key, value in dump.items():
            annotation = cls.__get_annotation(
                key,
                infos,
            )

            yield MongoAnnotationField(
                annotation=annotation,  # type: ignore
                key=key,
                value=value,
            )

    @classmethod
    def query_filter(
        cls,
        model: BaseModel,
        *dump_args,
        **dump_kwargs,
    ):
        result = {}

        for field in cls.get_fields(
            model,
            *dump_args,
            **dump_kwargs,
        ):
            if field.annotation.filter_condition is not None:
                if not field.annotation.filter_condition(field):
                    continue

            field.annotation.filter_writer(
                MongoAnnotationWriter(
                    field=field,
                    result=result,
                )
            )

        return result

    @classmethod
    def upsert(
        cls,
        collection: Collection,
        model: BaseModel,
        *dump_args,
        **dump_kwargs,
    ):
        filter = cls.query_filter(
            model,
            *dump_args,
            **dump_kwargs,
        )
        update = cls.query_update(
            model,
            *dump_args,
            **dump_kwargs,
        )

        return collection.update_one(
            filter=filter,
            update=update,
            upsert=True,
        )

    @classmethod
    def query_update(
        cls,
        model: BaseModel,
        *dump_args,
        **dump_kwargs,
    ):
        """
        Returns a query object for updating in MongoDB.
        """
        result = {}

        for field in cls.get_fields(
            model,
            *dump_args,
            **dump_kwargs,
        ):
            if field.annotation.update_condition is not None:
                if not field.annotation.update_condition(field):
                    continue

            field.annotation.update_writer(
                MongoAnnotationWriter(
                    field=field,
                    result=result,
                )
            )

        return result
