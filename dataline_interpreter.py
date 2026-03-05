import sys
import re
import json
import datetime

# Initialize logging
def init_logging(filename=None, log_level="ALL"):
    global current_log_level
    current_log_level = log_level
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if log_level != "NONE":
        if filename:
            log_entry = f"[{timestamp}] DataLine interpreter started - File: {filename} - Level: {log_level}\n"
        else:
            log_entry = f"[{timestamp}] DataLine interpreter started - Level: {log_level}\n"
        
        # Append to history.log
        with open("history.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Also print to console for visibility
        if filename:
            print(f"DataLine Interpreter v1.0 - Started at {timestamp} - File: {filename} - Level: {log_level}")
        else:
            print(f"DataLine Interpreter v1.0 - Started at {timestamp} - Level: {log_level}")
    else:
        # Silent mode - no logging output
        print(f"DataLine Interpreter v1.0 - Started at {timestamp} - Silent mode")

def log_info(info_msg):
    if current_log_level in ["ALL", "INFO"]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] INFO: {info_msg}\n"
        
        # Append to history.log
        with open("history.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Also print to console
        print(f"INFO: {info_msg}")

def log_error(error_msg):
    if current_log_level in ["ALL", "ERROR"]:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ERROR: {error_msg}\n"
        
        # Append to history.log
        with open("history.log", "a") as log_file:
            log_file.write(log_entry)
        
        # Also print to console
        print(f"ERROR: {error_msg}")

def generate_code_tree(content, filename):
    """Generate flat code tree structure (legacy)"""
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
            # Add empty lines to preserve structure
            tree_lines.append("")
    
    # Generate filename without extension
    filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
    output_filename = f"{filename_base}-code_tree.md"
    
    with open(output_filename, "w") as f:
        f.write('\n'.join(tree_lines))

def generate_hierarchical_code_tree(content, filename):
    """Generate structured, hierarchical code tree"""
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
        
        # Calculate indentation level
        leading_spaces = len(line) - len(line.lstrip())
        indent_level = leading_spaces // 2  # Assuming 2 spaces per indent level
        
        # Skip syntax tokens but track them for context
        if stripped in ['{', '}']:
            i += 1
            continue
        
        # Parse different constructs
        node = {
            'line_num': line_number,
            'indent': indent_level,
            'content': stripped,
            'type': 'unknown',
            'children': []
        }
        
        # Identify node type
        if stripped.startswith('if '):
            node['type'] = 'if'
            # Extract condition without the opening brace
            condition = stripped[3:].rstrip('{').strip()
            node['display'] = f"if({condition})"
        elif stripped.startswith('} else if'):
            node['type'] = 'else_if'
            # Extract condition without the opening brace
            condition = stripped[10:].rstrip('{').strip()
            node['display'] = f"else if({condition})"
        elif stripped.startswith('else if'):
            node['type'] = 'else_if'
            # Extract condition without the opening brace
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
            # Remove opening brace if present
            foreach_content = stripped.rstrip('{').strip()
            node['display'] = foreach_content
        elif any(stripped.startswith(cmd) for cmd in ['get(', 'print(', 'send(', 'write(']):
            node['type'] = 'command'
            node['display'] = stripped
        elif stripped.startswith('#'):
            node['type'] = 'comment'
            node['display'] = stripped
        elif '=' in stripped and not stripped.startswith(('if', 'foreach', 'print', 'get', 'send', 'write')):
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
        # Handle if/else if/else chains specially
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
    
    # Generate hierarchical output
    def render_node(node, counter, prefix=""):
        result = []
        node_num = next(counter)
        indent_prefix = "    " * node['indent']
        
        # Render the node
        result.append(f"{indent_prefix}{prefix}{node_num:02d}. {node['display']}")
        
        # Render children
        for child in node['children']:
            result.extend(render_node(child, counter))
        
        return result
    
    # Render all root nodes
    counter = iter(range(1, 1000))
    for root_node in hierarchy:
        tree_lines.extend(render_node(root_node, counter))
    
    # Generate filename without extension
    filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
    output_filename = f"{filename_base}-code_tree.md"
    
    with open(output_filename, "w") as f:
        f.write('\n'.join(tree_lines))

def generate_flow_graph(content, filename):
    """Generate proper control-flow graph structure"""
    lines = content.split('\n')
    flow_lines = ["# Flow Graph - " + filename + "\n"]
    flow_lines.append("```mermaid")
    flow_lines.append("graph TD")
    
    # Parse the code structure with proper block handling
    parsed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#') or line in ['{', '}'] or line == 'else' or line.startswith('else if') or line.startswith('} else') or line.startswith('} else if'):
            i += 1
            continue
        
        # Handle different construct types
        if line.startswith('if '):
            condition = line[3:].split('{')[0].strip()
            parsed_lines.append({'type': 'if', 'condition': condition, 'line_num': i+1})
        elif line.startswith('foreach'):
            # Extract foreach statement without the brace
            foreach_content = line.rstrip('{').strip()
            parsed_lines.append({'type': 'foreach', 'content': foreach_content, 'line_num': i+1})
        elif any(line.startswith(cmd) for cmd in ['get(', 'print(', 'send(', 'type(']):
            # Extract meaningful operation
            cmd_end = line.rfind(')') + 1
            operation = line[:cmd_end] if cmd_end > 0 else line
            parsed_lines.append({'type': 'command', 'operation': operation, 'line_num': i+1})
        elif '=' in line and not line.startswith(('if', 'foreach', 'print', 'get', 'send')):
            # Variable assignment
            parsed_lines.append({'type': 'assignment', 'content': line, 'line_num': i+1})
        
        i += 1
    
    # Generate flow graph nodes and edges
    node_id = 0
    for i, parsed in enumerate(parsed_lines):
        node_id += 1
        current_node = f"N{node_id}"
        
        if parsed['type'] == 'if':
            condition = parsed['condition']
            # Decision node with diamond shape
            display_condition = condition[:30] + '...' if len(condition) > 30 else condition
            flow_lines.append(f'    {current_node}{{{display_condition}}}')
            
            # Create true and false branches
            if i + 1 < len(parsed_lines):
                true_node = f"N{node_id + 1}"
                flow_lines.append(f'    {current_node} -->|true| {true_node}')
                
                # Find the node after the if block for false branch
                false_node = f"N{node_id + 2}" if i + 2 < len(parsed_lines) else f"End{node_id}"
                flow_lines.append(f'    {current_node} -->|false| {false_node}')
            else:
                flow_lines.append(f'    {current_node} -->|true| End{node_id}')
                flow_lines.append(f'    {current_node} -->|false| End{node_id}')
            
        elif parsed['type'] == 'foreach':
            content = parsed['content']
            # Extract meaningful part (truncate if needed)
            display_text = content[:40] + '...' if len(content) > 40 else content
            flow_lines.append(f'    {current_node}[{display_text}]')
            
            # Create cycle for foreach
            if i + 1 < len(parsed_lines):
                body_node = f"N{node_id + 1}"
                next_node = f"N{node_id + 2}" if i + 2 < len(parsed_lines) else f"End{node_id}"
                
                flow_lines.append(f'    {current_node} --> {body_node}')
                flow_lines.append(f'    {body_node} --> {current_node}')
                flow_lines.append(f'    {current_node} -.->|exit| {next_node}')
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
    
    # Generate filename without extension
    filename_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
    output_filename = f"{filename_base}-flow_graph.md"
    
    with open(output_filename, "w") as f:
        f.write('\n'.join(flow_lines))

# Read file
def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

# Translate dataline commands to Python
def translate_command(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return ""
    
    # Handle closing braces with content first
    if line.startswith('}'):
        line = line[1:].strip()
    
    # Handle opening braces
    if line == '{':
        return ""
    elif line.endswith('}'):
        line = line[:-1].strip()
    
    # If/else/else if blocks
    if line.startswith('if '):
        condition = line[3:].strip()
        # Remove opening brace if present
        condition = condition.rstrip('{').strip()
        # Require parentheses around condition
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1]
            # Convert boolean values in condition
            condition = condition.replace('true', 'True').replace('false', 'False')
            return f'if ({condition}):'
        else:
            return f"# Error: if condition must be enclosed in parentheses: {line}"
    
    elif line.startswith('else if '):
        condition = line[8:].strip()
        # Remove opening brace if present
        condition = condition.rstrip('{').strip()
        # Require parentheses around condition
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1]
            # Convert boolean values in condition
            condition = condition.replace('true', 'True').replace('false', 'False')
            return f'elif ({condition}):'
        else:
            return f"# Error: else if condition must be enclosed in parentheses: {line}"
    
    elif line == 'else':
        return 'else:'
    elif line.startswith('else'):
        # Handle else with opening brace
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
    
    # Variable assignment with automatic type detection
    if '=' in line and not line.startswith(('if', 'foreach', 'print', 'get', 'send')):
        var_name, value = line.split('=', 1)
        var_name = var_name.strip()
        value = value.strip()
        
        # Remove quotes for string values
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
        else:
            return f'{var_name} = "{value}"'
    
    # Print command
    elif line.startswith('print('):
        return line
    
    # Get command
    elif line.startswith('get('):
        return line
    
    # Type command
    elif line.startswith('type('):
        return f'builtin_type({line[5:].strip()})'
    
    # Built-in type function (renamed to avoid conflicts)
    elif line.startswith('builtin_type('):
        return line
    
    # Send command  
    elif line.startswith('send('):
        return line
    
    elif line.startswith('foreach'):
        # Parse foreach (items as item) or foreach (items as key => value)
        # Remove opening brace if present
        clean_line = line.rstrip('{').strip()
        
        # Check for key => value syntax
        match_arrow = re.match(r'foreach\s*\(\s*(\w+)\s+as\s+(\w+)\s*=>\s*(\w+)\s*\)', clean_line)
        if match_arrow:
            collection, key_var, value_var = match_arrow.groups()
            return f'for {key_var}, {value_var} in {collection}.items():'
        
        # Check for simple as item syntax
        match_simple = re.match(r'foreach\s*\(\s*(\w+)\s+as\s+(\w+)\s*\)', clean_line)
        if match_simple:
            collection, alias = match_simple.groups()
            # Simple iteration - Python will handle both dicts and arrays appropriately
            return f'for {alias} in {collection}:'
        
        # Error if no match
        return f"# Error parsing foreach: {line}"
    
    # Return as-is for other Python-like code
    else:
        return line

# Translate file content
def translate_file(content):
    python_code = []
    indent_level = 0
    
    # Add runtime functions at the beginning
    runtime_code = '''
import json
import urllib.request
import urllib.parse

def get(source):
    if source.startswith('http'):
        try:
            with urllib.request.urlopen(source) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching {source}: {e}")
            return None
    else:
        with open(source, 'r') as file:
            if source.endswith('.json'):
                return json.load(file)
            else:
                return file.read()

def send(destination, data, payload=None, headers=None):
    if destination.startswith('http'):
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
        with open(destination, 'w') as file:
            if destination.endswith('.json'):
                json.dump(data, file, indent=2)
            else:
                file.write(str(data))
        return True

def builtin_type(variable):
    return variable.__class__.__name__
'''
    
    python_code.append(runtime_code.strip())
    
    for line in content.split('\n'):
        original_line = line.strip()
        translated = translate_command(line)
        
        # Check if this is a closing brace
        if original_line.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        if translated:
            # Handle indentation for blocks
            if translated.endswith(':'):
                # For if/elif/else, reduce indent first, then add the line
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

if __name__ == "__main__":
    # Parse command line arguments
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
    
    if not filename:
        print("Usage: python dataline_interpreter.py <filename> [--level=ALL|INFO|ERROR|NONE] [--generate_flow_graph] [--generate_code_tree]")
        print("  --level: Set log level (default: ALL)")
        print("    ALL: Show all logs")
        print("    INFO: Show only info logs") 
        print("    ERROR: Show only error logs")
        print("    NONE: Disable all logging")
        print("  --generate_flow_graph: Generate flow graph (filename-flow_graph.md)")
        print("  --generate_code_tree: Generate hierarchical code tree (filename-code_tree.md)")
        sys.exit(1)
    
    # Set global log level
    current_log_level = log_level
    
    # Initialize logging with filename and level
    init_logging(filename, log_level)
    
    try:
        content = read_file(filename)
        code = translate_file(content)
        
        # Debug: Check for type function conflicts
        exec_globals = {}
        exec(code, exec_globals)
        
        # Debug: Print what's in exec_globals
        if current_log_level != "NONE":
            log_info(f"Exec globals keys: {list(exec_globals.keys())}")
        
        # Generate optional outputs
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
        
        if current_log_level != "NONE":
            log_info(f"Successfully executed: {filename}")
    except Exception as e:
        if current_log_level != "NONE":
            log_error(f"Execution failed: {str(e)}")
        sys.exit(1)
