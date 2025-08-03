from typing import Any, Type, TypeVar

from .model import Model

T = TypeVar("T", bound=Model)


def query_result_mapper(model_cls: Type[T], results: list[dict[str, Any]]):
    objects: list[T] = []
    for row in results:
        object: Model = model_cls()
        for col, value in zip(model_cls.get_columns(), row):
            setattr(object, col, value)
        objects.append(object)

    return objects
