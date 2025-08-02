# src/canonmap/connectors/mysql_connector/managers/database_manager/requests/requests.py

from typing import Optional, Union, Any
from pathlib import Path
import pandas as pd

from pydantic import BaseModel, field_validator, ConfigDict
from canonmap.connectors.mysql_connector.validators.models import IfExists

class CreateDatabaseRequest(BaseModel):
    database_name: str
    autoconnect: bool = False
    if_exists: IfExists = IfExists.ERROR

    @field_validator("database_name")
    def validate_db_name(cls, v: str) -> str:
        if not v:
            raise ValueError("Database name cannot be empty")
        return v
    
    @field_validator("autoconnect")
    def validate_autoconnect(cls, v: bool) -> bool:
        return v
    
class DropDatabaseRequest(BaseModel):
    database_name: str

    @field_validator("database_name")
    def validate_database_name(cls, v: str) -> str:
        if not v:
            raise ValueError("Database name cannot be empty")
        return v
    
# def create_mysql_ddl(table_name: str, data: Union[str, pd.DataFrame, list, Path], save_dir=None):

class CreateDDLRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    table_name: str
    data: Union[str, pd.DataFrame, list, Path]
    save_dir: Optional[str] = None
