from __future__ import annotations

from datetime import datetime

from pydantic import Field

from pydantic_db import Model


class ModelA(Model):
    id: int
    a: str


class ModelB(Model):
    id: int
    b: str


class ModelC(Model):
    _eq_excluded_fields = {"updated"}

    id: int
    c: str
    updated: datetime


class ModelD(Model):
    _skip_prefix_fields = {"b": "id"}

    id: int
    d: str
    a: ModelA | None
    b: ModelB | None


class ModelE(Model):
    _skip_sortable_fields = {"d__a__id", "d__b__id"}
    # union not containing model to trigger test branches
    id_: int | float = Field(..., alias="id")
    e: str
    d: ModelD  # Nested NestedModel


class ModelF(Model):
    id: int
    models: list[ModelA]


class ModelG(Model):
    id: int
    models: list[ModelA] | None
