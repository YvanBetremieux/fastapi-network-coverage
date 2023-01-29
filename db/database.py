import os
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DB_STRING"), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()

def get_db():
    """Get database session"""
    datab = SessionLocal()
    try:
        yield datab
    finally:
        datab.close()


def db_add(func):
    """Decorator for adding data.

    :param func: function
    """

    @wraps(func)
    def add(datab, *args, **kwargs):
        try:
            db_object = func(datab, *args, **kwargs)
            if db_object:
                datab.add(db_object)
                datab.commit()
        except SQLAlchemyError:
            datab.flush()
            datab.rollback()
            raise
        return db_object

    return add


def db_commit(func):
    """Decorator for commiting data.

    :param func: function
    """

    @wraps(func)
    def commit(datab, *args, **kwargs):
        try:
            db_object = func(datab, *args, **kwargs)
            if db_object:
                datab.commit()
        except SQLAlchemyError:
            datab.flush()
            datab.rollback()
            raise
        return db_object

    return commit


def db_delete(func):
    """Decorator for deleting data.

    :param func: function
    """

    @wraps(func)
    def delete(datab, *args, **kwargs):
        try:
            db_object = func(datab, *args, **kwargs)
            if db_object:
                if isinstance(db_object, list):
                    for obj in db_object:
                        datab.delete(obj)
                else:
                    datab.delete(db_object)
                datab.commit()
        except SQLAlchemyError:
            datab.flush()
            datab.rollback()
            raise
        return db_object

    return delete
