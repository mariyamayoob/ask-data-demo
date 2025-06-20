"""
Simple database-agnostic schema manager.
Just reads JSON schema and formats it - no hardcoded assumptions.
"""

import logging
from typing import Dict, List
from core.config_loader import get_config_manager

logger = logging.getLogger(__name__)

class SchemaManager:
    """Simple schema manager - just reads and formats JSON."""
    
    def __init__(self, schema_path: str):
        # schema_path parameter is ignored - we use the config manager
        self.config_manager = get_config_manager()
        
        # Validate we have tables
        tables = self.get_available_tables()
        if not tables:
            raise ValueError("No tables found in schema configuration")
        
        logger.info(f"Schema manager loaded {len(tables)} tables")
    
    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        schema = self.config_manager.get_schema_all()
        return list(schema.keys())
    
    def get_table_count(self) -> int:
        """Get total number of tables."""
        return len(self.get_available_tables())
    
    def get_table_info(self, table_name: str) -> Dict:
        """Get all information for a table."""
        return self.config_manager.get_table_schema(table_name)
    
    def get_table_summaries_text(self) -> str:
        """Get formatted text summary of all tables."""
        lines = []
        
        for table_name in self.get_available_tables():
            table_info = self.get_table_info(table_name)
            
            # Basic info
            description = table_info.get("description", "")
            keywords = table_info.get("keywords", [])
            
            lines.append(f"• {table_name}: {description}")
            if keywords:
                lines.append(f"  Keywords: {', '.join(keywords[:6])}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_full_schema_text(self, table_names: List[str]) -> str:
        """Get detailed schema for selected tables."""
        lines = []
        
        for table_name in table_names:
            table_info = self.get_table_info(table_name)
            if not table_info:
                continue
            
            lines.append(f"=== {table_name.upper()} ===")
            
            # Description and purpose
            description = table_info.get("description", "")
            business_purpose = table_info.get("business_purpose", "")
            
            if description:
                lines.append(f"Description: {description}")
            if business_purpose:
                lines.append(f"Business Purpose: {business_purpose}")
            lines.append("")
            
            # Columns
            columns = table_info.get("columns", {})
            if columns:
                lines.append("Columns:")
                for col_name, col_info in columns.items():
                    col_type = col_info.get("type", "")
                    col_desc = col_info.get("description", "")
                    
                    line = f"  - {col_name}"
                    if col_type:
                        line += f" ({col_type})"
                    if col_desc:
                        line += f": {col_desc}"
                    
                    # Add enum values if present
                    enum_values = col_info.get("enum_values", [])
                    if enum_values:
                        line += f" [Values: {', '.join(enum_values)}]"
                    
                    lines.append(line)
                lines.append("")
            
            # Table hints (from domain config)
            table_hints = self.config_manager.get_table_hints(table_name)
            if table_hints:
                lines.append("SQL Hints:")
                for hint in table_hints:
                    lines.append(f"  - {hint}")
                lines.append("")
            
            # Common joins (from schema)
            relationships = table_info.get("relationships", {})
            common_joins = relationships.get("common_joins", [])
            if common_joins:
                lines.append("Common JOINs:")
                for join in common_joins[:3]:  # Limit to 3
                    purpose = join.get("purpose", "")
                    sql_example = join.get("sql_example", "")
                    if purpose:
                        lines.append(f"  - {purpose}")
                    if sql_example:
                        lines.append(f"    {sql_example}")
                lines.append("")
            
            lines.append("-" * 50)
            lines.append("")
        
        return "\n".join(lines)