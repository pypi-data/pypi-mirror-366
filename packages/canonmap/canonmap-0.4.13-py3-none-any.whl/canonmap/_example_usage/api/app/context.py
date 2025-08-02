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

def validate_environment():
    """Validate that required environment variables are set."""
    missing_vars = []
    
    # Check required variables
    if not os.getenv("DB_USER"):
        missing_vars.append("DB_USER")
    if not os.getenv("DB_PASSWORD"):
        missing_vars.append("DB_PASSWORD")
    if not os.getenv("COHERE_API_KEY"):
        missing_vars.append("COHERE_API_KEY")
    
    if missing_vars:
        error_msg = f"""
🚨 Missing required environment variables: {', '.join(missing_vars)}

📋 Setup Instructions:
1. Copy the example environment file:
   cp .env.example .env

2. Edit .env and fill in your values:
   - DB_USER: Your MySQL username
   - DB_PASSWORD: Your MySQL password  
   - COHERE_API_KEY: Your Cohere API key (get one at https://cohere.ai)

3. Restart the application

💡 For development, you can use:
   - DB_USER: root
   - DB_PASSWORD: (your local MySQL password)
   - COHERE_API_KEY: (your Cohere API key)

🔧 Need help? Check the README or visit: https://github.com/vinceberry/canonmap
"""
        logger.error(error_msg)
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate environment on startup
validate_environment()

ENV = os.getenv("ENV", "dev")
MYSQL_USER = os.getenv("DB_USER", "")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "")
MYSQL_HOST = os.getenv("DB_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("DB_PORT", "3306"))
MYSQL_UNIX_SOCKET = os.getenv("DB_UNIX_SOCKET", "")

try:
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
except Exception as e:
    logger.error(f"""
❌ Failed to initialize MySQL connector: {e}

🔧 Troubleshooting:
1. Check your .env file has correct database credentials
2. Ensure MySQL server is running
3. Verify network connectivity to {MYSQL_HOST}:{MYSQL_PORT}
4. For production, check DB_UNIX_SOCKET path

💡 Development setup:
   - Install MySQL locally
   - Create a database
   - Update .env with your credentials
""")
    raise

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