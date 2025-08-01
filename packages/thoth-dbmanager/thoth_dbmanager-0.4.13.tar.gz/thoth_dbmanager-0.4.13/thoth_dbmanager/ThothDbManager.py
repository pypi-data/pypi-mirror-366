import pickle
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Union, ClassVar, Type, TypeVar

from .lsh.manager import LshManager
from .core.factory import ThothDbFactory
from .core.interfaces import DbPlugin

# Import plugins to register them
from .plugins.postgresql import PostgreSQLPlugin
from .plugins.sqlite import SQLitePlugin

T = TypeVar('T', bound='ThothDbManager')

class ThothDbManager(ABC):
    """
    This class provides methods for interacting with a database.
    It follows a singleton pattern for each unique set of connection parameters.
    
    This class now serves as a compatibility layer over the new plugin architecture.
    """
    _instances: ClassVar[Dict[tuple, Any]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_instance(cls: Type[T], db_type: str, **kwargs) -> T:
        """
        Get or create a singleton instance based on the database type.
        This acts as a factory for different database manager implementations.
        
        Now uses the new plugin architecture while maintaining backward compatibility.
        
        Args:
            db_type (str): The type of database (e.g., 'postgresql', 'sqlite', 'mysql').
            **kwargs: Connection parameters specific to the database implementation.
            
        Returns:
            An instance of the appropriate database manager.
            
        Raises:
            ValueError: If the database type is unsupported or required parameters are missing.
        """
        # Try new plugin architecture first
        try:
            if db_type in ["postgresql", "sqlite"]:  # Currently supported by new architecture
                # Extract required parameters
                db_root_path = kwargs.get('db_root_path')
                db_mode = kwargs.get('db_mode', 'dev')

                if not db_root_path:
                    raise ValueError("db_root_path is required")

                # Remove extracted parameters from kwargs to avoid duplicate parameter errors
                kwargs_clean = kwargs.copy()
                kwargs_clean.pop('db_root_path', None)
                kwargs_clean.pop('db_mode', None)

                # Create plugin instance using factory
                plugin = ThothDbFactory.create_manager(db_type, db_root_path, db_mode, **kwargs_clean)
                
                # Wrap plugin in compatibility adapter
                return ThothDbManagerAdapter(plugin)
            
        except Exception as e:
            logging.warning(f"Failed to use new plugin architecture for {db_type}: {e}. Falling back to legacy implementation.")
        
        # Use unified plugin system for all database types
        try:
            # Import all plugins to ensure they're registered
            from . import plugins
            
            # Create plugin instance using factory
            plugin = ThothDbFactory.create_manager(db_type, **kwargs)
            
            # Wrap plugin in compatibility adapter
            return ThothDbManagerAdapter(plugin)
            
        except Exception as e:
            logging.error(f"Failed to create {db_type} manager: {e}")
            raise ValueError(f"Unsupported database type '{db_type}' or invalid parameters: {e}")
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", db_type: Optional[str] = None, **kwargs) -> None:
        """
        Initialize the database manager.
        
        Args:
            db_root_path (str): Path to the database root directory.
            db_mode (str, optional): Database mode (dev, prod, etc.). Defaults to "dev".
            db_type (Optional[str], optional): Type of database. Defaults to None.
            **kwargs: Additional parameters specific to the database implementation.
        """
        self._validate_common_params(db_root_path, db_mode)
        
        self.db_root_path = db_root_path
        self.db_mode = db_mode
        self.db_type = db_type
        
        # These will be set by subclasses
        self.engine = None
        self.db_id = None
        self.db_directory_path = None
        
        # LSH related attributes (for backward compatibility)
        self.lsh = None
        self.minhashes = None
        self.vector_db = None
        
        # New LSH manager (lazy initialization)
        self._lsh_manager = None
        
        # Flag to track initialization
        self._initialized = False
    
    def _validate_common_params(self, db_root_path: str, db_mode: str) -> None:
        """
        Validate common parameters for all database implementations.
        
        Args:
            db_root_path (str): Path to the database root directory.
            db_mode (str): Database mode (dev, prod, etc.).
            
        Raises:
            ValueError: If parameters are invalid.
        """
        if not db_root_path:
            raise ValueError("db_root_path is required")
        
        if not isinstance(db_mode, str):
            raise TypeError("db_mode must be a string")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """
        Set up the database directory path.
        
        Args:
            db_id (str): Database identifier.
        """
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = self.db_root_path / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None

    @property
    def lsh_manager(self) -> Optional[LshManager]:
        """
        Lazy load LSH manager.
        
        Returns:
            LshManager instance if db_directory_path is set, None otherwise
        """
        if self._lsh_manager is None and self.db_directory_path:
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager

    @abstractmethod
    def execute_sql(self,
                   sql: str, 
                   params: Optional[Dict] = None, 
                   fetch: Union[str, int] = "all", 
                   timeout: int = 60) -> Any:
        """
        Abstract method to execute SQL queries.

        Args:
            sql (str): The SQL query to execute.
            params (Optional[Dict]): Parameters for the SQL query.
            fetch (Union[str, int]): Specifies how to fetch the results.
            timeout (int): Timeout for the query execution.

        Returns:
            Any: The result of the SQL query execution.
        """
        pass
    
    @abstractmethod
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get unique values from the database.
        
        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of unique values
        """
        pass

    @abstractmethod
    def get_tables(self) -> List[Dict[str, str]]:
        """
        Abstract method to get a list of tables in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a table with 'name' and 'comment' keys.
        """
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Abstract method to get a list of columns for a given table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents a column with 'name', 'data_type',
                                  'comment', and 'is_pk' keys.
        """
        pass

    @abstractmethod
    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """
        Abstract method to get a list of foreign key relationships in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a foreign key relationship with
                                  'source_table_name', 'source_column_name',
                                  'target_table_name', and 'target_column_name' keys.
        """
        pass
    
    @abstractmethod
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Abstract method to get example data (most frequent values) for each column in a table.

        Args:
            table_name (str): The name of the table.
            number_of_rows (int, optional): Maximum number of example values to return per column. Defaults to 30.

        Returns:
            Dict[str, List[Any]]: A dictionary mapping column names to lists of example values.
        """
        pass
    
    def set_lsh(self) -> str:
        """
        Sets the LSH and minhashes attributes by loading from storage.
        
        This method maintains backward compatibility while using the new LSH manager.
        """
        with self._lock:
            if self.lsh is None:
                try:
                    # Use the new LSH manager
                    if self.lsh_manager and self.lsh_manager.load_lsh():
                        # Set backward compatibility attributes
                        self.lsh = self.lsh_manager.lsh
                        self.minhashes = self.lsh_manager.minhashes
                        return "success"
                    else:
                        # Fallback to old method for compatibility
                        lsh_path = self.db_directory_path / "preprocessed" / f"{self.db_id}_lsh.pkl"
                        minhashes_path = self.db_directory_path / "preprocessed" / f"{self.db_id}_minhashes.pkl"

                        if not lsh_path.exists() or not minhashes_path.exists():
                            raise FileNotFoundError(f"LSH or MinHashes file not found for {self.db_id}")

                        with lsh_path.open("rb") as file:
                            self.lsh = pickle.load(file)
                        with minhashes_path.open("rb") as file:
                            self.minhashes = pickle.load(file)
                        return "success"
                except Exception as e:
                    logging.error(f"Error loading LSH: {str(e)}")
                    self.lsh = "error"
                    self.minhashes = "error"
                    return "error"
            elif self.lsh == "error":
                return "error"
            else:
                return "success"

    def query_lsh(self,
                 keyword: str,
                 signature_size: int = 30,
                 n_gram: int = 3,
                 top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """
        Queries the LSH for similar values to the given keyword.

        Args:
            keyword (str): The keyword to search for.
            signature_size (int, optional): The size of the MinHash signature. Defaults to 30.
            n_gram (int, optional): The n-gram size for the MinHash. Defaults to 3.
            top_n (int, optional): The number of top results to return. Defaults to 10.

        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of similar strings
        """
        # Try using the new LSH manager first
        if self.lsh_manager:
            try:
                return self.lsh_manager.query(
                    keyword=keyword,
                    signature_size=signature_size,
                    n_gram=n_gram,
                    top_n=top_n
                )
            except Exception as e:
                logging.warning(f"LSH manager query failed, falling back to old method: {e}")
        
        # Fallback to old method for backward compatibility
        lsh_status = self.set_lsh()
        if lsh_status == "success":
            # Import here to avoid circular imports
            from .helpers.search import _query_lsh
            return _query_lsh(self.lsh, self.minhashes, keyword, signature_size, n_gram, top_n)
        else:
            raise Exception(f"Error loading LSH for {self.db_id}")


class ThothDbManagerAdapter(ThothDbManager):
    """
    Adapter class that wraps the new plugin architecture to provide backward compatibility
    with the original ThothDbManager interface.
    """
    
    def __init__(self, plugin: DbPlugin):
        """
        Initialize the adapter with a plugin instance.
        
        Args:
            plugin: Database plugin instance
        """
        self.plugin = plugin
        
        # Copy plugin attributes for backward compatibility
        self.db_root_path = plugin.db_root_path
        self.db_mode = plugin.db_mode
        self.db_type = plugin.supported_db_types[0] if plugin.supported_db_types else "unknown"
        self.db_id = getattr(plugin, 'db_id', None)
        self.db_directory_path = getattr(plugin, 'db_directory_path', None)
        self.schema = getattr(plugin, 'schema', "")
        
        # Engine and connection (delegated to adapter)
        self.engine = getattr(plugin.adapter, 'engine', None) if plugin.adapter else None
        
        # LSH related attributes (for backward compatibility)
        self.lsh = None
        self.minhashes = None
        self.vector_db = None
        
        # Flag to track initialization
        self._initialized = plugin._initialized
    
    @property
    def lsh_manager(self):
        """Access LSH manager through plugin"""
        return getattr(self.plugin, 'lsh_manager', None)
    
    def execute_sql(self, sql: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL queries through plugin"""
        return self.plugin.execute_sql(sql, params, fetch, timeout)
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values through plugin"""
        return self.plugin.get_unique_values()
    
    def get_tables(self) -> List[Dict[str, str]]:
        """Get tables through plugin"""
        return self.plugin.get_tables()
    
    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get columns through plugin"""
        return self.plugin.get_columns(table_name)
    
    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """Get foreign keys through plugin"""
        return self.plugin.get_foreign_keys()
    
    def set_lsh(self) -> str:
        """Set LSH through plugin"""
        if hasattr(self.plugin, 'set_lsh'):
            result = self.plugin.set_lsh()
            
            # Update backward compatibility attributes
            if result == "success" and self.lsh_manager:
                self.lsh = getattr(self.lsh_manager, 'lsh', None)
                self.minhashes = getattr(self.lsh_manager, 'minhashes', None)
            
            return result
        else:
            # Fallback to original implementation
            return super().set_lsh()
    
    def query_lsh(self, keyword: str, signature_size: int = 30, n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Query LSH through plugin"""
        if hasattr(self.plugin, 'query_lsh'):
            return self.plugin.query_lsh(keyword, signature_size, n_gram, top_n)
        else:
            # Fallback to original implementation
            return super().query_lsh(keyword, signature_size, n_gram, top_n)
    
    # Document-based methods (new functionality)
    def get_tables_as_documents(self):
        """Get tables as document objects"""
        if self.plugin.adapter:
            return self.plugin.adapter.get_tables_as_documents()
        return []
    
    def get_columns_as_documents(self, table_name: str):
        """Get columns as document objects"""
        if self.plugin.adapter:
            return self.plugin.adapter.get_columns_as_documents(table_name)
        return []
    
    def get_foreign_keys_as_documents(self):
        """Get foreign keys as document objects"""
        if self.plugin.adapter:
            return self.plugin.adapter.get_foreign_keys_as_documents()
        return []
    
    def get_schemas_as_documents(self):
        """Get schemas as document objects"""
        if self.plugin.adapter:
            return self.plugin.adapter.get_schemas_as_documents()
        return []
    
    def get_indexes_as_documents(self, table_name: Optional[str] = None):
        """Get indexes as document objects"""
        if self.plugin.adapter:
            return self.plugin.adapter.get_indexes_as_documents(table_name)
        return []
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        if hasattr(self.plugin, 'get_connection_info'):
            return self.plugin.get_connection_info()
        return {}
    
    def health_check(self) -> bool:
        """Check database health"""
        if self.plugin.adapter:
            return self.plugin.adapter.health_check()
        return False
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through plugin"""
        if hasattr(self.plugin, 'get_example_data'):
            return self.plugin.get_example_data(table_name, number_of_rows)
        elif self.plugin.adapter:
            return self.plugin.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized or doesn't support get_example_data")
