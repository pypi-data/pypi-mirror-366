"""
Unit tests for the new plugin-based architecture.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from dbmanager.documents import (
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
from dbmanager.core.registry import DbPluginRegistry, register_plugin
from dbmanager.core.factory import ThothDbFactory
from dbmanager.core.interfaces import DbPlugin, DbAdapter
from dbmanager.plugins.postgresql import PostgreSQLPlugin
from dbmanager.plugins.sqlite import SQLitePlugin
from dbmanager.adapters.sqlite import SQLiteAdapter
from dbmanager.ThothDbManager import ThothDbManager, ThothDbManagerAdapter


class TestDocuments:
    """Test document models"""
    
    def test_table_document_creation(self):
        """Test TableDocument creation and validation"""
        doc = TableDocument(
            table_name="users",
            schema_name="public",
            comment="User information table"
        )
        
        assert doc.table_name == "users"
        assert doc.schema_name == "public"
        assert doc.comment == "User information table"
        assert doc.thoth_type == ThothDbType.TABLE
        assert doc.id is not None
        assert "Table: users in schema public" in doc.text
    
    def test_column_document_creation(self):
        """Test ColumnDocument creation and validation"""
        doc = ColumnDocument(
            table_name="users",
            column_name="id",
            data_type="integer",
            is_pk=True,
            is_nullable=False,
            comment="Primary key"
        )
        
        assert doc.table_name == "users"
        assert doc.column_name == "id"
        assert doc.data_type == "integer"
        assert doc.is_pk is True
        assert doc.is_nullable is False
        assert doc.thoth_type == ThothDbType.COLUMN
        assert "Primary Key" in doc.text
    
    def test_query_document_creation(self):
        """Test QueryDocument creation and validation"""
        doc = QueryDocument(
            query="SELECT * FROM users WHERE active = true",
            query_type="SELECT",
            description="Get all active users"
        )
        
        assert doc.query == "SELECT * FROM users WHERE active = true"
        assert doc.query_type == "SELECT"
        assert doc.description == "Get all active users"
        assert doc.thoth_type == ThothDbType.QUERY
        assert "SELECT query" in doc.text
    
    def test_foreign_key_document_creation(self):
        """Test ForeignKeyDocument creation and validation"""
        doc = ForeignKeyDocument(
            source_table_name="orders",
            source_column_name="user_id",
            target_table_name="users",
            target_column_name="id",
            constraint_name="fk_orders_user"
        )
        
        assert doc.source_table_name == "orders"
        assert doc.source_column_name == "user_id"
        assert doc.target_table_name == "users"
        assert doc.target_column_name == "id"
        assert doc.thoth_type == ThothDbType.FOREIGN_KEY
        assert "orders.user_id -> users.id" in doc.text
    
    def test_create_document_factory(self):
        """Test document factory function"""
        doc = create_document(
            ThothDbType.TABLE,
            table_name="products",
            comment="Product catalog"
        )
        
        assert isinstance(doc, TableDocument)
        assert doc.table_name == "products"
        assert doc.comment == "Product catalog"
    
    def test_create_document_invalid_type(self):
        """Test document factory with invalid type"""
        with pytest.raises(ValueError, match="Unsupported document type"):
            create_document("invalid_type", table_name="test")


class TestPluginRegistry:
    """Test plugin registry functionality"""
    
    def setup_method(self):
        """Clear registry before each test"""
        DbPluginRegistry.clear_registry()
    
    def teardown_method(self):
        """Clear registry after each test"""
        DbPluginRegistry.clear_registry()
    
    def test_plugin_registration(self):
        """Test plugin registration"""
        class TestPlugin(DbPlugin):
            plugin_name = "Test Plugin"
            plugin_version = "1.0.0"
            supported_db_types = ["test"]
            
            def create_adapter(self, **kwargs):
                return Mock()
            
            def validate_connection_params(self, **kwargs):
                return True
        
        DbPluginRegistry.register("test", TestPlugin)
        
        assert "test" in DbPluginRegistry.list_plugins()
        assert DbPluginRegistry.get_plugin_class("test") == TestPlugin
    
    def test_plugin_unregistration(self):
        """Test plugin unregistration"""
        class TestPlugin(DbPlugin):
            plugin_name = "Test Plugin"
            plugin_version = "1.0.0"
            supported_db_types = ["test"]
            
            def create_adapter(self, **kwargs):
                return Mock()
            
            def validate_connection_params(self, **kwargs):
                return True
        
        DbPluginRegistry.register("test", TestPlugin)
        assert "test" in DbPluginRegistry.list_plugins()
        
        DbPluginRegistry.unregister("test")
        assert "test" not in DbPluginRegistry.list_plugins()
    
    def test_get_nonexistent_plugin(self):
        """Test getting non-existent plugin"""
        with pytest.raises(ValueError, match="No plugin registered"):
            DbPluginRegistry.get_plugin_class("nonexistent")
    
    def test_plugin_validation(self):
        """Test plugin validation"""
        class ValidPlugin(DbPlugin):
            plugin_name = "Valid Plugin"
            plugin_version = "1.0.0"
            supported_db_types = ["valid"]
            
            def create_adapter(self, **kwargs):
                return Mock()
            
            def validate_connection_params(self, **kwargs):
                return True
        
        class InvalidPlugin:
            pass
        
        assert DbPluginRegistry.validate_plugin(ValidPlugin) is True
        assert DbPluginRegistry.validate_plugin(InvalidPlugin) is False
    
    def test_register_decorator(self):
        """Test register decorator"""
        @register_plugin("decorated")
        class DecoratedPlugin(DbPlugin):
            plugin_name = "Decorated Plugin"
            plugin_version = "1.0.0"
            supported_db_types = ["decorated"]
            
            def create_adapter(self, **kwargs):
                return Mock()
            
            def validate_connection_params(self, **kwargs):
                return True
        
        assert "decorated" in DbPluginRegistry.list_plugins()
        assert DbPluginRegistry.get_plugin_class("decorated") == DecoratedPlugin


class TestThothDbFactory:
    """Test database factory functionality"""
    
    def setup_method(self):
        """Clear registry before each test"""
        DbPluginRegistry.clear_registry()
        
        # Register a mock plugin for testing
        class MockPlugin(DbPlugin):
            plugin_name = "Mock Plugin"
            plugin_version = "1.0.0"
            supported_db_types = ["mock"]
            
            def create_adapter(self, **kwargs):
                mock_adapter = Mock(spec=DbAdapter)
                mock_adapter.connect.return_value = None
                mock_adapter.health_check.return_value = True
                return mock_adapter
            
            def validate_connection_params(self, **kwargs):
                return "db_name" in kwargs
        
        DbPluginRegistry.register("mock", MockPlugin)
    
    def teardown_method(self):
        """Clear registry after each test"""
        DbPluginRegistry.clear_registry()
    
    def test_create_manager_success(self):
        """Test successful manager creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ThothDbFactory.create_manager(
                db_type="mock",
                db_root_path=temp_dir,
                db_mode="test",
                db_name="test_db"
            )
            
            assert manager is not None
            assert manager.db_root_path == temp_dir
            assert manager.db_mode == "test"
    
    def test_create_manager_invalid_type(self):
        """Test manager creation with invalid type"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(RuntimeError, match="Failed to create"):
                ThothDbFactory.create_manager(
                    db_type="invalid",
                    db_root_path=temp_dir,
                    db_mode="test"
                )
    
    def test_list_available_databases(self):
        """Test listing available databases"""
        databases = ThothDbFactory.list_available_databases()
        assert "mock" in databases
    
    def test_validate_database_type(self):
        """Test database type validation"""
        assert ThothDbFactory.validate_database_type("mock") is True
        assert ThothDbFactory.validate_database_type("invalid") is False
    
    def test_create_with_validation(self):
        """Test creation with parameter validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Should succeed with required parameter
            manager = ThothDbFactory.create_with_validation(
                db_type="mock",
                db_root_path=temp_dir,
                db_mode="test",
                db_name="test_db"
            )
            assert manager is not None
            
            # Should fail without required parameter
            with pytest.raises(ValueError, match="Missing required parameters"):
                ThothDbFactory.create_with_validation(
                    db_type="mock",
                    db_root_path=temp_dir,
                    db_mode="test"
                )


class TestSQLiteIntegration:
    """Test SQLite plugin integration"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_sqlite_adapter_creation(self):
        """Test SQLite adapter creation"""
        adapter = SQLiteAdapter({
            'database_path': str(self.db_path)
        })
        
        assert adapter.database_path == str(self.db_path)
        assert adapter.connection is None
        assert not adapter._initialized
    
    def test_sqlite_plugin_validation(self):
        """Test SQLite plugin parameter validation"""
        plugin = SQLitePlugin(db_root_path=self.temp_dir, db_mode="test")
        
        # Valid parameters
        assert plugin.validate_connection_params(database_path=str(self.db_path)) is True
        assert plugin.validate_connection_params(database_name="test_db") is True
        
        # Invalid parameters
        assert plugin.validate_connection_params() is False
        assert plugin.validate_connection_params(database_path=123) is False
    
    @patch('sqlite3.connect')
    @patch('sqlalchemy.create_engine')
    def test_sqlite_connection(self, mock_engine, mock_connect):
        """Test SQLite connection establishment"""
        # Mock SQLAlchemy engine
        mock_engine_instance = Mock()
        mock_conn = Mock()
        mock_engine_instance.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = None
        mock_engine.return_value = mock_engine_instance
        
        # Mock sqlite3 connection
        mock_sqlite_conn = Mock()
        mock_connect.return_value = mock_sqlite_conn
        
        adapter = SQLiteAdapter({
            'database_path': str(self.db_path)
        })
        
        adapter.connect()
        
        assert adapter._initialized is True
        mock_engine.assert_called_once()
        mock_connect.assert_called_once()


class TestBackwardCompatibility:
    """Test backward compatibility with existing API"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_thoth_db_manager_adapter(self):
        """Test ThothDbManagerAdapter functionality"""
        # Create a mock plugin
        mock_plugin = Mock(spec=DbPlugin)
        mock_plugin.db_root_path = self.temp_dir
        mock_plugin.db_mode = "test"
        mock_plugin.supported_db_types = ["mock"]
        mock_plugin._initialized = True
        mock_plugin.db_id = "test_db"
        mock_plugin.db_directory_path = Path(self.temp_dir) / "test_db"
        
        # Mock adapter
        mock_adapter = Mock(spec=DbAdapter)
        mock_adapter.engine = Mock()
        mock_plugin.adapter = mock_adapter
        
        # Create adapter
        adapter = ThothDbManagerAdapter(mock_plugin)
        
        assert adapter.db_root_path == self.temp_dir
        assert adapter.db_mode == "test"
        assert adapter.db_type == "mock"
        assert adapter.db_id == "test_db"
        assert adapter._initialized is True
    
    def test_adapter_method_delegation(self):
        """Test that adapter methods are properly delegated"""
        # Create mock plugin with methods
        mock_plugin = Mock(spec=DbPlugin)
        mock_plugin.db_root_path = self.temp_dir
        mock_plugin.db_mode = "test"
        mock_plugin.supported_db_types = ["mock"]
        mock_plugin._initialized = True
        
        # Mock methods
        mock_plugin.execute_sql.return_value = [{"result": "test"}]
        mock_plugin.get_tables.return_value = [{"name": "test_table", "comment": ""}]
        mock_plugin.get_columns.return_value = [{"name": "id", "data_type": "integer", "comment": "", "is_pk": True}]
        mock_plugin.get_foreign_keys.return_value = []
        mock_plugin.get_unique_values.return_value = {}
        
        adapter = ThothDbManagerAdapter(mock_plugin)
        
        # Test method delegation
        result = adapter.execute_sql("SELECT 1")
        assert result == [{"result": "test"}]
        mock_plugin.execute_sql.assert_called_once_with("SELECT 1", None, "all", 60)
        
        tables = adapter.get_tables()
        assert tables == [{"name": "test_table", "comment": ""}]
        mock_plugin.get_tables.assert_called_once()
        
        columns = adapter.get_columns("test_table")
        assert columns == [{"name": "id", "data_type": "integer", "comment": "", "is_pk": True}]
        mock_plugin.get_columns.assert_called_once_with("test_table")


class TestDocumentOperations:
    """Test document-based operations"""
    
    def test_document_serialization(self):
        """Test document serialization to dict"""
        doc = TableDocument(
            table_name="users",
            schema_name="public",
            comment="User table"
        )
        
        doc_dict = doc.model_dump()
        
        assert doc_dict["table_name"] == "users"
        assert doc_dict["schema_name"] == "public"
        assert doc_dict["comment"] == "User table"
        assert doc_dict["thoth_type"] == "table"
    
    def test_document_deserialization(self):
        """Test document deserialization from dict"""
        doc_dict = {
            "table_name": "products",
            "schema_name": "public",
            "comment": "Product catalog",
            "thoth_type": "table"
        }
        
        doc = TableDocument(**doc_dict)
        
        assert doc.table_name == "products"
        assert doc.schema_name == "public"
        assert doc.comment == "Product catalog"
        assert doc.thoth_type == ThothDbType.TABLE
    
    def test_document_validation(self):
        """Test document validation"""
        # Valid document
        doc = ColumnDocument(
            table_name="users",
            column_name="email",
            data_type="varchar"
        )
        assert doc.table_name == "users"
        
        # Invalid document (missing required field)
        with pytest.raises(ValueError):
            ColumnDocument(
                column_name="email",
                data_type="varchar"
                # missing table_name
            )


if __name__ == "__main__":
    pytest.main([__file__])