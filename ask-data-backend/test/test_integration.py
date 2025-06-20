#!/usr/bin/env python3
"""
Simple integration test for the complete pipeline - database agnostic.
"""

import asyncio
from core.schema_manager import SchemaManager
from core.table_selector import TableSelector
from core.sql_generator import SQLGenerator
from core.config_loader import get_system_config
from services.azure_openai_service import AzureOpenAIService
from config.settings import settings

async def test_pipeline():
    """Test the complete pipeline without database execution."""
    print("Testing Complete Pipeline")
    print("=" * 35)
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        
        schema_manager = SchemaManager(settings.schema_metadata_path)
        config = get_system_config()
        
        azure_service = AzureOpenAIService(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint
        )
        
        table_selector = TableSelector(schema_manager, azure_service)
        sql_generator = SQLGenerator(schema_manager, table_selector, azure_service)
        
        print(f" Components initialized")
        print(f"  📊 Schema: {schema_manager.get_table_count()} tables")
        print(f"  🤖 Azure OpenAI: Connected")
        print()
        
        # Get test questions from config
        basic_questions = config.get("test_questions.basic", [
            "Show me recent records", "List active items"  # fallback
        ])
        
        print(f"Running {len(basic_questions)} test cases from config...")
        print()
        
        for i, question in enumerate(basic_questions, 1):
            print(f"Test {i}: {question}")
            
            # Test SQL generation (no execution for safety)
            result = await sql_generator.generate_sql(
                user_question=question
            )
            
            print(f" Success: {result.success}")
            if result.success:
                print(f"  Tables: {result.selected_tables}")
                print(f"  Time: {result.execution_time_ms}ms")
                print(f"  SQL: {result.sql_query[:80]}...")
            else:
                print(f"   Error: {result.error_message}")
            
            print()
        
        # Test advanced questions if available
        advanced_questions = config.get("test_questions.advanced", [])
        if advanced_questions:
            print("🎯 Testing advanced questions...")
            
            for question in advanced_questions[:2]:  # Just test first 2
                print(f"  Advanced: {question}")
                result = await sql_generator.generate_sql(user_question=question)
                print(f"   Success: {result.success}")
                if not result.success:
                    print(f"     Error: {result.error_message}")
            print()
        
        print("Pipeline test completed!")
        
    except Exception as e:
        print(f" Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pipeline())