"""
Simple database-agnostic query executor.
Just executes SQL safely - no hardcoded assumptions.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Simple execution result."""
    success: bool
    data: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: int
    error_message: Optional[str] = None

class QueryExecutor:
    """Simple query executor - database agnostic safety checks."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Get limits from config (with defaults if config not available)
        try:
            from core.config_loader import get_config_manager
            config_manager = get_config_manager()
            execution_config = config_manager.get_execution_config()
            self.max_rows = execution_config.get("max_rows", 1000)
            self.timeout_seconds = execution_config.get("timeout_seconds", 30)
            self.dangerous_words = execution_config.get("dangerous_words", [
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE'
            ])
        except Exception as e:
            logger.warning(f"Could not load config, using defaults: {e}")
            self.max_rows = 1000
            self.timeout_seconds = 30
            self.dangerous_words = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        
        logger.info("Query executor initialized")
    
    async def execute_sql(self, sql: str) -> ExecutionResult:
        """Execute SQL with safety checks."""
        start_time = time.time()
        
        try:
            # Basic safety check
            if not self._is_safe_query(sql):
                return ExecutionResult(
                    success=False,
                    data=[],
                    row_count=0,
                    execution_time_ms=0,
                    error_message="Query not safe for execution"
                )
            
            # Add row limit
            limited_sql = self._add_row_limit(sql)
            
            # Execute query
            result = self.db_manager.execute_query_sync(limited_sql)
            execution_time = int((time.time() - start_time) * 1000)
            
            if result["success"]:
                # Format data for JSON
                formatted_data = self._format_data(result["data"])
                
                return ExecutionResult(
                    success=True,
                    data=formatted_data,
                    row_count=len(formatted_data),
                    execution_time_ms=execution_time
                )
            else:
                return ExecutionResult(
                    success=False,
                    data=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                    error_message=result.get("error", "Unknown database error")
                )
                
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Query execution failed: {e}")
            
            return ExecutionResult(
                success=False,
                data=[],
                row_count=0,
                execution_time_ms=execution_time,
                error_message=str(e)
            )
    
    def _is_safe_query(self, sql: str) -> bool:
        """Basic safety check - SELECT only, configurable dangerous words."""
        sql_upper = sql.upper().strip()
        
        # Must be SELECT
        if not sql_upper.startswith('SELECT'):
            logger.warning(f"Query rejected: Does not start with SELECT")
            return False
        
        # Split SQL into words to avoid false positives
        sql_words = set(word.strip() for word in sql_upper.split())
        
        for word in self.dangerous_words:
            if word in sql_words:  # Check whole words only
                logger.warning(f"Query rejected: Contains dangerous word '{word}'")
                return False
        
        logger.debug(f"Query accepted as safe: {sql[:100]}...")
        return True
    
    def _add_row_limit(self, sql: str) -> str:
        """Add row limit if not present."""
        sql_upper = sql.upper()
        
        # Check if LIMIT already exists
        if 'LIMIT' in sql_upper:
            return sql
        
        # Add LIMIT
        sql = sql.rstrip(';')
        return f"{sql} LIMIT {self.max_rows};"
    
    def _format_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for JSON serialization - database agnostic."""
        if not data:
            return []
        
        formatted = []
        for row in data:
            formatted_row = {}
            for key, value in row.items():
                # Handle common data types
                if isinstance(value, (date, datetime)):
                    formatted_row[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    formatted_row[key] = float(value)
                elif isinstance(value, bytes):
                    formatted_row[key] = value.decode('utf-8', errors='ignore')
                elif value is None:
                    formatted_row[key] = None
                else:
                    formatted_row[key] = value
            formatted.append(formatted_row)
        
        return formatted