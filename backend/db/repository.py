"""
Repository Layer - Pure DB I/O
No FastAPI imports, no AI imports, only database operations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .connection import get_connection, DATABASE_TYPE


def _build_query(query: str) -> str:
    """
    Replace ? placeholders with correct placeholder for current database.
    
    Args:
        query: SQL query with ? placeholders
        
    Returns:
        Query with correct placeholders (? for SQLite, %s for Postgres)
    """
    if DATABASE_TYPE == "postgres":
        # Replace ? with %s for PostgreSQL
        return query.replace("?", "%s")
    return query


def create_session(session_id: str, session_start_ts: Optional[datetime] = None) -> None:
    """
    Create a new session record.
    
    Args:
        session_id: Unique session identifier
        session_start_ts: Session start timestamp (defaults to now)
    """
    conn = get_connection()
    try:
        ts = session_start_ts or datetime.now()
        
        # Use INSERT ... ON CONFLICT for Postgres, INSERT OR IGNORE for SQLite
        if DATABASE_TYPE == "postgres":
            query = "INSERT INTO sessions (session_id, session_start_ts) VALUES (%s, %s) ON CONFLICT (session_id) DO NOTHING"
        else:
            query = "INSERT OR IGNORE INTO sessions (session_id, session_start_ts) VALUES (?, ?)"
        
        cursor = conn.cursor()
        cursor.execute(query, (session_id, ts))
        conn.commit()
    finally:
        conn.close()


def insert_request(request_data: Dict[str, Any]) -> None:
    """
    Insert a request record.
    
    Args:
        request_data: Dict with keys:
            - request_id: str
            - session_id: str
            - query: str
            - prompt_tokens: int
            - total_chunk_tokens: int
            - completion_tokens: int
            - llm_latency_ms: float
            - total_latency_ms: float
            - operation_type: str (default: 'chat_message')
            - status: str (default: 'success')
            - error_message: Optional[str]
    """
    conn = get_connection()
    try:
        query = _build_query("""
            INSERT INTO requests (
                request_id, session_id, query, prompt_tokens, total_chunk_tokens,
                completion_tokens, llm_latency_ms, total_latency_ms, 
                operation_type, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)
        
        cursor = conn.cursor()
        cursor.execute(
            query,
            (
                request_data['request_id'],
                request_data['session_id'],
                request_data['query'],
                request_data['prompt_tokens'],
                request_data['total_chunk_tokens'],
                request_data['completion_tokens'],
                request_data['llm_latency_ms'],
                request_data['total_latency_ms'],
                request_data.get('operation_type', 'chat_message'),
                request_data.get('status', 'success'),
                request_data.get('error_message')
            )
        )
        conn.commit()
    finally:
        conn.close()


def insert_chunks(request_id: str, chunks: List[Dict[str, Any]]) -> None:
    """
    Insert multiple chunk records for a request.
    
    Args:
        request_id: Request identifier
        chunks: List of dicts with keys:
            - chunk_index: int
            - paper_title: str
            - content_preview: str
            - chunk_token_count: int
    """
    conn = get_connection()
    try:
        query = _build_query("""
            INSERT INTO chunks (
                request_id, chunk_index, paper_title, 
                content_preview, chunk_token_count
            ) VALUES (?, ?, ?, ?, ?)
            """)
        
        cursor = conn.cursor()
        cursor.executemany(
            query,
            [
                (
                    request_id,
                    chunk['chunk_index'],
                    chunk['paper_title'],
                    chunk['content_preview'],
                    chunk['chunk_token_count']
                )
                for chunk in chunks
            ]
        )
        conn.commit()
    finally:
        conn.close()


def get_requests_by_session(session_id: str) -> List[Dict[str, Any]]:
    """
    Get all requests for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of request dicts
    """
    conn = get_connection()
    try:
        query = _build_query("""
            SELECT * FROM requests 
            WHERE session_id = ? 
            ORDER BY created_at DESC
            """)
        
        cursor = conn.cursor()
        cursor.execute(query, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_request_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single request by ID.
    
    Args:
        request_id: Request identifier
        
    Returns:
        Request dict or None if not found
    """
    conn = get_connection()
    try:
        query = _build_query("SELECT * FROM requests WHERE request_id = ?")
        cursor = conn.cursor()
        cursor.execute(query, (request_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_chunks_by_request(request_id: str) -> List[Dict[str, Any]]:
    """
    Get all chunks for a request.
    
    Args:
        request_id: Request identifier
        
    Returns:
        List of chunk dicts
    """
    conn = get_connection()
    try:
        query = _build_query("""
            SELECT * FROM chunks 
            WHERE request_id = ? 
            ORDER BY chunk_index
            """)
        
        cursor = conn.cursor()
        cursor.execute(query, (request_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_session_metrics(session_id: str) -> Dict[str, Any]:
    """
    Get aggregated metrics for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dict with aggregated stats
    """
    conn = get_connection()
    try:
        query = _build_query("""
            SELECT 
                COUNT(*) as total_requests,
                AVG(llm_latency_ms) as avg_llm_latency,
                AVG(total_latency_ms) as avg_total_latency,
                SUM(prompt_tokens) as total_prompt_tokens,
                SUM(total_chunk_tokens) as total_chunk_tokens,
                SUM(completion_tokens) as total_completion_tokens,
                SUM(prompt_tokens + total_chunk_tokens + completion_tokens) as total_tokens
            FROM requests
            WHERE session_id = ? AND status = 'success'
            """)
        
        cursor = conn.cursor()
        cursor.execute(query, (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def get_session_query_metrics(session_id: str) -> List[Dict[str, Any]]:
    """
    Get individual query metrics for a session (for frontend display).
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of query metrics with details
    """
    conn = get_connection()
    try:
        query = _build_query("""
            SELECT 
                request_id,
                query,
                prompt_tokens,
                total_chunk_tokens,
                completion_tokens,
                llm_latency_ms,
                total_latency_ms,
                created_at
            FROM requests
            WHERE session_id = ? AND status = 'success'
            ORDER BY created_at ASC
            """)
        
        cursor = conn.cursor()
        cursor.execute(query, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_recent_requests(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get most recent requests across all sessions.
    
    Args:
        limit: Maximum number of requests to return
        
    Returns:
        List of request dicts
    """
    conn = get_connection()
    try:
        query = _build_query("""
            SELECT * FROM requests 
            ORDER BY created_at DESC 
            LIMIT ?
            """)
        
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
