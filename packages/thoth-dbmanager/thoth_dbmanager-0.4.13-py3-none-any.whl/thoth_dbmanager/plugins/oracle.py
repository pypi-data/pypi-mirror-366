"""
Oracle plugin implementation.
"""
import logging
from typing import Any, Dict, List
from pathlib import Path

from ..core.interfaces import DbPlugin, DbAdapter
from ..core.registry import register_plugin
from ..adapters.oracle import OracleAdapter

logger = logging.getLogger(__name__)


@register_plugin("oracle")
class OraclePlugin(DbPlugin):
    """
    Oracle database plugin implementation.
    """

    plugin_name = "Oracle Plugin"
    plugin_version = "1.0.0"
    supported_db_types = ["oracle"]
    required_dependencies = ["cx_Oracle", "SQLAlchemy"]

    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        super().__init__(db_root_path, db_mode, **kwargs)
        self.db_id = None
        self.db_directory_path = None

        # LSH manager integration (for backward compatibility)
        self._lsh_manager = None

    def create_adapter(self, **kwargs) -> DbAdapter:
        """Create and return an Oracle adapter instance"""
        return OracleAdapter(kwargs)

    def validate_connection_params(self, **kwargs) -> bool:
        """Validate connection parameters for Oracle"""
        required_params = ['host', 'port', 'service_name', 'user', 'password']

        for param in required_params:
            if param not in kwargs:
                logger.error(f"Missing required parameter: {param}")
                return False

        # Validate types
        try:
            port = int(kwargs['port'])
            if port <= 0 or port > 65535:
                logger.error(f"Invalid port number: {port}")
                return False
        except (ValueError, TypeError):
            logger.error(f"Port must be a valid integer: {kwargs.get('port')}")
            return False

        # Validate required string parameters are not empty
        string_params = ['host', 'service_name', 'user', 'password']
        for param in string_params:
            if not kwargs.get(param) or not isinstance(kwargs[param], str):
                logger.error(f"Parameter {param} must be a non-empty string")
                return False

        return True

    def initialize(self, **kwargs) -> None:
        """Initialize the Oracle plugin"""
        super().initialize(**kwargs)

        # Set up database directory path (for LSH and other features)
        if 'service_name' in kwargs:
            self.db_id = kwargs['service_name']
            self._setup_directory_path(self.db_id)

        logger.info(f"Oracle plugin initialized for service: {self.db_id}")

    def _setup_directory_path(self, db_id: str) -> None:
        """Set up directory path for database-specific files"""
        if self.db_root_path:
            self.db_directory_path = Path(self.db_root_path) / "oracle" / db_id
            self.db_directory_path.mkdir(parents=True, exist_ok=True)

    @property
    def lsh_manager(self):
        """Get LSH manager (for backward compatibility)"""
        return self._lsh_manager

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        base_info = super().get_plugin_info()

        if self.adapter:
            adapter_info = self.adapter.get_connection_info()
            base_info.update(adapter_info)

        base_info.update({
            "db_id": self.db_id,
            "db_directory_path": str(self.db_directory_path) if self.db_directory_path else None,
            "lsh_available": self.lsh_manager is not None
        })

        return base_info

    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through adapter"""
        if self.adapter:
            return self.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized")
    
    def validate_connection_string(self, connection_string: str) -> bool:
        """Validate Oracle connection string format."""
        return connection_string.startswith("oracle+cx_oracle://")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get Oracle database information."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "features": [
                "transactions",
                "foreign_keys",
                "indexes",
                "views",
                "stored_procedures",
                "triggers",
                "sequences",
                "partitions",
                "materialized_views"
            ],
            "data_types": [
                "NUMBER", "BINARY_INTEGER", "PLS_INTEGER",
                "VARCHAR2", "NVARCHAR2", "CHAR", "NCHAR", "CLOB", "NCLOB", "BLOB", "BFILE",
                "DATE", "TIMESTAMP", "INTERVAL",
                "RAW", "LONG", "LONG RAW",
                "ROWID", "UROWID"
            ]
        }
    
    def get_sample_connection_config(self) -> Dict[str, Any]:
        """Get sample connection configuration."""
        return {
            "host": "localhost",
            "port": 1521,
            "service_name": "ORCL",
            "username": "user",
            "password": "password"
        }
