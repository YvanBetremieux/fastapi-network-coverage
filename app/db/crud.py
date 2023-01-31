"""
Crud Module
"""
from typing import Optional

import sqlalchemy
from sqlalchemy.orm import Session

from app.db import models, schemas
from app.db.database import db_add, db_delete, engine
from app.utils import add_city_to_dataframe, csv_to_dataframe, find_operator, logger


def get_operator(database: Session, code: str):
    """
    Query the database to retrieve operator
    :param database: db
    :param code: Operator code
    :return: Operator
    """
    return database.query(models.Operator).filter(models.Operator.code == code).first()


def get_operators(database: Session):
    """
    Query the database to retrieve operator
    :param database: db
    :return: All operators
    """
    return database.query(models.Operator).all()


@db_delete
def delete_operator(database: Session, code: str):
    """
    Delete operator by code
    :param database: db
    :param code: operator
    :return: id deleted
    """
    return get_operator(database=database, code=code)


@db_add
def create_operator(
    database: Session, operator=schemas.PydanticOperator
):  # pylint: disable=W0613
    """
    Query the database to create operator
    :param database: db
    :param operator: operator
    :return: id of created operator
    """
    operator_name = find_operator(operator)
    db_operator = models.Operator(code=operator.code, name=operator_name)
    return db_operator


# City
def get_city(database: Session, city: str):
    """
    Query the database to retrieve city
    :param database: db
    :param city: city
    :return: City model
    """
    return database.query(models.City).filter(models.City.name == city).first()


def get_cities(database: Session):
    """
    Query the database to retrieve cities
    :param database: db
    :return: All cities
    """
    return database.query(models.City).all()


@db_add
def create_city(database: Session, city: schemas.PydanticCity):  # pylint: disable=W0613
    """
    Query the database to create city
    :param database: db
    :param city: city
    :return: city model
    """
    db_city = models.City(name=city.name)
    return db_city


@db_delete
def delete_city(database: Session, city: str):
    """
    Delete city by name
    :param database: db
    :param city: city
    :return: id deleted
    """
    return get_city(database=database, city=city)


def get_coverage_network(database: Session, operator: Optional[str] = None, city=str):
    """
    Query the database to retrieve city
    :param database: db
    :param operator: operator (optionnal)
    :param city: city
    :return: Result set from db
    """
    if not operator:
        return (
            database.query(models.NetworkCoverage)
            .filter(
                models.NetworkCoverage.city == city,
            )
            .all()
        )
    return (
        database.query(models.NetworkCoverage)
        .filter(
            models.NetworkCoverage.operator == operator,
            models.NetworkCoverage.city == city,
        )
        .all()
    )


def get_network_coverage(database: Session, city: str):
    """
    Create return structure when retrieving network coverage
    :param database: db
    :param city: city
    :return: json structure
    """
    res = get_coverage_network(database=database, city=city)

    results = {}
    for elem in res:
        if not results.get(elem.operator):
            networks = {
                "2G": elem.two_g,
                "3G": elem.three_g,
                "4G": elem.four_g,
            }

        else:
            networks = {
                "2G": elem.two_g or results.get(elem.operator).get("2G"),
                "3G": elem.three_g or results.get(elem.operator).get("3G"),
                "4G": elem.four_g or results.get(elem.operator).get("4G"),
            }
        results.update({elem.operator: networks})
    return results


def save_to_db(file):
    """
    Save data to db. Using dataframe.to_sql() to save multiple rows
    :param file: csv file
    :return: Boolean, just insert
    """

    try:
        network_cov_df = csv_to_dataframe(file)

        logger.info("Saving Cities")
        network_cov_df = add_city_to_dataframe(network_cov_df)
        city_df = network_cov_df[["city"]].drop_duplicates()
        city_df.rename(columns={"city": "name"}, inplace=True)
        city_df.to_sql(
            "city", con=engine, if_exists="append", index=False, chunksize=1000
        )

        logger.info("Saving Operators")
        network_cov_df["operator"] = network_cov_df.apply(
            lambda row: find_operator(int(row["Operateur"])), axis=1
        )
        operator_df = network_cov_df[["operator", "Operateur"]].drop_duplicates()
        operator_df.rename(
            columns={"operator": "name", "Operateur": "code"}, inplace=True
        )
        operator_df.to_sql(
            "operator", con=engine, if_exists="append", index=False, chunksize=1000
        )

        logger.info("Saving Network Coverage")
        network_coverage_df = network_cov_df[
            ["operator", "city", "2G", "3G", "4G"]
        ].drop_duplicates()
        network_coverage_df.to_sql(
            "network_coverage",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
            dtype={
                "2G": sqlalchemy.types.Boolean,
                "3G": sqlalchemy.types.Boolean,
                "4G": sqlalchemy.types.Boolean,
            },
        )
    except Exception as exc:
        logger.exception("Error occured when saving to db")
        raise exc
    return True
