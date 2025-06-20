"""
Simple in-memory database for logging.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

class SimpleDB:
    """Simple in-memory SQLite database."""
    
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.init_db()
    
    def init_db(self):
        """Initialize tables."""
        self.conn.execute("""
            CREATE TABLE query_logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                question TEXT,
                sql_query TEXT,
                success BOOLEAN,
                executed BOOLEAN,
                row_count INTEGER,
                execution_time_ms INTEGER,
                error_message TEXT,
                feedback INTEGER
            )
        """)
        self.conn.commit()
    
    def log_query(self, question: str, sql_query: str = "", success: bool = False, 
                  executed: bool = False, row_count: int = 0, execution_time_ms: int = 0, 
                  error_message: str = "") -> int:
        """Log a query."""
        cursor = self.conn.execute("""
            INSERT INTO query_logs 
            (timestamp, question, sql_query, success, executed, row_count, execution_time_ms, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), question, sql_query, success, executed, 
              row_count, execution_time_ms, error_message))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_feedback(self, query_id: int, feedback: int):
        """Add feedback (1 for positive, -1 for negative)."""
        self.conn.execute("UPDATE query_logs SET feedback = ? WHERE id = ?", (feedback, query_id))
        self.conn.commit()
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent queries."""
        cursor = self.conn.execute("""
            SELECT * FROM query_logs ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM query_logs")
        total = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM query_logs WHERE success = 1")
        successful = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT AVG(execution_time_ms) FROM query_logs WHERE execution_time_ms > 0")
        avg_time = cursor.fetchone()[0] or 0
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM query_logs WHERE feedback = 1")
        positive_feedback = cursor.fetchone()[0]
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            "total_queries": total,
            "successful_queries": successful,
            "success_rate": round(success_rate, 1),
            "avg_execution_time": round(avg_time, 0),
            "positive_feedback": positive_feedback
        }

# Global instance
db = SimpleDB()