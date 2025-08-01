"""
Thoth Database Manager - A unified interface for multiple database systems.

This package provides database-agnostic operations, LSH similarity search,
and an extensible plugin architecture for managing SQL databases.
"""

# Core classes - always available
from .ThothDbManager import ThothDbManager
from .core.factory import ThothDbFactory
from .core.interfaces import DbPlugin, DbAdapter
from .core.registry import DbPluginRegistry

# Document models
from .documents import (
    BaseThothDbDocument,
    TableDocument,
    ColumnDocument,
    QueryDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument,
    ThothDbType,
    create_document
)

# Export LSH functionality for backward compatibility
from .lsh.factory import make_db_lsh
from .lsh import LshManager, LshFactory

# Dynamic import system
from .dynamic_imports import (
    import_manager,
    import_adapter,
    import_plugin,
    get_available_databases,
    import_database_components,
    DatabaseImportError,
    # Convenience functions
    import_postgresql,
    import_mysql,
    import_sqlite,
    import_sqlserver,
    import_oracle,
    import_mariadb,
    import_supabase,
)

# Legacy API - will be dynamically imported when accessed
def __getattr__(name: str):
    """Dynamic attribute access for database managers."""
    if name == 'ThothPgManager':
        return import_manager('postgresql')
    elif name == 'ThothSqliteManager':
        return import_manager('sqlite')
    elif name == 'ThothMySqlManager':
        return import_manager('mysql')
    elif name == 'ThothMariaDbManager':
        return import_manager('mariadb')
    elif name == 'ThothSqlServerManager':
        return import_manager('sqlserver')
    elif name == 'ThothOracleManager':
        return import_manager('oracle')
    elif name == 'ThothSupabaseManager':
        return import_manager('supabase')
    
    raise AttributeError(f"module 'thoth_dbmanager' has no attribute '{name}'")

# Public API
__all__ = [
    # Legacy API
    "ThothDbManager",
    "ThothPgManager",
    "ThothSqliteManager",
    "ThothMySqlManager",
    "ThothMariaDbManager",
    "ThothSqlServerManager",
    "ThothOracleManager",
    "ThothSupabaseManager",
    
    # New architecture
    "ThothDbFactory",
    "DbPluginRegistry",
    "DbPlugin",
    "DbAdapter",
    
    # Document models
    "BaseThothDbDocument",
    "TableDocument",
    "ColumnDocument",
    "QueryDocument",
    "SchemaDocument",
    "ForeignKeyDocument",
    "IndexDocument",
    "ThothDbType",
    "create_document",
    
    # Plugins
    "PostgreSQLPlugin",
    "SQLitePlugin",
    "MySQLPlugin",
    "MariaDBPlugin",
    "SQLServerPlugin",
    "OraclePlugin",
    "SupabasePlugin",
    
    # Adapters
    "PostgreSQLAdapter",
    "SQLiteAdapter",
    "MySQLAdapter",
    "MariaDBAdapter",
    "SQLServerAdapter",
    "OracleAdapter",
    "SupabaseAdapter",
    
    # LSH functionality
    "make_db_lsh",
    "LshManager",
    "LshFactory",
    
    # Dynamic import system
    "import_manager",
    "import_adapter",
    "import_plugin",
    "get_available_databases",
    "import_database_components",
    "DatabaseImportError",
]

__version__ = "0.4.3"
