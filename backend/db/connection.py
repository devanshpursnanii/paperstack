"""
Database Connection Layer
Supports both SQLite (local) and PostgreSQL (Supabase cloud).
"""

import os
import sqlite3
from pathlib import Path
from typing import Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
SQLITE_DB_PATH = Path(__file__).parent.parent.parent / os.getenv("SQLITE_DB_PATH", "logs.db")

# Supabase PostgreSQL credentials
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_PORT = os.getenv("SUPABASE_PORT", "5432")
SUPABASE_DATABASE = os.getenv("SUPABASE_DATABASE", "postgres")
SUPABASE_USER = os.getenv("SUPABASE_USER", "postgres")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")


def get_connection() -> Union[sqlite3.Connection, any]:
    """
    Get a database connection based on DATABASE_TYPE environment variable.
    
    Returns:
        - sqlite3.Connection if DATABASE_TYPE=sqlite
        - psycopg2.connection if DATABASE_TYPE=postgres
    
    Raises:
        ValueError: If DATABASE_TYPE is invalid
        ConnectionError: If database connection fails
    """
    if DATABASE_TYPE == "sqlite":
        return _get_sqlite_connection()
    elif DATABASE_TYPE == "postgres":
        return _get_postgres_connection()
    else:
        raise ValueError(f"Invalid DATABASE_TYPE: {DATABASE_TYPE}. Must be 'sqlite' or 'postgres'")


def _get_sqlite_connection() -> sqlite3.Connection:
    """
    Get a SQLite database connection with proper configuration.
    
    Returns:
        Configured sqlite3.Connection
    """
    conn = sqlite3.connect(str(SQLITE_DB_PATH), check_same_thread=False)
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Enable dict-like row access
    conn.row_factory = sqlite3.Row
    
    return conn


def _get_postgres_connection():
    """
    Get a PostgreSQL connection to Supabase.
    
    Returns:
        psycopg2.connection with RealDictCursor for dict-like access
    
    Raises:
        ConnectionError: If Supabase credentials are missing or connection fails
    """
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        raise ImportError(
            "psycopg2-binary is required for PostgreSQL support. "
            "Install it with: pip install psycopg2-binary"
        )
    
    if not all([SUPABASE_HOST, SUPABASE_PASSWORD]):
        raise ConnectionError(
            "Missing Supabase credentials. Set SUPABASE_HOST and SUPABASE_PASSWORD in .env file"
        )
    
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            database=SUPABASE_DATABASE,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            cursor_factory=RealDictCursor  # Returns dict-like rows (same as SQLite Row)
        )
        return conn
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")


def get_placeholder() -> str:
    """
    Get the correct SQL placeholder for the current database type.
    
    Returns:
        - "?" for SQLite
        - "%s" for PostgreSQL
    """
    return "?" if DATABASE_TYPE == "sqlite" else "%s"
