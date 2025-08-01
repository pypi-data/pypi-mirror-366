import unittest
import os
import logging
from pathlib import Path

from thoth_dbmanager import ThothSqliteManager

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestThothSqliteManager(unittest.TestCase):
    """Test suite for ThothSqliteManager with california_schools database."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Define paths
        cls.project_root = Path(__file__).parent.parent
        cls.db_root_path = str(cls.project_root)
        cls.db_id = "california_schools"
        cls.db_mode = "dev"

        # Verify that the database file exists
        db_file_path = cls.project_root / "data" / f"{cls.db_mode}_databases" / cls.db_id / f"{cls.db_id}.sqlite"
        if not db_file_path.exists():
            # Create the directory structure if it doesn't exist
            db_file_path.parent.mkdir(parents=True, exist_ok=True)
            # Create an empty SQLite database for testing
            import sqlite3
            conn = sqlite3.connect(str(db_file_path))
            conn.execute("""CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )""")
            conn.execute("INSERT INTO test_table (name, value) VALUES ('test1', 100)")
            conn.execute("INSERT INTO test_table (name, value) VALUES ('test2', 200)")
            conn.commit()
            conn.close()
            logger.info(f"Created test database at: {db_file_path}")

        logger.info(f"Using database file at: {db_file_path}")

        # Get database manager instance
        try:
            cls.db_manager = ThothSqliteManager.get_instance(
                db_id=cls.db_id,
                db_root_path=cls.db_root_path,
                db_mode=cls.db_mode
            )
            logger.info("Successfully connected to california_schools SQLite database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def test_singleton_pattern(self):
        """Test that get_instance returns the same instance for same parameters."""
        second_instance = ThothSqliteManager.get_instance(
            db_id=self.db_id,
            db_root_path=self.db_root_path,
            db_mode=self.db_mode
        )

        self.assertIs(self.db_manager, second_instance,
                      "get_instance should return the same instance for same parameters")

    def test_different_parameters_create_new_instance(self):
        """Test that get_instance returns a new instance for different parameters."""
        # Using a different db_mode should create a new instance
        different_instance = ThothSqliteManager.get_instance(
            db_id=self.db_id,
            db_root_path=self.db_root_path,
            db_mode="different_mode"
        )

        self.assertIsNot(self.db_manager, different_instance,
                         "get_instance should return a different instance for different parameters")

    def test_execute_sql_select(self):
        """Test executing a simple SELECT query."""
        # Get the list of tables in the database
        sql = """SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"""

        result = self.db_manager.execute_sql(sql)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "Result items should be dictionaries")
            logger.info(f"Tables in database: {[table['name'] for table in result]}")

    def test_execute_sql_with_params(self):
        """Test executing a parameterized query."""
        # Find tables with names containing a specific string
        sql = """SELECT name FROM sqlite_master WHERE type='table' AND name LIKE :pattern"""

        params = {"pattern": "%test%"}
        result = self.db_manager.execute_sql(sql, params)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        logger.info(f"Tables matching pattern '%test%': {[table['name'] for table in result]}")

    def test_execute_sql_fetch_one(self):
        """Test executing a query with fetch='one'."""
        sql = """SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"""

        result = self.db_manager.execute_sql(sql, fetch="one")

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("table_count", result, "Result should contain 'table_count' key")
        logger.info(f"Number of tables: {result['table_count']}")

    def test_execute_sql_fetch_many(self):
        """Test executing a query with fetch=N."""
        sql = """SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' LIMIT 10"""

        fetch_count = 3
        result = self.db_manager.execute_sql(sql, fetch=fetch_count)

        self.assertIsNotNone(result, "Query result should not be None")
        self.assertIsInstance(result, list, "Result should be a list")
        self.assertLessEqual(len(result), fetch_count,
                             f"Result should contain at most {fetch_count} items")
        logger.info(f"Fetched {len(result)} tables: {[table['name'] for table in result]}")

    def test_get_unique_values(self):
        """Test retrieving unique values from the database."""
        unique_values = self.db_manager.get_unique_values()

        self.assertIsNotNone(unique_values, "Unique values should not be None")
        self.assertIsInstance(unique_values, dict, "Unique values should be a dictionary")

        # Log the structure of unique_values for debugging
        logger.info(f"Unique values structure: {list(unique_values.keys())}")

        # If there are tables with unique values, check their structure
        if unique_values:
            table_name = next(iter(unique_values))
            table_values = unique_values[table_name]

            self.assertIsInstance(table_values, dict,
                                  "Table values should be a dictionary")

            if table_values:
                column_name = next(iter(table_values))
                column_values = table_values[column_name]

                self.assertIsInstance(column_values, list,
                                      "Column values should be a list")

                logger.info(f"Sample unique values for {table_name}.{column_name}: "
                            f"{column_values[:5] if len(column_values) > 5 else column_values}")

    def test_complex_query(self):
        """Test executing a more complex query with joins if applicable."""
        # First, get the list of tables
        tables_sql = """SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"""

        tables = self.db_manager.execute_sql(tables_sql)
        table_names = [table['name'] for table in tables]

        logger.info(f"Available tables: {table_names}")

        # If we have at least one table, try to query it
        if table_names:
            sample_table = table_names[0]

            # Get column information for the sample table
            columns_sql = f"PRAGMA table_info({sample_table})"

            columns = self.db_manager.execute_sql(columns_sql)
            column_names = [col['name'] for col in columns]

            logger.info(f"Columns in {sample_table}: {column_names}")

            # If we have columns, try a simple query
            if column_names:
                sample_column = column_names[0]
                query_sql = f"SELECT {sample_column} FROM {sample_table} LIMIT 5"

                result = self.db_manager.execute_sql(query_sql)

                self.assertIsNotNone(result, "Query result should not be None")
                self.assertIsInstance(result, list, "Result should be a list")

                logger.info(f"Sample data from {sample_table}.{sample_column}: {result}")

    def test_error_handling(self):
        """Test error handling for invalid SQL."""
        invalid_sql = "SELECT * FROM non_existent_table"

        with self.assertRaises(Exception) as context:
            self.db_manager.execute_sql(invalid_sql)

        logger.info(f"Expected error was raised: {str(context.exception)}")

    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        # First, clean up any existing test table
        cleanup_sql = "DROP TABLE IF EXISTS test_rollback"
        try:
            self.db_manager.execute_sql(cleanup_sql, fetch=None)
        except:
            pass  # Ignore if table doesn't exist

        # Create a temporary table
        create_table_sql = """CREATE TABLE test_rollback (
                                id INTEGER PRIMARY KEY,
                                name TEXT
                            )"""

        try:
            # Create the table (use fetch=None to avoid fetchall() on non-SELECT)
            create_result = self.db_manager.execute_sql(create_table_sql, fetch=None)
            logger.info(f"Table creation result: {create_result}")

            # Insert a valid row (use fetch=None to avoid fetchall() on non-SELECT)
            insert_sql = """INSERT INTO test_rollback (name) VALUES ('test_value')"""
            insert_result = self.db_manager.execute_sql(insert_sql, fetch=None)
            logger.info(f"Insert result: {insert_result}")

            # Try an invalid insert that should cause an error
            invalid_insert = """INSERT INTO test_rollback (non_existent_column) VALUES ('test')"""

            with self.assertRaises(Exception):
                self.db_manager.execute_sql(invalid_insert, fetch=None)

            # Check that the valid insert was committed (SQLite behavior differs from PostgreSQL)
            count_sql = """SELECT COUNT(*) as count FROM test_rollback"""
            result = self.db_manager.execute_sql(count_sql)

            # In SQLite, each statement is its own transaction by default,
            # so the first INSERT should still be there
            # Legacy manager returns list of dictionaries
            self.assertIsNotNone(result, "Count result should not be None")
            self.assertIsInstance(result, list, "Result should be a list")
            self.assertEqual(len(result), 1, "Should have one result row")
            self.assertEqual(result[0]['count'], 1, "Valid insert should be committed")

            logger.info("Transaction rollback test completed successfully")

        except Exception as e:
            logger.error(f"Transaction test failed: {str(e)}")
            raise
        finally:
            # Clean up - drop the test table
            try:
                self.db_manager.execute_sql("DROP TABLE IF EXISTS test_rollback", fetch=None)
            except Exception as cleanup_error:
                logger.warning(f"Cleanup failed: {cleanup_error}")

    def test_database_file_exists(self):
        """Test that the database file exists at the expected location."""
        db_file_path = self.project_root / "data" / f"{self.db_mode}_databases" / self.db_id / f"{self.db_id}.sqlite"
        self.assertTrue(db_file_path.exists(), f"Database file should exist at {db_file_path}")
        self.assertTrue(db_file_path.is_file(), f"{db_file_path} should be a file")

        # Check that the file has some content (not empty)
        self.assertGreater(db_file_path.stat().st_size, 0,
                           "Database file should not be empty")

        logger.info(f"Database file exists and has size: {db_file_path.stat().st_size} bytes")

    def test_data_types(self):
        """Test handling of different data types in SQLite."""
        # Create a test table with various data types
        create_table_sql = """CREATE TABLE IF NOT EXISTS test_data_types (
                                id INTEGER PRIMARY KEY,
                                text_col TEXT,
                                integer_col INTEGER,
                                real_col REAL,
                                blob_col BLOB,
                                null_col TEXT
                            )"""

        try:
            # Create the table
            self.db_manager.execute_sql(create_table_sql, fetch=None)

            # Insert test data with various types
            insert_sql = """INSERT INTO test_data_types
                           (text_col, integer_col, real_col, blob_col, null_col)
                           VALUES ('test_string', 42, 3.14159, 'binary_data', NULL)"""
            self.db_manager.execute_sql(insert_sql, fetch=None)

            # Get column information including data types
            columns_sql = "PRAGMA table_info(test_data_types)"
            columns = self.db_manager.execute_sql(columns_sql)

            # Log column types for the test table
            column_types = {col['name']: col['type'] for col in columns}
            logger.info(f"Column types in test_data_types: {column_types}")

            # Test a query that returns different data types
            query_sql = "SELECT * FROM test_data_types LIMIT 1"
            result = self.db_manager.execute_sql(query_sql, fetch="one")

            if result:
                # Log the types of values returned
                value_types = {key: type(value).__name__ for key, value in result.items()}
                logger.info(f"Value types in result: {value_types}")

                # Verify that we can access the values
                for key, value in result.items():
                    self.assertIsNotNone(key, "Column name should not be None")
                    # Value can be None, so we don't assert on that

                # Test specific data type handling
                self.assertEqual(result['text_col'], 'test_string')
                self.assertEqual(result['integer_col'], 42)
                self.assertAlmostEqual(result['real_col'], 3.14159, places=5)
                self.assertIsNone(result['null_col'])

            # Clean up
            self.db_manager.execute_sql("DROP TABLE IF EXISTS test_data_types", fetch=None)

        except Exception as e:
            logger.error(f"Data types test failed: {str(e)}")
            # Clean up on error
            try:
                self.db_manager.execute_sql("DROP TABLE IF EXISTS test_data_types", fetch=None)
            except:
                pass
            raise

    def test_large_result_set(self):
        """Test handling of larger result sets."""
        # Create a test table with sufficient data
        create_table_sql = """CREATE TABLE IF NOT EXISTS test_large_data (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                value INTEGER
                            )"""

        try:
            self.db_manager.execute_sql(create_table_sql, fetch=None)

            # Insert multiple rows to create a larger dataset
            # Insert 50 rows of test data
            for i in range(50):
                # Use fetch=None for INSERT statements
                self.db_manager.execute_sql(
                    f"INSERT INTO test_large_data (name, value) VALUES ('test_name_{i}', {i})",
                    fetch=None
                )

            # Test fetching all rows
            query_sql = "SELECT * FROM test_large_data"
            result = self.db_manager.execute_sql(query_sql)

            self.assertIsNotNone(result, "Query result should not be None")
            self.assertIsInstance(result, list, "Result should be a list")
            self.assertEqual(len(result), 50, "Should have 50 rows")
            logger.info(f"Successfully fetched {len(result)} rows from test_large_data")

            # Test fetching with LIMIT
            limit_query_sql = "SELECT * FROM test_large_data LIMIT 25"
            limit_result = self.db_manager.execute_sql(limit_query_sql)

            self.assertIsNotNone(limit_result, "Limited query result should not be None")
            self.assertIsInstance(limit_result, list, "Limited result should be a list")
            self.assertEqual(len(limit_result), 25, "Should have 25 rows with LIMIT")

            # Clean up - drop the test table
            cleanup_sql = "DROP TABLE IF EXISTS test_large_data"
            self.db_manager.execute_sql(cleanup_sql, fetch=None)

        except Exception as e:
            logger.error(f"Large result set test failed: {str(e)}")
            # Clean up on error
            try:
                self.db_manager.execute_sql("DROP TABLE IF EXISTS test_large_data", fetch=None)
            except:
                pass
            raise

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        # No explicit cleanup needed for read-only tests
        # For tests that modify the database, we've already cleaned up in the test methods
        logger.info("Test suite completed")


if __name__ == '__main__':
    unittest.main()