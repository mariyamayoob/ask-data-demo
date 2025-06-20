"""
Simple database-agnostic configuration settings.
Only essential settings - no hardcoded assumptions.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Simple application settings."""
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-01"
    
    # Database Configuration (generic)
    database_type: str = "mysql"  # mysql, postgresql, sqlite, etc.
    database_host: str
    database_port: int = 3306
    database_user: str
    database_password: str
    database_name: str
    
    # Configuration Files
    schema_metadata_path: str = "/app/data/schema_metadata.json"
    system_config_path: str = "/app/data/system_config.json"
    
    # LLM Configuration
    table_selection_model: str = "gpt-4"
    sql_generation_model: str = "gpt-4"
    max_tokens_table_selection: int = 100
    max_tokens_sql_generation: int = 1000
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8015
    debug_mode: bool = False
    
    # Security Configuration
    allowed_origins: list[str] = ["*"]
    api_key_header: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_settings()
        
    def _validate_settings(self):
        """Validate critical settings."""
        
        # Validate Azure OpenAI settings
        if not self.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required")
        if not self.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required")
            
        # Validate schema file exists
        schema_path = Path(self.schema_metadata_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_metadata_path}")
            
        # Validate database settings
        if not all([self.database_host, self.database_user, self.database_password]):
            raise ValueError("Database connection settings (host, user, password) are required")
    
    @property
    def database_url(self) -> str:
        """Generate database connection URL."""
        if self.database_type.lower() == "mysql":
            return f"mysql+pymysql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        elif self.database_type.lower() == "postgresql":
            return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        elif self.database_type.lower() == "sqlite":
            return f"sqlite:///{self.database_name}"
        else:
            # Generic format
            return f"{self.database_type}://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @property
    def azure_openai_config(self) -> dict:
        """Get Azure OpenAI configuration."""
        return {
            "api_key": self.azure_openai_api_key,
            "azure_endpoint": self.azure_openai_endpoint,
            "api_version": self.azure_openai_api_version
        }
    

# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance."""
    return settings