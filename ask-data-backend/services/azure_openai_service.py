"""
Simplified Azure OpenAI Service for AskData application.
Handles table selection and SQL generation with basic error handling.
"""

import logging
import time
import ssl
import os
import asyncio
from typing import Optional, Dict
from dataclasses import dataclass

from openai import AzureOpenAI
import httpx

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Simple response from LLM."""
    content: str
    model: str
    tokens_used: int
    response_time_ms: int
    success: bool
    error_message: Optional[str] = None

class AzureOpenAIService:
    """
    Simple Azure OpenAI service for table selection and SQL generation.
    """
    
    def __init__(self, api_key: str, endpoint: str, api_version: str = "2024-02-01"):
        # Use system CA bundle for corporate proxies
        ca_bundle = '/etc/ssl/certs/ca-certificates.crt'
        
        if os.path.exists(ca_bundle):
            ssl_context = ssl.create_default_context(cafile=ca_bundle)
            verify = ssl_context
        else:
            verify = True
        
        http_client = httpx.Client(
            verify=verify,
            timeout=httpx.Timeout(60.0),
            trust_env=True,
            follow_redirects=True
        )
        
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
            http_client=http_client
        )
        
        self.deployment_name = "gpt-4"
        logger.info(f"Azure OpenAI service initialized")
    
    async def call_for_table_selection(self, question: str, table_summaries: str) -> LLMResponse:
        """Use LLM for table selection."""
        start_time = time.time()
        
        try:
            prompt = f"""Given this user question: "{question}"

Available tables:
{table_summaries}

Select the 2-4 most relevant tables needed to answer this question.
Return only table names, comma-separated.

Selected tables:"""

            response = await self._make_api_call(
                messages=[
                    {"role": "system", "content": "You are a database expert. Select only the most relevant tables for SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            return response
            
        except Exception as e:
            return self._error_response(start_time, str(e))
    
    async def call_for_sql_generation(
        self, 
        question: str, 
        schema_context: str, 
        selected_tables: list
    ) -> LLMResponse:
        """Use LLM for SQL generation."""
        start_time = time.time()
        
        try:
            prompt = f"""Generate MySQL SQL to answer: "{question}"

Database Schema:
{schema_context}

Requirements:
- Use proper JOINs based on foreign key relationships
- Include appropriate WHERE clauses
- Use table aliases for readability
- Return only the SQL query

SQL Query:"""

            response = await self._make_api_call(
                messages=[
                    {"role": "system", "content": "You are an expert MySQL developer. Generate only valid SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            if response.success:
                # Clean SQL response
                response.content = self._clean_sql(response.content)
            
            return response
            
        except Exception as e:
            return self._error_response(start_time, str(e))
    
    async def _make_api_call(self, messages: list, max_tokens: int, temperature: float) -> LLMResponse:
        """Make API call to Azure OpenAI."""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            response_time = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=tokens,
                response_time_ms=response_time,
                success=True
            )
            
        except Exception as e:
            return self._error_response(start_time, str(e))
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL response."""
        content = sql.strip()
        
        # Remove markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            lines = lines[1:]  # Remove first line
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove last line
            content = "\n".join(lines).strip()
        
        # Remove SQL: prefix
        if content.upper().startswith("SQL:"):
            content = content[4:].strip()
        
        # Ensure semicolon
        if content and not content.rstrip().endswith(";"):
            content = content.rstrip() + ";"
        
        return content
    
    def _error_response(self, start_time: float, error: str) -> LLMResponse:
        """Create error response."""
        response_time = int((time.time() - start_time) * 1000)
        
        return LLMResponse(
            content="",
            model=self.deployment_name,
            tokens_used=0,
            response_time_ms=response_time,
            success=False,
            error_message=error
        )
    
    def test_connection(self):
        """Test Azure OpenAI connection."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Test connection. Reply with 'OK'."}],
                max_tokens=10,
                temperature=0
            )
            
            if response.choices and response.choices[0].message.content:
                return True, "Connection successful"
            else:
                return False, "No response received"
                
        except Exception as e:
            return False, f"Connection failed: {str(e)}"