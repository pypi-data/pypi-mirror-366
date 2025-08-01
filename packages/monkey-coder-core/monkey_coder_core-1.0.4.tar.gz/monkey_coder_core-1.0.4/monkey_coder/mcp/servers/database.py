"""
Database MCP Server
Provides database operations through MCP protocol
"""

import json
import logging
from typing import Dict, Any
import asyncpg
import aiomysql
import aiosqlite

logger = logging.getLogger(__name__)


class DatabaseMCPServer:
    """
    MCP server for database operations
    Provides tools for querying, schema management, and migrations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database server
        
        Args:
            config: Server configuration including connection details
        """
        self.config = config
        self.connection_string = config.get("connection_string")
        self.db_type = config.get("type", "postgres")
        self.pool = None
        self._connection = None
        
        # Define available tools
        self.tools = {
            "query": {
                "name": "query",
                "description": "Execute a SQL query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL query to execute"
                        },
                        "params": {
                            "type": "array",
                            "description": "Query parameters",
                            "items": {"type": ["string", "number", "boolean", "null"]}
                        },
                        "fetch_all": {
                            "type": "boolean",
                            "description": "Fetch all results",
                            "default": True
                        }
                    },
                    "required": ["sql"]
                }
            },
            "execute": {
                "name": "execute",
                "description": "Execute a SQL statement (INSERT, UPDATE, DELETE)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL statement to execute"
                        },
                        "params": {
                            "type": "array",
                            "description": "Statement parameters",
                            "items": {"type": ["string", "number", "boolean", "null"]}
                        }
                    },
                    "required": ["sql"]
                }
            },
            "get_schema": {
                "name": "get_schema",
                "description": "Get database schema information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Specific table name (optional)"
                        },
                        "schema_name": {
                            "type": "string",
                            "description": "Schema name",
                            "default": "public"
                        }
                    }
                }
            },
            "list_tables": {
                "name": "list_tables",
                "description": "List all tables in database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schema_name": {
                            "type": "string",
                            "description": "Schema name",
                            "default": "public"
                        }
                    }
                }
            },
            "describe_table": {
                "name": "describe_table",
                "description": "Get detailed information about a table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Table name"
                        },
                        "schema_name": {
                            "type": "string",
                            "description": "Schema name",
                            "default": "public"
                        }
                    },
                    "required": ["table_name"]
                }
            },
            "create_table": {
                "name": "create_table",
                "description": "Create a new table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Table name"
                        },
                        "columns": {
                            "type": "array",
                            "description": "Column definitions",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "primary_key": {"type": "boolean"},
                                    "not_null": {"type": "boolean"},
                                    "unique": {"type": "boolean"},
                                    "default": {"type": "string"}
                                },
                                "required": ["name", "type"]
                            }
                        },
                        "if_not_exists": {
                            "type": "boolean",
                            "description": "Use IF NOT EXISTS",
                            "default": True
                        }
                    },
                    "required": ["table_name", "columns"]
                }
            },
            "drop_table": {
                "name": "drop_table",
                "description": "Drop a table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Table name"
                        },
                        "if_exists": {
                            "type": "boolean",
                            "description": "Use IF EXISTS",
                            "default": True
                        },
                        "cascade": {
                            "type": "boolean",
                            "description": "Use CASCADE",
                            "default": False
                        }
                    },
                    "required": ["table_name"]
                }
            },
            "backup": {
                "name": "backup",
                "description": "Create database backup",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["sql", "csv", "json"],
                            "description": "Backup format",
                            "default": "sql"
                        },
                        "tables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific tables to backup"
                        }
                    }
                }
            },
            "migrate": {
                "name": "migrate",
                "description": "Run database migration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "migration_sql": {
                            "type": "string",
                            "description": "Migration SQL script"
                        },
                        "rollback_sql": {
                            "type": "string",
                            "description": "Rollback SQL script"
                        },
                        "version": {
                            "type": "string",
                            "description": "Migration version"
                        }
                    },
                    "required": ["migration_sql", "version"]
                }
            }
        }
        
        # Define available resources
        self.resources = {
            "db://": {
                "uri": "db://",
                "name": "Database",
                "description": "Access database resources",
                "mimeType": "application/json"
            }
        }
        
    async def connect(self):
        """Establish database connection"""
        if self.db_type == "postgres":
            self.pool = await asyncpg.create_pool(self.connection_string)
        elif self.db_type == "mysql":
            # Parse connection string for MySQL
            import urllib.parse
            parsed = urllib.parse.urlparse(self.connection_string)
            self.pool = await aiomysql.create_pool(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                db=parsed.path[1:],  # Remove leading /
                autocommit=True
            )
        elif self.db_type == "sqlite":
            self._connection = await aiosqlite.connect(self.connection_string)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
            
    async def disconnect(self):
        """Close database connection"""
        if self.pool:
            if self.db_type == "postgres":
                await self.pool.close()
            elif self.db_type == "mysql":
                self.pool.close()
                await self.pool.wait_closed()
        elif self._connection:
            await self._connection.close()
            
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
            
        try:
            # Ensure connected
            if not self.pool and not self._connection:
                await self.connect()
                
            if tool_name == "query":
                return await self._query(arguments)
            elif tool_name == "execute":
                return await self._execute(arguments)
            elif tool_name == "get_schema":
                return await self._get_schema(arguments)
            elif tool_name == "list_tables":
                return await self._list_tables(arguments)
            elif tool_name == "describe_table":
                return await self._describe_table(arguments)
            elif tool_name == "create_table":
                return await self._create_table(arguments)
            elif tool_name == "drop_table":
                return await self._drop_table(arguments)
            elif tool_name == "backup":
                return await self._backup(arguments)
            elif tool_name == "migrate":
                return await self._migrate(arguments)
            else:
                return {"error": f"Tool not implemented: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
            
    async def _query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query"""
        sql = args["sql"]
        params = args.get("params", [])
        fetch_all = args.get("fetch_all", True)
        
        try:
            if self.db_type == "postgres":
                async with self.pool.acquire() as conn:
                    if fetch_all:
                        rows = await conn.fetch(sql, *params)
                        results = [dict(row) for row in rows]
                    else:
                        row = await conn.fetchrow(sql, *params)
                        results = dict(row) if row else None
                        
            elif self.db_type == "mysql":
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(sql, params)
                        if fetch_all:
                            results = await cursor.fetchall()
                        else:
                            results = await cursor.fetchone()
                            
            elif self.db_type == "sqlite":
                self._connection.row_factory = aiosqlite.Row
                cursor = await self._connection.execute(sql, params)
                if fetch_all:
                    rows = await cursor.fetchall()
                    results = [dict(row) for row in rows]
                else:
                    row = await cursor.fetchone()
                    results = dict(row) if row else None
                await cursor.close()
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(results, indent=2, default=str)
                }],
                "metadata": {
                    "row_count": len(results) if isinstance(results, list) else 1 if results else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Query failed: {e}"}
            
    async def _execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute statement"""
        sql = args["sql"]
        params = args.get("params", [])
        
        try:
            if self.db_type == "postgres":
                async with self.pool.acquire() as conn:
                    result = await conn.execute(sql, *params)
                    affected = int(result.split()[-1]) if result else 0
                    
            elif self.db_type == "mysql":
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        affected = await cursor.execute(sql, params)
                        
            elif self.db_type == "sqlite":
                cursor = await self._connection.execute(sql, params)
                affected = cursor.rowcount
                await self._connection.commit()
                await cursor.close()
                
            return {
                "content": [{
                    "type": "text",
                    "text": f"Statement executed successfully. Affected rows: {affected}"
                }],
                "metadata": {
                    "affected_rows": affected
                }
            }
            
        except Exception as e:
            return {"error": f"Execution failed: {e}"}
            
    async def _get_schema(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get schema information"""
        table_name = args.get("table_name")
        schema_name = args.get("schema_name", "public")
        
        try:
            if self.db_type == "postgres":
                sql = """
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = $1
                """
                params = [schema_name]
                if table_name:
                    sql += " AND table_name = $2"
                    params.append(table_name)
                sql += " ORDER BY table_name, ordinal_position"
                
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(sql, *params)
                    schema = {}
                    for row in rows:
                        table = row["table_name"]
                        if table not in schema:
                            schema[table] = []
                        schema[table].append({
                            "column": row["column_name"],
                            "type": row["data_type"],
                            "nullable": row["is_nullable"] == "YES",
                            "default": row["column_default"]
                        })
                        
            elif self.db_type == "mysql":
                sql = """
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                """
                if table_name:
                    sql += " AND TABLE_NAME = %s"
                    params = [table_name]
                else:
                    params = []
                sql += " ORDER BY TABLE_NAME, ORDINAL_POSITION"
                
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(sql, params)
                        rows = await cursor.fetchall()
                        schema = {}
                        for row in rows:
                            table = row["TABLE_NAME"]
                            if table not in schema:
                                schema[table] = []
                            schema[table].append({
                                "column": row["COLUMN_NAME"],
                                "type": row["DATA_TYPE"],
                                "nullable": row["IS_NULLABLE"] == "YES",
                                "default": row["COLUMN_DEFAULT"]
                            })
                            
            elif self.db_type == "sqlite":
                if table_name:
                    cursor = await self._connection.execute(f"PRAGMA table_info({table_name})")
                    rows = await cursor.fetchall()
                    schema = {table_name: []}
                    for row in rows:
                        schema[table_name].append({
                            "column": row[1],
                            "type": row[2],
                            "nullable": row[3] == 0,
                            "default": row[4]
                        })
                    await cursor.close()
                else:
                    # Get all tables
                    cursor = await self._connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                    tables = await cursor.fetchall()
                    await cursor.close()
                    
                    schema = {}
                    for table in tables:
                        table_name = table[0]
                        cursor = await self._connection.execute(f"PRAGMA table_info({table_name})")
                        rows = await cursor.fetchall()
                        schema[table_name] = []
                        for row in rows:
                            schema[table_name].append({
                                "column": row[1],
                                "type": row[2],
                                "nullable": row[3] == 0,
                                "default": row[4]
                            })
                        await cursor.close()
                        
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(schema, indent=2)
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to get schema: {e}"}
            
    async def _list_tables(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List tables"""
        schema_name = args.get("schema_name", "public")
        
        try:
            if self.db_type == "postgres":
                sql = """
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = $1
                ORDER BY table_name
                """
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(sql, schema_name)
                    tables = [{"name": row["table_name"], "type": row["table_type"]} for row in rows]
                    
            elif self.db_type == "mysql":
                sql = "SHOW TABLES"
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(sql)
                        rows = await cursor.fetchall()
                        tables = [{"name": row[0], "type": "TABLE"} for row in rows]
                        
            elif self.db_type == "sqlite":
                cursor = await self._connection.execute(
                    "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')"
                )
                rows = await cursor.fetchall()
                tables = [{"name": row[0], "type": row[1].upper()} for row in rows]
                await cursor.close()
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(tables, indent=2)
                }],
                "metadata": {
                    "count": len(tables)
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to list tables: {e}"}
            
    async def _describe_table(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Describe table in detail"""
        table_name = args["table_name"]
        
        # Get schema first
        schema_result = await self._get_schema({"table_name": table_name})
        if "error" in schema_result:
            return schema_result
            
        # Get additional info like indexes, constraints
        try:
            info = {
                "columns": json.loads(schema_result["content"][0]["text"])[table_name],
                "indexes": [],
                "constraints": []
            }
            
            if self.db_type == "postgres":
                # Get indexes
                sql = """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = $1
                """
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(sql, table_name)
                    info["indexes"] = [
                        {"name": row["indexname"], "definition": row["indexdef"]}
                        for row in rows
                    ]
                    
                # Get constraints
                sql = """
                SELECT conname, contype
                FROM pg_constraint
                WHERE conrelid = $1::regclass
                """
                rows = await conn.fetch(sql, table_name)
                info["constraints"] = [
                    {"name": row["conname"], "type": row["contype"]}
                    for row in rows
                ]
                
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(info, indent=2)
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to describe table: {e}"}
            
    async def _create_table(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create table"""
        table_name = args["table_name"]
        columns = args["columns"]
        if_not_exists = args.get("if_not_exists", True)
        
        try:
            # Build CREATE TABLE statement
            sql_parts = ["CREATE TABLE"]
            if if_not_exists:
                sql_parts.append("IF NOT EXISTS")
            sql_parts.append(f"{table_name} (")
            
            col_defs = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get("primary_key"):
                    col_def += " PRIMARY KEY"
                if col.get("not_null"):
                    col_def += " NOT NULL"
                if col.get("unique"):
                    col_def += " UNIQUE"
                if "default" in col:
                    col_def += f" DEFAULT {col['default']}"
                col_defs.append(col_def)
                
            sql_parts.append(", ".join(col_defs))
            sql_parts.append(")")
            
            sql = " ".join(sql_parts)
            
            # Execute
            result = await self._execute({"sql": sql})
            if "error" in result:
                return result
                
            return {
                "content": [{
                    "type": "text",
                    "text": f"Table '{table_name}' created successfully"
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to create table: {e}"}
            
    async def _drop_table(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Drop table"""
        table_name = args["table_name"]
        if_exists = args.get("if_exists", True)
        cascade = args.get("cascade", False)
        
        try:
            sql_parts = ["DROP TABLE"]
            if if_exists:
                sql_parts.append("IF EXISTS")
            sql_parts.append(table_name)
            if cascade:
                sql_parts.append("CASCADE")
                
            sql = " ".join(sql_parts)
            
            result = await self._execute({"sql": sql})
            if "error" in result:
                return result
                
            return {
                "content": [{
                    "type": "text",
                    "text": f"Table '{table_name}' dropped successfully"
                }]
            }
            
        except Exception as e:
            return {"error": f"Failed to drop table: {e}"}
            
    async def _backup(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup (simplified)"""
        format_type = args.get("format", "sql")
        tables_to_backup = args.get("tables")
        
        # This is a simplified backup - real implementation would be more complex
        return {
            "content": [{
                "type": "text",
                "text": f"Backup functionality would export data in {format_type} format for {len(tables_to_backup) if tables_to_backup else 'all'} tables"
            }],
            "metadata": {
                "note": "Full backup implementation requires additional setup",
                "tables": tables_to_backup or []
            }
        }
        
    async def _migrate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run migration"""
        migration_sql = args["migration_sql"]
        version = args["version"]
        rollback_sql = args.get("rollback_sql")  # Reserved for future rollback functionality
        
        try:
            # Create migrations table if not exists
            create_migrations_table = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            await self._execute({"sql": create_migrations_table})
            
            # Check if migration already applied
            check_sql = "SELECT 1 FROM schema_migrations WHERE version = $1"
            if self.db_type == "mysql":
                check_sql = check_sql.replace("$1", "%s")
            elif self.db_type == "sqlite":
                check_sql = check_sql.replace("$1", "?")
                
            result = await self._query({
                "sql": check_sql,
                "params": [version],
                "fetch_all": False
            })
            
            if result["metadata"]["row_count"] > 0:
                return {"error": f"Migration '{version}' already applied"}
                
            # Run migration
            for statement in migration_sql.split(";"):
                statement = statement.strip()
                if statement:
                    await self._execute({"sql": statement})
                    
            # Record migration
            record_sql = "INSERT INTO schema_migrations (version) VALUES ($1)"
            if self.db_type == "mysql":
                record_sql = record_sql.replace("$1", "%s")
            elif self.db_type == "sqlite":
                record_sql = record_sql.replace("$1", "?")
                
            await self._execute({
                "sql": record_sql,
                "params": [version]
            })
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Migration '{version}' applied successfully"
                }]
            }
            
        except Exception as e:
            return {"error": f"Migration failed: {e}"}
            
    async def handle_resource_request(self, uri: str) -> Dict[str, Any]:
        """
        Handle resource request
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if not uri.startswith("db://"):
            return {"error": f"Invalid URI scheme: {uri}"}
            
        # Parse URI: db://table_name
        table_name = uri[5:]  # Remove db:// prefix
        
        if table_name:
            # Get table data
            return await self._query({
                "sql": f"SELECT * FROM {table_name} LIMIT 100",
                "fetch_all": True
            })
        else:
            # List tables
            return await self._list_tables({})
