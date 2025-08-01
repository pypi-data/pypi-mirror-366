"""
Oracle adapter implementation.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from ..core.interfaces import DbAdapter
from ..documents import TableDocument, ColumnDocument, ForeignKeyDocument, SchemaDocument, IndexDocument

logger = logging.getLogger(__name__)


class OracleAdapter(DbAdapter):
    """Oracle database adapter implementation."""

    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.engine = None
        self.host = connection_params.get('host', 'localhost')
        self.port = connection_params.get('port', 1521)
        self.service_name = connection_params.get('service_name')
        self.user = connection_params.get('user')
        self.password = connection_params.get('password')
        
    def connect(self) -> None:
        """Establish database connection."""
        try:
            # Build connection string for Oracle
            connection_string = self._build_connection_string()
            self.engine = create_engine(connection_string, pool_pre_ping=True)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM DUAL"))

            self._initialized = True
            logger.info("Oracle connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {e}")
            raise ConnectionError(f"Failed to connect to Oracle: {e}")

    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string for Oracle"""
        if not all([self.service_name, self.user, self.password]):
            raise ValueError("Missing required connection parameters: service_name, user, password")

        # Try different Oracle connection methods in order of preference
        connection_methods = [
            # Try python-oracledb (thin mode - no client required)
            lambda: f"oracle+oracledb://{self.user}:{self.password}@{self.host}:{self.port}/?service_name={self.service_name}&mode=thin",
            # Try python-oracledb (thick mode)
            lambda: f"oracle+oracledb://{self.user}:{self.password}@{self.host}:{self.port}/?service_name={self.service_name}",
            # Try cx_Oracle with service name format
            lambda: f"oracle+cx_oracle://{self.user}:{self.password}@{self.host}:{self.port}/?service_name={self.service_name}",
            # Try oracledb with SID format (fallback)
            lambda: f"oracle+oracledb://{self.user}:{self.password}@{self.host}:{self.port}/{self.service_name}",
            # Try cx_Oracle with SID format (fallback)
            lambda: f"oracle+cx_oracle://{self.user}:{self.password}@{self.host}:{self.port}/{self.service_name}",
        ]

        # Try each connection method until one works
        for i, method in enumerate(connection_methods):
            try:
                connection_string = method()
                logger.info(f"Attempting connection method {i+1}: {connection_string.split('@')[0]}@...")

                # Test the connection string by creating a temporary engine
                test_engine = create_engine(connection_string, pool_pre_ping=True)
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1 FROM DUAL"))
                test_engine.dispose()

                driver_name = "python-oracledb" if "oracledb" in connection_string else "cx_oracle"
                mode = "thin" if "mode=thin" in connection_string else "thick"
                logger.info(f"Successfully connected using {driver_name} ({mode} mode)")
                return connection_string

            except Exception as e:
                logger.debug(f"Connection method {i+1} failed: {e}")
                continue

        # If all methods fail, provide helpful error message
        raise ConnectionError(
            f"Failed to connect to Oracle using any available method. "
            f"Tried: python-oracledb (thin/thick), cx_Oracle. "
            f"For cx_Oracle, ensure Oracle Instant Client is installed. "
            f"For python-oracledb, ensure the package is installed: pip install oracledb"
        )

    def disconnect(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self._initialized = False

    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL query"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        try:
            with self.engine.connect() as conn:
                # Execute query
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))

                # Handle different fetch modes
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    if fetch == "all":
                        return result.fetchall()
                    elif fetch == "one":
                        return result.fetchone()
                    elif isinstance(fetch, int):
                        return result.fetchmany(fetch)
                    else:
                        return result.fetchall()
                else:
                    # For non-SELECT queries, return rowcount
                    conn.commit()
                    return result.rowcount

        except SQLAlchemyError as e:
            logger.error(f"Oracle query error: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an update query and return affected row count."""
        if not self.engine:
            self.connect()
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.rowcount
        except SQLAlchemyError as e:
            raise RuntimeError(f"Oracle update failed: {e}")
    
    def get_tables(self) -> List[str]:
        """Get list of tables in the database."""
        query = """
        SELECT table_name as name
        FROM user_tables
        ORDER BY table_name
        """
        result = self.execute_query(query)
        return [row['name'] for row in result]
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        query = f"""
        SELECT 
            column_name as name,
            data_type as type,
            nullable,
            data_default as default_value,
            CASE WHEN constraint_type = 'P' THEN 1 ELSE 0 END as is_primary_key
        FROM user_tab_columns c
        LEFT JOIN (
            SELECT cc.column_name, uc.constraint_type
            FROM user_constraints uc
            JOIN user_cons_columns cc ON uc.constraint_name = cc.constraint_name
            WHERE uc.table_name = '{table_name.upper()}'
            AND uc.constraint_type = 'P'
        ) pk ON c.column_name = pk.column_name
        WHERE c.table_name = '{table_name.upper()}'
        ORDER BY c.column_id
        """
        
        columns = self.execute_query(query)
        
        schema = {
            'table_name': table_name,
            'columns': []
        }
        
        for col in columns:
            schema['columns'].append({
                'name': col['name'],
                'type': col['type'],
                'nullable': col['nullable'] == 'Y',
                'default': col['default_value'],
                'primary_key': bool(col['is_primary_key'])
            })
        
        return schema
    
    def get_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        query = f"""
        SELECT 
            index_name as name,
            column_name,
            uniqueness as unique_index,
            index_type
        FROM user_ind_columns ic
        JOIN user_indexes i ON ic.index_name = i.index_name
        WHERE ic.table_name = '{table_name.upper()}'
        ORDER BY ic.index_name, ic.column_position
        """
        
        return self.execute_query(query)
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        query = f"""
        SELECT 
            constraint_name as name,
            column_name,
            r_table_name as referenced_table,
            r_column_name as referenced_column
        FROM user_cons_columns cc
        JOIN user_constraints c ON cc.constraint_name = c.constraint_name
        JOIN user_cons_columns rcc ON c.r_constraint_name = rcc.constraint_name
        WHERE c.table_name = '{table_name.upper()}'
        AND c.constraint_type = 'R'
        ORDER BY cc.constraint_name, cc.position
        """
        
        return self.execute_query(query)
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        """Create a new table with the given schema."""
        columns = []
        for col in schema.get('columns', []):
            col_def = f'"{col["name"]}" {col["type"]}'
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            if col.get('default') is not None:
                col_def += f" DEFAULT {col['default']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            columns.append(col_def)
        
        query = f'CREATE TABLE "{table_name}" ({", ".join(columns)})'
        self.execute_update(query)
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table."""
        query = f'DROP TABLE "{table_name}"'
        self.execute_update(query)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        query = f"""
        SELECT COUNT(*) as count
        FROM user_tables
        WHERE table_name = '{table_name.upper()}'
        """
        result = self.execute_query(query)
        return result[0]['count'] > 0
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            'type': 'oracle',
            'host': self.host,
            'port': self.port,
            'service_name': self.service_name,
            'user': self.user,
            'connected': self.engine is not None and self._initialized
        }

    def health_check(self) -> bool:
        """Check if Oracle database connection is healthy"""
        try:
            # Use Oracle-specific syntax for health check
            self.execute_query("SELECT 1 FROM DUAL", fetch="one")
            return True
        except Exception:
            return False

    def get_tables_as_documents(self) -> List[TableDocument]:
        """Get tables as TableDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        query = "SELECT TABLE_NAME as name FROM USER_TABLES ORDER BY TABLE_NAME"

        try:
            result = self.execute_query(query)
            tables = []

            for row in result:
                # Oracle consistently returns tuples, so access by index
                table_name = row[0]  # Keep Oracle UPPERCASE naming standard

                table_doc = TableDocument(
                    table_name=table_name,
                    schema_name=self.user.upper(),
                    comment='',
                    columns=[],  # Will be populated separately if needed
                    foreign_keys=[],
                    indexes=[]
                )
                tables.append(table_doc)

            return tables

        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            raise

    def get_columns_as_documents(self, table_name: str = None) -> List[ColumnDocument]:
        """Get columns as ColumnDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        if table_name:
            # Get columns for specific table
            query = f"""
            SELECT
                c.TABLE_NAME as table_name,
                c.COLUMN_NAME as column_name,
                c.DATA_TYPE as data_type,
                c.NULLABLE as is_nullable,
                c.DATA_DEFAULT as default_value,
                CASE WHEN EXISTS (
                    SELECT 1 FROM ALL_CONSTRAINTS ac, ALL_CONS_COLUMNS acc
                    WHERE ac.CONSTRAINT_NAME = acc.CONSTRAINT_NAME
                    AND ac.CONSTRAINT_TYPE = 'P'
                    AND acc.TABLE_NAME = c.TABLE_NAME
                    AND acc.COLUMN_NAME = c.COLUMN_NAME
                    AND ac.OWNER = USER
                ) THEN 1 ELSE 0 END as is_primary_key
            FROM ALL_TAB_COLUMNS c
            WHERE c.TABLE_NAME = '{table_name.upper()}'
            AND c.OWNER = USER
            ORDER BY c.COLUMN_ID
            """
        else:
            # Get all columns
            query = """
            SELECT
                c.TABLE_NAME as table_name,
                c.COLUMN_NAME as column_name,
                c.DATA_TYPE as data_type,
                c.NULLABLE as is_nullable,
                c.DATA_DEFAULT as default_value,
                CASE WHEN EXISTS (
                    SELECT 1 FROM ALL_CONSTRAINTS ac, ALL_CONS_COLUMNS acc
                    WHERE ac.CONSTRAINT_NAME = acc.CONSTRAINT_NAME
                    AND ac.CONSTRAINT_TYPE = 'P'
                    AND acc.TABLE_NAME = c.TABLE_NAME
                    AND acc.COLUMN_NAME = c.COLUMN_NAME
                    AND ac.OWNER = SYS_CONTEXT('USERENV', 'SESSION_USER')
                ) THEN 1 ELSE 0 END as is_primary_key
            FROM ALL_TAB_COLUMNS c
            WHERE c.OWNER = SYS_CONTEXT('USERENV', 'SESSION_USER')
            ORDER BY c.TABLE_NAME, c.COLUMN_ID
            """

        try:
            result = self.execute_query(query)
            columns = []

            for row in result:
                # Oracle consistently returns tuples, so access by index based on SELECT order
                column_doc = ColumnDocument(
                    table_name=row[0],  # Keep Oracle UPPERCASE naming standard
                    column_name=row[1],  # Keep Oracle UPPERCASE naming standard
                    data_type=row[2],  # data_type (keep as-is for Oracle type names)
                    is_nullable=row[3] == 'Y',  # is_nullable
                    default_value=row[4] if len(row) > 4 else None,  # default_value
                    is_pk=bool(row[5]) if len(row) > 5 else False,  # is_pk (use is_pk, not is_primary_key)
                    comment=''
                )
                columns.append(column_doc)

            return columns

        except Exception as e:
            logger.error(f"Error getting columns: {e}")
            raise

    def get_foreign_keys_as_documents(self, table_name: str = None) -> List[ForeignKeyDocument]:
        """Get foreign keys as ForeignKeyDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        if table_name:
            where_clause = f"AND ac.TABLE_NAME = '{table_name.upper()}'"
        else:
            where_clause = ""

        query = f"""
        SELECT
            ac.CONSTRAINT_NAME as constraint_name,
            ac.TABLE_NAME as table_name,
            acc.COLUMN_NAME as column_name,
            r_ac.TABLE_NAME as referenced_table,
            r_acc.COLUMN_NAME as referenced_column
        FROM ALL_CONSTRAINTS ac
        JOIN ALL_CONS_COLUMNS acc ON ac.CONSTRAINT_NAME = acc.CONSTRAINT_NAME
        JOIN ALL_CONSTRAINTS r_ac ON ac.R_CONSTRAINT_NAME = r_ac.CONSTRAINT_NAME
        JOIN ALL_CONS_COLUMNS r_acc ON r_ac.CONSTRAINT_NAME = r_acc.CONSTRAINT_NAME
        WHERE ac.CONSTRAINT_TYPE = 'R'
        AND ac.OWNER = USER
        {where_clause}
        ORDER BY ac.CONSTRAINT_NAME
        """

        try:
            result = self.execute_query(query)
            foreign_keys = []

            for row in result:
                fk_doc = ForeignKeyDocument(
                    constraint_name=row['constraint_name'],
                    table_name=row['table_name'],
                    column_name=row['column_name'],
                    referenced_table=row['referenced_table'],
                    referenced_column=row['referenced_column']
                )
                foreign_keys.append(fk_doc)

            return foreign_keys

        except Exception as e:
            logger.error(f"Error getting foreign keys: {e}")
            raise

    def get_indexes_as_documents(self, table_name: str = None) -> List[IndexDocument]:
        """Get indexes as IndexDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        if table_name:
            where_clause = f"AND ai.TABLE_NAME = '{table_name.upper()}'"
        else:
            where_clause = ""

        query = f"""
        SELECT
            ai.INDEX_NAME as index_name,
            ai.TABLE_NAME as table_name,
            aic.COLUMN_NAME as column_name,
            ai.UNIQUENESS as uniqueness,
            CASE WHEN EXISTS (
                SELECT 1 FROM ALL_CONSTRAINTS ac
                WHERE ac.CONSTRAINT_TYPE = 'P'
                AND ac.INDEX_NAME = ai.INDEX_NAME
                AND ac.OWNER = SYS_CONTEXT('USERENV', 'SESSION_USER')
            ) THEN 1 ELSE 0 END as is_primary
        FROM ALL_INDEXES ai
        JOIN ALL_IND_COLUMNS aic ON ai.INDEX_NAME = aic.INDEX_NAME
        WHERE ai.OWNER = SYS_CONTEXT('USERENV', 'SESSION_USER')
        {where_clause}
        ORDER BY ai.INDEX_NAME, aic.COLUMN_POSITION
        """

        try:
            result = self.execute_query(query)
            indexes = []

            for row in result:
                index_doc = IndexDocument(
                    index_name=row['index_name'],
                    table_name=row['table_name'],
                    column_name=row['column_name'],
                    is_unique=row['uniqueness'] == 'UNIQUE',
                    is_primary=bool(row['is_primary'])
                )
                indexes.append(index_doc)

            return indexes

        except Exception as e:
            logger.error(f"Error getting indexes: {e}")
            raise

    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Get schemas as SchemaDocument objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        query = """
        SELECT
            USERNAME as schema_name,
            '' as comment
        FROM ALL_USERS
        WHERE USERNAME = SYS_CONTEXT('USERENV', 'SESSION_USER')
        ORDER BY USERNAME
        """

        try:
            result = self.execute_query(query)
            schemas = []

            for row in result:
                schema_doc = SchemaDocument(
                    schema_name=row['schema_name'],
                    comment=row.get('comment', ''),
                    tables=[],  # Will be populated separately if needed
                    views=[]
                )
                schemas.append(schema_doc)

            return schemas

        except Exception as e:
            logger.error(f"Error getting schemas: {e}")
            raise

    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values from the database."""
        # This is a placeholder implementation.
        # A more sophisticated version should be implemented based on requirements.
        return {}

    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data (most frequent values) for each column in a table."""
        inspector = inspect(self.engine)
        try:
            columns = inspector.get_columns(table_name.upper())
        except SQLAlchemyError as e:
            logger.error(f"Error inspecting columns for table {table_name}: {e}")
            raise e

        if not columns:
            logger.warning(f"No columns found for table {table_name}")
            return {}

        most_frequent_values: Dict[str, List[Any]] = {}

        for column in columns:
            column_name = column['name']
            try:
                # Get most frequent values for this column
                query = f"""
                SELECT * FROM (
                    SELECT "{column_name}", COUNT(*) as frequency
                    FROM "{table_name.upper()}"
                    WHERE "{column_name}" IS NOT NULL
                    GROUP BY "{column_name}"
                    ORDER BY COUNT(*) DESC
                ) WHERE ROWNUM <= {number_of_rows}
                """

                result = self.execute_query(query)
                values = [row[column_name] for row in result]
                most_frequent_values[column_name] = values

            except Exception as e:
                logger.warning(f"Error getting example data for column {column_name}: {e}")
                most_frequent_values[column_name] = []

        return most_frequent_values
