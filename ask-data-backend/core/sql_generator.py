"""
Simple database-agnostic SQL generator.
Just orchestrates table selection and SQL generation - no hardcoded logic.
"""

import logging
import time
from typing import Optional
from dataclasses import dataclass

from core.schema_manager import SchemaManager
from core.table_selector import TableSelector
from services.azure_openai_service import AzureOpenAIService

logger = logging.getLogger(__name__)

@dataclass
class SQLResult:
    """Simple SQL generation result."""
    success: bool
    sql_query: str
    selected_tables: list
    error_message: Optional[str] = None
    execution_time_ms: int = 0

class SQLGenerator:
    """Simple SQL generator - just coordinates LLM calls."""
    
    def __init__(
        self, 
        schema_manager: SchemaManager,
        table_selector: TableSelector,
        azure_service: AzureOpenAIService
    ):
        self.schema_manager = schema_manager
        self.table_selector = table_selector
        self.azure_service = azure_service
        
        logger.info("SQL generator initialized")
    
    async def generate_sql(self, user_question: str, max_tables: int = 4) -> SQLResult:
        """Generate SQL from user question."""
        start_time = time.time()
        
        try:
            # Step 1: Select tables
            table_result = await self.table_selector.select_tables(
                user_question=user_question,
                max_tables=max_tables
            )
            
            if not table_result.selected_tables:
                return SQLResult(
                    success=False,
                    sql_query="",
                    selected_tables=[],
                    error_message="No relevant tables found",
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Step 2: Get schema context
            schema_context = self.schema_manager.get_full_schema_text(
                table_result.selected_tables
            )
            
            # Step 3: Generate SQL
            sql_result = await self.azure_service.call_for_sql_generation(
                question=user_question,
                schema_context=schema_context,
                selected_tables=table_result.selected_tables
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            if sql_result.success:
                return SQLResult(
                    success=True,
                    sql_query=sql_result.content,
                    selected_tables=table_result.selected_tables,
                    execution_time_ms=execution_time
                )
            else:
                return SQLResult(
                    success=False,
                    sql_query="",
                    selected_tables=table_result.selected_tables,
                    error_message=sql_result.error_message,
                    execution_time_ms=execution_time
                )
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return SQLResult(
                success=False,
                sql_query="",
                selected_tables=[],
                error_message=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )