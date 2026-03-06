# DataLine Programming Language Interpreter
# Author: Anastasios Bolkas
# Website: https://anastasios-bolkas.tech
# Version: 1.0
# Description: A lightweight, dependency-free data pipeline language that compiles to Python
# License: MIT

import sys
import re
import json
import sqlite3
import urllib.request
import urllib.parse
import time
import datetime
from urllib.parse import urlparse

# Optional imports with safe loading
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Database availability constants (missing from original)
SQLITE_AVAILABLE = True
MYSQL_AVAILABLE = False
POSTGRESQL_AVAILABLE = False
MONGODB_AVAILABLE = False
REDIS_AVAILABLE = False
CASSANDRA_AVAILABLE = False
ELASTICSEARCH_AVAILABLE = False

# =============================================================================
# CUSTOM EXCEPTION CLASSES
# =============================================================================
# Improved error handling with specific exception types for better debugging

class DataLineError(Exception):
    """Base exception class for DataLine interpreter errors."""
    pass

class SyntaxError(DataLineError):
    """Raised when DataLine syntax is invalid."""
    pass

class CompilationError(DataLineError):
    """Raised when code compilation fails."""
    pass

class RuntimeError(DataLineError):
    """Raised when runtime execution fails."""
    pass

# =============================================================================
# LOGGING SYSTEM
# =============================================================================
# Centralized logging system with configurable levels and persistent history

class LoggingSystem:
    """
    Provides comprehensive logging with multiple levels (ALL, INFO, ERROR, NONE)
    Logs to both console and persistent history.log file for debugging and auditing
    """
    
    def __init__(self):
        self.current_log_level = "ALL"
        self.history_filename = "history.log"
    
    def init(self, filename=None, log_level="ALL"):
        """
        Initialize the logging system with specified log level and optional filename.
        
        Args:
            filename (str, optional): Name of the DataLine file being executed
            log_level (str): Logging level - ALL, INFO, ERROR, or NONE
            
        Global Effects:
            - Sets current_log_level for subsequent log operations
            - Creates/updates history.log with execution timestamp
            - Prints startup message to console (unless in NONE mode)
        """
        self.current_log_level = log_level
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if log_level != "NONE":
            if filename:
                log_entry = f"[{timestamp}] DataLine interpreter started - File: {filename} - Level: {log_level}\n"
            else:
                log_entry = f"[{timestamp}] DataLine interpreter started - Level: {log_level}\n"
            
            # Append to history.log for persistent audit trail
            with open(self.history_filename, "a") as log_file:
                log_file.write(log_entry)
            
            # Console output for immediate user feedback
            if filename:
                print(f"DataLine Interpreter v1.0 - Started at {timestamp} - File: {filename} - Level: {log_level}")
            else:
                print(f"DataLine Interpreter v1.0 - Started at {timestamp} - Level: {log_level}")
        else:
            # Silent mode for production/automated environments
            print(f"DataLine Interpreter v1.0 - Started at {timestamp} - Silent mode")

    def log_info(self, info_msg):
        """
        Log informational messages with timestamp.
        
        Args:
            info_msg (str): Information message to log
            
        Behavior:
            - Logs to history.log with timestamp
            - Prints to console if log_level is ALL or INFO
            - No output in ERROR or NONE modes
        """
        if self.current_log_level in ["ALL", "INFO"]:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] INFO: {info_msg}\n"
            
            # Persistent logging for audit trail
            with open(self.history_filename, "a") as log_file:
                log_file.write(log_entry)
            
            # Real-time console feedback
            print(f"INFO: {info_msg}")

    def log_error(self, error_msg):
        """
        Log error messages with timestamp.
        
        Args:
            error_msg (str): Error message to log
            
        Behavior:
            - Logs to history.log with timestamp
            - Prints to console if log_level is ALL or ERROR
            - No output in INFO or NONE modes
        """
        if self.current_log_level in ["ALL", "ERROR"]:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] ERROR: {error_msg}\n"
            
            # Persistent error logging for debugging
            with open(self.history_filename, "a") as log_file:
                log_file.write(log_entry)
            
            # Immediate error visibility
            print(f"ERROR: {error_msg}")

# =============================================================================
# CODE VISUALIZATION SYSTEM
# =============================================================================
# Generates hierarchical code trees and flow graphs for documentation
# and debugging purposes. Essential for understanding complex data pipelines.

class CodeVisualizer:
    """
    Generates code trees and flow graphs for DataLine programs.
    Provides visualization capabilities for debugging and documentation.
    """
    
    def generate_code_tree(self, content, filename):
        """
        Generate flat code tree structure (legacy implementation).
        
        NOTE: This function is deprecated in favor of generate_hierarchical_code_tree()
        which provides better structure visualization with proper nesting.
        
        Args:
            content (str): Raw DataLine source code
            filename (str): Name of the source file
            
        Output:
            Creates filename-code_tree.md with line-by-line code listing
        """
        lines = content.split('\n')
        tree_lines = ["# Code Tree - " + filename + "\n"]
        
        line_number = 1
        for line in lines:
            if line.strip():
                # Calculate indentation based on leading spaces/tabs
                leading_spaces = len(line) - len(line.lstrip())
                indent_level = leading_spaces // 4  # Assuming 4 spaces per indent
                indent = "    " * indent_level
                tree_lines.append(f"{indent}{line_number:02d}. {line.rstrip()}")
                line_number += 1
            elif line == "":
                # Preserve empty lines for code structure
                tree_lines.append("")
        
        # Generate output filename without extension
        filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
        output_filename = f"{filename_base}-code_tree.md"
        
        with open(output_filename, "w") as f:
            f.write('\n'.join(tree_lines))

    def generate_hierarchical_code_tree(self, content, filename):
        """
        Generate structured, hierarchical code tree with proper block nesting.
        
        This function parses DataLine source code and creates a visual representation
        of the program structure, showing:
        - Hierarchical nesting of control structures (if, foreach)
        - Sequential numbering of operations
        - Proper indentation reflecting code blocks
        - Filtering of syntax tokens ({, }, else) for clarity
        
        Args:
            content (str): Raw DataLine source code
            filename (str): Name of the source file
            
        Output:
            Creates filename-code_tree.md with hierarchical structure visualization
        """
        lines = content.split('\n')
        tree_lines = ["# Hierarchical Code Tree - " + filename + "\n"]
        
        # Parse the code structure with proper block handling
        parsed_structure = []
        i = 0
        line_number = 1
        
        while i < len(lines):
            line = lines[i].rstrip()
            stripped = line.strip()
            
            if not stripped:
                i += 1
                continue
            
            # Calculate indentation level (2 spaces per indent level)
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 2
            
            # Skip syntax tokens but track them for context
            if stripped in ['{', '}']:
                i += 1
                continue
            
            # Parse different constructs with type identification
            node = {
                'line_num': line_number,
                'indent': indent_level,
                'content': stripped,
                'type': 'unknown',
                'children': []
            }
            
            # Identify node type and create display representation
            if stripped.startswith('if '):
                node['type'] = 'if'
                condition = stripped[3:].rstrip('{').strip()
                node['display'] = f"if({condition})"
            elif stripped.startswith('} else if'):
                node['type'] = 'else_if'
                condition = stripped[10:].rstrip('{').strip()
                node['display'] = f"else if({condition})"
            elif stripped.startswith('else if'):
                node['type'] = 'else_if'
                condition = stripped[8:].rstrip('{').strip()
                node['display'] = f"else if({condition})"
            elif stripped.startswith('} else'):
                node['type'] = 'else'
                node['display'] = 'else'
            elif stripped == 'else':
                node['type'] = 'else'
                node['display'] = 'else'
            elif stripped.startswith('foreach'):
                node['type'] = 'foreach'
                foreach_content = stripped.rstrip('{').strip()
                node['display'] = foreach_content
            elif any(stripped.startswith(cmd) for cmd in ['get(', 'print(', 'send(', 'write(']):
                node['type'] = 'command'
                node['display'] = stripped
            elif '=' in stripped and not stripped.startswith(('if', 'foreach', 'print', 'get', 'send')):
                node['type'] = 'assignment'
                node['display'] = stripped
            else:
                node['display'] = stripped
            
            parsed_structure.append(node)
            line_number += 1
            i += 1
        
        # Build hierarchical structure with proper if/else handling
        hierarchy = []
        stack = []  # Stack to track parent nodes at each indent level
        
        for node in parsed_structure:
            # Handle if/else if/else chains with special logic
            if node['type'] in ['else_if', 'else']:
                # Find the most recent if or else_if at the same or higher level
                for i in range(len(stack) - 1, -1, -1):
                    parent = stack[i]
                    if parent['type'] in ['if', 'else_if'] and parent['indent'] <= node['indent']:
                        parent['children'].append(node)
                        break
                else:
                    # If no parent found, add to root
                    hierarchy.append(node)
                # Don't push else_if/else to stack as they can't have nested blocks
                continue
            
            # Find the appropriate parent based on indent level
            while stack and stack[-1]['indent'] >= node['indent']:
                stack.pop()
            
            if stack:
                # Add as child to current parent
                stack[-1]['children'].append(node)
            else:
                # Add to root level
                hierarchy.append(node)
            
            # Push current node to stack if it could have children
            if node['type'] in ['if', 'foreach']:
                stack.append(node)
        
        # Generate hierarchical output with recursive rendering
        def render_node(node, counter, prefix=""):
            result = []
            node_num = next(counter)
            indent_prefix = "    " * node['indent']
            
            # Render the node with sequential numbering
            result.append(f"{indent_prefix}{prefix}{node_num:02d}. {node['display']}")
            
            # Recursively render children
            for child in node['children']:
                result.extend(render_node(child, counter))
            
            return result
        
        # Render all root nodes with sequential numbering
        counter = iter(range(1, 1000))
        for root_node in hierarchy:
            tree_lines.extend(render_node(root_node, counter))
        
        # Generate output filename without extension
        filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
        output_filename = f"{filename_base}-code_tree.md"
        
        with open(output_filename, "w") as f:
            f.write('\n'.join(tree_lines))

    def generate_flow_graph(self, content, filename):
        """
        Generate control-flow graph in Mermaid format for visualization.
        
        Creates a visual representation of program flow showing:
        - Decision points (if statements) as diamond nodes
        - Loops (foreach) with cycle edges
        - Sequential operations as rectangular nodes
        - True/false branches for conditions
        
        Args:
            content (str): Raw DataLine source code
            filename (str): Name of the source file
            
        Output:
            Creates filename-flow_graph.md with Mermaid graph definition
        """
        lines = content.split('\n')
        flow_lines = ["# Flow Graph - " + filename + "\n"]
        flow_lines.append("```mermaid")
        flow_lines.append("graph TD")
        
        # Parse code structure with proper block handling
        parsed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Skip non-executable lines and syntax tokens
            if not line or line.startswith('#') or line in ['{', '}'] or line == 'else' or line.startswith('else if') or line.startswith('} else') or line.startswith('} else if'):
                i += 1
                continue
            
            # Handle different construct types for flow analysis
            if line.startswith('if '):
                condition = line[3:].split('{')[0].strip()
                parsed_lines.append({'type': 'if', 'condition': condition, 'line_num': i+1})
            elif line.startswith('foreach'):
                foreach_content = line.rstrip('{').strip()
                parsed_lines.append({'type': 'foreach', 'content': foreach_content, 'line_num': i+1})
            elif any(line.startswith(cmd) for cmd in ['get(', 'print(', 'send(', 'type(']):
                cmd_end = line.rfind(')') + 1
                operation = line[:cmd_end] if cmd_end > 0 else line
                parsed_lines.append({'type': 'command', 'operation': operation, 'line_num': i+1})
            elif '=' in line and not line.startswith(('if', 'foreach', 'print', 'get', 'send')):
                parsed_lines.append({'type': 'assignment', 'content': line, 'line_num': i+1})
            
            i += 1
        
        # Generate flow graph nodes and edges with proper connections
        node_id = 0
        for i, parsed in enumerate(parsed_lines):
            node_id += 1
            current_node = f"N{node_id}"
            
            if parsed['type'] == 'if':
                condition = parsed['condition']
                display_condition = condition[:30] + '...' if len(condition) > 30 else condition
                flow_lines.append(f'    {current_node}{{{display_condition}}}')
                
                if i + 1 < len(parsed_lines):
                    true_node = f"N{node_id + 1}"
                    flow_lines.append(f'    {current_node} -->|true| {true_node}')
                    
                    false_node = f"N{node_id + 2}" if i + 2 < len(parsed_lines) else f"End{node_id}"
                    flow_lines.append(f'    {current_node} -->|false| {false_node}')
                else:
                    flow_lines.append(f'    {current_node} -->|true| End{node_id}')
                    flow_lines.append(f'    {current_node} -->|false| End{node_id}')
                
            elif parsed['type'] == 'foreach':
                content = parsed['content']
                display_text = content[:40] + '...' if len(content) > 40 else content
                flow_lines.append(f'    {current_node}[{display_text}]')
                
                if i + 1 < len(parsed_lines):
                    body_node = f"N{node_id + 1}"
                    next_node = f"N{node_id + 2}" if i + 2 < len(parsed_lines) else f"End{node_id}"
                    
                    flow_lines.append(f'    {current_node} --> {body_node}')
                    flow_lines.append(f'    {body_node} --> {current_node}')  # Loop back edge
                    flow_lines.append(f'    {current_node} -.->|exit| {next_node}')  # Exit edge
                else:
                    flow_lines.append(f'    {current_node} --> End{node_id}')
                
            elif parsed['type'] == 'command':
                operation = parsed['operation']
                display_text = operation[:40] + '...' if len(operation) > 40 else operation
                flow_lines.append(f'    {current_node}[{display_text}]')
                
                if i + 1 < len(parsed_lines):
                    next_node = f"N{node_id + 1}"
                    flow_lines.append(f'    {current_node} --> {next_node}')
                    
            elif parsed['type'] == 'assignment':
                content = parsed['content']
                display_text = content[:40] + '...' if len(content) > 40 else content
                flow_lines.append(f'    {current_node}[{display_text}]')
                
                if i + 1 < len(parsed_lines):
                    next_node = f"N{node_id + 1}"
                    flow_lines.append(f'    {current_node} --> {next_node}')
        
        flow_lines.append("```")
        
        # Generate output filename without extension
        filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
        output_filename = f"{filename_base}-flow_graph.md"
        
        with open(output_filename, "w") as f:
            f.write('\n'.join(flow_lines))

# =============================================================================
# RUNTIME LIBRARY
# =============================================================================
# Contains all runtime functions that are injected into translated DataLine programs

class RuntimeLibrary:
    """
    Runtime library containing all built-in functions available to DataLine programs.
    These functions are injected into the translated Python code during compilation.
    """
    
    def get_runtime_code(self):
        """
        Generate the complete runtime library code as a string.
        
        Returns:
            str: Complete runtime library code with all built-in functions
        """
        return '''
import json
import urllib.request
import urllib.parse
import sqlite3
import re
from urllib.parse import urlparse

# Database availability constants
SQLITE_AVAILABLE = True
MYSQL_AVAILABLE = False
POSTGRESQL_AVAILABLE = False
MONGODB_AVAILABLE = False
REDIS_AVAILABLE = False
CASSANDRA_AVAILABLE = False
ELASTICSEARCH_AVAILABLE = False

def get(source, headers=None):
    """
    Universal data retrieval function supporting both local files and HTTP endpoints.
    
    Args:
        source (str): File path or HTTP URL
        headers (dict, optional): Custom headers for HTTP requests
        
    Returns:
        - JSON files: Parsed dictionary/object
        - Text files: String content
        - HTTP: Parsed JSON or raw text
        - Errors: None (with error logging)
    """
    if source.startswith('http'):
        try:
            req = urllib.request.Request(source)
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                # Auto-parse JSON responses
                if response.headers.get('content-type', '').startswith('application/json'):
                    return json.loads(content)
                return content
        except Exception as e:
            print(f"Error fetching {source}: {e}")
            return None
    else:
        # Local file access
        with open(source, 'r') as file:
            if source.endswith('.json'):
                return json.load(file)
            else:
                return file.read()

def send(destination, data, payload=None, headers=None):
    """
    Universal data output function supporting both files and HTTP endpoints.
    
    Args:
        destination (str): File path or HTTP URL
        data (any): Data to send
        payload (any, optional): Custom payload for HTTP requests
        headers (dict, optional): Custom headers for HTTP requests
        
    Returns:
        - Files: True on success
        - HTTP: Status code (e.g., 200, 201)
        - Errors: None (with error logging)
    """
    if destination.startswith('http'):
        # HTTP request with custom headers and payload support
        if payload is None:
            payload = data
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(destination, data=data_bytes, headers=headers)
            with urllib.request.urlopen(req) as response:
                return response.getcode()
        except Exception as e:
            print(f"Error sending to {destination}: {e}")
            return None
    else:
        # Local file output with automatic formatting
        with open(destination, 'w') as file:
            if destination.endswith('.json'):
                json.dump(data, file, indent=2)
            else:
                file.write(str(data))
        return True

def builtin_type(variable):
    """
    Type inspection function that avoids conflicts with Python's built-in type().
    
    Args:
        variable (any): Variable to inspect
        
    Returns:
        str: Type name of the variable
    """
    return variable.__class__.__name__

def query(database_uri, query_or_collection, filter_dict=None):
    """
    Universal database query function supporting multiple database types.
    
    Args:
        database_uri (str): Database connection URI
            - SQLite: "sqlite://path/to/database.db"
            - MySQL: "mysql://user:pass@host:port/database"
            - PostgreSQL: "postgresql://user:pass@host:port/database"
            - MongoDB: "mongodb://host:port/database"
            - Redis: "redis://host:port/database"
            - Cassandra: "cassandra://host:port/keyspace"
            - Elasticsearch: "elasticsearch://host:port/index"
        query_or_collection (str): SQL query, collection name, or index operation
        filter_dict (dict, optional): MongoDB filter document, Redis key pattern, or ES query
        
    Returns:
        list: Query results as list of dictionaries
        None: On error (with error logging)
    """
    try:
        # Parse database type from URI
        parsed = urlparse(database_uri)
        db_type = parsed.scheme.lower()
        
        if db_type == 'sqlite':
            if not SQLITE_AVAILABLE:
                print("Warning: SQLite not available. Please ensure sqlite3 is installed.")
                return None
            # For SQLite, path comes after scheme
            db_path = database_uri[len('sqlite://'):]
            return _query_sqlite(db_path, query_or_collection)
        elif db_type == 'mysql':
            if not MYSQL_AVAILABLE:
                print("Warning: MySQL not available. Please install: pip install pymysql")
                return None
            return _query_mysql(parsed, query_or_collection)
        elif db_type == 'postgresql':
            if not POSTGRESQL_AVAILABLE:
                print("Warning: PostgreSQL not available. Please install: pip install psycopg2-binary")
                return None
            return _query_postgresql(parsed, query_or_collection)
        elif db_type == 'mongodb':
            if not MONGODB_AVAILABLE:
                print("Warning: MongoDB not available. Please install: pip install pymongo")
                return None
            return _query_mongodb(parsed, query_or_collection, filter_dict)
        elif db_type == 'redis':
            if not REDIS_AVAILABLE:
                print("Warning: Redis not available. Please install: pip install redis")
                return None
            return _query_redis(parsed, query_or_collection, filter_dict)
        elif db_type == 'cassandra':
            if not CASSANDRA_AVAILABLE:
                print("Warning: Cassandra not available. Please install: pip install cassandra-driver")
                return None
            return _query_cassandra(parsed, query_or_collection)
        elif db_type == 'elasticsearch':
            if not ELASTICSEARCH_AVAILABLE:
                print("Warning: Elasticsearch not available. Please install: pip install elasticsearch")
                return None
            return _query_elasticsearch(parsed, query_or_collection, filter_dict)
        else:
            print(f"Error: Unsupported database type '{db_type}'. Supported: sqlite, mysql, postgresql, mongodb, redis, cassandra, elasticsearch")
            return None
            
    except Exception as e:
        print(f"Database query error: {e}")
        return None

def _query_sqlite(db_path, query):
    """Execute SQLite query and return results as list of dictionaries"""
    try:
        # Remove leading slash from path and handle relative paths
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        # If path doesn't exist, try current directory
        if not db_path.endswith('.db'):
            db_path += '.db'
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"SQLite error: {e}")
        print(f"Database path attempted: '{db_path}'")
        return None

def _query_mysql(parsed, query):
    """Execute MySQL query"""
    try:
        import pymysql
        # Extract connection details from parsed URI
        # Implementation would go here
        print("MySQL support is available but not fully implemented")
        print(f"Would execute: {query}")
        print(f"Connection: {parsed.netloc}")
        return []
    except ImportError:
        print("Warning: MySQL not available. Please install: pip install pymysql")
        return None
    except Exception as e:
        print(f"MySQL error: {e}")
        return None

def _query_postgresql(parsed, query):
    """Execute PostgreSQL query"""
    try:
        import psycopg2
        # Extract connection details from parsed URI
        # Implementation would go here
        print("PostgreSQL support is available but not fully implemented")
        print(f"Would execute: {query}")
        print(f"Connection: {parsed.netloc}")
        return []
    except ImportError:
        print("Warning: PostgreSQL not available. Please install: pip install psycopg2-binary")
        return None
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return None

def _query_mongodb(parsed, collection_name, filter_dict):
    """Execute MongoDB query"""
    try:
        import pymongo
        # Extract connection details from parsed URI
        # Implementation would go here
        print("MongoDB support is available but not fully implemented")
        print(f"Would query collection: {collection_name}")
        print(f"Filter: {filter_dict}")
        print(f"Connection: {parsed.netloc}")
        return []
    except ImportError:
        print("Warning: MongoDB not available. Please install: pip install pymongo")
        return None
    except Exception as e:
        print(f"MongoDB error: {e}")
        return None

def _query_redis(parsed, operation, filter_dict):
    """Execute Redis operation"""
    try:
        import redis
        # Extract connection details from parsed URI
        # Implementation would go here
        print("Redis support is available but not fully implemented")
        print(f"Would execute: {operation}")
        print(f"Filter: {filter_dict}")
        print(f"Connection: {parsed.netloc}")
        return []
    except ImportError:
        print("Warning: Redis not available. Please install: pip install redis")
        return None
    except Exception as e:
        print(f"Redis error: {e}")
        return None

def _query_cassandra(parsed, query):
    """Execute Cassandra query"""
    try:
        import cassandra
        # Extract connection details from parsed URI
        # Implementation would go here
        print("Cassandra support is available but not fully implemented")
        print(f"Would execute: {query}")
        print(f"Connection: {parsed.netloc}")
        return []
    except ImportError:
        print("Warning: Cassandra not available. Please install: pip install cassandra-driver")
        return None
    except Exception as e:
        print(f"Cassandra error: {e}")
        return None

def _query_elasticsearch(parsed, operation, filter_dict):
    """Execute Elasticsearch operation"""
    try:
        import elasticsearch
        # Extract connection details from parsed URI
        # Implementation would go here
        print("Elasticsearch support is available but not fully implemented")
        print(f"Would execute: {operation}")
        print(f"Filter: {filter_dict}")
        print(f"Connection: {parsed.netloc}")
        return []
    except ImportError:
        print("Warning: Elasticsearch not available. Please install: pip install elasticsearch")
        return None
    except Exception as e:
        print(f"Elasticsearch error: {e}")
        return None
'''

# =============================================================================
# COMMAND TRANSLATOR
# =============================================================================
# Core translation engine that converts DataLine syntax to Python bytecode

class CommandTranslator:
    """
    Translates individual DataLine commands to their Python equivalents.
    Handles all language constructs including control structures, assignments,
    and built-in function calls.
    """
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def translate_command(self, line):
        """
        Translate a single DataLine command to Python equivalent.
        
        This function handles the core language translation:
        - Control structures (if/else/foreach)
        - Variable assignments with type inference
        - Built-in function calls (get, send, print, type)
        - Syntax normalization and error checking
        
        Args:
            line (str): Single line of DataLine source code
            
        Returns:
            str: Equivalent Python code or empty string for comments/syntax tokens
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return ""
        
        # Handle closing braces with content first (common pattern in DataLine)
        if line.startswith('}'):
            line = line[1:].strip()
        
        # Handle opening braces (syntax tokens, not translated)
        if line == '{':
            return ""
        elif line.endswith('}'):
            line = line[:-1].strip()
        
        # Conditional statements - require parentheses for safety
        if line.startswith('if '):
            return self._translate_if_statement(line)
        
        elif line.startswith('else if '):
            return self._translate_elif_statement(line)
        
        elif line == 'else':
            return 'else:'
        elif line.startswith('else'):
            return self._translate_else_statement(line)
        
        # Variable assignment with automatic type detection and inference
        if '=' in line and not line.startswith(('if', 'foreach', 'print', 'get', 'send')):
            return self._translate_assignment(line)
        
        # Built-in function calls (pass-through to Python)
        elif line.startswith('print('):
            return line
        elif line.startswith('get('):
            return line
        elif line.startswith('type('):
            return f'builtin_type({line[5:].strip()})'
        elif line.startswith('builtin_type('):
            return line
        elif line.startswith('send('):
            return line
        elif line.startswith('query('):
            return line
        
        # Function definition command
        elif line.startswith('function '):
            return self._translate_function_definition(line)
        
        elif line.startswith('foreach'):
            return self._translate_foreach(line)
        
        # Pass-through for any other Python-compatible code
        else:
            return line
    
    def _translate_if_statement(self, line):
        """Translate if statement with proper validation."""
        condition = line[3:].strip()
        condition = condition.rstrip('{').strip()
        
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1]
            condition = condition.replace('true', 'True').replace('false', 'False')
            return f'if ({condition}):'
        else:
            error_msg = f"Error: if condition must be enclosed in parentheses: {line}"
            if self.logger:
                self.logger.log_error(error_msg)
            return f"# {error_msg}"
    
    def _translate_elif_statement(self, line):
        """Translate else if statement with proper validation."""
        condition = line[8:].strip()
        condition = condition.rstrip('{').strip()
        
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1]
            condition = condition.replace('true', 'True').replace('false', 'False')
            return f'elif ({condition}):'
        else:
            error_msg = f"Error: else if condition must be enclosed in parentheses: {line}"
            if self.logger:
                self.logger.log_error(error_msg)
            return f"# {error_msg}"
    
    def _translate_else_statement(self, line):
        """Translate else statement variations."""
        clean_line = line.rstrip('{').strip()
        if clean_line == 'else':
            return 'else:'
        elif clean_line.startswith('else if '):
            condition = clean_line[8:].strip()
            if condition.startswith('(') and condition.endswith(')'):
                condition = condition[1:-1]
            return f'elif ({condition}):'
        else:
            return clean_line
    
    def _translate_assignment(self, line):
        """Translate variable assignment with type inference."""
        var_name, value = line.split('=', 1)
        var_name = var_name.strip()
        value = value.strip()
        
        # Type inference based on value patterns
        if value.startswith('"') and value.endswith('"'):
            return f'{var_name} = {value}'
        elif value.startswith("'") and value.endswith("'"):
            return f'{var_name} = {value}'
        elif value.lower() == 'true':
            return f'{var_name} = True'
        elif value.lower() == 'false':
            return f'{var_name} = False'
        elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return f'{var_name} = {value}'
        elif value.startswith('get('):
            return f'{var_name} = {value}'
        elif any(op in value for op in ['+', '-', '*', '/', '**', '%']):
            return f'{var_name} = {value}'
        elif re.match(r'^\w+\(', value):
            return f'{var_name} = {value}'
        else:
            return f'{var_name} = "{value}"'
    
    def _translate_function_definition(self, line):
        """Translate function definition."""
        func_match = re.match(r'function\s+(\w+)\s*\(([^)]*)\)\s*\{', line)
        if func_match:
            func_name = func_match.group(1)
            params = func_match.group(2).strip()
            return f'def {func_name}({params}):'
        else:
            error_msg = f"Error parsing function: {line}"
            if self.logger:
                self.logger.log_error(error_msg)
            return f'# {error_msg}'
    
    def _translate_foreach(self, line):
        """Translate foreach loop with proper syntax validation."""
        clean_line = line.rstrip('{').strip()
        
        # Check for key => value syntax (for dictionaries/objects)
        match_arrow = re.match(r'foreach\s*\(\s*(\w+)\s+as\s+(\w+)\s*=>\s*(\w+)\s*\)', clean_line)
        if match_arrow:
            collection, key_var, value_var = match_arrow.groups()
            return f'for {key_var}, {value_var} in {collection}.items():'
        
        # Check for simple as item syntax (for arrays/lists)
        match_simple = re.match(r'foreach\s*\(\s*(\w+)\s+as\s+(\w+)\s*\)', clean_line)
        if match_simple:
            collection, alias = match_simple.groups()
            return f'for {alias} in {collection}:'
        
        # Syntax error if no pattern matches
        error_msg = f"Error parsing foreach: {line}"
        if self.logger:
            self.logger.log_error(error_msg)
        return f"# {error_msg}"

# =============================================================================
# DATA LINE INTERPRETER
# =============================================================================
# Main orchestrator class that coordinates all components

class DataLineInterpreter:
    """
    Main interpreter class that orchestrates the compilation and execution
    of DataLine programs. Coordinates all architectural components.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the interpreter with optional custom logger.
        
        Args:
            logger (LoggingSystem, optional): Custom logging system
        """
        self.logger = logger or LoggingSystem()
        self.visualizer = CodeVisualizer()
        self.runtime_library = RuntimeLibrary()
        self.command_translator = CommandTranslator(logger)
    
    def read_file(self, filename):
        """
        Read the contents of a file as a string.
        
        Args:
            filename (str): Path to the file to read
            
        Returns:
            str: Complete file contents
            
        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there are permission or I/O issues
        """
        with open(filename, 'r') as file:
            return file.read()
    
    def translate_file(self, content):
        """
        Translate complete DataLine file to executable Python code.
        
        This function:
        1. Injects runtime library functions (get, send, builtin_type)
        2. Translates each line using CommandTranslator
        3. Manages indentation and block structure
        4. Produces valid Python bytecode for execution
        
        Args:
            content (str): Complete DataLine source file contents
            
        Returns:
            str: Executable Python code with runtime library
        """
        python_code = []
        indent_level = 0
        
        # Inject runtime library at beginning of every translated program
        runtime_code = self.runtime_library.get_runtime_code()
        python_code.append(runtime_code.strip())
        
        # Process each line of the DataLine source
        lines = content.split('\n')
        in_function = False
        current_function_name = None
        function_body = []
        
        for line_num, line in enumerate(lines):
            original_line = line.strip()
            
            # Handle function definitions
            if line.startswith('function ') and '{' in line:
                func_match = re.match(r'function\s+(\w+)\s*\(([^)]*)\)\s*\{', line)
                if func_match:
                    current_function_name = func_match.group(1)
                    params = func_match.group(2).strip()
                    python_code.append(f'def {current_function_name}({params}):')
                    in_function = True
                    function_body = []
                continue
            
            # Handle function body
            if in_function and line.strip() != '}':
                if line.strip() and not line.startswith('function '):
                    function_body.append(line)
                continue
            
            # Handle function closing
            if in_function and line.strip() == '}':
                # Process function body with proper indentation handling
                for body_line in function_body:
                    leading_spaces = len(body_line) - len(body_line.lstrip())
                    indent_level = leading_spaces // 4
                    
                    translated_line = self.command_translator.translate_command(body_line)
                    if translated_line:
                        total_indent = 4 + (indent_level * 4)
                        python_code.append(' ' * total_indent + translated_line)
                
                python_code.append('')  # Empty line after function
                in_function = False
                current_function_name = None
                function_body = []
                indent_level = 0
                continue
            
            # Skip function definition lines
            if current_function_name and line_num > 0:
                continue
            
            translated = self.command_translator.translate_command(line)
            
            # Handle indentation for closing braces
            if original_line.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            if translated:
                # Handle indentation for block structures
                if translated.endswith(':'):
                    if any(translated.startswith(prefix) for prefix in ['if (', 'elif (', 'else:']):
                        indent_level = max(0, indent_level - 1)
                        python_code.append('    ' * indent_level + translated)
                        indent_level += 1
                    else:
                        python_code.append('    ' * indent_level + translated)
                        indent_level += 1
                else:
                    python_code.append('    ' * indent_level + translated)
        
        return '\n'.join(python_code)
    
    def execute_file(self, filename, options=None):
        """
        Execute a DataLine file with the specified options.
        
        Args:
            filename (str): Path to the DataLine file
            options (dict, optional): Execution options including:
                - log_level: Logging level
                - generate_flow_graph: Generate flow graph
                - generate_code_tree: Generate code tree
                - time_execution: Measure execution time
                - track_usage: Track CPU/RAM usage
                
        Returns:
            bool: True if execution succeeded, False otherwise
        """
        if options is None:
            options = {}
        
        # Extract options with defaults
        log_level = options.get('log_level', 'ALL')
        should_generate_flow_graph = options.get('generate_flow_graph', False)
        should_generate_code_tree = options.get('generate_code_tree', False)
        should_time_execution = options.get('time_execution', False)
        should_track_usage = options.get('track_usage', False)
        
        # Initialize logging
        self.logger.init(filename, log_level)
        
        # Performance monitoring setup
        start_time = None
        start_cpu = None
        start_memory = None
        
        if should_time_execution:
            start_time = time.time()
            self.logger.log_info(f"Execution timing started at {start_time}")
        
        if should_track_usage and PSUTIL_AVAILABLE:
            start_cpu = psutil.cpu_percent()
            start_memory = psutil.virtual_memory().percent
            self.logger.log_info(f"Initial CPU usage: {start_cpu}%")
            self.logger.log_info(f"Initial RAM usage: {start_memory}%")
        
        try:
            # Read and translate DataLine source
            content = self.read_file(filename)
            code = self.translate_file(content)
            
            # Execute translated code in isolated namespace
            exec_globals = {}
            exec(code, exec_globals)
            
            # Debug information
            if log_level != "NONE":
                self.logger.log_info(f"Exec globals keys: {list(exec_globals.keys())}")
            
            # Generate optional visualization outputs
            if should_generate_code_tree:
                self.visualizer.generate_hierarchical_code_tree(content, filename)
                if log_level != "NONE":
                    filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    output_filename = f"{filename_base}-code_tree.md"
                    self.logger.log_info(f"Generated hierarchical code tree: {output_filename}")
            
            if should_generate_flow_graph:
                self.visualizer.generate_flow_graph(content, filename)
                if log_level != "NONE":
                    filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    output_filename = f"{filename_base}-flow_graph.md"
                    self.logger.log_info(f"Generated flow graph: {output_filename}")
            
            # Log successful execution
            if log_level != "NONE":
                self.logger.log_info(f"Successfully executed: {filename}")
            
            # Performance monitoring results
            if should_time_execution and start_time:
                end_time = time.time()
                execution_time = end_time - start_time
                self.logger.log_info(f"Execution completed in {execution_time:.3f} seconds")
                print(f"⏱️  Execution time: {execution_time:.3f} seconds")
            
            if should_track_usage and start_cpu and start_memory and PSUTIL_AVAILABLE:
                end_cpu = psutil.cpu_percent()
                end_memory = psutil.virtual_memory().percent
                self.logger.log_info(f"Final CPU usage: {end_cpu}%")
                self.logger.log_info(f"Final RAM usage: {end_memory}%")
                print(f"📊 CPU usage: {end_cpu}% (start: {start_cpu}%)")
                print(f"💾 RAM usage: {end_memory}% (start: {start_memory}%)")
            
            return True
            
        except Exception as e:
            # Comprehensive error handling with logging
            if log_level != "NONE":
                self.logger.log_error(f"Execution failed: {str(e)}")
            return False

# =============================================================================
# MAIN EXECUTION ENTRY POINT
# =============================================================================
# Command-line interface and execution orchestration for DataLine interpreter.

if __name__ == "__main__":
    """
    Main entry point for DataLine interpreter.
    
    Command-line interface:
    - Required: filename.datal
    - Optional: --level (log level)
    - Optional: --generate_flow_graph
    - Optional: --generate_code_tree
    
    Execution Flow:
    1. Parse command-line arguments
    2. Initialize logging system
    3. Read and translate DataLine source
    4. Execute generated Python code
    5. Generate optional visualizations
    6. Handle errors gracefully
    """
    # Parse command line arguments with validation
    log_level = "ALL"
    filename = None
    should_generate_flow_graph = False
    should_generate_code_tree = False
    should_time_execution = False
    should_track_usage = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--level="):
            log_level = arg[8:].upper()
        elif arg == "--generate_flow_graph":
            should_generate_flow_graph = True
        elif arg == "--generate_code_tree":
            should_generate_code_tree = True
        elif arg == "--time":
            should_time_execution = True
        elif arg == "--usage":
            should_track_usage = True
        elif not arg.startswith("-"):
            filename = arg
        i += 1
    
    # Validate required arguments and show usage if needed
    if not filename:
        print("Usage: python dataline.py <filename> [--level=ALL|INFO|ERROR|NONE] [--generate_flow_graph|--generate_flow_chart] [--generate_code_tree] [--time] [--usage]")
        print("  --level: Set log level (default: ALL)")
        print("    ALL: Show all logs")
        print("    INFO: Show only info logs") 
        print("    ERROR: Show only error logs")
        print("    NONE: Disable all logging")
        print("  --generate_flow_graph or --generate_flow_chart: Generate flow graph (filename-flow_graph.md)")
        print("  --generate_code_tree: Generate hierarchical code tree (filename-code_tree.md)")
        print("  --time: Measure and log script execution time")
        print("  --usage: Track CPU and RAM usage during execution")
        sys.exit(1)
    
    # Create interpreter instance and execute
    interpreter = DataLineInterpreter()
    
    # Prepare execution options
    options = {
        'log_level': log_level,
        'generate_flow_graph': should_generate_flow_graph,
        'generate_code_tree': should_generate_code_tree,
        'time_execution': should_time_execution,
        'track_usage': should_track_usage
    }
    
    # Execute the file
    success = interpreter.execute_file(filename, options)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
