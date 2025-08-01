"""
Supabase plugin implementation.
"""
import logging
from typing import Any, Dict, List
from pathlib import Path
from urllib.parse import urlparse

from ..core.interfaces import DbPlugin, DbAdapter
from ..core.registry import register_plugin
from ..adapters.supabase import SupabaseAdapter

logger = logging.getLogger(__name__)


@register_plugin("supabase")
class SupabasePlugin(DbPlugin):
    """
    Supabase database plugin implementation.
    Extends PostgreSQL functionality with Supabase-specific features.
    """
    
    plugin_name = "Supabase Plugin"
    plugin_version = "1.0.0"
    supported_db_types = ["supabase", "supabase-postgresql"]
    required_dependencies = ["psycopg2-binary", "SQLAlchemy", "supabase", "postgrest-py"]
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        super().__init__(db_root_path, db_mode, **kwargs)
        self.db_id = None
        self.db_directory_path = None
        self.project_url = None
        self.api_key = None
        
        # LSH manager integration (for backward compatibility)
        self._lsh_manager = None
    
    def create_adapter(self, **kwargs) -> DbAdapter:
        """Create and return a Supabase adapter instance"""
        return SupabaseAdapter(kwargs)
    
    def validate_connection_params(self, **kwargs) -> bool:
        """Validate connection parameters for Supabase"""
        # Support both direct database connection and REST API connection
        use_rest_api = kwargs.get('use_rest_api', False)
        
        if use_rest_api:
            return self._validate_rest_params(**kwargs)
        else:
            return self._validate_direct_params(**kwargs)
    
    def _validate_rest_params(self, **kwargs) -> bool:
        """Validate REST API connection parameters"""
        required_params = ['project_url', 'api_key']
        
        for param in required_params:
            if param not in kwargs:
                logger.error(f"Missing required parameter for REST API: {param}")
                return False
        
        # Validate project URL format
        project_url = kwargs.get('project_url')
        try:
            parsed = urlparse(project_url)
            if not parsed.netloc.endswith('.supabase.co'):
                logger.error("Invalid Supabase project URL format")
                return False
        except Exception:
            logger.error("Invalid project URL format")
            return False
        
        # Validate API key format
        api_key = kwargs.get('api_key')
        if not api_key or not isinstance(api_key, str):
            logger.error("API key must be a non-empty string")
            return False
        
        return True
    
    def _validate_direct_params(self, **kwargs) -> bool:
        """Validate direct database connection parameters"""
        required_params = ['host', 'port', 'database', 'user', 'password']
        
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
        string_params = ['host', 'database', 'user', 'password']
        for param in string_params:
            if not kwargs.get(param) or not isinstance(kwargs[param], str):
                logger.error(f"Parameter {param} must be a non-empty string")
                return False
        
        # Validate SSL parameters if provided
        ssl_params = ['sslcert', 'sslkey', 'sslrootcert']
        for param in ssl_params:
            if param in kwargs and kwargs[param]:
                if not isinstance(kwargs[param], str):
                    logger.error(f"SSL parameter {param} must be a string")
                    return False
        
        return True
    
    def initialize(self, **kwargs) -> None:
        """Initialize the Supabase plugin"""
        super().initialize(**kwargs)
        
        # Store connection parameters
        self.project_url = kwargs.get('project_url')
        self.api_key = kwargs.get('api_key')
        
        # Set up database directory path (for LSH and other features)
        if 'database' in kwargs:
            self.db_id = kwargs['database']
        elif 'project_url' in kwargs:
            # Extract database name from project URL
            parsed = urlparse(kwargs['project_url'])
            self.db_id = parsed.netloc.split('.')[0]
        
        if self.db_id:
            self._setup_directory_path(self.db_id)
        
        logger.info(f"Supabase plugin initialized for project: {self.db_id}")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """Set up the database directory path"""
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = Path(self.db_root_path) / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None
    
    @property
    def lsh_manager(self):
        """Lazy load LSH manager for backward compatibility"""
        if self._lsh_manager is None and self.db_directory_path:
            from ..lsh.manager import LshManager
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager
    
    # LSH integration methods for backward compatibility
    def set_lsh(self) -> str:
        """Set LSH for backward compatibility"""
        try:
            if self.lsh_manager and self.lsh_manager.load_lsh():
                return "success"
            else:
                return "error"
        except Exception as e:
            logger.error(f"Error loading LSH: {e}")
            return "error"
    
    def query_lsh(self, keyword: str, signature_size: int = 30, n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Query LSH for backward compatibility"""
        if self.lsh_manager:
            try:
                return self.lsh_manager.query(
                    keyword=keyword,
                    signature_size=signature_size,
                    n_gram=n_gram,
                    top_n=top_n
                )
            except Exception as e:
                logger.error(f"LSH query failed: {e}")
                raise Exception(f"Error querying LSH for {self.db_id}: {e}")
        else:
            raise Exception(f"LSH not available for {self.db_id}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        base_info = super().get_plugin_info()
        
        if self.adapter:
            adapter_info = self.adapter.get_connection_info()
            base_info.update(adapter_info)
        
        base_info.update({
            "db_id": self.db_id,
            "db_directory_path": str(self.db_directory_path) if self.db_directory_path else None,
            "lsh_available": self.lsh_manager is not None,
            "project_url": self.project_url,
            "connection_mode": "REST API" if self.connection_params.get('use_rest_api') else "Direct Database"
        })
        
        return base_info
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through adapter"""
        if self.adapter:
            return self.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized")
    
    def get_required_parameters(self) -> Dict[str, Any]:
        """Get required connection parameters for Supabase"""
        use_rest_api = self.connection_params.get('use_rest_api', False)
        
        if use_rest_api:
            return {
                "required": ["project_url", "api_key"],
                "optional": ["schema", "timeout", "pool_size"],
                "connection_mode": "REST API"
            }
        else:
            return {
                "required": ["host", "port", "database", "user", "password"],
                "optional": ["schema", "sslmode", "sslcert", "sslkey", "sslrootcert", "pool_size", "connect_timeout"],
                "connection_mode": "Direct Database"
            }
