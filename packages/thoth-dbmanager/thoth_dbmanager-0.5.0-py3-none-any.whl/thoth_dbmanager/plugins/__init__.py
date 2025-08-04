"""
Database plugins for Thoth SQL Database Manager.
"""

# Import all plugins to ensure they are registered
from .postgresql import PostgreSQLPlugin
from .sqlite import SQLitePlugin
from .supabase import SupabasePlugin
from .mysql import MySQLPlugin
from .mariadb import MariaDBPlugin
from .sqlserver import SQLServerPlugin
from .oracle import OraclePlugin

# This ensures all plugins are registered when the module is imported
__all__ = [
    "PostgreSQLPlugin",
    "SQLitePlugin",
    "SupabasePlugin",
    "MySQLPlugin",
    "MariaDBPlugin",
    "SQLServerPlugin",
    "OraclePlugin",
]
