#!/usr/bin/env python3
"""
Simple API test - database agnostic.
"""

import requests
import time
from core.config_loader import get_system_config

# API Configuration
API_BASE_URL = "http://localhost:8015/api/v1"
TIMEOUT = 30

def test_api():
    """Test essential API endpoints."""
    print("🌐 Testing API Endpoints")
    print("=" * 30)
    
    # Test 1: Health Check
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            health_data = response.json()
            print(f"  Status: {health_data['status']}")
            print(f"  Tables: {health_data.get('tables_available', 'N/A')}")
        else:
            print(f"  Failed: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
    
    # Test 2: Schema Info
    print("Testing Schema Info...")
    try:
        response = requests.get(f"{API_BASE_URL}/schema", timeout=TIMEOUT)
        if response.status_code == 200:
            schema_data = response.json()
            print(f"  Retrieved schema info")
            print(f"  Tables: {schema_data['total_tables']}")
            print(f"  Sample: {schema_data['tables'][:3]}...")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3: SQL Generation using config questions
    print("Testing SQL Generation...")
    
    # Get test questions from config
    config = get_system_config()
    basic_questions = config.get("test_questions.basic", ["Show me recent records"])
    
    test_queries = []
    for question in basic_questions[:2]:  # Test first 2 questions
        test_queries.append({
            "question": question,
            "max_tables": 3,
            "execute_sql": False  # Safety first
        })
    
    for i, query in enumerate(test_queries, 1):
        print(f"  Test {i}: {query['question']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/generate-sql",
                json=query,
                timeout=TIMEOUT
            )
            request_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data['success']}")
                
                if data['success']:
                    print(f"    SQL length: {len(data['sql_query'])} chars")
                    print(f"    Tables: {data['selected_tables']}")
                    print(f"    Time: {request_time}ms")
                    
                    # Show first part of SQL
                    sql_preview = data['sql_query'][:60] + "..." if len(data['sql_query']) > 60 else data['sql_query']
                    print(f"    SQL: {sql_preview}")
                else:
                    print(f"     Error: {data.get('error_message', 'Unknown')}")
                    
            else:
                print(f"     Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"     Error: {e}")
        
        print()
    
    print("API test completed!")

def test_error_handling():
    """Test API error handling using config error cases."""
    print("Testing Error Handling...")
    
    # Get error cases from config
    config = get_system_config()
    error_questions = config.get("test_questions.error_cases", ["", "invalid query"])
    
    error_tests = [
        {
            "name": "Empty question",
            "data": {"question": error_questions[0] if error_questions else "", "execute_sql": False}
        },
        {
            "name": "Invalid question", 
            "data": {"question": error_questions[1] if len(error_questions) > 1 else "xyz123", "execute_sql": False}
        },
        {
            "name": "Invalid max_tables",
            "data": {"question": "test", "max_tables": -1, "execute_sql": False}
        }
    ]
    
    for test in error_tests:
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate-sql",
                json=test['data'],
                timeout=TIMEOUT
            )
            
            if response.status_code in [200, 422]:
                print(f" {test['name']}: Handled correctly")
            else:
                print(f"  {test['name']}: Unexpected status {response.status_code}")
                
        except Exception as e:
            print(f"   {test['name']}: Exception {e}")
    
    print()

if __name__ == "__main__":
    print("API Test Suite")
    print("=" * 20)
    print(f"Testing API at: {API_BASE_URL}")
    print()
    
    # Main API test
    test_api()
    
    # Error handling test
    test_error_handling()
    
    print(" All tests completed!")