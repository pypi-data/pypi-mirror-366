"""
Supabase adapter implementation.
"""
import logging
from typing import Any, Dict, List, Optional, Union
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse, parse_qs

from .postgresql import PostgreSQLAdapter
from ..core.interfaces import DbAdapter
from ..documents import (
    TableDocument,
    ColumnDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument
)

logger = logging.getLogger(__name__)


class SupabaseAdapter(PostgreSQLAdapter):
    """
    Supabase database adapter implementation.
    Extends PostgreSQL adapter with Supabase-specific features.
    """
    
    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.supabase_url = None
        self.api_key = None
        self.use_rest_api = False
        
    def connect(self) -> None:
        """Establish Supabase connection with SSL enforcement"""
        try:
            # Check if we should use REST API or direct database connection
            self.use_rest_api = self.connection_params.get('use_rest_api', False)
            
            if self.use_rest_api:
                # REST API connection setup
                self.supabase_url = self.connection_params.get('project_url')
                self.api_key = self.connection_params.get('api_key')
                
                if not self.supabase_url or not self.api_key:
                    raise ValueError("project_url and api_key are required for REST API mode")
                
                logger.info("Supabase REST API connection established")
            else:
                # Direct database connection (PostgreSQL with SSL)
                super().connect()
                
                # Ensure SSL is enabled for Supabase
                if hasattr(self, 'engine') and self.engine:
                    # Update connection string to enforce SSL
                    connection_string = self._build_connection_string()
                    if 'sslmode=' not in connection_string:
                        connection_string += '?sslmode=require'
                    
                    self.engine = create_engine(connection_string, echo=False)
                    
                    # Test connection
                    with self.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                
                logger.info("Supabase database connection established with SSL")
                
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string with Supabase-specific parameters"""
        params = self.connection_params
        
        if self.use_rest_api:
            return params.get('project_url')
        
        # Direct database connection
        host = params.get('host')
        port = params.get('port', 5432)
        database = params.get('database')
        user = params.get('user')
        password = params.get('password')
        
        if not all([host, database, user, password]):
            raise ValueError("Missing required connection parameters: host, database, user, password")
        
        # Ensure SSL mode for Supabase
        ssl_mode = params.get('sslmode', 'require')
        
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
        
        # Add additional SSL parameters if provided
        if params.get('sslcert'):
            connection_string += f"&sslcert={params['sslcert']}"
        if params.get('sslkey'):
            connection_string += f"&sslkey={params['sslkey']}"
        if params.get('sslrootcert'):
            connection_string += f"&sslrootcert={params['sslrootcert']}"
            
        return connection_string
    
    def _get_psycopg2_params(self) -> Dict[str, Any]:
        """Get parameters for psycopg2 connection with SSL"""
        params = super()._get_psycopg2_params()
        
        # Ensure SSL is enabled for Supabase
        params['sslmode'] = self.connection_params.get('sslmode', 'require')
        
        # Add SSL certificates if provided
        if self.connection_params.get('sslcert'):
            params['sslcert'] = self.connection_params['sslcert']
        if self.connection_params.get('sslkey'):
            params['sslkey'] = self.connection_params['sslkey']
        if self.connection_params.get('sslrootcert'):
            params['sslrootcert'] = self.connection_params['sslrootcert']
            
        return params
    
    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL queries with Supabase-specific optimizations"""
        if self.use_rest_api:
            return self._execute_rest_query(query, params, fetch, timeout)
        else:
            return super().execute_query(query, params, fetch, timeout)
    
    def _execute_rest_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute query using Supabase REST API"""
        try:
            from supabase import create_client
            from postgrest.exceptions import APIError
            
            # Create Supabase client
            supabase = create_client(self.supabase_url, self.api_key)
            
            # For REST API, we need to convert SQL to Postgrest queries
            # This is a simplified implementation - in practice, you'd need a SQL parser
            if query.strip().upper().startswith('SELECT'):
                # Extract table name and conditions from query
                table_name = self._extract_table_name(query)
                
                # Build Postgrest query
                result = supabase.table(table_name).select('*').execute()
                
                if fetch == "all":
                    return result.data
                elif fetch == "one":
                    return result.data[0] if result.data else None
                elif isinstance(fetch, int):
                    return result.data[:fetch]
                else:
                    return result.data
            else:
                # For non-SELECT queries, use RPC
                result = supabase.rpc('execute_sql', {'sql': query}).execute()
                return result.data
                
        except ImportError:
            raise RuntimeError("supabase-py package is required for REST API mode")
        except APIError as e:
            logger.error(f"Supabase REST API error: {e}")
            raise
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from SQL query (simplified)"""
        # This is a basic implementation - in practice, you'd use a proper SQL parser
        query = query.upper()
        from_index = query.find('FROM')
        if from_index != -1:
            after_from = query[from_index + 4:].strip()
            # Find first space or end of string
            space_index = after_from.find(' ')
            if space_index != -1:
                return after_from[:space_index].lower()
            else:
                return after_from.lower()
        return "unknown"
    
    def get_tables_as_documents(self) -> List[TableDocument]:
        """Get tables with Supabase schema considerations"""
        tables = super().get_tables_as_documents()
        
        # Filter out Supabase system schemas
        filtered_tables = []
        for table in tables:
            if table.schema_name not in ['auth', 'storage', 'realtime', 'supabase_functions']:
                filtered_tables.append(table)
        
        return filtered_tables
    
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """Get columns with Supabase-specific handling"""
        columns = super().get_columns_as_documents(table_name)
        
        # Add Supabase-specific metadata
        for column in columns:
            if column.column_name in ['created_at', 'updated_at']:
                column.comment = f"{column.comment} (Supabase auto-timestamp)"
            elif column.column_name == 'id':
                column.comment = f"{column.comment} (Supabase auto-increment)"
        
        return columns
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values with Supabase schema filtering"""
        result = super().get_unique_values()
        
        # Filter out Supabase system tables
        filtered_result = {}
        for table_name, columns in result.items():
            if not table_name.startswith('auth_') and not table_name.startswith('storage_'):
                filtered_result[table_name] = columns
        
        return filtered_result
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data with Supabase-specific handling"""
        if self.use_rest_api:
            return self._get_example_data_rest(table_name, number_of_rows)
        else:
            return super().get_example_data(table_name, number_of_rows)
    
    def _get_example_data_rest(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data using REST API"""
        try:
            from supabase import create_client
            
            supabase = create_client(self.supabase_url, self.api_key)
            
            # Get data from REST API
            result = supabase.table(table_name).select('*').limit(number_of_rows).execute()
            
            # Convert to the expected format
            example_data = {}
            if result.data:
                for key in result.data[0].keys():
                    example_data[key] = [row.get(key) for row in result.data]
            
            return example_data
            
        except ImportError:
            raise RuntimeError("supabase-py package is required for REST API mode")
        except Exception as e:
            logger.error(f"Error getting example data via REST API: {e}")
            return {}
