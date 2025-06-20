"""
Simple database-agnostic REST API routes.
Just essential endpoints with minimal dependencies.
"""

import logging
import time
from typing import List, Dict, Optional, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.schema_manager import SchemaManager
from core.table_selector import TableSelector
from core.sql_generator import SQLGenerator
from core.query_executor import QueryExecutor
from services.azure_openai_service import AzureOpenAIService
from config.database import get_database_manager
from config.settings import settings

logger = logging.getLogger(__name__)

# Simple request/response models
class SQLRequest(BaseModel):
    question: str
    max_tables: int = 4
    execute_sql: bool = True

class SQLResponse(BaseModel):
    success: bool
    sql_query: str
    selected_tables: List[str]
    executed: bool
    data: List[Dict[str, Any]] = []
    row_count: int = 0
    execution_time_ms: int
    error_message: str = ""

# Router
router = APIRouter()

# Simple component container
class Components:
    def __init__(self):
        self.sql_generator = None
        self.query_executor = None
        self.schema_manager = None
        self.db_manager = None
        self._initialized = False
    
    def initialize(self):
        """Initialize components once."""
        if self._initialized:
            return
        
        logger.info("Initializing components...")
        
        # Initialize in order
        self.schema_manager = SchemaManager(settings.schema_metadata_path)
        
        azure_service = AzureOpenAIService(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint
        )
        
        table_selector = TableSelector(self.schema_manager, azure_service)
        
        self.sql_generator = SQLGenerator(
            self.schema_manager, 
            table_selector, 
            azure_service
        )
        
        self.db_manager = get_database_manager()
        self.query_executor = QueryExecutor(self.db_manager)
        
        self._initialized = True
        logger.info("Components initialized successfully")

# Global components
components = Components()

@router.post("/generate-sql", response_model=SQLResponse)
async def generate_sql(request: SQLRequest):
    """Main endpoint: Generate and optionally execute SQL."""
    start_time = time.time()
    
    try:
        # Initialize if needed
        components.initialize()
        
        # Generate SQL
        sql_result = await components.sql_generator.generate_sql(
            user_question=request.question,
            max_tables=request.max_tables
        )
        
        # Prepare response
        response_data = {
            "success": sql_result.success,
            "sql_query": sql_result.sql_query,
            "selected_tables": sql_result.selected_tables,
            "executed": False,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "error_message": sql_result.error_message or ""
        }
        
        # Execute if requested and generation succeeded
        if request.execute_sql and sql_result.success and sql_result.sql_query:
            execution_result = await components.query_executor.execute_sql(sql_result.sql_query)
            
            response_data["executed"] = True
            
            if execution_result.success:
                response_data.update({
                    "data": execution_result.data,
                    "row_count": execution_result.row_count
                })
            else:
                response_data["success"] = False
                response_data["error_message"] = execution_result.error_message
        
        return SQLResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Generate SQL failed: {e}")
        return SQLResponse(
            success=False,
            sql_query="",
            selected_tables=[],
            executed=False,
            execution_time_ms=int((time.time() - start_time) * 1000),
            error_message=str(e)
        )

@router.get("/health")
async def health_check():
    """Simple health check."""
    try:
        components.initialize()
        
        # Test database connection
        db_success, db_message = components.db_manager.test_connection()
        
        return {
            "status": "healthy" if db_success else "degraded",
            "database": db_message,
            "tables_available": components.schema_manager.get_table_count(),
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

@router.get("/schema")
async def get_schema_info():
    """Get available tables and basic info."""
    try:
        components.initialize()
        
        return {
            "tables": components.schema_manager.get_available_tables(),
            "total_tables": components.schema_manager.get_table_count(),
            "schema_summary": components.schema_manager.get_table_summaries_text()[:500] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))