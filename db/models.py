import os

from sqlalchemy import Column, Integer, String, ForeignKey, Sequence, UniqueConstraint

from .database import Base
from dotenv import load_dotenv
load_dotenv()

class Operator(Base):
    """
        Defines the Operator table
    """
    __tablename__ = "operator"
    __table_args__ = {"schema": os.getenv("SCHEMA")}

    id = Column(Integer, Sequence("operator_seq"), primary_key=True)
    code = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)


class Network(Base):
    """
        Defines the Network table
    """
    __tablename__ = "network"
    __table_args__ = {"schema": os.getenv("SCHEMA")}

    id = Column(Integer, Sequence("network_seq"), primary_key=True)
    name = Column(String(5), nullable=False)


class City(Base):
    """
        Defines the City table
    """
    __tablename__ = "city"
    __table_args__ = {"schema": os.getenv("SCHEMA")}

    id = Column(Integer, Sequence("city_seq"), primary_key=True)
    name = Column(String(100), nullable=False)


class NetworkCoverage(Base):
    """
        Defines the NetworkCoverage table
    """
    __tablename__ = "network_coverage"
    __table_args__ = (UniqueConstraint('city', 'operator', 'network'), {"schema": os.getenv("SCHEMA")})

    id = Column(Integer, Sequence("network_coverage_seq"), primary_key=True)
    city = Column(ForeignKey(City.id))
    operator = Column(ForeignKey(Operator.id))
    network = Column(ForeignKey(Network.id))

