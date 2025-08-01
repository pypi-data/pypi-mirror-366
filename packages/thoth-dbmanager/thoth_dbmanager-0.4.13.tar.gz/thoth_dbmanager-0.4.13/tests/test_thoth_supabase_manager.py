"""
Test suite for Supabase database manager.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from dbmanager.impl.ThothSupabaseManager import ThothSupabaseManager
from dbmanager.plugins.supabase import SupabasePlugin
from dbmanager.adapters.supabase import SupabaseAdapter
from dbmanager.core.factory import ThothDbFactory


class TestThothSupabaseManager:
    """Test cases for ThothSupabaseManager"""
    
    def test_direct_connection_params(self):
        """Test direct database connection parameter validation"""
        with pytest.raises(ValueError):
            ThothSupabaseManager.get_instance(
                host=None,
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path="/tmp"
            )
    
    def test_rest_connection_params(self):
        """Test REST API connection parameter validation"""
        with pytest.raises(ValueError):
            ThothSupabaseManager.get_instance(
                project_url=None,
                api_key="test-key",
                db_root_path="/tmp",
                use_rest_api=True
            )
    
    def test_project_url_validation(self):
        """Test Supabase project URL format validation"""
        with pytest.raises(ValueError):
            ThothSupabaseManager.get_instance(
                project_url="invalid-url",
                api_key="test-key",
                db_root_path="/tmp",
                use_rest_api=True
            )
    
    def test_singleton_pattern(self):
        """Test singleton pattern for Supabase manager"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create first instance
            manager1 = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            # Create second instance with same params
            manager2 = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            assert manager1 is manager2
    
    def test_different_instances(self):
        """Test different instances for different parameters"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager1 = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test1",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            manager2 = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test2",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            assert manager1 is not manager2
    
    def test_ssl_enforcement(self):
        """Test SSL is enforced for Supabase connections"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            # Check that SSL is required in connection string
            assert "sslmode=require" in manager._build_supabase_connection_string()
    
    def test_connection_pooling(self):
        """Test connection pooling parameters are included"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            # Check that pooling parameters are included
            conn_str = manager._build_supabase_connection_string()
            assert "pool_size=10" in conn_str
            assert "max_overflow=20" in conn_str


class TestSupabasePlugin:
    """Test cases for SupabasePlugin"""
    
    def test_plugin_creation(self):
        """Test Supabase plugin creation"""
        plugin = SupabasePlugin("/tmp")
        assert plugin.plugin_name == "Supabase Plugin"
        assert plugin.plugin_version == "1.0.0"
    
    def test_validate_direct_params(self):
        """Test direct connection parameter validation"""
        plugin = SupabasePlugin("/tmp")
        
        # Valid parameters
        assert plugin._validate_direct_params(
            host="localhost",
            port=5432,
            database="test",
            user="user",
            password="pass"
        )
        
        # Invalid port
        assert not plugin._validate_direct_params(
            host="localhost",
            port=99999,
            database="test",
            user="user",
            password="pass"
        )
    
    def test_validate_rest_params(self):
        """Test REST API parameter validation"""
        plugin = SupabasePlugin("/tmp")
        
        # Valid parameters
        assert plugin._validate_rest_params(
            project_url="https://test.supabase.co",
            api_key="test-key"
        )
        
        # Invalid URL
        assert not plugin._validate_rest_params(
            project_url="invalid-url",
            api_key="test-key"
        )
    
    def test_create_adapter(self):
        """Test adapter creation"""
        plugin = SupabasePlugin("/tmp")
        adapter = plugin.create_adapter()
        assert isinstance(adapter, SupabaseAdapter)


class TestSupabaseAdapter:
    """Test cases for SupabaseAdapter"""
    
    def test_adapter_creation(self):
        """Test adapter creation"""
        params = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "user",
            "password": "pass"
        }
        adapter = SupabaseAdapter(params)
        assert adapter.connection_params == params
    
    def test_build_connection_string(self):
        """Test connection string building"""
        params = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "user",
            "password": "pass"
        }
        adapter = SupabaseAdapter(params)
        conn_str = adapter._build_connection_string()
        
        assert "postgresql://user:pass@localhost:5432/test" in conn_str
        assert "sslmode=require" in conn_str
    
    def test_ssl_parameters(self):
        """Test SSL parameter inclusion"""
        params = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "user",
            "password": "pass",
            "sslcert": "/path/to/cert.pem",
            "sslkey": "/path/to/key.pem"
        }
        adapter = SupabaseAdapter(params)
        conn_str = adapter._build_connection_string()
        
        assert "sslcert=/path/to/cert.pem" in conn_str
        assert "sslkey=/path/to/key.pem" in conn_str
    
    def test_system_table_filtering(self):
        """Test system table filtering"""
        params = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "user",
            "password": "pass"
        }
        adapter = SupabaseAdapter(params)
        
        # Mock the parent method to return some tables
        with patch.object(adapter, 'get_tables_as_documents') as mock_tables:
            mock_tables.return_value = [
                Mock(schema_name='public', table_name='users'),
                Mock(schema_name='auth', table_name='users'),
                Mock(schema_name='storage', table_name='objects')
            ]
            
            tables = adapter.get_tables_as_documents()
            # Should filter out auth and storage schemas
            assert len(tables) == 1
            assert tables[0].schema_name == 'public'


class TestFactoryIntegration:
    """Test cases for factory integration"""
    
    def test_factory_creation(self):
        """Test factory creation of Supabase manager"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = ThothDbFactory.create_manager(
                db_type="supabase",
                db_root_path=tmp_dir,
                host="localhost",
                port=5432,
                database="test",
                user="user",
                password="pass"
            )
            assert isinstance(manager, SupabasePlugin)
    
    def test_factory_validation(self):
        """Test factory validation"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Valid parameters
            manager = ThothDbFactory.create_with_validation(
                db_type="supabase",
                db_root_path=tmp_dir,
                host="localhost",
                port=5432,
                database="test",
                user="user",
                password="pass"
            )
            assert isinstance(manager, SupabasePlugin)
    
    def test_factory_validation_error(self):
        """Test factory validation error"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(ValueError):
                ThothDbFactory.create_with_validation(
                    db_type="supabase",
                    db_root_path=tmp_dir,
                    # Missing required parameters
                )
    
    def test_list_available_databases(self):
        """Test listing available databases"""
        databases = ThothDbFactory.list_available_databases()
        assert "supabase" in databases
    
    def test_get_required_parameters(self):
        """Test getting required parameters"""
        params = ThothDbFactory.get_required_parameters("supabase")
        assert "required" in params
        assert "host" in params["required"]
        assert "port" in params["required"]
        assert "database" in params["required"]
        assert "user" in params["required"]
        assert "password" in params["required"]


class TestSupabaseIntegration:
    """Integration tests for Supabase support"""
    
    def test_backward_compatibility(self):
        """Test backward compatibility with legacy manager"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test legacy manager creation
            manager = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            
            assert manager.db_type == "supabase"
            assert hasattr(manager, 'get_tables')
            assert hasattr(manager, 'get_columns')
    
    def test_plugin_system_integration(self):
        """Test integration with plugin system"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test plugin system
            plugin = ThothDbFactory.create_manager(
                db_type="supabase",
                db_root_path=tmp_dir,
                host="localhost",
                port=5432,
                database="test",
                user="user",
                password="pass"
            )
            
            assert plugin.plugin_name == "Supabase Plugin"
            assert plugin.supported_db_types == ["supabase", "supabase-postgresql"]
    
    def test_connection_modes(self):
        """Test both connection modes"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Test direct connection
            direct_manager = ThothSupabaseManager.get_instance(
                host="localhost",
                port=5432,
                dbname="test",
                user="user",
                password="pass",
                db_root_path=tmp_dir
            )
            assert not direct_manager.use_rest_api
            
            # Test REST API connection
            rest_manager = ThothSupabaseManager.get_instance(
                project_url="https://test.supabase.co",
                api_key="test-key",
                db_root_path=tmp_dir,
                use_rest_api=True
            )
            assert rest_manager.use_rest_api


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
