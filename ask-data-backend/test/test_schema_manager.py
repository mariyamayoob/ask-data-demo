#!/usr/bin/env python3
"""
Simple test for SchemaManager - database agnostic.
"""

from core.schema_manager import SchemaManager
from config.settings import settings

def test_schema_manager():
    """Test basic schema manager functionality."""
    print("Testing Schema Manager")
    print("=" * 40)
    
    try:
        # Initialize
        print(f"📁 Loading schema from: {settings.schema_metadata_path}")
        schema_manager = SchemaManager(settings.schema_metadata_path)
        
        # Basic info
        table_count = schema_manager.get_table_count()
        available_tables = schema_manager.get_available_tables()
        
        print(f" Loaded {table_count} tables")
        print(f"📊 Tables: {', '.join(available_tables[:5])}...")
        print()
        
        # Test table summaries
        print("Testing table summaries...")
        summaries_text = schema_manager.get_table_summaries_text()
        print(f"Summary length: {len(summaries_text)} characters")
        print("First 200 chars:")
        print(summaries_text[:200] + "...")
        print()
        
        # Test full schema for first few tables
        print("🔍 Testing full schema...")
        test_tables = available_tables[:2]  # First 2 tables
        full_schema = schema_manager.get_full_schema_text(test_tables)
        
        print(f"Full schema for {test_tables}:")
        print(f"Length: {len(full_schema)} characters")
        print("First 300 chars:")
        print(full_schema[:300] + "...")
        print()
        
        print("Schema Manager test passed!")
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schema_manager()