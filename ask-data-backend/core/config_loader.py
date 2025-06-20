"""
Simplified configuration loader with three-file architecture.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SystemConfig:
    """Simple JSON configuration loader."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info(f"Loaded config from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config {self.config_path}: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key path (dot notation)."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration."""
        return self._config.copy()

class ConfigManager:
    """Manages all three configuration files."""
    
    def __init__(self, 
                 db_syntax_path: str = "/app/data/db_syntax_helpers.json",
                 domain_config_path: str = "/app/data/domain_config.json", 
                 schema_path: str = "/app/data/schema_metadata.json"):
        
        self.db_syntax = SystemConfig(db_syntax_path)
        self.domain = SystemConfig(domain_config_path)
        self.schema = SystemConfig(schema_path)
        
        logger.info("ConfigManager initialized with three config files")
    
    # Database syntax helpers (generic framework)
    def get_database_config(self, db_type: str) -> Dict[str, Any]:
        """Get database-specific syntax configuration."""
        return self.db_syntax.get(f"database_config.{db_type}", {})
    
    def get_execution_config(self) -> Dict[str, Any]:
        """Get execution settings."""
        return self.db_syntax.get("execution", {})
    
    # Domain-specific configuration  
    def get_default_tables(self, fallback_type: str) -> List[str]:
        """Get default tables for fallback scenarios."""
        return self.domain.get(f"default_tables.{fallback_type}", [])
    
    def get_table_priorities(self) -> Dict[str, int]:
        """Get table priority mappings."""
        return self.domain.get("table_priorities", {})
    
    def get_table_hints(self, table_name: str) -> List[str]:
        """Get domain-specific hints for a table."""
        return self.domain.get(f"table_hints.{table_name}", [])
    
    def get_business_rules(self) -> Dict[str, Any]:
        """Get business rules and thresholds."""
        return self.domain.get("business_rules", {})
    
    def get_test_questions(self, category: str) -> List[str]:
        """Get test questions for a category."""
        return self.domain.get(f"test_questions.{category}", [])
    
    def get_query_keywords(self, category: str) -> List[str]:
        """Get query keywords for a category."""
        return self.domain.get(f"query_keywords.{category}", [])
    
    def get_common_filters(self) -> Dict[str, str]:
        """Get common SQL filters."""
        return self.domain.get("common_filters", {})
    
    # Schema metadata
    def get_schema_all(self) -> Dict[str, Any]:
        """Get complete schema metadata."""
        return self.schema.get_all()
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for specific table."""
        return self.schema.get(table_name, {})
    
    # Combined operations
    def get_sorted_tables_by_priority(self, table_list: List[str]) -> List[str]:
        """Sort tables by their priority scores (highest first)."""
        priorities = self.get_table_priorities()
        return sorted(table_list, key=lambda t: priorities.get(t, 5), reverse=True)

# Global instances
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get configuration manager instance (singleton pattern)."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# Legacy support functions
def get_system_config() -> SystemConfig:
    """Legacy support - returns domain config."""
    return get_config_manager().domain

def get_schema_config() -> SystemConfig:
    """Legacy support - returns schema config."""
    return get_config_manager().schema