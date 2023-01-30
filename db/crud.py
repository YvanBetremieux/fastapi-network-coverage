from sqlalchemy.orm import Session

from app.utils import find_operator, logger
from db import models
# Operator
from db.database import db_add


def get_operator(database: Session, operator=None):
    """Query the database to retrieve operator"""
    if not operator:
        raise ValueError("None operator")
    return database.query(models.Operator).filter(models.Operator.code == operator).first()


@db_add
def create_operator(database: Session, operator=None):
    """Query the database to create operator"""
    if not operator:
        logger.exception(f"No Operator provided")
        raise ValueError("No Operator provided")
    operator_name = find_operator(operator)
    # logger.info(f"Creating Operator {operator_name}")
    db_operator = models.Operator(code=operator, name=operator_name)
    return db_operator


# Network
def get_network(database: Session, network=None):
    """Query the database to retrieve network"""
    if not network:
        raise ValueError("None network")
    return database.query(models.Network).filter(models.Network.name == network).first()


@db_add
def create_network(database: Session, network=None):
    """Query the database to create network"""
    if not network:
        raise ValueError("None network")
    # logger.info(f"Creating Network {network}")
    db_network = models.Network(name=network)
    return db_network


# City
def get_city(database: Session, city=None):
    """Query the database to retrieve city"""
    if not city:
        raise ValueError("None city")
    return database.query(models.City).filter(models.City.name == city).first()


@db_add
def create_city(database: Session, city=None):
    """Query the database to create city"""
    if not city:
        raise ValueError("None city")
    # logger.info(f"Creating City {city}")
    db_city = models.City(name=city)
    return db_city


# Network Coverage
@db_add
def create_coverage_network(database: Session, operator=None, city=None, network=None):
    """Query the database to create coverage network"""
    if not operator and not city and not network:
        raise ValueError("None city")
    # logger.info(f"Creating NeworkCoverage with city {city}, network {network} and operator {operator}")
    db_city = models.NetworkCoverage(
        city=city,
        network=network,
        operator=operator
    )
    return db_city


def get_coverage_network(database: Session, operator=None, city=None, network=None):
    """Query the database to retrieve city"""
    if not operator and not city and not network:
        raise ValueError("None cn")
    return database.query(models.NetworkCoverage).filter(
        models.NetworkCoverage.operator == operator,
        models.NetworkCoverage.network == network,
        models.NetworkCoverage.city == city,
    ).first()


def create_coverage_networks(database: Session, row=None):

    operator_dict = {"operator": row["Operateur"]}
    city_dict = {"city": row["city"]}
    # logger.debug(f"Creating CN city {row['city']} operator {row['Operateur']}")

    data = []
    for col in row.index.to_list()[3:6]:
        if row[col] == 1:
            data.append(operator_dict | city_dict | {"network": col})

    for line in data:
        operator_id = get_operator(database, line.get("operator"))
        if not operator_id:
            raise ValueError(f"Operator {line.get('operator')} is not in the db")
        city_id = get_city(database, line.get("city"))
        if not city_id:
            raise ValueError(f"City {line.get('city')} is not in the db")
        network_id = get_network(database, line.get("network"))
        if not network_id:
            raise ValueError(f"Network {line.get('network')} is not in the db")
        cn = get_coverage_network(database=database, operator=operator_id.id, city=city_id.id, network=network_id.id)
        if not cn:
            cn = create_coverage_network(database=database, operator=operator_id.id, city=city_id.id,
                                         network=network_id.id)
    return True


def get_network_coverage(database: Session, city=None):
    res = database.query(models.NetworkCoverage.operator, models.NetworkCoverage.network).filter(
        models.NetworkCoverage.city == city).group_by(models.NetworkCoverage.operator,
                                                   models.NetworkCoverage.network).all()

    results = {}
    for elem in res:
        operator = database.query(models.Operator.name).filter(models.Operator.id == elem[0]).first()[0]
        network = database.query(models.Network.name).filter(models.Network.id == elem[1]).first()[0]
        if not operator in results:
            results.update({operator: {network: True}})
        elif results.get(operator) and not results.get(operator).get(network):
            results.get(operator).update({network: True})
    networks = [elem[0] for elem in database.query(models.Network.name).all()]
    for elem_key, elem_val in results.items():
        for net in networks:
            if not net in elem_val.keys():
                results.get(elem_key).update({net:False})
    return results
