import unittest
from unittest.mock import patch, MagicMock
from dbmanager.impl.ThothMariaDbManager import ThothMariaDbManager

class TestThothMariaDbManager(unittest.TestCase):

    @patch('dbmanager.impl.ThothMariaDbManager.create_engine')
    def test_get_instance(self, mock_create_engine):
        # Mock the engine and connection
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Test creating a new instance
        instance1 = ThothMariaDbManager.get_instance(
            host="localhost",
            port=3306,
            dbname="testdb",
            user="testuser",
            password="testpassword",
            db_root_path="/tmp"
        )
        self.assertIsInstance(instance1, ThothMariaDbManager)

        # Test retrieving an existing instance
        instance2 = ThothMariaDbManager.get_instance(
            host="localhost",
            port=3306,
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