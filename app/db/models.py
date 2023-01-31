"""
Models module
"""

import os

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Sequence,
    String,
    UniqueConstraint,
)

from .database import Base

load_dotenv()


class Operator(Base):
    """
    Defines the Operator table
    """

    __tablename__ = "operator"
    __table_args__ = {"schema": os.getenv("SCHEMA")}

    name = Column(String(50), nullable=False, primary_key=True)
    code = Column(Integer, nullable=False)


class City(Base):
    """
    Defines the City table
    """

    __tablename__ = "city"
    __table_args__ = {"schema": os.getenv("SCHEMA")}

    name = Column(String(100), nullable=False, primary_key=True)


class NetworkCoverage(Base):
    """
    Defines the NetworkCoverage table
    """

    __tablename__ = "network_coverage"
    __table_args__ = (
        UniqueConstraint("city", "operator", "2G", "3G", "4G"),
        {"schema": os.getenv("SCHEMA")},
    )

    id = Column(Integer, Sequence("network_coverage_seq"), primary_key=True)
    city = Column(ForeignKey(City.name))
    operator = Column(ForeignKey(Operator.name))
    two_g = Column("2G", Boolean, default=False)
    three_g = Column("3G", Boolean, default=False)
    four_g = Column("4G", Boolean, default=False)
