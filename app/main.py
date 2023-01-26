import json
import typing

import uvicorn
from fastapi import FastAPI, APIRouter
from starlette.responses import JSONResponse



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