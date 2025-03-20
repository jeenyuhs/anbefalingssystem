import sqlalchemy
from fastapi import FastAPI

import settings

application: FastAPI
engine = sqlalchemy.create_engine(f"mariadb+mariadbconnector://{settings.DB_USER}:{settings.DB_PASS}@127.0.0.1:{settings.DB_PORT}/{settings.DB_NAME}")