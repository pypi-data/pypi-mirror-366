# app/context.py

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from canonmap.connectors.mysql_connector import (
    MySQLConnector,
    MySQLConnectorConfig,
    MySQLConnectionMethod,
    Matcher,
    FieldManager,
    CreateHelperFieldsRequest,
)

logger = logging.getLogger(__name__)

load_dotenv(override=True)

ENV = os.getenv("ENV", "dev")
MYSQL_USER = os.getenv("DB_USER", "")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
MYSQL_HOST = os.getenv("DB_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))
MYSQL_UNIX_SOCKET = os.getenv("GCP_CLOUD_SQL_UNIX_SOCKET", "")

if ENV.lower().strip() == "prod":
    mysql_config = MySQLConnectorConfig(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        unix_socket=MYSQL_UNIX_SOCKET,
        connection_method=MySQLConnectionMethod.SOCKET,
        autocommit=True,
    )
else:
    mysql_config = MySQLConnectorConfig(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        connection_method=MySQLConnectionMethod.TCP,
        autocommit=True,
    )
    mysql_connector = MySQLConnector(mysql_config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    mysql_connector.connect()
    app.state.mysql_connector = mysql_connector
    app.state.matcher = Matcher(mysql_connector)
    logger.info("🎉 API initialized!")
    yield
    # On shutdown
    mysql_connector.close()
    logger.info("🛑 API shutdown.")

app = FastAPI(lifespan=lifespan)