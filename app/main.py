import json
import typing

import requests
import uvicorn
from fastapi import FastAPI, APIRouter, UploadFile
from starlette.responses import JSONResponse

from app.utils import lat_long_to_lambert93


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
    data_gouv_coords = data_gouv_adress.get("features")[0].get("geometry").get("coordinates")
    lambert_coords = lat_long_to_lambert93(data_gouv_coords[0], data_gouv_coords[1])
    return res.json()

@router.get("/transform/file/lambert/wsg84")
async def transform_file_lambert_to_wsg84(file: UploadFile):
    """From file """
    if not adress:
        raise ValueError("Adress is required")

    url_data_gouv = "https://api-adresse.data.gouv.fr/search/"
    params_data_gouv = {"q": adress, "autocomplete":0}
    res = requests.get(url=url_data_gouv, params=params_data_gouv)
    data_gouv_adress = res.json()
    data_gouv_coords = data_gouv_adress.get("features")[0].get("geometry").get("coordinates")
    lambert_coords = lat_long_to_lambert93(data_gouv_coords[0], data_gouv_coords[1])
    return res.json()

@router.get("/")
async def root():
    return "Hello World"


@router.get("/health")
async def health():
    """Test liveliness of the app"""
    return "The api is running"


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

app.include_router(router=router)