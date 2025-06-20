"""
Simplified Database connection for AskData application.
Basic MySQL connectivity with essential functionality only.
"""

import logging
import time
from typing import Dict, Any, Tuple

import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple database manager with basic MySQL connectivity."""
    
    def __init__(self):
        self.host = settings.database_host
        self.port = settings.database_port
        self.user = settings.database_user
        self.password = settings.database_password
        self.database = settings.database_name
        self._engine = None
        
        logger.info(f"Database manager initialized for {self.host}:{self.port}/{self.database}")
    
    @property
    def engine(self):
        """Get SQLAlchemy engine."""
        if self._engine is None:
            connection_string = (
                f"mysql+pymysql://{self.user}:{self.password}@"
                f"{self.host}:{self.port}/{self.database}"
            )
            self._engine = create_engine(connection_string, pool_pre_ping=True)
            logger.info("Database engine created")
        return self._engine
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                if result and result[0] == 1:
                    return True, "Database connection successful"
                else:
                    return False, "Unexpected result from database"
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False, f"Connection failed: {str(e)}"
    
    def execute_query_sync(self, sql: str) -> Dict[str, Any]:
        """Execute SQL and return results."""
        start_time = time.time()
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                
                if result.returns_rows:
                    # SELECT query
                    rows = result.fetchall()
                    columns = list(result.keys())
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    return {
                        "success": True,
                        "data": data,
                        "columns": columns,
                        "row_count": len(data),
                        "execution_time_ms": int((time.time() - start_time) * 1000)
                    }
                else:
                    # Non-SELECT query
                    return {
                        "success": True,
                        "data": [],
                        "columns": [],
                        "row_count": result.rowcount,
                        "execution_time_ms": int((time.time() - start_time) * 1000)
                    }
                    
        except SQLAlchemyError as e:
            logger.error(f"SQL execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

# Global instance
db_manager = DatabaseManager()

def get_database_manager() -> DatabaseManager:
    """Get database manager instance."""
    return db_manager