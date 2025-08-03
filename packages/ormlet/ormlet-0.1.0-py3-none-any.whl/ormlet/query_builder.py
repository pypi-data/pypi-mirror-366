import sqlite3
from typing import Any, Generic, Type, TypeVar, Union

from .model import Model
from .result_map import query_result_mapper

T = TypeVar("T", bound=Model)


class QueryBuilder(Generic[T]):
    def __init__(self, cls: Type[T]):
        self.model_cls = cls
        self.query = ""
        self.insert_values = []
        self.operation = None

    def select(self):
        fields = list(self.model_cls.get_columns().keys())
        field_str = ", ".join(fields)
        self.query = f"SELECT {field_str} FROM {self.model_cls.get_table_name()}"
        self.operation = "select"
        return self

    def insert(self):
        table_name = self.model_cls.get_table_name()
        self.query = f"INSERT INTO {table_name}"
        self.operation = "insert"
        return self

    def update(self):
        table_name = self.model_cls.get_table_name()
        self.query = f"UPDATE {table_name}"
        self.operation = "update"
        return self

    def delete(self):
        table_name = self.model_cls.get_table_name()
        self.query = f"DELETE FROM {table_name}"
        self.operation = "delete"
        return self

    def set(self, *args: Any, **kwargs: Any):
        if kwargs:
            fields = list(kwargs.keys())
            placeholders = ", ".join([f"{_} = ?" for _ in fields])
            self.query += f" SET {placeholders}"
            self.insert_values = list(kwargs.values())
        return self

    def values(self, *args: Any, **kwargs: Any):
        if kwargs:
            fields = list(kwargs.keys())
            placeholders = ", ".join(["?" for _ in fields])
            field_str = ", ".join(fields)
            self.query += f" ({field_str}) VALUES ({placeholders})"
            self.insert_values = list(kwargs.values())
        else:
            fields = list(self.model_cls.get_columns().keys())
            placeholders = ", ".join(["?" for _ in args])
            field_str = ", ".join(fields)
            self.query += f" ({field_str}) VALUES ({placeholders})"
            self.insert_values = list(args)
        return self

    def where(self, clause: str):
        self.query += f" WHERE {clause}"
        return self

    def and_(self, clause: str):
        self.query += f" AND {clause}"
        return self

    def or_(self, clause: str):
        self.query += f" OR {clause}"
        return self

    def order_by(self, *fields: str):
        if fields:
            ordering = ", ".join(fields)
            self.query += f" ORDER BY {ordering}"
        return self

    def offset(self, offset_val: int):
        self.query += f" OFFSET {offset_val}"
        return self

    def limit(self, limit: int):
        self.query += f" LIMIT {limit}"
        return self

    def execute(self, connection: sqlite3.Connection) -> Union[list[T], int, None]:
        try:
            cursor = connection.cursor()

            if self.operation == "insert":
                cursor.execute(self.query, self.insert_values)
                connection.commit()
                return cursor.lastrowid
            elif self.operation == "select":
                cursor.execute(self.query)
                result = cursor.fetchall()
                return query_result_mapper(self.model_cls, result)
            elif self.operation == "update":
                cursor.execute(self.query, self.insert_values)
                connection.commit()
                return cursor.rowcount
            elif self.operation == "delete":
                cursor.execute(self.query, self.insert_values)
                connection.commit()
                return cursor.rowcount

        except Exception as e:
            print(f"Database error: {e}")


def select(cls: Type[T]) -> QueryBuilder[T]:
    return QueryBuilder(cls).select()


def insert(cls: Type[T]) -> QueryBuilder[T]:
    return QueryBuilder(cls).insert()


def update(cls: Type[T]) -> QueryBuilder[T]:
    return QueryBuilder(cls).update()


def delete(cls: Type[T]) -> QueryBuilder[T]:
    return QueryBuilder(cls).delete()
