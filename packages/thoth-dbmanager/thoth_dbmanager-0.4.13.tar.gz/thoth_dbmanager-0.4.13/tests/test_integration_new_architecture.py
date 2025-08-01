"""
Integration tests for the new plugin-based architecture with real databases.
"""
import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path

from dbmanager import (
    ThothDbManager,
    ThothDbFactory,
    DbPluginRegistry,
    TableDocument,
    ColumnDocument,
    ThothDbType
)


class TestSQLiteIntegration:
    """Integration tests with real SQLite database"""
    
    def setup_method(self):
        """Set up test environment with real SQLite database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_integration.db"
        
        # Create a test database with sample data
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX idx_posts_user_id ON posts (user_id)
        """)
        
        # Insert sample data
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("john_doe", "john@example.com"))
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("jane_smith", "jane@example.com"))
        cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", (1, "First Post", "Hello World"))
        cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", (1, "Second Post", "Another post"))
        cursor.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", (2, "Jane's Post", "Jane's content"))
        
        conn.commit()
        conn.close()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_factory_create_sqlite_manager(self):
        """Test creating SQLite manager through factory"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        assert manager is not None
        assert manager.db_root_path == self.temp_dir
        assert manager.db_mode == "test"
        assert manager._initialized is True
    
    def test_backward_compatibility_get_instance(self):
        """Test backward compatibility with ThothDbManager.get_instance"""
        manager = ThothDbManager.get_instance(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        assert manager is not None
        
        # Test legacy methods
        tables = manager.get_tables()
        assert len(tables) == 2
        
        table_names = [table["name"] for table in tables]
        assert "users" in table_names
        assert "posts" in table_names
    
    def test_execute_sql_operations(self):
        """Test SQL execution through new architecture"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        # Test SELECT query
        result = manager.execute_sql("SELECT COUNT(*) as count FROM users")
        assert len(result) == 1
        assert result[0].count == 2
        
        # Test INSERT query
        rows_affected = manager.execute_sql(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            params={"username": "test_user", "email": "test@example.com"}
        )
        assert rows_affected == 1
        
        # Verify insert
        result = manager.execute_sql("SELECT COUNT(*) as count FROM users")
        assert result[0].count == 3
    
    def test_document_based_operations(self):
        """Test new document-based operations"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        # Test getting tables as documents
        if hasattr(manager, 'get_tables_as_documents'):
            table_docs = manager.get_tables_as_documents()
            assert len(table_docs) == 2
            assert all(isinstance(doc, TableDocument) for doc in table_docs)
            
            table_names = [doc.table_name for doc in table_docs]
            assert "users" in table_names
            assert "posts" in table_names
        
        # Test getting columns as documents
        if hasattr(manager, 'get_columns_as_documents'):
            column_docs = manager.get_columns_as_documents("users")
            assert len(column_docs) >= 4  # id, username, email, created_at
            assert all(isinstance(doc, ColumnDocument) for doc in column_docs)
            
            column_names = [doc.column_name for doc in column_docs]
            assert "id" in column_names
            assert "username" in column_names
            assert "email" in column_names
            
            # Check primary key detection
            id_column = next(doc for doc in column_docs if doc.column_name == "id")
            assert id_column.is_pk is True
    
    def test_foreign_key_detection(self):
        """Test foreign key detection"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        if hasattr(manager, 'get_foreign_keys_as_documents'):
            fk_docs = manager.get_foreign_keys_as_documents()
            assert len(fk_docs) >= 1
            
            # Find the posts -> users foreign key
            posts_fk = next((doc for doc in fk_docs if doc.source_table_name == "posts"), None)
            assert posts_fk is not None
            assert posts_fk.source_column_name == "user_id"
            assert posts_fk.target_table_name == "users"
            assert posts_fk.target_column_name == "id"
    
    def test_index_detection(self):
        """Test index detection"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        if hasattr(manager, 'get_indexes_as_documents'):
            index_docs = manager.get_indexes_as_documents()
            assert len(index_docs) >= 1
            
            # Check for our custom index
            custom_index = next((doc for doc in index_docs if doc.index_name == "idx_posts_user_id"), None)
            assert custom_index is not None
            assert custom_index.table_name == "posts"
            assert "user_id" in custom_index.columns
    
    def test_unique_values_extraction(self):
        """Test unique values extraction"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        unique_values = manager.get_unique_values()
        
        assert "users" in unique_values
        assert "posts" in unique_values
        
        # Check username values
        if "username" in unique_values["users"]:
            usernames = unique_values["users"]["username"]
            assert "john_doe" in usernames
            assert "jane_smith" in usernames
    
    def test_health_check(self):
        """Test database health check"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        if hasattr(manager, 'health_check'):
            assert manager.health_check() is True
    
    def test_connection_info(self):
        """Test connection information retrieval"""
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        if hasattr(manager, 'get_connection_info'):
            info = manager.get_connection_info()
            
            assert "plugin_name" in info
            assert "adapter_type" in info
            assert "database_path" in info
            assert info["database_path"] == str(self.db_path)


class TestPluginRegistryIntegration:
    """Test plugin registry with real plugins"""
    
    def test_registered_plugins(self):
        """Test that plugins are properly registered"""
        plugins = DbPluginRegistry.list_plugins()
        
        assert "postgresql" in plugins
        assert "sqlite" in plugins
    
    def test_plugin_info(self):
        """Test plugin information retrieval"""
        sqlite_info = DbPluginRegistry.get_plugin_info("sqlite")
        
        assert sqlite_info["plugin_name"] == "SQLite Plugin"
        assert sqlite_info["plugin_version"] == "1.0.0"
        assert "sqlite" in sqlite_info["supported_db_types"]
    
    def test_factory_status(self):
        """Test factory status information"""
        status = ThothDbFactory.get_plugin_status()
        
        assert "total_plugins" in status
        assert status["total_plugins"] >= 2
        assert "available_types" in status
        assert "sqlite" in status["available_types"]
        assert "postgresql" in status["available_types"]


class TestDocumentWorkflow:
    """Test complete document-based workflow"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "workflow_test.db"
        
        # Create a simple test database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                status TEXT DEFAULT 'active'
            )
        """)
        
        cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
        cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))
        
        conn.commit()
        conn.close()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_document_workflow(self):
        """Test complete workflow using document-based operations"""
        # Create manager
        manager = ThothDbFactory.create_manager(
            db_type="sqlite",
            db_root_path=self.temp_dir,
            db_mode="test",
            database_path=str(self.db_path)
        )
        
        # Get table documents
        if hasattr(manager, 'get_tables_as_documents'):
            table_docs = manager.get_tables_as_documents()
            customers_table = next(doc for doc in table_docs if doc.table_name == "customers")
            
            assert customers_table.table_name == "customers"
            assert customers_table.thoth_type == ThothDbType.TABLE
            
            # Get column documents for this table
            if hasattr(manager, 'get_columns_as_documents'):
                column_docs = manager.get_columns_as_documents("customers")
                
                # Verify column structure
                column_names = [doc.column_name for doc in column_docs]
                assert "id" in column_names
                assert "name" in column_names
                assert "email" in column_names
                assert "status" in column_names
                
                # Check primary key
                id_column = next(doc for doc in column_docs if doc.column_name == "id")
                assert id_column.is_pk is True
                
                # Check data types
                name_column = next(doc for doc in column_docs if doc.column_name == "name")
                assert "TEXT" in name_column.data_type.upper()
        
        # Test query execution
        result = manager.execute_sql("SELECT name FROM customers ORDER BY name")
        names = [row.name for row in result]
        assert names == ["Alice", "Bob"]
        
        # Test unique values
        unique_values = manager.get_unique_values()
        if "customers" in unique_values and "name" in unique_values["customers"]:
            customer_names = unique_values["customers"]["name"]
            assert "Alice" in customer_names
            assert "Bob" in customer_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])