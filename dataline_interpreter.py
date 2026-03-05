# DataLine Programming Language Interpreter
# Author: Anastasios Bolkas
# Version: 1.0
# Description: A lightweight, dependency-free data pipeline language that compiles to Python
# License: MIT

import sys
import re
import json
import datetime

# =============================================================================
# LOGGING SYSTEM
# =============================================================================
# Provides comprehensive logging with multiple levels (ALL, INFO, ERROR, NONE)
# Logs to both console and persistent history.log file for debugging and auditing

def init_logging(filename=None, log_level="ALL"):
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
    global current_log_level
    current_log_level = log_level
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if log_level != "NONE":
        if filename:
            log_entry = f"[{timestamp}] DataLine interpreter started - File: {filename} - Level: {log_level}\n"
        else:
            log_entry = f"[{timestamp}] DataLine interpreter started - Level: {log_level}\n"
        
        # Append to history.log for persistent audit trail
        with open("history.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Console output for immediate user feedback
        if filename:
            print(f"DataLine Interpreter v1.0 - Started at {timestamp} - File: {filename} - Level: {log_level}")
        else:
            print(f"DataLine Interpreter v1.0 - Started at {timestamp} - Level: {log_level}")
    else:
        # Silent mode for production/automated environments
        print(f"DataLine Interpreter v1.0 - Started at {timestamp} - Silent mode")

def log_info(info_msg):
    """
    Log informational messages with timestamp.
    
    Args:
        info_msg (str): Information message to log
        
    Behavior:
        - Logs to history.log with timestamp
        - Prints to console if log_level is ALL or INFO
        - No output in ERROR or NONE modes
    """
    if current_log_level in ["ALL", "INFO"]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] INFO: {info_msg}\n"
        
        # Persistent logging for audit trail
        with open("history.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Real-time console feedback
        print(f"INFO: {info_msg}")

def log_error(error_msg):
    """
    Log error messages with timestamp.
    
    Args:
        error_msg (str): Error message to log
        
    Behavior:
        - Logs to history.log with timestamp
        - Prints to console if log_level is ALL or ERROR
        - No output in INFO or NONE modes
    """
    if current_log_level in ["ALL", "ERROR"]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ERROR: {error_msg}\n"
        
        # Persistent error logging for debugging
        with open("history.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Immediate error visibility
        print(f"ERROR: {error_msg}")

# =============================================================================
# CODE VISUALIZATION SYSTEM
# =============================================================================
# Generates hierarchical code trees and flow graphs for documentation
# and debugging purposes. Essential for understanding complex data pipelines.

def generate_code_tree(content, filename):
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

def generate_hierarchical_code_tree(content, filename):
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
        
    Algorithm:
        1. Parse each line and identify node types (if, foreach, command, etc.)
        2. Build hierarchical tree structure using stack-based approach
        3. Handle special cases for if/else if/else chains
        4. Render tree with proper indentation and sequential numbering
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
            # Extract condition without the opening brace
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

def generate_flow_graph(content, filename):
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
        
    Algorithm:
        1. Parse code to identify control flow constructs
        2. Generate nodes for each operation with appropriate shapes
        3. Create edges showing execution flow
        4. Handle special cases for loops and conditionals
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
            # Extract foreach statement without opening brace
            foreach_content = line.rstrip('{').strip()
            parsed_lines.append({'type': 'foreach', 'content': foreach_content, 'line_num': i+1})
        elif any(line.startswith(cmd) for cmd in ['get(', 'print(', 'send(', 'type(']):
            # Extract meaningful operation for display
            cmd_end = line.rfind(')') + 1
            operation = line[:cmd_end] if cmd_end > 0 else line
            parsed_lines.append({'type': 'command', 'operation': operation, 'line_num': i+1})
        elif '=' in line and not line.startswith(('if', 'foreach', 'print', 'get', 'send')):
            # Variable assignment operation
            parsed_lines.append({'type': 'assignment', 'content': line, 'line_num': i+1})
        
        i += 1
    
    # Generate flow graph nodes and edges with proper connections
    node_id = 0
    for i, parsed in enumerate(parsed_lines):
        node_id += 1
        current_node = f"N{node_id}"
        
        if parsed['type'] == 'if':
            condition = parsed['condition']
            # Decision node with diamond shape for conditional logic
            display_condition = condition[:30] + '...' if len(condition) > 30 else condition
            flow_lines.append(f'    {current_node}{{{display_condition}}}')
            
            # Create true and false branches for decision
            if i + 1 < len(parsed_lines):
                true_node = f"N{node_id + 1}"
                flow_lines.append(f'    {current_node} -->|true| {true_node}')
                
                # Find node after if block for false branch
                false_node = f"N{node_id + 2}" if i + 2 < len(parsed_lines) else f"End{node_id}"
                flow_lines.append(f'    {current_node} -->|false| {false_node}')
            else:
                flow_lines.append(f'    {current_node} -->|true| End{node_id}')
                flow_lines.append(f'    {current_node} -->|false| End{node_id}')
            
        elif parsed['type'] == 'foreach':
            content = parsed['content']
            # Extract meaningful part (truncate if needed for display)
            display_text = content[:40] + '...' if len(content) > 40 else content
            flow_lines.append(f'    {current_node}[{display_text}]')
            
            # Create cycle for foreach loop structure
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
            
            # Sequential flow to next operation
            if i + 1 < len(parsed_lines):
                next_node = f"N{node_id + 1}"
                flow_lines.append(f'    {current_node} --> {next_node}')
                
        elif parsed['type'] == 'assignment':
            content = parsed['content']
            display_text = content[:40] + '...' if len(content) > 40 else content
            flow_lines.append(f'    {current_node}[{display_text}]')
            
            # Sequential flow to next operation
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
# FILE I/O OPERATIONS
# =============================================================================
# Basic file reading functionality for DataLine source files

def read_file(filename):
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

# =============================================================================
# LANGUAGE TRANSLATION ENGINE
# =============================================================================
# Core translation engine that converts DataLine syntax to Python bytecode.
# This is the heart of the interpreter - each DataLine construct is mapped
# to its Python equivalent with proper syntax and semantics.

def translate_command(line):
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
        
    Translation Strategy:
        1. Strip whitespace and handle comments
        2. Process brace syntax (remove, handle indentation)
        3. Identify command type and apply specific translation rules
        4. Validate syntax and generate appropriate Python code
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
        condition = line[3:].strip()
        # Remove opening brace if present
        condition = condition.rstrip('{').strip()
        # Validate and translate condition
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1]
            # Convert DataLine boolean literals to Python
            condition = condition.replace('true', 'True').replace('false', 'False')
            return f'if ({condition}):'
        else:
            return f"# Error: if condition must be enclosed in parentheses: {line}"
    
    elif line.startswith('else if '):
        condition = line[8:].strip()
        # Remove opening brace if present
        condition = condition.rstrip('{').strip()
        # Validate and translate condition
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1]
            # Convert DataLine boolean literals to Python
            condition = condition.replace('true', 'True').replace('false', 'False')
            return f'elif ({condition}):'
        else:
            return f"# Error: else if condition must be enclosed in parentheses: {line}"
    
    elif line == 'else':
        return 'else:'
    elif line.startswith('else'):
        # Handle else with opening brace or else if variations
        clean_line = line.rstrip('{').strip()
        if clean_line == 'else':
            return 'else:'
        elif clean_line.startswith('else if '):
            condition = clean_line[8:].strip()
            if condition.startswith('(') and condition.endswith(')'):
                condition = condition[1:-1]
            return f'elif {condition}:'
        else:
            return clean_line
    
    # Variable assignment with automatic type detection and inference
    if '=' in line and not line.startswith(('if', 'foreach', 'print', 'get', 'send')):
        var_name, value = line.split('=', 1)
        var_name = var_name.strip()
        value = value.strip()
        
        # Type inference based on value patterns
        if value.startswith('"') and value.endswith('"'):
            # Double-quoted string
            return f'{var_name} = {value}'
        elif value.startswith("'") and value.endswith("'"):
            # Single-quoted string
            return f'{var_name} = {value}'
        elif value.lower() == 'true':
            # Boolean true
            return f'{var_name} = True'
        elif value.lower() == 'false':
            # Boolean false
            return f'{var_name} = False'
        elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            # Integer (positive or negative)
            return f'{var_name} = {value}'
        elif value.startswith('get('):
            # Function call result
            return f'{var_name} = {value}'
        else:
            # Default to string (unquoted values become strings)
            return f'{var_name} = "{value}"'
    
    # Built-in function calls (pass-through to Python)
    elif line.startswith('print('):
        # Print function - direct translation
        return line
    
    elif line.startswith('get('):
        # Get function - direct translation (handles headers parameter)
        return line
    
    elif line.startswith('type('):
        # Type inspection - map to built-in function to avoid conflicts
        return f'builtin_type({line[5:].strip()})'
    
    elif line.startswith('builtin_type('):
        # Built-in type function (internal use)
        return line
    
    # Send command (HTTP/file output)
    elif line.startswith('send('):
        return line
    
    elif line.startswith('foreach'):
        # Parse foreach loop with two syntax variants:
        # 1. foreach (items as item) - simple iteration
        # 2. foreach (items as key => value) - key-value iteration
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
            # Python handles both dicts and arrays with this syntax
            return f'for {alias} in {collection}:'
        
        # Syntax error if no pattern matches
        return f"# Error parsing foreach: {line}"
    
    # Pass-through for any other Python-compatible code
    else:
        return line

# =============================================================================
# COMPILATION ENGINE
# =============================================================================
# Orchestrates the translation of DataLine source to executable Python code.
# Handles indentation, block structure, and runtime library injection.

def translate_file(content):
    """
    Translate complete DataLine file to executable Python code.
    
    This function:
    1. Injects runtime library functions (get, send, builtin_type)
    2. Translates each line using translate_command()
    3. Manages indentation and block structure
    4. Produces valid Python bytecode for execution
    
    Args:
        content (str): Complete DataLine source file contents
        
    Returns:
        str: Executable Python code with runtime library
        
    Runtime Library:
        - get(): HTTP/file access with JSON parsing
        - send(): HTTP/file output with headers support
        - builtin_type(): Type inspection without conflicts
    """
    python_code = []
    indent_level = 0
    
    # Inject runtime library at the beginning of every translated program
    runtime_code = '''
import json
import urllib.request
import urllib.parse

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
'''
    
    python_code.append(runtime_code.strip())
    
    # Process each line of the DataLine source
    for line in content.split('\n'):
        original_line = line.strip()
        translated = translate_command(line)
        
        # Handle indentation for closing braces
        if original_line.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        if translated:
            # Handle indentation for block structures
            if translated.endswith(':'):
                # Special handling for control structures
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

# =============================================================================
# MAIN EXECUTION ENTRY POINT
# =============================================================================
# Command-line interface and execution orchestration for DataLine interpreter.
# Handles argument parsing, file processing, and optional output generation.

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
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--level="):
            log_level = arg[8:].upper()
        elif arg == "--generate_flow_graph":
            should_generate_flow_graph = True
        elif arg == "--generate_code_tree":
            should_generate_code_tree = True
        elif not arg.startswith("-"):
            filename = arg
        i += 1
    
    # Validate required arguments and show usage if needed
    if not filename:
        print("Usage: python dataline.py <filename> [--level=ALL|INFO|ERROR|NONE] [--generate_flow_graph] [--generate_code_tree]")
        print("  --level: Set log level (default: ALL)")
        print("    ALL: Show all logs")
        print("    INFO: Show only info logs") 
        print("    ERROR: Show only error logs")
        print("    NONE: Disable all logging")
        print("  --generate_flow_graph: Generate flow graph (filename-flow_graph.md)")
        print("  --generate_code_tree: Generate hierarchical code tree (filename-code_tree.md)")
        sys.exit(1)
    
    # Initialize global logging state
    current_log_level = log_level
    
    # Initialize logging system with file context
    init_logging(filename, log_level)
    
    try:
        # Read DataLine source file
        content = read_file(filename)
        
        # Translate to executable Python code
        code = translate_file(content)
        
        # Execute translated code in isolated namespace
        exec_globals = {}
        exec(code, exec_globals)
        
        # Debug information for development (only in non-silent modes)
        if current_log_level != "NONE":
            log_info(f"Exec globals keys: {list(exec_globals.keys())}")
        
        # Generate optional visualization outputs
        if should_generate_code_tree:
            generate_hierarchical_code_tree(content, filename)
            if current_log_level != "NONE":
                filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
                output_filename = f"{filename_base}-code_tree.md"
                log_info(f"Generated hierarchical code tree: {output_filename}")
        
        if should_generate_flow_graph:
            generate_flow_graph(content, filename)
            if current_log_level != "NONE":
                filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
                output_filename = f"{filename_base}-flow_graph.md"
                log_info(f"Generated flow graph: {output_filename}")
        
        # Log successful execution
        if current_log_level != "NONE":
            log_info(f"Successfully executed: {filename}")
            
    except Exception as e:
        # Comprehensive error handling with logging
        if current_log_level != "NONE":
            log_error(f"Execution failed: {str(e)}")
        sys.exit(1)
