from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Literal
from pydantic import BaseModel, field_validator
from sqlglot.expressions import (
    Alias,
    Column,
    Condition,
    column,
    condition,
    table_,
    Table,
)

from semantext.helper_models import (
    SQLTypes,
    SQLExpressions,
    SQLOperations,
    SQLGlotTable,
)


class GlobalColumn(BaseModel):
    column_name: str
    table_name: str


class ChartColumn(BaseModel):
    column_name: str
    data_type: SQLTypes
    table_name: str
    expression: SQLExpressions | None = None
    where_value: (
        Literal["yesterday", "last week", "last month", "last year"]
        | datetime
        | str
        | int
        | None
    ) = None
    operation: SQLOperations | None = None

    @field_validator("data_type", mode="before")
    @classmethod
    def validate_data_type(cls, value):
        if isinstance(value, str):
            try:
                return SQLTypes[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid data_type: {value}. Valid options are: {[e.name for e in SQLTypes]}"
                )
        return value

    @field_validator("expression", mode="before")
    @classmethod
    def validate_expression(cls, value):
        if isinstance(value, str) and value is not None:
            try:
                return SQLExpressions[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid expression: {value}. Valid options are: {[e.name for e in SQLExpressions]}"
                )
        return value

    @field_validator("operation", mode="before")
    @classmethod
    def validate_operation(cls, value):
        if isinstance(value, str) and value is not None:
            try:
                return SQLOperations[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid operation: {value}. Valid options are: {[e.name for e in SQLOperations]}"
                )
        return value

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ChartColumn):
            return self.column_name == value.column_name
        return False

    def encode_select(self) -> Alias | Column:
        table = self.__get_table_name()
        if self.expression is None:
            return column(
                col=self.column_name,
                quoted=True,
                **table.model_dump(),
            ).as_(self.column_name, quoted=True)
        else:
            return self.expression.expression(
                column=column(col=self.column_name, quoted=True, **table.model_dump()),
            )

    def encode_on(self) -> Column:
        table = self.__get_table_name()
        if self.expression is None:
            return column(
                col=self.column_name,
                quoted=True,
                **table.model_dump(),
            )
        else:
            raise ValueError("Not Good")

    # def __get_time_amount(self):
    #     if self.where_value is None:
    #         return None
    #     if type(self.where_value) is not str:
    #         return self.where_value
    #     middle = [int(s) for s in self.where_value.split() if s.isdigit()]
    #     if len(middle) > 0:

    def encode_where(self):
        if self.where_value is None or self.operation is None:
            raise ValueError(
                "Both 'where_value' and 'operation' must be set to encode a where condition"
            )
        conversion_dict = {r"week": datetime.now() - timedelta(days=7)}
        return condition(
            self.operation.expression(
                column=column(
                    self.column_name,
                    **self.__get_table_name().model_dump(),
                    quoted=True,
                ),
                right=self.data_type.expression(self.where_value),
            )
        )

    def encode_table(self) -> Table:
        table = self.__get_table_name()
        return table_(**table.model_dump(), quoted=True)

    def __get_table_name(self) -> SQLGlotTable:
        try:
            catalog, schema, table = self.table_name.split(".")
            return SQLGlotTable(catalog=catalog, db=schema, table=table)
        except ValueError:
            return SQLGlotTable(table=self.table_name)


class Dimension(GlobalColumn):
    column_name_display: str
    label: str
    hierarchy: bool = False
    filters: List[Filter] | None = None


class Metric(GlobalColumn):
    expression: SQLExpressions

    @field_validator("expression", mode="before")
    @classmethod
    def validate_expression(cls, value):
        if isinstance(value, str):
            try:
                return SQLExpressions[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid expression: {value}. Valid options are: {[e.name for e in SQLExpressions]}"
                )
        return value


class ChartProperties(BaseModel):
    dimension: Dimension
    metrics: List[Metric]
    filters: List[Filter] | None = None


class Filter(GlobalColumn):
    value: int | str | datetime
    operation: SQLOperations

    @field_validator("operation", mode="before")
    @classmethod
    def validate_operation(cls, value):
        if isinstance(value, str):
            try:
                return SQLOperations[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid operation: {value}. Valid options are: {[e.name for e in SQLOperations]}"
                )
        return value
