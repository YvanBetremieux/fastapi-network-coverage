"""
Schema module
"""

from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.db import models

PydanticOperator = sqlalchemy_to_pydantic(models.Operator)
PydanticCity = sqlalchemy_to_pydantic(models.City)
PydanticNetworkCoverage = sqlalchemy_to_pydantic(models.NetworkCoverage)


class PydanticCityNoId(BaseModel):
    """
    Define Pydantic model for City table
    """

    name: str


class PydanticOperatorNoId(BaseModel):
    """
    Define Pydantic model for Operator table
    """

    code: int
    name: str


class PydanticNetworkCoverageNoId(BaseModel):
    """
    Define Pydantic model for Network coverage table
    """

    city: int
    operator: int
