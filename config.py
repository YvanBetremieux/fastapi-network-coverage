from typing import Union

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class Settings(BaseSettings):
    DB_STRING: Union[PostgresDsn, str]
    SCHEMA: str


settings = Settings()