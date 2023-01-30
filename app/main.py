import json
import logging
import typing

import requests
import uvicorn
from fastapi import FastAPI, APIRouter, UploadFile, File
from starlette.responses import JSONResponse

from app.utils import csv_to_dataframe, extract_operators, extract_networks, extract_cities, \
    add_city_to_df, logger
from db import crud
from db.database import get_db
import time


class NewJsonResponse(JSONResponse):
    """ Class to return Json Response """

    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            allow_nan=True,
            ensure_ascii=False,
            indent=None,
            separators=(",", ":")
        ).encode("utf-8")


app = FastAPI(
    title="Papernest_technical_test",
    redoc_url="/redoc",
    docs_url="/docs",
    openapi_url="/openapi.json",
    default_response_class=NewJsonResponse
)

router = APIRouter()


@router.get("/network/coverage")
async def network_coverage(adress: str):
    """Get network coverage by adress"""
    if not adress:
        raise ValueError("Adress is required")

    url_data_gouv = "https://api-adresse.data.gouv.fr/search/"
    params_data_gouv = {"q": adress, "autocomplete":0}
    res = requests.get(url=url_data_gouv, params=params_data_gouv)
    data_gouv_adress = res.json()
    city =  data_gouv_adress.get("features")[0].get("properties").get("city")
    if not city:
        return "This adress is not linked to a city"
    city_id = crud.get_city(database=next(get_db()), city=city).id
    results = crud.get_network_coverage(database=next(get_db()), city=city_id)
    return results


@router.post("/add_data/csv")
async def add_data_csv(file: UploadFile= File(...)):
    """From file, transform"""

    start_time = time.time()
    # logger.info(f"Adding data to db with file : {file.filename}")
    if not file:
        raise ValueError("Adress is required")
    if not "csv" in file.filename:
        raise ValueError("You must provide a csv file")

    status = save_to_db(file.file)
    logger.info("--- %s seconds ---" % (time.time() - start_time))
    if status:
        return "Everything ok"


@router.get("/")
async def root():
    return "Hello World"


@router.get("/health")
async def health():
    """Test liveliness of the app"""
    return "The api is running"


def save_to_db(file):
    database = next(get_db())
    # logger.info("Converting to df")
    network_cov_df = csv_to_dataframe(file)
    # logger.info("Converted to df")

    operators = extract_operators(network_cov_df)
    for operator in operators:
        try:
            op = crud.get_operator(database=database, operator=operator)
            if not op:
                op = crud.create_operator(database=database, operator=operator)
        except Exception as exc:
            logger.exception(msg=f"Error during creation of operator {operator}")
            return False

    networks = extract_networks(network_cov_df)
    for network in networks:
        try:
            op = crud.get_network(database=database, network=network)
            if not op:
                op = crud.create_network(database=database, network=network)
        except Exception as exc:
            logger.exception(msg=f"Error during creation of network {network}")
            return False
    network_cov_df = add_city_to_df(network_cov_df)
    cities = extract_cities(network_cov_df)
    for city in cities:
        try:
            op = crud.get_city(database=database, city=city)
            if not op:
                op = crud.create_city(database=database, city=city)
        except Exception as exc:
            logger.exception(msg=f"Error during creation of city {city}")
            return False
    try:
        # logger.debug("before applying network coverage creation")
        network_cov_df.apply(lambda row: crud.create_coverage_networks(database=database, row=row), axis=1)
        # logger.debug("after applying network coverage creation")

    except Exception as exc:
        logger.exception(msg=f"Error during creation of network_coverage")
        return False
    return True


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

app.include_router(router=router)