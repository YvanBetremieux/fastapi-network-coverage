import json
from typing import Any, List

import requests
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, File, Request, UploadFile
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.utils import (
    logger,
)
from app.db import schemas, crud
from app.db.database import get_db


class NewJsonResponse(JSONResponse):
    """Class to return Json Response"""

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            allow_nan=True,
            ensure_ascii=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="Papernest_technical_test",
    redoc_url="/redoc",
    docs_url="/docs",
    openapi_url="/openapi.json",
    default_response_class=NewJsonResponse,
)

router = APIRouter()


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Exception handler to return Json format"""
    return NewJsonResponse(status_code=400, content={"Error": str(exc)})


@router.get("/network/coverage")
async def network_coverage(q: str):
    """Get network coverage by adress"""
    url_data_gouv = "https://api-adresse.data.gouv.fr/search/"
    params_data_gouv = {"q": q, "autocomplete": 0}
    try:
        res = requests.get(url=url_data_gouv, params=params_data_gouv)
        data_gouv_adress = res.json()
        city = data_gouv_adress.get("features")[0].get("properties").get("city")
        if not city:
            raise ValueError("This adress is not linked to a city")
        db_city = crud.get_city(database=next(get_db()), city=city)
        if not db_city:
            raise ValueError(
                f"This adress does not correspond to a city in db: city: {city}"
            )
        results = crud.get_network_coverage(database=next(get_db()), city=db_city.name)
        if not results:
            raise ValueError(f"No data found for city: {city}")
    except Exception as exc:
        logger.exception(f"Error when retrieve network coverage: {exc}")
        raise exc
    return results


@router.post("/add_data/csv")
async def add_data_csv(file: UploadFile = File(...)):
    """Add data to db"""

    if not file:
        raise ValueError("Data file is required")
    if not "csv" in file.filename:
        raise ValueError("You must provide a csv file")
    status = crud.save_to_db(file.file)
    if status:
        return "Everything ok"
    else:
        return "Error occured"


@router.post("/add/city", response_model=schemas.PydanticCity)
async def add_city(city: schemas.PydanticCityNoId, database: Session = Depends(get_db)):
    """Add city to db"""

    if not city:
        raise ValueError("City is required")
    try:
        db_city = crud.get_city(database=database, city=city)
        if not db_city:
            db_city = crud.create_city(database=database, city=city)
    except Exception as exc:
        logger.exception(f"Exception occured when creating city {exc}")
        raise exc
    return db_city


@router.get("/city", response_model=schemas.PydanticCity)
async def get_city(city: str, database: Session = Depends(get_db)):
    """Retrieve city from db"""
    try:
        db_city = crud.get_city(database=database, city=city)
        if not db_city:
            raise ValueError("City not found")
    except Exception as exc:
        logger.exception(f"Exception occured when retrieving city {exc}")
        raise exc
    return db_city


@router.get("/cities", response_model=List[schemas.PydanticCity])
async def get_cities(database: Session = Depends(get_db)):
    """Retrieve city from db"""
    try:
        db_cities = crud.get_cities(database=database)
        if not db_cities:
            raise ValueError("City not found")
    except Exception as exc:
        logger.exception(f"Exception occured when fetching cities {exc}")
        raise exc
    return db_cities


@router.delete("/city", response_model=schemas.PydanticCity)
async def delete_city(city: str, database: Session = Depends(get_db)):
    """delete city from db"""
    try:
        db_city = crud.get_city(database=database, city=city)
        if not db_city:
            raise ValueError("City not found")
    except Exception as exc:
        logger.exception(f"Exception occured when creating city {exc}")
        raise exc
    return db_city


@router.post("/add/operator", response_model=schemas.PydanticOperator)
async def add_operator(operator: str, database: Session = Depends(get_db)):
    """Add operator to db"""

    if not operator:
        raise ValueError("City is required")
    try:
        db_operator = crud.get_operator(database=database, operator=operator)
        if not db_operator:
            db_operator = crud.create_operator(database=database, operator=operator)
    except Exception as exc:
        logger.exception(f"Exception occured when creating operator {exc}")
        raise exc
    return db_operator


@router.get("/operator", response_model=schemas.PydanticOperator)
async def get_operator(code: str, database: Session = Depends(get_db)):
    """Retrieve operator from db"""
    try:
        db_operator = crud.get_operator(database=database, code=code)
        if not db_operator:
            raise ValueError("Operator not found")
    except Exception as exc:
        logger.exception(f"Exception occured when creating operator {exc}")
        raise exc
    return db_operator


@router.get("/operators", response_model=List[schemas.PydanticOperator])
async def get_operators(database: Session = Depends(get_db)):
    """Retrieve city from db"""
    try:
        db_operators = crud.get_operators(database=database)
        if not db_operators:
            raise ValueError("Operators not found")
    except Exception as exc:
        logger.exception(f"Exception occured when fetching operators {exc}")
        raise exc
    return db_operators


@router.delete("/operator", response_model=schemas.PydanticCity)
async def delete_operator(operator: str, database: Session = Depends(get_db)):
    """delete city from db"""
    try:
        db_operator = crud.get_operator(database=database, operator=operator)
        if not db_operator:
            raise ValueError("Operator not found")
    except Exception as exc:
        logger.exception(f"Exception occured when creating operator {exc}")
        raise exc
    return db_operator


@router.get("/")
async def root():
    return "Hello World"


@router.get("/health")
async def health():
    """Test liveliness of the app"""
    return "The api is running"

    return True


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

app.include_router(router=router)
