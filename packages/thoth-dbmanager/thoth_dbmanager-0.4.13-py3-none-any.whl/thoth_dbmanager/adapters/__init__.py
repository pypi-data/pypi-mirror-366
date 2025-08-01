"""
Database adapters for Thoth SQL Database Manager.
"""

from .postgresql import PostgreSQLAdapter
from .sqlite import SQLiteAdapter
from .supabase import SupabaseAdapter
from .mysql import MySQLAdapter
from .mariadb import MariaDBAdapter
from .sqlserver import SQLServerAdapter
from .oracle import OracleAdapter

__all__ = [
    "PostgreSQLAdapter",
    "SQLiteAdapter",
    "SupabaseAdapter",
    "MySQLAdapter",
    "MariaDBAdapter",
    "SQLServerAdapter",
    "OracleAdapter",
]
