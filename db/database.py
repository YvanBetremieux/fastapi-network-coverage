import os
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv

load_dotenv()


# Base = declarative_base()
from sqlalchemy.orm import registry, sessionmaker

engine = create_engine(os.getenv("DB_STRING"), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

mapper_registry = registry()
Base = mapper_registry.generate_base()


def get_db():
    """Get databasease session"""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def db_add(func):
    """Decorator for adding data.

    :param func: function
    """

    @wraps(func)
    def add(database, *args, **kwargs):
        try:
            db_object = func(database, *args, **kwargs)
            if db_object:
                database.add(db_object)
                database.commit()
        except SQLAlchemyError:
            database.flush()
            database.rollback()
            raise
        return db_object

    return add


def db_commit(func):
    """Decorator for commiting data.

    :param func: function
    """

    @wraps(func)
    def commit(database, *args, **kwargs):
        try:
            db_object = func(database, *args, **kwargs)
            if db_object:
                database.commit()
        except SQLAlchemyError:
            database.flush()
            database.rollback()
            raise
        return db_object

    return commit


def db_delete(func):
    """Decorator for deleting data.

    :param func: function
    """

    @wraps(func)
    def delete(database, *args, **kwargs):
        try:
            db_object = func(database, *args, **kwargs)
            if db_object:
                if isinstance(db_object, list):
                    for obj in db_object:
                        database.delete(obj)
                else:
                    database.delete(db_object)
                database.commit()
        except SQLAlchemyError:
            database.flush()
            database.rollback()
            raise
        return db_object

    return delete
