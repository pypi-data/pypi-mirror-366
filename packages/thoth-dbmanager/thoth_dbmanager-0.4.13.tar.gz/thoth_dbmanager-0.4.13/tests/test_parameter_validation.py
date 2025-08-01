import unittest
import os
from pathlib import Path


class TestParameterValidation(unittest.TestCase):
    """Separate tests for parameter validation that work with all manager types"""
    
    def test_sqlite_manager_invalid_params(self):
        """Test parameter validation specifically for SQLite manager"""
        from dbmanager.impl.ThothSqliteManager import ThothSqliteManager
        
        with self.assertRaises(ValueError):
            ThothSqliteManager(db_id="test", db_root_path="", db_mode="test")
    
    def test_pg_manager_invalid_params(self):
        """Test parameter validation specifically for PostgreSQL manager"""
        from dbmanager.impl.ThothPgManager import ThothPgManager
        
        with self.assertRaises(ValueError):
            ThothPgManager(
                host="localhost", 
                port=5432, 
                dbname="test", 
                user="test", 
                password="test",
                db_root_path="", 
                db_mode="test"
            )
    
    def test_sqlite_manager_invalid_db_id(self):
        """Test SQLite manager with invalid db_id"""
        from dbmanager.impl.ThothSqliteManager import ThothSqliteManager
        
        with self.assertRaises((ValueError, TypeError)):
            ThothSqliteManager(db_id="", db_root_path="data", db_mode="test")
    
    def test_pg_manager_invalid_connection_params(self):
        """Test PostgreSQL manager with invalid connection parameters"""
        from dbmanager.impl.ThothPgManager import ThothPgManager
        
        # Test with empty host
        with self.assertRaises((ValueError, TypeError)):
            ThothPgManager(
                host="", 
                port=5432, 
                dbname="test", 
                user="test", 
                password="test",
                db_root_path="data", 
                db_mode="test"
            )
        
        # Test with invalid port
        with self.assertRaises((ValueError, TypeError)):
            ThothPgManager(
                host="localhost", 
                port=-1, 
                dbname="test", 
                user="test", 
                password="test",
                db_root_path="data", 
                db_mode="test"
            )


if __name__ == '__main__':
    unittest.main()