# app/routes/db_routes.py

from fastapi import APIRouter, Request, HTTPException
from canonmap.connectors.mysql_connector import DatabaseManager, CreateDatabaseRequest
from canonmap.exceptions import DatabaseManagerError

router = APIRouter(prefix="/database", tags=["database"])

@router.post("/create-database")
async def create_database(request: Request, create_database_request: CreateDatabaseRequest):
    try:
        connector = request.app.state.mysql_connector
        db_manager = DatabaseManager(connector)
        db_manager.create_database(create_database_request)
        return {"message": f"Database {create_database_request.db_name} created"}
    except DatabaseManagerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/get-databases")
async def get_databases(request: Request):
    try:
        connector = request.app.state.mysql_connector
        db_manager = DatabaseManager(connector)
        return db_manager.get_databases()
    except DatabaseManagerError as e:
        raise HTTPException(status_code=400, detail=str(e))

