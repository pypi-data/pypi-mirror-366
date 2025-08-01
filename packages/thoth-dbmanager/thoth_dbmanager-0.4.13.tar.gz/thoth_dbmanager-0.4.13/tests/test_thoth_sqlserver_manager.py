import unittest
from unittest.mock import patch, MagicMock
from dbmanager.impl.ThothSqlServerManager import ThothSqlServerManager

class TestThothSqlServerManager(unittest.TestCase):

    @patch('dbmanager.impl.ThothSqlServerManager.create_engine')
    def test_get_instance(self, mock_create_engine):
        # Mock the engine and connection
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Test creating a new instance
        instance1 = ThothSqlServerManager.get_instance(
            host="localhost",
            port=1433,
            dbname="testdb",
            user="testuser",
            password="testpassword",
            db_root_path="/tmp"
        )
        self.assertIsInstance(instance1, ThothSqlServerManager)

        # Test retrieving an existing instance
        instance2 = ThothSqlServerManager.get_instance(
            host="localhost",
            port=1433,
            dbname="testdb",
            user="testuser",
            password="testpassword",
            db_root_path="/tmp"
        )
        self.assertIs(instance1, instance2)

    # Add more tests for other methods (get_tables, get_columns, etc.)
    # These will likely require more extensive mocking of SQLAlchemy components.

if __name__ == '__main__':
    unittest.main()