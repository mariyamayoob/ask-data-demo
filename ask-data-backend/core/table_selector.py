"""
Simple database-agnostic table selector.
Uses only JSON configuration - no hardcoded logic.
"""

import logging
from typing import List
from dataclasses import dataclass

from core.schema_manager import SchemaManager
from services.azure_openai_service import AzureOpenAIService
from core.config_loader import get_config_manager

logger = logging.getLogger(__name__)

@dataclass
class TableSelectionResult:
    """Simple result container."""
    selected_tables: List[str]
    reasoning: str
    fallback_used: bool

class TableSelector:
    """Simple table selector driven entirely by JSON config."""
    
    def __init__(self, schema_manager: SchemaManager, azure_service: AzureOpenAIService):
        self.schema_manager = schema_manager
        self.azure_service = azure_service
        self.config_manager = get_config_manager()
        
        logger.info("Table selector initialized")
    
    async def select_tables(self, user_question: str, max_tables: int = 4) -> TableSelectionResult:
        """Select relevant tables for a question."""
        
        try:
            # Try LLM selection
            table_summaries = self.schema_manager.get_table_summaries_text()
            
            llm_result = await self.azure_service.call_for_table_selection(
                question=user_question,
                table_summaries=table_summaries
            )
            
            if llm_result.success:
                selected_tables = self._parse_table_names(llm_result.content)
                if selected_tables:
                    # Limit and prioritize
                    final_tables = self._prioritize_tables(selected_tables)[:max_tables]
                    
                    return TableSelectionResult(
                        selected_tables=final_tables,
                        reasoning="LLM selection",
                        fallback_used=False
                    )
            
            # Keyword fallback
            keyword_tables = self._keyword_selection(user_question)
            final_tables = self._prioritize_tables(keyword_tables)[:max_tables]
            
            return TableSelectionResult(
                selected_tables=final_tables,
                reasoning="Keyword fallback",
                fallback_used=True
            )
            
        except Exception as e:
            logger.error(f"Table selection failed: {e}")
            
            # Emergency fallback from config
            emergency_tables = self.config_manager.get_default_tables("emergency_fallback")
            
            return TableSelectionResult(
                selected_tables=emergency_tables[:max_tables],
                reasoning=f"Emergency fallback: {str(e)}",
                fallback_used=True
            )
    
    def _parse_table_names(self, llm_response: str) -> List[str]:
        """Extract table names from LLM response."""
        # Simple parsing - just split and clean
        if ":" in llm_response:
            llm_response = llm_response.split(":", 1)[1]
        
        # Split by common separators
        parts = llm_response.replace("\n", ",").split(",")
        
        # Clean and validate
        available_tables = set(self.schema_manager.get_available_tables())
        valid_tables = []
        
        for part in parts:
            table_name = part.strip().strip('"\'[]()- ')
            if table_name in available_tables:
                valid_tables.append(table_name)
        
        return valid_tables
    
    def _keyword_selection(self, question: str) -> List[str]:
        """Simple keyword-based table selection."""
        question_lower = question.lower()
        candidate_tables = []
        
        # Check each table's keywords
        for table_name in self.schema_manager.get_available_tables():
            table_info = self.schema_manager.get_table_info(table_name)
            keywords = table_info.get("keywords", [])
            
            # Simple keyword matching
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    if table_name not in candidate_tables:
                        candidate_tables.append(table_name)
                    break
        
        # If no matches, use fallback from config
        if not candidate_tables:
            candidate_tables = self.config_manager.get_default_tables("keyword_fallback")
        
        return candidate_tables
    
    def _prioritize_tables(self, tables: List[str]) -> List[str]:
        """Sort tables by priority from config."""
        return self.config_manager.get_sorted_tables_by_priority(tables)