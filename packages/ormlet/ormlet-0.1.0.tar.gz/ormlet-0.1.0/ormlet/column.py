from typing import Any, Optional, Sequence


class Column:
    field_name: Optional[str]
    field_type: str
    unique: bool
    primary_key: bool
    default: Any
    nullable: bool

    def __init__(
        self,
        field_type: str,
        unique: bool = False,
        primary_key: bool = False,
        default: Any = None,
        nullable: bool = True,
    ) -> None:
        self.field_name = None
        self.field_type = field_type
        self.unique = unique
        self.primary_key = primary_key
        self.default = default
        self.nullable = nullable

    def to_sql(self) -> str:
        sql: str = f"{self.field_name} {self.field_type}"
        if self.primary_key:
            sql += " PRIMARY KEY"
        if self.unique:
            sql += " UNIQUE"
        if not self.nullable:
            sql += " NOT NULL"
        if self.default is not None:
            sql += f" DEFAULT {repr(self.default)}"
        return sql

    def __eq__(self, other: Any) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        return f"{self.field_name} = {repr(other)}"

    def __ne__(self, other: Any) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        return f"{self.field_name} != {repr(other)}"

    def __lt__(self, other: Any) -> str:
        return f"{self.field_name} < {repr(other)}"

    def __le__(self, other: Any) -> str:
        return f"{self.field_name} <= {repr(other)}"

    def __gt__(self, other: Any) -> str:
        return f"{self.field_name} > {repr(other)}"

    def __ge__(self, other: Any) -> str:
        return f"{self.field_name} >= {repr(other)}"

    def like(self, pattern: str) -> str:
        return f"{self.field_name} LIKE {repr(pattern)}"

    def ilike(self, pattern: str) -> str:
        return f"{self.field_name} ILIKE {repr(pattern)}"

    def in_(self, values: Sequence[Any]) -> str:
        values_list = ", ".join(repr(v) for v in values)
        return f"{self.field_name} IN ({values_list})"

    def not_in(self, values: Sequence[Any]) -> str:
        values_list = ", ".join(repr(v) for v in values)
        return f"{self.field_name} NOT IN ({values_list})"

    def is_null(self) -> str:
        return f"{self.field_name} IS NULL"

    def is_not_null(self) -> str:
        return f"{self.field_name} IS NOT NULL"


class IntegerField(Column):
    def __init__(
        self,
        unique: bool = False,
        primary_key: bool = False,
        default: Optional[int] = None,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type="INTEGER",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )


class VarCharField(Column):
    def __init__(
        self,
        max_length: int = 255,
        unique: bool = False,
        primary_key: bool = False,
        default: Optional[str] = None,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type=f"VARCHAR({max_length})",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )


class TextField(Column):
    def __init__(
        self,
        unique: bool = False,
        primary_key: bool = False,
        default: Optional[str] = None,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type="TEXT",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )


class BooleanField(Column):
    def __init__(
        self,
        unique: bool = False,
        primary_key: bool = False,
        default: bool = False,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type="BOOLEAN",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )


class FloatField(Column):
    def __init__(
        self,
        unique: bool = False,
        primary_key: bool = False,
        default: Optional[float] = None,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type="REAL",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )


class DateField(Column):
    def __init__(
        self,
        unique: bool = False,
        primary_key: bool = False,
        default: Optional[str] = None,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type="DATE",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )


class DateTimeField(Column):
    def __init__(
        self,
        unique: bool = False,
        primary_key: bool = False,
        default: Optional[str] = None,
        nullable: bool = True,
    ) -> None:
        super().__init__(
            field_type="DATETIME",
            unique=unique,
            primary_key=primary_key,
            default=default,
            nullable=nullable,
        )
