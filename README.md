# DataLine Programming Language

A lightweight, dependency-free data pipeline language that makes data processing simple and maintainable. DataLine compiles to Python and runs without any external dependencies - just pure Python power!

## Why DataLine?

- **Simple Syntax**: Clean, readable syntax designed specifically for data workflows
- **Zero Dependencies**: Uses only Python's built-in libraries - no pip install required!
- **Data-Focused**: Built-in functions for data retrieval, processing, and storage
- **Built-in Visualization**: Automatic code trees and flow graphs for understanding your pipelines
- **Comprehensive Logging**: Detailed execution history for debugging and auditing

## Quick Start

### Installation
```bash
# No installation needed! Just ensure you have Python 3.6+
python --version
```

### Your First DataLine Program
Create a file called `hello.datal`:
```dataline
# Get data from a public API
weather = get("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m")

# Display the temperature data
print("Weather data:", weather)
print("Current temperature:", weather["hourly"]["temperature_2m"][0], "°C")
```

### Run Your Program
```bash
python dataline.py hello.datal
```

That's it! You've just created your first data pipeline!

## Core Concepts

### Getting Data (`get`)
The universal data retrieval function that works with both files and APIs.

```dataline
# Local files
data = get("data.json")           # Auto-parses JSON
text = get("report.txt")          # Returns as string

# API calls
users = get("https://api.example.com/users")
api_data = get("https://api.github.com/user", headers={"Authorization": "Bearer token"})
```

**Parameters:**
- `source` (string, required) - File path or HTTP URL
- `headers` (object, optional) - Custom headers for HTTP requests

**Returns:**
- JSON files: Parsed dictionary
- Text files: String content
- HTTP: Parsed JSON or raw text
- Errors: `None` with error logged

### Sending Data (`send`)
Store or transmit your processed data.

```dataline
# Save to files (auto-formatted)
send("results.json", processed_data)    # JSON format
send("report.txt", summary)             # Text format

# Send to APIs
send("https://api.example.com/webhook", data, headers={"Content-Type": "application/json"})
```

**Parameters:**
- `destination` (string, required) - File path or HTTP URL
- `data` (any, required) - Data to send
- `headers` (object, optional) - Custom headers for HTTP requests

**Returns:**
- Files: `True` on success
- HTTP: Status code (200, 201, etc.)
- Errors: `None` with error logged

### Database Operations (`query`)
Built-in database support for multiple database types.

```dataline
# SQLite (built-in)
users = query("sqlite:demo_database.db", "SELECT * FROM users WHERE age > 30")

# MySQL, PostgreSQL, MongoDB, Redis (with pip install)
mysql_data = query("mysql:host=localhost;dbname=test", "SELECT * FROM products")
```

**Parameters:**
- `connection_string` (string, required) - Database connection details
- `sql_query` (string, required) - SQL query to execute

**Supported Databases:**
- **SQLite**: Built-in (no installation needed)
- **MySQL**: `pip install pymysql`
- **PostgreSQL**: `pip install psycopg2-binary`
- **MongoDB**: `pip install pymongo`
- **Redis**: `pip install redis`
- **Cassandra**: `pip install cassandra-driver`
- **Elasticsearch**: `pip install elasticsearch`

### Console Output (`print`)
Display data to console with multiple arguments support.

```dataline
# Single value
print("Hello World")

# Multiple values
print("User:", name, "Age:", age)

# Variables and expressions
print(data)
print("Total items:", count * 2)
```

### Type Checking (`type`)
Display the type of a variable for debugging.

```dataline
# Check variable type
data = get("config.json")
type(data)  # Output: dict, list, str, int, bool, etc.

# Type checking in conditions
if (type(data) == "dict") {
    print("Data is a dictionary")
}
```

### Control Flow

#### Conditions (`if/else if/else`)
Conditional statements for program flow control.

```dataline
# Simple conditions
if (age >= 18) {
    print("Adult")
} else {
    print("Minor")
}

# Complex conditions
if (user_type == "admin" and has_permission == true) {
    print("Access granted")
} else if (user_type == "user") {
    print("Limited access")
} else {
    print("Access denied")
}
```

**Supported Operators:**
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Boolean: `and`, `or`, `not`
- Boolean values: `true`, `false`

#### Loops (`foreach`)
Loop through arrays or objects.

```dataline
# Simple iteration
numbers = [1, 2, 3, 4, 5]
foreach (numbers as num) {
    print("Number:", num)
}

# Key-value iteration (for objects/dictionaries)
user = {"name": "John", "age": 30, "city": "NYC"}
foreach (user as key => value) {
    print(key, ":", value)
}

# Process API response data
data = get("https://api.example.com/users")
foreach (data as user) {
    print("User:", user["name"], "Email:", user["email"])
}
```

#### Functions
Create reusable functions for complex operations.

```dataline
# Define a function
function calculateTotal(price, quantity, tax_rate) {
    subtotal = price * quantity
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total
}

# Use the function
total = calculateTotal(19.99, 3, 0.08)
print("Total cost:", total)
```

### Data Types & Variables
Automatic type detection for variables:

```dataline
# String
name = "DataLine"
message = 'Hello World'

# Number
age = 25
price = 19.99
negative = -10

# Boolean
is_valid = true
has_permission = false

# Array
numbers = [1, 2, 3, 4, 5]
mixed = ["text", 123, true]

# Object (from JSON or created)
config = get("config.json")
user = {"name": "John", "age": 30}
```

### Comments
Comments start with # and are ignored by the interpreter:

```dataline
# This is a comment
data = get("file.json") # This is also a comment

# Multi-line comments require # on each line
# This is a multi-line comment
# explaining the data processing logic
```

### Code Style
- Each statement on a new line (no semicolons)
- Code blocks use curly braces `{` and `}`
- Conditions must be enclosed in parentheses `(condition)`
- Case-sensitive language
- Indentation recommended for readability (2 spaces per level)

## Real-World Examples

### Example 1: Data Processing Pipeline
```dataline
# Fetch user data from API
users = get("https://jsonplaceholder.typicode.com/users")

# Process active users
active_users = []
foreach (users as user) {
    if (user["email"] and user["address"]["city"] == "New York") {
        processed_user = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "city": user["address"]["city"]
        }
        active_users.append(processed_user)
        print("Processed:", user["name"])
    }
}

# Save results
send("active_users_nyc.json", active_users)
print("Found", len(active_users), "active users in NYC")
```

### Example 2: Database Analytics
```dataline
# Query user data from database
users = query("sqlite:demo_database.db", "SELECT * FROM users WHERE age > 30")

# Get their orders
foreach (users as user) {
    orders = query("sqlite:demo_database.db", 
                   "SELECT * FROM orders WHERE user_id = " + user["id"])
    
    print("User:", user["name"], "Orders:", len(orders))
    
    # Calculate total spending
    total = 0
    foreach (orders as order) {
        total = total + order["amount"]
    }
    print("Total spent:", total)
}
```

### Example 3: API Integration
```dataline
# Get weather data
weather = get("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m")

# Process temperature data
temps = weather["hourly"]["temperature_2m"]
max_temp = 0
min_temp = 100

foreach (temps as temp) {
    if (temp > max_temp) {
        max_temp = temp
    }
    if (temp < min_temp) {
        min_temp = temp
    }
}

# Create summary
summary = {
    "location": "Berlin",
    "max_temp": max_temp,
    "min_temp": min_temp,
    "data_points": len(temps)
}

# Send to webhook and save locally
send("https://api.example.com/weather", summary)
send("weather_summary.json", summary)
print("Weather analysis complete!")
```

## Running DataLine

### Command Line Options
```bash
# Basic execution
python dataline.py script.datal

# Control logging verbosity
python dataline.py script.datal --level=INFO        # Less verbose
python dataline.py script.datal --level=ERROR       # Only errors
python dataline.py script.datal --level=NONE        # Silent mode

# Generate visualizations
python dataline.py script.datal --generate_code_tree
python dataline.py script.datal --generate_flow_graph

# Combined options
python dataline.py script.datal --level=INFO --generate_code_tree
```

### Log Levels
- **ALL**: Show everything (default)
- **INFO**: Important messages and errors
- **ERROR**: Only error messages  
- **NONE**: Silent execution

### Generated Files
- **history.log**: Detailed execution log with timestamps
- **filename-code_tree.md**: Hierarchical code structure
- **filename-flow_graph.md**: Control flow visualization

## Database Support

### Built-in: SQLite
```dataline
# No setup required - works out of the box!
users = query("sqlite:database.db", "SELECT * FROM users")
```

### Optional Databases (install with pip)
```bash
pip install pymysql psycopg2-binary pymongo redis cassandra-driver elasticsearch
```

```dataline
# MySQL
mysql_data = query("mysql:host=localhost;dbname=test", "SELECT * FROM products")

# PostgreSQL  
postgres_data = query("postgresql:host=localhost;dbname=test", "SELECT * FROM users")

# MongoDB
mongo_data = query("mongodb://localhost:27017/test", "collection.find()")

# Redis
redis_data = query("redis://localhost:6379/0", "GET key")
```

## Debugging Tips

### Check Variable Types
```dataline
data = get("api_response.json")
type(data)  # Shows: dict, list, str, etc.
```

### Use Logging
```bash
# Run with detailed logging
python dataline.py script.datal --level=ALL
```

### Generate Code Trees
```bash
# See your program structure
python dataline.py script.datal --generate_code_tree
```

## Language Reference

### Built-in Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `get()` | Retrieve data from files/APIs | `data = get("api.example.com/data")` |
| `send()` | Save/transmit data | `send("output.json", data)` |
| `query()` | Database operations | `users = query("sqlite:db.db", "SELECT *")` |
| `print()` | Console output | `print("Hello", name)` |
| `type()` | Check variable type | `type(data)` |

### Operators
- **Comparison**: `==`, `!=`, `>`, `<`, `>=`, `<=`
- **Boolean**: `and`, `or`, `not`
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`, `**`

## Contributing

DataLine is open source! We welcome contributions:

1. **Report Issues**: Found a bug? Let us know!
2. **Feature Requests**: Have ideas? We'd love to hear them!
3. **Code Contributions**: See the source code and submit pull requests.

## License

MIT License - feel free to use DataLine in your projects!

## Need Help?

- **Check the examples**: Look at `demo_file.datal` for comprehensive examples
- **Read the logs**: Check `history.log` for detailed execution information
- **Generate visualizations**: Use `--generate_code_tree` to understand program flow

---

**Happy DataLine coding!**

Remember: DataLine is designed to make data processing simple and enjoyable. No complex setup, no dependency management - just clean, readable data pipelines!
