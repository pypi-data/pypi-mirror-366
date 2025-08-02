# src/canonmap/connectors/mysql_connector/managers/database_manager/database_manager.py

import logging

from canonmap.connectors.mysql_connector.mysql_connector import MySQLConnector
from canonmap.connectors.mysql_connector.managers.database_manager.validators.requests import CreateDatabaseRequest
from canonmap.connectors.mysql_connector.managers.database_manager.utils.create_database import create_database_util
from canonmap.connectors.mysql_connector.managers.database_manager.validators.requests import DropDatabaseRequest
from canonmap.connectors.mysql_connector.managers.database_manager.utils.drop_database import drop_database_util
from canonmap.connectors.mysql_connector.utils.check_existence import check_database_existence
from canonmap.exceptions import DatabaseManagerError

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, connector: MySQLConnector):
        self.connector = connector

    def create_database(self, request: CreateDatabaseRequest) -> None:
        if check_database_existence(request.database_name, self.connector):
            raise DatabaseManagerError(f"Database {request.database_name} already exists")
        return create_database_util(request, self.connector)
        
    def drop_database(self, request: DropDatabaseRequest) -> None:
        return drop_database_util(request, self.connector)

