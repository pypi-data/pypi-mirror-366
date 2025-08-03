"""
Database Analyzer Engine for AI Project Builder.

This module provides PostgreSQL database analysis capabilities including
schema extraction, relationship analysis, and model generation.
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
from contextlib import contextmanager
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from .base import BaseDatabaseAnalyzer
from ..core.models import (
    DatabaseConnection, DatabaseSchema, TableMetadata, ColumnMetadata,
    IndexMetadata, ConstraintMetadata, Relationship, DatabaseModel,
    DatabaseAnalysisResult, DatabaseConnectionError, ValidationError
)
from ..core.interfaces import AIClientInterface, StateManagerInterface


logger = logging.getLogger(__name__)


class DatabaseAnalyzer(BaseDatabaseAnalyzer):
    """
    PostgreSQL database analyzer for schema extraction and model generation.
    
    This engine connects to PostgreSQL databases, analyzes their schema,
    extracts table structures, relationships, and generates corresponding
    Python model classes.
    """
    
    def __init__(self, ai_client: Optional[AIClientInterface] = None,
                 state_manager: Optional[StateManagerInterface] = None):
        """
        Initialize the database analyzer.
        
        Args:
            ai_client: Client for AI service interactions
            state_manager: Manager for project state persistence
        """
        super().__init__(ai_client, state_manager)
        self._connection_pools: Dict[str, ThreadedConnectionPool] = {}
        self._active_connections: Dict[str, DatabaseConnection] = {}
    
    def connect_to_database(self, connection_string: str, **kwargs) -> DatabaseConnection:
        """
        Connect to a PostgreSQL database with secure connection handling.
        
        Args:
            connection_string: PostgreSQL connection string
            **kwargs: Additional connection parameters
                - connection_timeout: Connection timeout in seconds (default: 30)
                - pool_size: Connection pool size (default: 5)
                - max_overflow: Maximum pool overflow (default: 10)
                - ssl_mode: SSL mode (default: 'prefer')
        
        Returns:
            DatabaseConnection: Connection object with metadata
            
        Raises:
            DatabaseConnectionError: If connection fails
        """
        self._ensure_initialized()
        
        try:
            # Parse connection string
            parsed = urlparse(connection_string)
            
            if not parsed.scheme or parsed.scheme != 'postgresql':
                raise DatabaseConnectionError(
                    "Invalid connection string: must use postgresql:// scheme",
                    connection_string=self._mask_password(connection_string),
                    troubleshooting_tips=[
                        "Use format: postgresql://username:password@host:port/database",
                        "Ensure the connection string starts with 'postgresql://'",
                        "Check that all required components are present"
                    ]
                )
            
            # Extract connection parameters
            host = parsed.hostname or 'localhost'
            port = parsed.port or 5432
            database = parsed.path.lstrip('/') if parsed.path else ''
            username = parsed.username or ''
            password = parsed.password or ''
            
            if not database:
                raise DatabaseConnectionError(
                    "Database name is required in connection string",
                    connection_string=self._mask_password(connection_string),
                    troubleshooting_tips=[
                        "Include database name in connection string",
                        "Format: postgresql://username:password@host:port/database_name"
                    ]
                )
            
            if not username:
                raise DatabaseConnectionError(
                    "Username is required in connection string",
                    connection_string=self._mask_password(connection_string),
                    troubleshooting_tips=[
                        "Include username in connection string",
                        "Format: postgresql://username:password@host:port/database"
                    ]
                )
            
            # Create connection object
            connection = DatabaseConnection(
                connection_string=connection_string,
                host=host,
                port=port,
                database=database,
                username=username,
                password=password,
                connection_timeout=kwargs.get('connection_timeout', 30),
                connection_pool_size=kwargs.get('pool_size', 5),
                max_overflow=kwargs.get('max_overflow', 10),
                ssl_mode=kwargs.get('ssl_mode', 'prefer')
            )
            
            connection.validate()
            
            # Test connection
            self._test_connection(connection)
            
            # Create connection pool with enhanced configuration
            pool_key = f"{host}:{port}:{database}:{username}"
            if pool_key not in self._connection_pools:
                try:
                    self._connection_pools[pool_key] = ThreadedConnectionPool(
                        minconn=1,
                        maxconn=connection.connection_pool_size,
                        host=host,
                        port=port,
                        database=database,
                        user=username,
                        password=password,
                        connect_timeout=connection.connection_timeout,
                        sslmode=connection.ssl_mode,
                        # Additional pool configuration
                        application_name='A3_DatabaseAnalyzer',
                        keepalives_idle=600,  # 10 minutes
                        keepalives_interval=30,  # 30 seconds
                        keepalives_count=3
                    )
                    
                    # Test the pool by getting and returning a connection
                    test_conn = self._connection_pools[pool_key].getconn()
                    self._connection_pools[pool_key].putconn(test_conn)
                    
                    logger.info(f"Created connection pool with {connection.connection_pool_size} max connections")
                    
                except psycopg2.Error as e:
                    # Clean up failed pool
                    if pool_key in self._connection_pools:
                        try:
                            self._connection_pools[pool_key].closeall()
                        except:
                            pass
                        del self._connection_pools[pool_key]
                    raise e
            
            connection.is_connected = True
            self._active_connections[pool_key] = connection
            
            logger.info(f"Successfully connected to database: {host}:{port}/{database}")
            return connection
            
        except psycopg2.Error as e:
            error_msg = f"PostgreSQL connection error: {str(e)}"
            troubleshooting_tips = self._get_connection_troubleshooting_tips(e)
            
            raise DatabaseConnectionError(
                error_msg,
                connection_string=self._mask_password(connection_string),
                error_code=e.pgcode if hasattr(e, 'pgcode') else None,
                troubleshooting_tips=troubleshooting_tips
            )
        except Exception as e:
            raise DatabaseConnectionError(
                f"Unexpected error connecting to database: {str(e)}",
                connection_string=self._mask_password(connection_string),
                troubleshooting_tips=[
                    "Check that PostgreSQL is running",
                    "Verify network connectivity to database host",
                    "Ensure connection string format is correct"
                ]
            )
    
    def analyze_database_schema(self, connection: DatabaseConnection, **kwargs) -> DatabaseSchema:
        """
        Analyze PostgreSQL database schema and extract metadata.
        
        Args:
            connection: Active database connection
            **kwargs: Additional analysis parameters
                - schemas: List of schemas to analyze (default: ['public'])
                - include_system_tables: Include system tables (default: False)
                - analyze_relationships: Analyze foreign key relationships (default: True)
        
        Returns:
            DatabaseSchema: Complete schema information
            
        Raises:
            DatabaseConnectionError: If database operations fail
        """
        self._ensure_initialized()
        
        if not connection.is_connected:
            raise DatabaseConnectionError("Database connection is not active")
        
        start_time = time.time()
        schemas_to_analyze = kwargs.get('schemas', ['public'])
        include_system = kwargs.get('include_system_tables', False)
        analyze_relationships = kwargs.get('analyze_relationships', True)
        
        try:
            with self.get_database_connection(connection) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get database version
                    cursor.execute("SELECT version()")
                    version_info = cursor.fetchone()['version']
                    
                    # Initialize schema object
                    schema = DatabaseSchema(
                        database_name=connection.database,
                        host=connection.host,
                        port=connection.port,
                        username=connection.username,
                        schemas=schemas_to_analyze,
                        version=version_info
                    )
                    
                    # Analyze each schema
                    for schema_name in schemas_to_analyze:
                        tables = self._extract_tables_metadata(cursor, schema_name, include_system)
                        schema.tables.extend(tables)
                    
                    # Analyze relationships if requested
                    if analyze_relationships:
                        relationships = self._analyze_relationships(cursor, schema.tables)
                        schema.relationships.extend(relationships)
                    
                    schema.validate()
                    
                    analysis_time = time.time() - start_time
                    logger.info(f"Database schema analysis completed in {analysis_time:.2f}s")
                    logger.info(f"Found {len(schema.tables)} tables and {len(schema.relationships)} relationships")
                    
                    return schema
                
        except psycopg2.Error as e:
            error_msg = f"Database analysis error: {str(e)}"
            raise DatabaseConnectionError(
                error_msg,
                error_code=e.pgcode if hasattr(e, 'pgcode') else None,
                troubleshooting_tips=[
                    "Ensure user has SELECT permissions on system tables",
                    "Check that specified schemas exist",
                    "Verify database connection is still active"
                ]
            )
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error during schema analysis: {str(e)}")
    
    def generate_database_models(self, schema: DatabaseSchema, **kwargs) -> List[DatabaseModel]:
        """
        Generate Python model classes based on database schema.
        
        Args:
            schema: Database schema information
            **kwargs: Model generation parameters
                - output_dir: Directory for generated models (default: 'models')
                - base_class: Base class for models (default: None)
                - include_relationships: Include relationship methods (default: True)
                - naming_convention: Naming convention ('snake_case' or 'PascalCase')
                - generate_queries: Generate query function templates (default: True)
        
        Returns:
            List[DatabaseModel]: Generated model information
        """
        self._ensure_initialized()
        
        output_dir = kwargs.get('output_dir', 'models')
        base_class = kwargs.get('base_class')
        include_relationships = kwargs.get('include_relationships', True)
        naming_convention = kwargs.get('naming_convention', 'PascalCase')
        generate_queries = kwargs.get('generate_queries', True)
        
        models = []
        
        for table in schema.tables:
            try:
                model = self._generate_table_model(
                    table, schema, output_dir, base_class, 
                    include_relationships, naming_convention
                )
                models.append(model)
                
            except Exception as e:
                logger.error(f"Error generating model for table {table.name}: {str(e)}")
                continue
        
        # Generate query functions if requested
        if generate_queries:
            self._generate_query_functions(schema, models, output_dir)
        
        logger.info(f"Generated {len(models)} database models")
        return models
    
    def generate_database_documentation(self, schema: DatabaseSchema, **kwargs) -> str:
        """
        Generate comprehensive database structure documentation.
        
        Args:
            schema: Database schema information
            **kwargs: Documentation parameters
                - format: Documentation format ('markdown' or 'rst', default: 'markdown')
                - include_relationships: Include relationship diagrams (default: True)
                - include_indexes: Include index information (default: True)
                - include_constraints: Include constraint information (default: True)
        
        Returns:
            str: Generated documentation
        """
        self._ensure_initialized()
        
        doc_format = kwargs.get('format', 'markdown')
        include_relationships = kwargs.get('include_relationships', True)
        include_indexes = kwargs.get('include_indexes', True)
        include_constraints = kwargs.get('include_constraints', True)
        
        if doc_format == 'markdown':
            return self._generate_markdown_documentation(
                schema, include_relationships, include_indexes, include_constraints
            )
        elif doc_format == 'rst':
            return self._generate_rst_documentation(
                schema, include_relationships, include_indexes, include_constraints
            )
        else:
            raise ValueError(f"Unsupported documentation format: {doc_format}")
    
    def _generate_query_functions(self, schema: DatabaseSchema, models: List[DatabaseModel], output_dir: str) -> None:
        """Generate query function templates for common database operations."""
        
        query_functions = []
        
        # Generate basic CRUD operations for each table
        for model in models:
            table = schema.get_table(model.table_name)
            if not table:
                continue
            
            # Generate SELECT queries
            query_functions.extend(self._generate_select_queries(table, model))
            
            # Generate INSERT queries
            query_functions.append(self._generate_insert_query(table, model))
            
            # Generate UPDATE queries
            query_functions.append(self._generate_update_query(table, model))
            
            # Generate DELETE queries
            query_functions.append(self._generate_delete_query(table, model))
        
        # Generate relationship queries
        for relationship in schema.relationships:
            query_functions.append(self._generate_relationship_query(relationship, schema))
        
        # Write query functions to file
        query_file_content = self._generate_query_file_content(query_functions)
        query_file_path = f"{output_dir}/queries.py"
        
        # In a real implementation, this would write to file
        logger.info(f"Generated {len(query_functions)} query functions in {query_file_path}")
    
    def _generate_select_queries(self, table: TableMetadata, model: DatabaseModel) -> List[Dict[str, str]]:
        """Generate SELECT query templates for a table."""
        queries = []
        
        # Basic select all
        queries.append({
            'name': f'get_all_{table.name}',
            'description': f'Get all records from {table.name} table',
            'query': f'SELECT * FROM {table.schema}.{table.name}',
            'parameters': [],
            'return_type': f'List[{model.class_name}]'
        })
        
        # Select by primary key
        pk_columns = table.get_primary_key_columns()
        if pk_columns:
            pk_params = ', '.join([f'{col}: {self._get_python_type_for_column(table.get_column(col))}' for col in pk_columns])
            pk_where = ' AND '.join([f'{col} = %s' for col in pk_columns])
            
            queries.append({
                'name': f'get_{table.name}_by_id',
                'description': f'Get {table.name} record by primary key',
                'query': f'SELECT * FROM {table.schema}.{table.name} WHERE {pk_where}',
                'parameters': pk_params,
                'return_type': f'Optional[{model.class_name}]'
            })
        
        # Select by foreign keys
        for column in table.columns:
            if column.is_foreign_key:
                queries.append({
                    'name': f'get_{table.name}_by_{column.name}',
                    'description': f'Get {table.name} records by {column.name}',
                    'query': f'SELECT * FROM {table.schema}.{table.name} WHERE {column.name} = %s',
                    'parameters': f'{column.name}: {self._get_python_type_for_column(column)}',
                    'return_type': f'List[{model.class_name}]'
                })
        
        return queries
    
    def _generate_insert_query(self, table: TableMetadata, model: DatabaseModel) -> Dict[str, str]:
        """Generate INSERT query template for a table."""
        non_pk_columns = [col for col in table.columns if not col.is_primary_key]
        column_names = ', '.join([col.name for col in non_pk_columns])
        placeholders = ', '.join(['%s'] * len(non_pk_columns))
        
        return {
            'name': f'insert_{table.name}',
            'description': f'Insert new record into {table.name} table',
            'query': f'INSERT INTO {table.schema}.{table.name} ({column_names}) VALUES ({placeholders}) RETURNING *',
            'parameters': f'data: {model.class_name}',
            'return_type': f'{model.class_name}'
        }
    
    def _generate_update_query(self, table: TableMetadata, model: DatabaseModel) -> Dict[str, str]:
        """Generate UPDATE query template for a table."""
        pk_columns = table.get_primary_key_columns()
        non_pk_columns = [col for col in table.columns if not col.is_primary_key]
        
        set_clause = ', '.join([f'{col.name} = %s' for col in non_pk_columns])
        where_clause = ' AND '.join([f'{col} = %s' for col in pk_columns])
        
        return {
            'name': f'update_{table.name}',
            'description': f'Update record in {table.name} table',
            'query': f'UPDATE {table.schema}.{table.name} SET {set_clause} WHERE {where_clause} RETURNING *',
            'parameters': f'data: {model.class_name}',
            'return_type': f'{model.class_name}'
        }
    
    def _generate_delete_query(self, table: TableMetadata, model: DatabaseModel) -> Dict[str, str]:
        """Generate DELETE query template for a table."""
        pk_columns = table.get_primary_key_columns()
        where_clause = ' AND '.join([f'{col} = %s' for col in pk_columns])
        pk_params = ', '.join([f'{col}: {self._get_python_type_for_column(table.get_column(col))}' for col in pk_columns])
        
        return {
            'name': f'delete_{table.name}',
            'description': f'Delete record from {table.name} table',
            'query': f'DELETE FROM {table.schema}.{table.name} WHERE {where_clause}',
            'parameters': pk_params,
            'return_type': 'bool'
        }
    
    def _generate_relationship_query(self, relationship: Relationship, schema: DatabaseSchema) -> Dict[str, str]:
        """Generate query template for relationship operations."""
        from_table = schema.get_table(relationship.from_table)
        to_table = schema.get_table(relationship.to_table)
        
        if not from_table or not to_table:
            return {}
        
        join_conditions = []
        for from_col, to_col in zip(relationship.from_columns, relationship.to_columns):
            join_conditions.append(f'{from_table.name}.{from_col} = {to_table.name}.{to_col}')
        
        join_clause = ' AND '.join(join_conditions)
        
        return {
            'name': f'get_{from_table.name}_with_{to_table.name}',
            'description': f'Get {from_table.name} records with related {to_table.name} data',
            'query': f'''
                SELECT {from_table.name}.*, {to_table.name}.*
                FROM {from_table.schema}.{from_table.name}
                JOIN {to_table.schema}.{to_table.name} ON {join_clause}
            '''.strip(),
            'parameters': '',
            'return_type': f'List[Tuple[{self._to_pascal_case(from_table.name)}, {self._to_pascal_case(to_table.name)}]]'
        }
    
    def _generate_query_file_content(self, query_functions: List[Dict[str, str]]) -> str:
        """Generate the content for the queries.py file."""
        lines = [
            '"""',
            'Database query functions generated from schema analysis.',
            '',
            'This module contains template functions for common database operations.',
            'These functions need to be implemented with actual database connection logic.',
            '"""',
            '',
            'from typing import List, Optional, Tuple',
            'from .models import *',
            '',
        ]
        
        for query_func in query_functions:
            if not query_func:  # Skip empty queries
                continue
                
            lines.extend([
                f'def {query_func["name"]}(connection, {query_func["parameters"]}) -> {query_func["return_type"]}:',
                f'    """',
                f'    {query_func["description"]}',
                f'    ',
                f'    Query: {query_func["query"]}',
                f'    """',
                f'    # TODO: Implement with actual database connection',
                f'    pass',
                '',
                ''
            ])
        
        return '\n'.join(lines)
    
    def _get_python_type_for_column(self, column: Optional[ColumnMetadata]) -> str:
        """Get Python type for a database column."""
        if not column:
            return 'Any'
        
        python_type = self._map_postgres_type_to_python(column.data_type)
        
        if column.is_nullable:
            return f'Optional[{python_type}]'
        
        return python_type
    
    def _test_connection(self, connection: DatabaseConnection) -> None:
        """Test database connection."""
        try:
            conn = psycopg2.connect(
                host=connection.host,
                port=connection.port,
                database=connection.database,
                user=connection.username,
                password=connection.password,
                connect_timeout=connection.connection_timeout,
                sslmode=connection.ssl_mode
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            conn.close()
            
        except psycopg2.Error as e:
            raise DatabaseConnectionError(
                f"Connection test failed: {str(e)}",
                error_code=e.pgcode if hasattr(e, 'pgcode') else None
            )
    
    def _extract_tables_metadata(self, cursor, schema_name: str, include_system: bool) -> List[TableMetadata]:
        """Extract metadata for all tables in a schema."""
        tables = []
        
        # Query to get all tables in schema
        table_query = """
        SELECT 
            t.table_name,
            t.table_type,
            obj_description(c.oid) as table_comment,
            pg_size_pretty(pg_total_relation_size(c.oid)) as table_size,
            pg_stat_get_tuples_inserted(c.oid) + 
            pg_stat_get_tuples_updated(c.oid) + 
            pg_stat_get_tuples_deleted(c.oid) as row_count_estimate
        FROM information_schema.tables t
        LEFT JOIN pg_class c ON c.relname = t.table_name
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE t.table_schema = %s
        AND t.table_type = 'BASE TABLE'
        """
        
        if not include_system:
            table_query += " AND t.table_name NOT LIKE 'pg_%' AND t.table_name NOT LIKE 'sql_%'"
        
        table_query += " ORDER BY t.table_name"
        
        cursor.execute(table_query, (schema_name,))
        table_rows = cursor.fetchall()
        
        for table_row in table_rows:
            table_name = table_row['table_name']
            
            # Extract columns
            columns = self._extract_columns_metadata(cursor, schema_name, table_name)
            
            # Extract indexes
            indexes = self._extract_indexes_metadata(cursor, schema_name, table_name)
            
            # Extract constraints
            constraints = self._extract_constraints_metadata(cursor, schema_name, table_name)
            
            table = TableMetadata(
                name=table_name,
                schema=schema_name,
                columns=columns,
                indexes=indexes,
                constraints=constraints,
                row_count=table_row.get('row_count_estimate'),
                table_size=table_row.get('table_size'),
                description=table_row.get('table_comment')
            )
            
            tables.append(table)
        
        return tables
    
    def _extract_columns_metadata(self, cursor, schema_name: str, table_name: str) -> List[ColumnMetadata]:
        """Extract column metadata for a table."""
        column_query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            col_description(pgc.oid, c.ordinal_position) as column_comment,
            CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
            CASE WHEN fk.column_name IS NOT NULL THEN true ELSE false END as is_foreign_key,
            fk.foreign_table_name,
            fk.foreign_column_name
        FROM information_schema.columns c
        LEFT JOIN pg_class pgc ON pgc.relname = c.table_name
        LEFT JOIN pg_namespace pgn ON pgn.oid = pgc.relnamespace AND pgn.nspname = c.table_schema
        LEFT JOIN (
            SELECT ku.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku ON tc.constraint_name = ku.constraint_name
            WHERE tc.table_schema = %s AND tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
        ) pk ON pk.column_name = c.column_name
        LEFT JOIN (
            SELECT 
                ku.column_name,
                ccu.table_name as foreign_table_name,
                ccu.column_name as foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage ku ON tc.constraint_name = ku.constraint_name
            JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_schema = %s AND tc.table_name = %s AND tc.constraint_type = 'FOREIGN KEY'
        ) fk ON fk.column_name = c.column_name
        WHERE c.table_schema = %s AND c.table_name = %s
        ORDER BY c.ordinal_position
        """
        
        cursor.execute(column_query, (schema_name, table_name, schema_name, table_name, schema_name, table_name))
        column_rows = cursor.fetchall()
        
        columns = []
        for row in column_rows:
            column = ColumnMetadata(
                name=row['column_name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'] == 'YES',
                default_value=row['column_default'],
                max_length=row['character_maximum_length'],
                precision=row['numeric_precision'],
                scale=row['numeric_scale'],
                is_primary_key=row['is_primary_key'],
                is_foreign_key=row['is_foreign_key'],
                foreign_key_table=row.get('foreign_table_name'),
                foreign_key_column=row.get('foreign_column_name'),
                description=row.get('column_comment')
            )
            columns.append(column)
        
        return columns
    
    def _extract_indexes_metadata(self, cursor, schema_name: str, table_name: str) -> List[IndexMetadata]:
        """Extract index metadata for a table."""
        index_query = """
        SELECT 
            i.indexname as index_name,
            i.indexdef,
            ix.indisunique as is_unique,
            ix.indisprimary as is_primary,
            am.amname as index_type,
            array_agg(a.attname ORDER BY a.attnum) as columns
        FROM pg_indexes i
        JOIN pg_class c ON c.relname = i.tablename
        JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = i.schemaname
        JOIN pg_index ix ON ix.indexrelid = (
            SELECT oid FROM pg_class WHERE relname = i.indexname AND relnamespace = n.oid
        )
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(ix.indkey)
        JOIN pg_am am ON am.oid = (
            SELECT relam FROM pg_class WHERE oid = ix.indexrelid
        )
        WHERE i.schemaname = %s AND i.tablename = %s
        GROUP BY i.indexname, i.indexdef, ix.indisunique, ix.indisprimary, am.amname
        ORDER BY i.indexname
        """
        
        cursor.execute(index_query, (schema_name, table_name))
        index_rows = cursor.fetchall()
        
        indexes = []
        for row in index_rows:
            index = IndexMetadata(
                name=row['index_name'],
                table_name=table_name,
                columns=row['columns'] or [],
                is_unique=row['is_unique'],
                is_primary=row['is_primary'],
                index_type=row['index_type'] or 'btree'
            )
            indexes.append(index)
        
        return indexes
    
    def _extract_constraints_metadata(self, cursor, schema_name: str, table_name: str) -> List[ConstraintMetadata]:
        """Extract constraint metadata for a table."""
        constraint_query = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            array_agg(kcu.column_name ORDER BY kcu.ordinal_position) as columns,
            ccu.table_name as referenced_table,
            array_agg(ccu.column_name ORDER BY kcu.ordinal_position) as referenced_columns,
            cc.check_clause
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name 
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage ccu 
            ON tc.constraint_name = ccu.constraint_name 
            AND tc.table_schema = ccu.table_schema
        LEFT JOIN information_schema.check_constraints cc 
            ON tc.constraint_name = cc.constraint_name 
            AND tc.table_schema = cc.constraint_schema
        WHERE tc.table_schema = %s AND tc.table_name = %s
        GROUP BY tc.constraint_name, tc.constraint_type, ccu.table_name, cc.check_clause
        ORDER BY tc.constraint_name
        """
        
        cursor.execute(constraint_query, (schema_name, table_name))
        constraint_rows = cursor.fetchall()
        
        constraints = []
        for row in constraint_rows:
            constraint = ConstraintMetadata(
                name=row['constraint_name'],
                table_name=table_name,
                constraint_type=row['constraint_type'],
                columns=row['columns'] or [],
                referenced_table=row.get('referenced_table'),
                referenced_columns=row.get('referenced_columns'),
                check_clause=row.get('check_clause')
            )
            constraints.append(constraint)
        
        return constraints
    
    def _analyze_relationships(self, cursor, tables: List[TableMetadata]) -> List[Relationship]:
        """Analyze relationships between tables."""
        relationships = []
        
        for table in tables:
            for column in table.columns:
                if column.is_foreign_key and column.foreign_key_table:
                    relationship = Relationship(
                        from_table=table.name,
                        to_table=column.foreign_key_table,
                        from_columns=[column.name],
                        to_columns=[column.foreign_key_column] if column.foreign_key_column else [],
                        relationship_type="FOREIGN_KEY"
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _generate_table_model(self, table: TableMetadata, schema: DatabaseSchema, 
                            output_dir: str, base_class: Optional[str],
                            include_relationships: bool, naming_convention: str) -> DatabaseModel:
        """Generate a Python model class for a database table."""
        
        # Generate class name
        if naming_convention == 'PascalCase':
            class_name = self._to_pascal_case(table.name)
        else:
            class_name = table.name.title().replace('_', '')
        
        # Generate module and file names
        module_name = f"{output_dir}.{table.name}"
        file_path = f"{output_dir}/{table.name}.py"
        
        # Generate field definitions
        fields = []
        imports = ["from typing import Optional", "from datetime import datetime"]
        
        if base_class:
            imports.append(f"from .base import {base_class}")
        
        for column in table.columns:
            field_info = {
                'name': column.name,
                'type': self._map_postgres_type_to_python(column.data_type),
                'nullable': column.is_nullable,
                'primary_key': column.is_primary_key,
                'foreign_key': column.is_foreign_key,
                'default': column.default_value
            }
            fields.append(field_info)
        
        # Generate relationship information
        relationships = []
        if include_relationships:
            table_relationships = schema.get_relationships_for_table(table.name)
            for rel in table_relationships:
                rel_info = {
                    'type': rel.relationship_type,
                    'related_table': rel.to_table if rel.from_table == table.name else rel.from_table,
                    'foreign_key': rel.from_columns[0] if rel.from_columns else None
                }
                relationships.append(rel_info)
        
        # Generate methods
        methods = ['__init__', '__repr__', '__str__']
        if any(col.is_primary_key for col in table.columns):
            methods.append('get_by_id')
        methods.extend(['save', 'delete', 'to_dict', 'from_dict'])
        
        # Generate code
        generated_code = self._generate_model_code(
            class_name, table, fields, relationships, methods, base_class, imports
        )
        
        model = DatabaseModel(
            table_name=table.name,
            class_name=class_name,
            module_name=module_name,
            file_path=file_path,
            fields=fields,
            relationships=relationships,
            methods=methods,
            imports=imports,
            generated_code=generated_code
        )
        
        return model
    
    def _generate_model_code(self, class_name: str, table: TableMetadata,
                           fields: List[Dict[str, Any]], relationships: List[Dict[str, Any]],
                           methods: List[str], base_class: Optional[str],
                           imports: List[str]) -> str:
        """Generate the actual Python code for a model class."""
        
        code_lines = []
        
        # Add imports
        code_lines.extend(imports)
        code_lines.append("")
        
        # Add class definition
        if base_class:
            code_lines.append(f"class {class_name}({base_class}):")
        else:
            code_lines.append(f"class {class_name}:")
        
        # Add comprehensive docstring
        docstring_lines = [
            f'    """',
            f'    Model for {table.name} table.',
            f'    ',
            f'    Table: {table.schema}.{table.name}'
        ]
        
        if table.description:
            docstring_lines.extend([
                f'    Description: {table.description}',
                f'    '
            ])
        
        # Add field documentation
        docstring_lines.append('    Fields:')
        for field in fields:
            field_doc = f"        {field['name']} ({field['type']})"
            if field['primary_key']:
                field_doc += " - Primary Key"
            if field['foreign_key']:
                field_doc += " - Foreign Key"
            if not field['nullable']:
                field_doc += " - Required"
            docstring_lines.append(field_doc)
        
        # Add relationship documentation
        if relationships:
            docstring_lines.extend(['    ', '    Relationships:'])
            for rel in relationships:
                rel_doc = f"        {rel['type']} -> {rel['related_table']}"
                if rel['foreign_key']:
                    rel_doc += f" (via {rel['foreign_key']})"
                docstring_lines.append(rel_doc)
        
        docstring_lines.append('    """')
        code_lines.extend(docstring_lines)
        code_lines.append("")
        
        # Add table name
        code_lines.append(f'    __tablename__ = "{table.name}"')
        code_lines.append("")
        
        # Add field definitions with comments
        for field in fields:
            field_type = field['type']
            if field['nullable'] and not field['primary_key']:
                field_type = f"Optional[{field_type}]"
            
            # Add field comment
            comment_parts = []
            if field['primary_key']:
                comment_parts.append("Primary Key")
            if field['foreign_key']:
                comment_parts.append("Foreign Key")
            if field['default']:
                comment_parts.append(f"Default: {field['default']}")
            
            if comment_parts:
                code_lines.append(f"    # {', '.join(comment_parts)}")
            
            field_line = f"    {field['name']}: {field_type}"
            if field['default'] and not field['primary_key']:
                field_line += f" = {field['default']}"
            elif field['nullable']:
                field_line += " = None"
            
            code_lines.append(field_line)
        
        code_lines.append("")
        
        # Add comprehensive __init__ method
        code_lines.append("    def __init__(self, **kwargs):")
        code_lines.append('        """Initialize model instance with field values."""')
        for field in fields:
            if not field['nullable'] and not field['primary_key'] and not field['default']:
                code_lines.append(f'        if "{field["name"]}" not in kwargs:')
                code_lines.append(f'            raise ValueError("Required field \'{field["name"]}\' not provided")')
        code_lines.append("        ")
        code_lines.append("        for key, value in kwargs.items():")
        code_lines.append("            setattr(self, key, value)")
        code_lines.append("")
        
        # Add __repr__ method
        code_lines.append("    def __repr__(self) -> str:")
        code_lines.append('        """Return string representation of the model."""')
        pk_fields = [f['name'] for f in fields if f['primary_key']]
        if pk_fields:
            pk_repr = ', '.join([f"{field}={{self.{field}}}" for field in pk_fields])
            code_lines.append(f'        return f"{class_name}({pk_repr})"')
        else:
            code_lines.append(f'        return f"{class_name}({{id(self)}})"')
        code_lines.append("")
        
        # Add __str__ method
        code_lines.append("    def __str__(self) -> str:")
        code_lines.append('        """Return human-readable string representation."""')
        code_lines.append("        return self.__repr__()")
        code_lines.append("")
        
        # Add to_dict method
        code_lines.append("    def to_dict(self) -> dict:")
        code_lines.append('        """Convert model instance to dictionary."""')
        code_lines.append("        return {")
        for field in fields:
            code_lines.append(f'            "{field["name"]}": self.{field["name"]},')
        code_lines.append("        }")
        code_lines.append("")
        
        # Add from_dict class method
        code_lines.append("    @classmethod")
        code_lines.append(f"    def from_dict(cls, data: dict) -> '{class_name}':")
        code_lines.append('        """Create model instance from dictionary."""')
        code_lines.append("        return cls(**data)")
        code_lines.append("")
        
        # Add validation method
        code_lines.append("    def validate(self) -> bool:")
        code_lines.append('        """Validate model instance data."""')
        code_lines.append("        try:")
        for field in fields:
            if not field['nullable'] and not field['primary_key']:
                code_lines.append(f'            if self.{field["name"]} is None:')
                code_lines.append(f'                raise ValueError("Required field \'{field["name"]}\' cannot be None")')
        code_lines.append("            return True")
        code_lines.append("        except (ValueError, TypeError) as e:")
        code_lines.append("            return False")
        code_lines.append("")
        
        # Add query helper methods if primary key exists
        pk_fields = [f for f in fields if f['primary_key']]
        if pk_fields:
            code_lines.append("    @classmethod")
            pk_params = ', '.join([f'{f["name"]}: {f["type"]}' for f in pk_fields])
            code_lines.append(f"    def get_by_id(cls, connection, {pk_params}) -> 'Optional[{class_name}]':")
            code_lines.append('        """Get model instance by primary key."""')
            code_lines.append("        # Implementation would require database connection")
            code_lines.append("        # This is a template for actual implementation")
            code_lines.append("        pass")
            code_lines.append("")
        
        # Add save method
        code_lines.append("    def save(self, connection) -> bool:")
        code_lines.append('        """Save model instance to database."""')
        code_lines.append("        # Implementation would require database connection")
        code_lines.append("        # This is a template for actual implementation")
        code_lines.append("        pass")
        code_lines.append("")
        
        # Add delete method
        code_lines.append("    def delete(self, connection) -> bool:")
        code_lines.append('        """Delete model instance from database."""')
        code_lines.append("        # Implementation would require database connection")
        code_lines.append("        # This is a template for actual implementation")
        code_lines.append("        pass")
        code_lines.append("")
        
        # Add relationship methods
        for rel in relationships:
            if rel['type'] == 'FOREIGN_KEY':
                related_class = self._to_pascal_case(rel['related_table'])
                method_name = f"get_{rel['related_table']}"
                code_lines.append(f"    def {method_name}(self, connection) -> 'Optional[{related_class}]':")
                code_lines.append(f'        """Get related {related_class} instance."""')
                code_lines.append("        # Implementation would require database connection")
                code_lines.append("        # This is a template for actual implementation")
                code_lines.append("        pass")
                code_lines.append("")
        
        return "\n".join(code_lines)
    
    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in snake_str.split('_'))
    
    def _map_postgres_type_to_python(self, pg_type: str) -> str:
        """Map PostgreSQL data types to Python types."""
        type_mapping = {
            'integer': 'int',
            'bigint': 'int',
            'smallint': 'int',
            'serial': 'int',
            'bigserial': 'int',
            'real': 'float',
            'double precision': 'float',
            'numeric': 'float',
            'decimal': 'float',
            'character varying': 'str',
            'varchar': 'str',
            'character': 'str',
            'char': 'str',
            'text': 'str',
            'boolean': 'bool',
            'date': 'datetime',
            'timestamp': 'datetime',
            'timestamp with time zone': 'datetime',
            'timestamp without time zone': 'datetime',
            'time': 'datetime',
            'json': 'dict',
            'jsonb': 'dict',
            'uuid': 'str',
            'bytea': 'bytes'
        }
        
        return type_mapping.get(pg_type.lower(), 'str')
    
    def _mask_password(self, connection_string: str) -> str:
        """Mask password in connection string for logging."""
        if ':' in connection_string and '@' in connection_string:
            parts = connection_string.split('@')
            if len(parts) >= 2:
                auth_part = parts[0]
                if ':' in auth_part:
                    auth_parts = auth_part.split(':')
                    if len(auth_parts) >= 3:  # postgresql://user:pass
                        auth_parts[-1] = '***'
                        parts[0] = ':'.join(auth_parts)
                        return '@'.join(parts)
        return connection_string
    
    def _get_connection_troubleshooting_tips(self, error: psycopg2.Error) -> List[str]:
        """Get troubleshooting tips based on the specific error."""
        tips = []
        
        error_str = str(error).lower()
        
        if 'connection refused' in error_str:
            tips.extend([
                "Check that PostgreSQL server is running",
                "Verify the host and port are correct",
                "Check firewall settings"
            ])
        elif 'authentication failed' in error_str:
            tips.extend([
                "Verify username and password are correct",
                "Check PostgreSQL authentication configuration (pg_hba.conf)",
                "Ensure user has login privileges"
            ])
        elif 'database' in error_str and 'does not exist' in error_str:
            tips.extend([
                "Verify the database name is correct",
                "Check that the database exists",
                "Ensure user has access to the database"
            ])
        elif 'timeout' in error_str:
            tips.extend([
                "Check network connectivity",
                "Increase connection timeout",
                "Verify server is not overloaded"
            ])
        else:
            tips.extend([
                "Check PostgreSQL server logs for more details",
                "Verify connection string format",
                "Test connection with psql command line tool"
            ])
        
        return tips
    
    def validate_connection(self, connection: DatabaseConnection) -> DatabaseAnalysisResult:
        """
        Validate database connection and provide troubleshooting guidance.
        
        Args:
            connection: Database connection to validate
            
        Returns:
            DatabaseAnalysisResult: Validation result with troubleshooting info
        """
        self._ensure_initialized()
        
        errors = []
        warnings = []
        
        try:
            # Test basic connection
            self._test_connection(connection)
            
            # Test permissions
            pool_key = f"{connection.host}:{connection.port}:{connection.database}:{connection.username}"
            pool = self._connection_pools.get(pool_key)
            
            if pool:
                conn = pool.getconn()
                try:
                    with conn.cursor() as cursor:
                        # Test schema access
                        cursor.execute("""
                            SELECT schema_name 
                            FROM information_schema.schemata 
                            WHERE schema_name = 'public'
                        """)
                        
                        if not cursor.fetchone():
                            warnings.append("Cannot access 'public' schema")
                        
                        # Test table access
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public'
                        """)
                        
                        table_count = cursor.fetchone()[0]
                        if table_count == 0:
                            warnings.append("No tables found in 'public' schema")
                        
                        # Test system table access
                        try:
                            cursor.execute("SELECT version()")
                            cursor.fetchone()
                        except psycopg2.Error:
                            warnings.append("Limited access to system information")
                        
                finally:
                    pool.putconn(conn)
            
            return DatabaseAnalysisResult(
                success=True,
                errors=errors,
                warnings=warnings
            )
            
        except DatabaseConnectionError as e:
            errors.append(str(e))
            return DatabaseAnalysisResult(
                success=False,
                errors=errors,
                warnings=warnings
            )
        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")
            return DatabaseAnalysisResult(
                success=False,
                errors=errors,
                warnings=warnings
            )
    
    def get_connection_troubleshooting_guide(self, error: Exception) -> Dict[str, Any]:
        """
        Get comprehensive troubleshooting guide for connection issues.
        
        Args:
            error: The connection error that occurred
            
        Returns:
            Dict containing troubleshooting information
        """
        guide = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'common_causes': [],
            'solutions': [],
            'verification_steps': [],
            'additional_resources': []
        }
        
        error_str = str(error).lower()
        
        if 'connection refused' in error_str:
            guide['common_causes'] = [
                'PostgreSQL server is not running',
                'Wrong host or port specified',
                'Firewall blocking connection',
                'PostgreSQL not configured to accept connections'
            ]
            guide['solutions'] = [
                'Start PostgreSQL service: sudo systemctl start postgresql',
                'Check PostgreSQL status: sudo systemctl status postgresql',
                'Verify host and port in connection string',
                'Check postgresql.conf for listen_addresses setting',
                'Review pg_hba.conf for authentication rules'
            ]
            guide['verification_steps'] = [
                'Test with psql: psql -h host -p port -U username -d database',
                'Check if port is open: telnet host port',
                'Verify PostgreSQL is listening: netstat -tlnp | grep :5432'
            ]
        
        elif 'authentication failed' in error_str:
            guide['common_causes'] = [
                'Incorrect username or password',
                'User does not exist',
                'Authentication method mismatch',
                'pg_hba.conf configuration issues'
            ]
            guide['solutions'] = [
                'Verify username and password are correct',
                'Check if user exists: SELECT * FROM pg_user WHERE usename = \'username\'',
                'Review pg_hba.conf authentication methods',
                'Consider using md5 or scram-sha-256 authentication',
                'Reset password if necessary: ALTER USER username PASSWORD \'newpassword\''
            ]
            guide['verification_steps'] = [
                'Test authentication with psql',
                'Check PostgreSQL logs for authentication errors',
                'Verify pg_hba.conf allows connections from your IP'
            ]
        
        elif 'database' in error_str and 'does not exist' in error_str:
            guide['common_causes'] = [
                'Database name is misspelled',
                'Database has not been created',
                'User lacks access to database'
            ]
            guide['solutions'] = [
                'Verify database name spelling',
                'Create database: CREATE DATABASE database_name',
                'Grant access: GRANT ALL PRIVILEGES ON DATABASE database_name TO username',
                'List available databases: \\l in psql'
            ]
            guide['verification_steps'] = [
                'List databases: SELECT datname FROM pg_database',
                'Check user permissions: \\dp in psql',
                'Verify connection to default database first'
            ]
        
        elif 'timeout' in error_str:
            guide['common_causes'] = [
                'Network latency or connectivity issues',
                'Server overloaded or unresponsive',
                'Connection timeout set too low',
                'Firewall or proxy delays'
            ]
            guide['solutions'] = [
                'Increase connection timeout in connection string',
                'Check network connectivity and latency',
                'Monitor server performance and load',
                'Review firewall and proxy configurations',
                'Consider connection pooling for high-load scenarios'
            ]
            guide['verification_steps'] = [
                'Test network connectivity: ping host',
                'Check server load and performance',
                'Try connecting from different network location'
            ]
        
        elif 'ssl' in error_str:
            guide['common_causes'] = [
                'SSL/TLS configuration mismatch',
                'Certificate issues',
                'SSL mode incompatibility'
            ]
            guide['solutions'] = [
                'Try different SSL modes: disable, allow, prefer, require',
                'Check server SSL configuration',
                'Verify SSL certificates',
                'Update connection string with appropriate sslmode'
            ]
            guide['verification_steps'] = [
                'Test with sslmode=disable first',
                'Check PostgreSQL SSL configuration',
                'Verify certificate validity and trust'
            ]
        
        else:
            guide['common_causes'] = [
                'Network connectivity issues',
                'Server configuration problems',
                'Client configuration issues'
            ]
            guide['solutions'] = [
                'Check PostgreSQL server logs',
                'Verify connection string format',
                'Test with psql command line tool',
                'Review PostgreSQL documentation'
            ]
            guide['verification_steps'] = [
                'Test basic connectivity',
                'Check server status and logs',
                'Verify client configuration'
            ]
        
        guide['additional_resources'] = [
            'PostgreSQL Documentation: https://www.postgresql.org/docs/',
            'Connection String Format: postgresql://user:password@host:port/database',
            'Common pg_hba.conf configurations',
            'PostgreSQL troubleshooting guides'
        ]
        
        return guide
    
    def monitor_connection_health(self, connection: DatabaseConnection) -> Dict[str, Any]:
        """
        Monitor the health of a database connection.
        
        Args:
            connection: Database connection to monitor
            
        Returns:
            Dict containing connection health metrics
        """
        health_metrics = {
            'connection_active': False,
            'response_time_ms': None,
            'pool_stats': {},
            'last_error': None,
            'recommendations': []
        }
        
        try:
            pool_key = f"{connection.host}:{connection.port}:{connection.database}:{connection.username}"
            pool = self._connection_pools.get(pool_key)
            
            if not pool:
                health_metrics['last_error'] = 'Connection pool not found'
                health_metrics['recommendations'].append('Reconnect to database')
                return health_metrics
            
            # Test connection response time
            start_time = time.time()
            conn = pool.getconn()
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                
                response_time = (time.time() - start_time) * 1000
                health_metrics['response_time_ms'] = round(response_time, 2)
                health_metrics['connection_active'] = True
                
                # Get pool statistics
                health_metrics['pool_stats'] = {
                    'min_connections': pool.minconn,
                    'max_connections': pool.maxconn,
                    'current_connections': len(pool._pool) + len(pool._used)
                }
                
                # Provide recommendations based on metrics
                if response_time > 1000:  # > 1 second
                    health_metrics['recommendations'].append('High response time detected - check network and server performance')
                
                if len(pool._used) / pool.maxconn > 0.8:  # > 80% pool utilization
                    health_metrics['recommendations'].append('High connection pool utilization - consider increasing pool size')
                
            finally:
                pool.putconn(conn)
                
        except Exception as e:
            health_metrics['last_error'] = str(e)
            health_metrics['recommendations'].append('Connection health check failed - verify connection status')
        
        return health_metrics
    
    def close_connections(self) -> None:
        """Close all active database connections and pools."""
        for pool_key, pool in self._connection_pools.items():
            try:
                pool.closeall()
                logger.info(f"Closed connection pool: {pool_key}")
            except Exception as e:
                logger.error(f"Error closing connection pool {pool_key}: {str(e)}")
        
        self._connection_pools.clear()
        self._active_connections.clear()
    
    def reconnect_database(self, connection: DatabaseConnection) -> DatabaseConnection:
        """
        Reconnect to database with retry logic and error recovery.
        
        Args:
            connection: Database connection to reconnect
            
        Returns:
            DatabaseConnection: Refreshed connection
            
        Raises:
            DatabaseConnectionError: If reconnection fails after retries
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        # Close existing connection if any
        pool_key = f"{connection.host}:{connection.port}:{connection.database}:{connection.username}"
        if pool_key in self._connection_pools:
            try:
                self._connection_pools[pool_key].closeall()
                del self._connection_pools[pool_key]
                del self._active_connections[pool_key]
            except Exception as e:
                logger.warning(f"Error closing existing connection: {str(e)}")
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{max_retries}")
                
                # Wait before retry (except first attempt)
                if attempt > 0:
                    time.sleep(retry_delay * attempt)
                
                # Attempt reconnection
                new_connection = self.connect_to_database(connection.connection_string)
                logger.info("Database reconnection successful")
                return new_connection
                
            except DatabaseConnectionError as e:
                last_error = e
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {str(e)}")
                
                # Provide specific guidance based on error
                if attempt == max_retries - 1:  # Last attempt
                    troubleshooting = self.get_connection_troubleshooting_guide(e)
                    logger.error("All reconnection attempts failed")
                    logger.error(f"Troubleshooting guide: {troubleshooting}")
        
        # All retries failed
        raise DatabaseConnectionError(
            f"Failed to reconnect after {max_retries} attempts. Last error: {str(last_error)}",
            connection_string=self._mask_password(connection.connection_string),
            troubleshooting_tips=[
                "Check network connectivity",
                "Verify PostgreSQL server is running",
                "Review connection parameters",
                "Check server logs for errors"
            ]
        )
    
    @contextmanager
    def get_database_connection(self, connection: DatabaseConnection):
        """
        Context manager for safe database connection handling.
        
        Args:
            connection: Database connection configuration
            
        Yields:
            Database connection object
            
        Raises:
            DatabaseConnectionError: If connection cannot be obtained
        """
        if not connection.is_connected:
            raise DatabaseConnectionError("Database connection is not active")
        
        pool_key = f"{connection.host}:{connection.port}:{connection.database}:{connection.username}"
        pool = self._connection_pools.get(pool_key)
        
        if not pool:
            raise DatabaseConnectionError("Connection pool not found")
        
        conn = None
        try:
            # Get connection from pool with timeout
            conn = pool.getconn()
            if conn is None:
                raise DatabaseConnectionError("Failed to get connection from pool")
            
            # Update last used timestamp
            connection.last_used = datetime.now()
            
            yield conn
            
        except psycopg2.Error as e:
            # Log database error
            logger.error(f"Database operation error: {str(e)}")
            
            # Check if connection is still valid
            if conn and conn.closed == 0:
                try:
                    conn.rollback()
                except:
                    pass
            
            raise DatabaseConnectionError(
                f"Database operation failed: {str(e)}",
                error_code=e.pgcode if hasattr(e, 'pgcode') else None
            )
            
        except Exception as e:
            logger.error(f"Unexpected database error: {str(e)}")
            raise DatabaseConnectionError(f"Unexpected database error: {str(e)}")
            
        finally:
            # Always return connection to pool
            if conn and pool:
                try:
                    pool.putconn(conn)
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {str(e)}")
    
    def execute_with_retry(self, connection: DatabaseConnection, query: str, 
                          params: Optional[Tuple] = None, max_retries: int = 3) -> Any:
        """
        Execute database query with automatic retry on connection failures.
        
        Args:
            connection: Database connection
            query: SQL query to execute
            params: Query parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            Query result
            
        Raises:
            DatabaseConnectionError: If query fails after all retries
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                with self.get_database_connection(connection) as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, params)
                        
                        # Return appropriate result based on query type
                        if query.strip().upper().startswith('SELECT'):
                            return cursor.fetchall()
                        elif query.strip().upper().startswith(('INSERT', 'UPDATE')) and 'RETURNING' in query.upper():
                            return cursor.fetchone()
                        else:
                            return cursor.rowcount
                            
            except DatabaseConnectionError as e:
                last_error = e
                
                # Check if this is a connection issue that might be resolved by retry
                if 'connection' in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Query attempt {attempt + 1} failed, retrying: {str(e)}")
                    
                    # Try to reconnect
                    try:
                        connection = self.reconnect_database(connection)
                    except Exception as reconnect_error:
                        logger.error(f"Reconnection failed: {str(reconnect_error)}")
                        continue
                else:
                    # Not a retryable error or max retries reached
                    raise e
                    
            except Exception as e:
                last_error = e
                logger.error(f"Non-retryable error in query execution: {str(e)}")
                raise DatabaseConnectionError(f"Query execution failed: {str(e)}")
        
        # All retries exhausted
        raise DatabaseConnectionError(
            f"Query failed after {max_retries} attempts. Last error: {str(last_error)}"
        )
    
    def _generate_markdown_documentation(self, schema: DatabaseSchema, 
                                       include_relationships: bool,
                                       include_indexes: bool, 
                                       include_constraints: bool) -> str:
        """Generate comprehensive database documentation in Markdown format."""
        
        lines = [
            f'# Database Schema Documentation',
            '',
            f'**Database:** {schema.database_name}',
            f'**Host:** {schema.host}:{schema.port}',
            f'**Version:** {schema.version}',
            f'**Analyzed:** {schema.analyzed_at.strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            '## Overview',
            '',
            f'This database contains {len(schema.tables)} tables across {len(schema.schemas)} schema(s).',
            f'Total relationships: {len(schema.relationships)}',
            '',
            '## Tables',
            ''
        ]
        
        # Document each table
        for table in sorted(schema.tables, key=lambda t: t.name):
            lines.extend([
                f'### {table.schema}.{table.name}',
                ''
            ])
            
            if table.description:
                lines.extend([
                    f'**Description:** {table.description}',
                    ''
                ])
            
            if table.row_count is not None:
                lines.extend([
                    f'**Estimated Rows:** {table.row_count:,}',
                    ''
                ])
            
            if table.table_size:
                lines.extend([
                    f'**Size:** {table.table_size}',
                    ''
                ])
            
            # Document columns
            lines.extend([
                '#### Columns',
                '',
                '| Column | Type | Nullable | Default | Description |',
                '|--------|------|----------|---------|-------------|'
            ])
            
            for column in table.columns:
                nullable = '✓' if column.is_nullable else '✗'
                default = column.default_value or ''
                description = column.description or ''
                
                # Add special markers
                markers = []
                if column.is_primary_key:
                    markers.append('🔑 PK')
                if column.is_foreign_key:
                    markers.append('🔗 FK')
                
                if markers:
                    description = f"{' '.join(markers)} {description}".strip()
                
                lines.append(f'| {column.name} | {column.data_type} | {nullable} | {default} | {description} |')
            
            lines.append('')
            
            # Document indexes if requested
            if include_indexes and table.indexes:
                lines.extend([
                    '#### Indexes',
                    '',
                    '| Index | Type | Unique | Columns |',
                    '|-------|------|--------|---------|'
                ])
                
                for index in table.indexes:
                    unique = '✓' if index.is_unique else '✗'
                    columns = ', '.join(index.columns)
                    lines.append(f'| {index.name} | {index.index_type} | {unique} | {columns} |')
                
                lines.append('')
            
            # Document constraints if requested
            if include_constraints and table.constraints:
                lines.extend([
                    '#### Constraints',
                    '',
                    '| Constraint | Type | Columns | Details |',
                    '|------------|------|---------|---------|'
                ])
                
                for constraint in table.constraints:
                    columns = ', '.join(constraint.columns)
                    details = ''
                    
                    if constraint.constraint_type == 'FOREIGN KEY' and constraint.referenced_table:
                        ref_cols = ', '.join(constraint.referenced_columns or [])
                        details = f'References {constraint.referenced_table}({ref_cols})'
                    elif constraint.constraint_type == 'CHECK' and constraint.check_clause:
                        details = constraint.check_clause
                    
                    lines.append(f'| {constraint.name} | {constraint.constraint_type} | {columns} | {details} |')
                
                lines.append('')
        
        # Document relationships if requested
        if include_relationships and schema.relationships:
            lines.extend([
                '## Relationships',
                '',
                '| From Table | To Table | Type | Columns |',
                '|------------|----------|------|---------|'
            ])
            
            for rel in sorted(schema.relationships, key=lambda r: (r.from_table, r.to_table)):
                from_cols = ', '.join(rel.from_columns)
                to_cols = ', '.join(rel.to_columns)
                columns = f'{from_cols} → {to_cols}'
                
                lines.append(f'| {rel.from_table} | {rel.to_table} | {rel.relationship_type} | {columns} |')
            
            lines.append('')
        
        # Add schema summary
        lines.extend([
            '## Schema Summary',
            '',
            f'- **Total Tables:** {len(schema.tables)}',
            f'- **Total Columns:** {sum(len(table.columns) for table in schema.tables)}',
            f'- **Total Indexes:** {sum(len(table.indexes) for table in schema.tables)}',
            f'- **Total Constraints:** {sum(len(table.constraints) for table in schema.tables)}',
            f'- **Total Relationships:** {len(schema.relationships)}',
            ''
        ])
        
        return '\n'.join(lines)
    
    def _generate_rst_documentation(self, schema: DatabaseSchema,
                                  include_relationships: bool,
                                  include_indexes: bool,
                                  include_constraints: bool) -> str:
        """Generate comprehensive database documentation in reStructuredText format."""
        
        lines = [
            '=' * 50,
            'Database Schema Documentation',
            '=' * 50,
            '',
            f'**Database:** {schema.database_name}',
            '',
            f'**Host:** {schema.host}:{schema.port}',
            '',
            f'**Version:** {schema.version}',
            '',
            f'**Analyzed:** {schema.analyzed_at.strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            'Overview',
            '-' * 8,
            '',
            f'This database contains {len(schema.tables)} tables across {len(schema.schemas)} schema(s).',
            f'Total relationships: {len(schema.relationships)}',
            '',
            'Tables',
            '-' * 6,
            ''
        ]
        
        # Document each table
        for table in sorted(schema.tables, key=lambda t: t.name):
            table_title = f'{table.schema}.{table.name}'
            lines.extend([
                table_title,
                '^' * len(table_title),
                ''
            ])
            
            if table.description:
                lines.extend([
                    f'**Description:** {table.description}',
                    ''
                ])
            
            # Document columns
            lines.extend([
                'Columns',
                '~' * 7,
                ''
            ])
            
            for column in table.columns:
                lines.extend([
                    f'**{column.name}**',
                    f'  :Type: {column.data_type}',
                    f'  :Nullable: {"Yes" if column.is_nullable else "No"}',
                ])
                
                if column.default_value:
                    lines.append(f'  :Default: {column.default_value}')
                
                if column.is_primary_key:
                    lines.append('  :Primary Key: Yes')
                
                if column.is_foreign_key:
                    lines.append(f'  :Foreign Key: {column.foreign_key_table}.{column.foreign_key_column}')
                
                if column.description:
                    lines.append(f'  :Description: {column.description}')
                
                lines.append('')
        
        return '\n'.join(lines)
    
    def __del__(self):
        """Cleanup connections on object destruction."""
        self.close_connections()