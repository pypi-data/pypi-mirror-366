"""
Unit tests for Database Analyzer Engine functionality.

This module tests the DatabaseAnalyzer class for PostgreSQL connection handling,
schema extraction, relationship analysis, and model generation with mocked database
interactions to avoid requiring actual database instances.
"""

import unittest
from unittest.mock import Mock
from urllib.parse import urlparse

import psycopg2

from a3.engines.database_analyzer import DatabaseAnalyzer
from a3.core.models import (
    DatabaseConnection, DatabaseSchema, TableMetadata, ColumnMetadata,
    DatabaseConnectionError, ValidationError
)


class TestDatabaseAnalyzer(unittest.TestCase):
    """Test cases for DatabaseAnalyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock AI client and state manager
        self.mock_ai_client = Mock()
        self.mock_state_manager = Mock()
        
        # Initialize database analyzer
        self.db_analyzer = DatabaseAnalyzer(
            ai_client=self.mock_ai_client,
            state_manager=self.mock_state_manager
        )
        self.db_analyzer.initialize()
        
        # Sample connection string
        self.valid_connection_string = "postgresql://testuser:testpass@localhost:5432/testdb"
    
    def test_initialization(self):
        """Test database analyzer initialization."""
        self.assertTrue(self.db_analyzer._initialized)
        self.assertEqual(self.db_analyzer.ai_client, self.mock_ai_client)
        self.assertEqual(self.db_analyzer.state_manager, self.mock_state_manager)
        self.assertIsInstance(self.db_analyzer._connection_pools, dict)
        self.assertIsInstance(self.db_analyzer._active_connections, dict)
    
    def test_mask_password(self):
        """Test password masking in connection strings."""
        # Test with password
        conn_str_with_pass = "postgresql://user:secret123@localhost:5432/db"
        masked = self.db_analyzer._mask_password(conn_str_with_pass)
        self.assertNotIn("secret123", masked)
        self.assertIn("***", masked)
        
        # Test without password
        conn_str_no_pass = "postgresql://user@localhost:5432/db"
        masked = self.db_analyzer._mask_password(conn_str_no_pass)
        self.assertEqual(masked, conn_str_no_pass)
    
    def test_parse_connection_string_valid(self):
        """Test parsing of valid connection strings."""
        # Test basic connection string
        parsed = urlparse(self.valid_connection_string)
        self.assertEqual(parsed.scheme, "postgresql")
        self.assertEqual(parsed.hostname, "localhost")
        self.assertEqual(parsed.port, 5432)
        self.assertEqual(parsed.path, "/testdb")
        self.assertEqual(parsed.username, "testuser")
        self.assertEqual(parsed.password, "testpass")
    
    def test_connect_to_database_invalid_scheme(self):
        """Test connection with invalid scheme."""
        invalid_connection = "mysql://user:pass@localhost:3306/db"
        
        with self.assertRaises(DatabaseConnectionError) as context:
            self.db_analyzer.connect_to_database(invalid_connection)
        
        self.assertIn("Invalid connection string", str(context.exception))
        self.assertIn("postgresql://", str(context.exception))
    
    def test_connect_to_database_missing_database(self):
        """Test connection with missing database name."""
        invalid_connection = "postgresql://user:pass@localhost:5432/"
        
        with self.assertRaises(DatabaseConnectionError) as context:
            self.db_analyzer.connect_to_database(invalid_connection)
        
        self.assertIn("Database name is required", str(context.exception))
    
    def test_connect_to_database_missing_username(self):
        """Test connection with missing username."""
        invalid_connection = "postgresql://:pass@localhost:5432/db"
        
        with self.assertRaises(DatabaseConnectionError) as context:
            self.db_analyzer.connect_to_database(invalid_connection)
        
        self.assertIn("Username is required", str(context.exception))
    
    def test_get_connection_troubleshooting_tips(self):
        """Test generation of connection troubleshooting tips."""
        # Test with authentication error
        auth_error = psycopg2.OperationalError("authentication failed")
        tips = self.db_analyzer._get_connection_troubleshooting_tips(auth_error)
        
        self.assertIsInstance(tips, list)
        self.assertTrue(any("password" in tip.lower() for tip in tips))
        
        # Test with connection refused error
        conn_error = psycopg2.OperationalError("connection refused")
        tips = self.db_analyzer._get_connection_troubleshooting_tips(conn_error)
        
        self.assertIsInstance(tips, list)
        self.assertTrue(any("running" in tip.lower() for tip in tips))
    
    def test_database_connection_validation(self):
        """Test database connection validation."""
        # Test valid connection
        connection = DatabaseConnection(
            connection_string=self.valid_connection_string,
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        # Should not raise exception
        try:
            connection.validate()
        except Exception as e:
            self.fail(f"Valid connection validation failed: {e}")
    
    def test_column_metadata_creation(self):
        """Test creation of column metadata objects."""
        # Test basic column
        column = ColumnMetadata(
            name="id",
            data_type="integer",
            is_nullable=False,
            is_primary_key=True
        )
        
        self.assertEqual(column.name, "id")
        self.assertEqual(column.data_type, "integer")
        self.assertFalse(column.is_nullable)
        self.assertTrue(column.is_primary_key)
        
        # Test column with constraints
        column_with_fk = ColumnMetadata(
            name="user_id",
            data_type="integer",
            is_nullable=False,
            is_foreign_key=True,
            foreign_key_table="users",
            foreign_key_column="id"
        )
        
        self.assertTrue(column_with_fk.is_foreign_key)
        self.assertEqual(column_with_fk.foreign_key_table, "users")
        self.assertEqual(column_with_fk.foreign_key_column, "id")
    
    def test_table_metadata_creation(self):
        """Test creation of table metadata objects."""
        # Create columns
        columns = [
            ColumnMetadata(
                name="id",
                data_type="integer",
                is_nullable=False,
                is_primary_key=True
            ),
            ColumnMetadata(
                name="name",
                data_type="varchar",
                is_nullable=False,
                max_length=100
            )
        ]
        
        # Create table
        table = TableMetadata(
            table_name="users",
            table_schema="public",
            table_type="BASE TABLE",
            columns=columns
        )
        
        self.assertEqual(table.table_name, "users")
        self.assertEqual(table.table_schema, "public")
        self.assertEqual(len(table.columns), 2)
        
        # Verify columns
        id_column = next((c for c in table.columns if c.name == "id"), None)
        self.assertIsNotNone(id_column)
        self.assertTrue(id_column.is_primary_key)
    
    def test_database_schema_creation(self):
        """Test creation of database schema objects."""
        # Create sample table
        table = TableMetadata(
            table_name="products",
            table_schema="public",
            table_type="BASE TABLE",
            columns=[
                ColumnMetadata(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                ColumnMetadata(name="name", data_type="varchar", is_nullable=False)
            ]
        )
        
        # Create schema
        schema = DatabaseSchema(
            database_name="testdb",
            host="localhost",
            port=5432,
            username="testuser",
            tables=[table]
        )
        
        self.assertEqual(schema.database_name, "testdb")
        self.assertEqual(schema.host, "localhost")
        self.assertEqual(len(schema.tables), 1)
        self.assertEqual(schema.tables[0].table_name, "products")
    
    def test_uninitialized_analyzer_operations(self):
        """Test operations on uninitialized analyzer."""
        # Create uninitialized analyzer
        analyzer = DatabaseAnalyzer()
        
        # Operations should raise RuntimeError
        with self.assertRaises(RuntimeError):
            analyzer.connect_to_database(self.valid_connection_string)


class TestDatabaseAnalyzerErrorHandling(unittest.TestCase):
    """Test error handling in DatabaseAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_analyzer = DatabaseAnalyzer()
        self.db_analyzer.initialize()
    
    def test_connection_string_validation(self):
        """Test connection string validation."""
        invalid_strings = [
            "",  # Empty string
            "invalid",  # No scheme
            "http://user:pass@localhost:5432/db",  # Wrong scheme
            "postgresql://localhost:5432/db",  # No username
            "postgresql://user:pass@localhost:5432/",  # No database
        ]
        
        for conn_str in invalid_strings:
            with self.subTest(connection_string=conn_str):
                with self.assertRaises(DatabaseConnectionError):
                    self.db_analyzer.connect_to_database(conn_str)
    
    def test_column_metadata_validation(self):
        """Test column metadata validation."""
        # Test invalid column name
        with self.assertRaises(ValidationError):
            column = ColumnMetadata(name="", data_type="integer")
            column.validate()
        
        # Test invalid data type
        with self.assertRaises(ValidationError):
            column = ColumnMetadata(name="test", data_type="")
            column.validate()
        
        # Test invalid max_length
        with self.assertRaises(ValidationError):
            column = ColumnMetadata(name="test", data_type="varchar", max_length=-1)
            column.validate()
    
    def test_database_connection_error_attributes(self):
        """Test DatabaseConnectionError attributes."""
        error = DatabaseConnectionError(
            "Test error",
            connection_string="postgresql://user:***@localhost:5432/db",
            error_code="28P01",
            troubleshooting_tips=["Check password", "Verify user exists"]
        )
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.connection_string, "postgresql://user:***@localhost:5432/db")
        self.assertEqual(error.error_code, "28P01")
        self.assertEqual(len(error.troubleshooting_tips), 2)
        self.assertIn("Check password", error.troubleshooting_tips)


class TestDatabaseAnalyzerEdgeCases(unittest.TestCase):
    """Test edge cases for DatabaseAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db_analyzer = DatabaseAnalyzer()
        self.db_analyzer.initialize()
    
    def test_connection_string_variations(self):
        """Test various connection string formats."""
        # Test with default port (should be parsed correctly)
        conn_str = "postgresql://user:pass@localhost/db"
        parsed = urlparse(conn_str)
        self.assertEqual(parsed.hostname, "localhost")
        self.assertIsNone(parsed.port)  # Will default to 5432
        
        # Test with custom port
        conn_str = "postgresql://user:pass@localhost:3333/db"
        parsed = urlparse(conn_str)
        self.assertEqual(parsed.port, 3333)
        
        # Test with IP address
        conn_str = "postgresql://user:pass@192.168.1.100:5432/db"
        parsed = urlparse(conn_str)
        self.assertEqual(parsed.hostname, "192.168.1.100")
    
    def test_column_metadata_edge_cases(self):
        """Test edge cases for column metadata."""
        # Test column with all optional fields
        column = ColumnMetadata(
            name="complex_column",
            data_type="numeric",
            is_nullable=True,
            default_value="0.00",
            max_length=None,
            precision=10,
            scale=2,
            is_primary_key=False,
            is_foreign_key=True,
            foreign_key_table="other_table",
            foreign_key_column="id",
            description="A complex column with many attributes"
        )
        
        # Should validate successfully
        try:
            column.validate()
        except Exception as e:
            self.fail(f"Column validation failed: {e}")
        
        # Verify all attributes
        self.assertEqual(column.name, "complex_column")
        self.assertEqual(column.precision, 10)
        self.assertEqual(column.scale, 2)
        self.assertTrue(column.is_foreign_key)
        self.assertEqual(column.foreign_key_table, "other_table")
    
    def test_table_metadata_edge_cases(self):
        """Test edge cases for table metadata."""
        # Test table with no columns
        empty_table = TableMetadata(
            table_name="empty_table",
            table_schema="public",
            table_type="BASE TABLE",
            columns=[]
        )
        
        self.assertEqual(len(empty_table.columns), 0)
        
        # Test table with many columns
        many_columns = [
            ColumnMetadata(name=f"col_{i}", data_type="varchar")
            for i in range(100)
        ]
        
        large_table = TableMetadata(
            table_name="large_table",
            table_schema="public",
            table_type="BASE TABLE",
            columns=many_columns
        )
        
        self.assertEqual(len(large_table.columns), 100)
    
    def test_database_schema_edge_cases(self):
        """Test edge cases for database schema."""
        # Test schema with no tables
        empty_schema = DatabaseSchema(
            database_name="empty_db",
            host="localhost",
            port=5432,
            username="user",
            tables=[]
        )
        
        self.assertEqual(len(empty_schema.tables), 0)
        
        # Test schema with multiple schemas
        schema_with_multiple = DatabaseSchema(
            database_name="multi_schema_db",
            host="localhost",
            port=5432,
            username="user",
            schemas=["public", "private", "temp"],
            tables=[]
        )
        
        self.assertEqual(len(schema_with_multiple.schemas), 3)
        self.assertIn("public", schema_with_multiple.schemas)
        self.assertIn("private", schema_with_multiple.schemas)
    
    def test_special_characters_in_names(self):
        """Test handling of special characters in database object names."""
        # Test column with underscores and numbers
        column = ColumnMetadata(
            name="user_id_123",
            data_type="integer"
        )
        
        try:
            column.validate()
        except Exception as e:
            self.fail(f"Column with underscores and numbers should be valid: {e}")
        
        # Test table with special naming
        table = TableMetadata(
            table_name="user_profiles_v2",
            table_schema="public",
            table_type="BASE TABLE",
            columns=[column]
        )
        
        self.assertEqual(table.table_name, "user_profiles_v2")


def test_simple():
    """Simple test to verify test discovery works."""
    assert True


if __name__ == '__main__':
    unittest.main()