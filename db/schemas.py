from pydantic import BaseModel
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from db import models

PydanticNetwork = sqlalchemy_to_pydantic(models.Network)
PydanticOperator = sqlalchemy_to_pydantic(models.Operator)
PydanticCity = sqlalchemy_to_pydantic(models.City)
PydanticNetworkCoverage = sqlalchemy_to_pydantic(models.NetworkCoverage)


class PydanticNetworkNoId(BaseModel):
    """
        Define Pydantic model for Network table
    """
    name: str


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
    network: int