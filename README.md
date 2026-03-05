# DataLine Programming Language

Data pipelines oriented programming language. The purpose of it is to make data pipeline creation easier and more maintainable for data scientists, by removing complexity and making code creation more deterministic. It runs python on the backend, which is why it's lightweight and easy to modify. Another strong point is that it doesn't depend on external dependencies - it only uses python's embedded functionalities.

## Key Characteristics
- Case-sensitive
- Comprehensive log file (history.log)
- Automatic code tree generation (code_tree.md)
- Automatic flow graph (flow_graph.md)
- Separated by new lines (no ; at the end of each line)

## Commands

## get

Get data from file or API. Supports both local files and HTTP endpoints. Automatically parses JSON files and returns parsed objects, otherwise returns raw text content.

**Parameters:**
- source (string, required) - Path to local file or HTTP URL
- headers (object, optional) - Custom headers for HTTP requests only

**Examples:**
```dataline
# Get data from local JSON file (automatically parsed)
data = get("data.json")

# Get data from local text file (returns as string)
content = get("data.csv")

# Get data from API endpoint (automatically parses JSON response)
api_data = get("https://jsonplaceholder.typicode.com/posts")

# Get data from API with custom headers
users = get("https://api.example.com/users", headers={"Authorization": "Bearer token123"})

# Get data from API with multiple custom headers
data = get("https://api.github.com/user", headers={
    "Authorization": "Bearer ghp_xxx",
    "User-Agent": "DataLine-App",
    "Accept": "application/vnd.github.v3+json"
})

# Get data from API with query parameters
users = get("https://api.example.com/users?page=1&limit=10")
```

**Return Values:**
- JSON files: Parsed Python dictionary/object
- Text files: String content
- HTTP responses: Parsed JSON (if Content-Type is application/json) or raw text
- Error handling: Returns `None` and logs error if request fails

## send

Send data to API endpoint or file. Supports HTTP requests with custom headers and file writing in various formats.

**Parameters:**
- destination (string, required) - File path or HTTP URL
- data (any, required) - Data to send
- payload (any, optional) - Custom payload for HTTP requests (defaults to data)
- headers (object, optional) - Custom headers for HTTP requests

**Examples:**
```dataline
# Send data to local JSON file (automatically formatted)
send("output.json", processed_data)

# Send data to local text file
send("report.txt", "Data processing complete")

# Send data to API endpoint (POST request)
send("https://api.example.com/data", results)

# Send data to API with custom headers
send("https://api.example.com/webhook", event_data, headers={"Authorization": "Bearer token123"})

# Send custom payload different from data
send("https://api.example.com/submit", metadata, payload={"data": actual_data, "meta": metadata})
```

**Return Values:**
- File operations: `True` on success
- HTTP requests: HTTP status code (e.g., 200, 201)
- Error handling: Returns `None` and logs error if request fails

## print

Output data to console. Can handle multiple arguments and various data types.

**Parameters:**
- ... (any, variadic) - Values to print

**Examples:**
```dataline
# Print single value
print("Hello World")

# Print multiple values
print("User:", name, "Age:", age)

# Print variables
print(data)

# Print expressions
print("Total items:", count * 2)
```

## type

Display the type of a variable. Useful for debugging and data validation.

**Parameters:**
- variable (any, required) - Variable to inspect

**Examples:**
```dataline
# Check type of variable
type(data)  # Output: dict, list, str, int, bool, etc.

# Type checking in conditions
data = get("config.json")
if (type(data) == "dict") {
    print("Data is a dictionary")
}

# Debug variable types
user = {"name": "John", "age": 30}
type(user)  # Output: dict

numbers = [1, 2, 3]
type(numbers)  # Output: list
```

## if / else / else if

Conditional statements for program flow control. Conditions must be enclosed in parentheses and support boolean logic.

**Syntax:**
```dataline
if (condition) {
    # code block
} else if (condition) {
    # code block  
} else {
    # code block
}
```

**Examples:**
```dataline
# Simple condition
if (x > 10) {
    print("x is greater than 10")
}

# Complex condition with boolean logic
if (age >= 18 and has_license == true) {
    print("Can drive")
} else if (age >= 16 and has_permit == true) {
    print("Can drive with supervision")
} else {
    print("Cannot drive")
}

# Nested conditions
if (user_type == "admin") {
    if (permissions["write"] == true) {
        print("Admin with write access")
    }
}

# Type checking
data = get("api_response.json")
if (type(data) == "dict" and data["success"] == true) {
    print("API call successful")
}
```

**Supported Operators:**
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Boolean: `and`, `or`, `not`
- Boolean values: `true`, `false`

### foreach

Loop through arrays or objects. Supports both simple iteration and key-value iteration for dictionaries.

**Syntax:**
```dataline
# Simple iteration
foreach (collection as item) {
    # code block
}

# Key-value iteration (for objects/dictionaries)
foreach (object as key => value) {
    # code block
}
```

**Examples:**
```dataline
# Iterate over array
numbers = [1, 2, 3, 4, 5]
foreach (numbers as num) {
    print("Number:", num)
}

# Iterate over dictionary keys and values
user = {"name": "John", "age": 30, "city": "NYC"}
foreach (user as key => value) {
    print(key, ":", value)
}

# Process API response data
data = get("https://api.example.com/users")
foreach (data as user) {
    print("User:", user["name"], "Email:", user["email"])
}

# Nested iteration
results = get("analytics.json")
foreach (results as category) {
    print("Category:", category["name"])
    foreach (category["items"] as item) {
        print("  -", item["title"])
    }
}

# Transform data during iteration
processed = []
foreach (raw_data as entry) {
    new_entry = {
        "id": entry["id"],
        "processed": true,
        "timestamp": get_current_time()
    }
    processed.append(new_entry)
}
```

## Variable Assignment

Automatic type detection for variables:
- String: `name = "DataLine"`
- Number: `age = 25`
- Boolean: `active = true`
- Array: `items = [1, 2, 3]`
- Object: Via get() function or JSON parsing

**Examples:**
```dataline
# String assignment
name = "John Doe"
message = 'Hello World'

# Number assignment
count = 42
price = 19.99
negative = -10

# Boolean assignment
is_valid = true
has_permission = false

# Array assignment
numbers = [1, 2, 3, 4, 5]
mixed = ["text", 123, true]

# Object assignment via get()
config = get("config.json")

# Complex nested structures
user_profile = {
    "name": "John",
    "age": 30,
    "preferences": {
        "theme": "dark",
        "notifications": true
    }
}
```

## Comments

Comments start with # and are ignored by the interpreter:
```dataline
# This is a comment
data = get("file.json") # This is also a comment

# Multi-line comments require # on each line
# This is a multi-line comment
# explaining the data processing logic
```

## Code Structure

- Each statement on a new line (no semicolons)
- Code blocks use curly braces `{` and `}`
- Conditions must be enclosed in parentheses `(condition)`
- Case-sensitive language
- Indentation recommended for readability (2 spaces per level)

## Complete Examples

### Example 1: Data Processing Pipeline
```dataline
# Fetch user data from API with authentication
users = get("https://jsonplaceholder.typicode.com/users", headers={"User-Agent": "DataLine-App"})

# Fetch data from authenticated API
api_data = get("https://api.github.com/repos/dataline/lang", headers={
    "Authorization": "Bearer your_token_here",
    "Accept": "application/vnd.github.v3+json"
})

# Process each user
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
        print("Processed user:", user["name"])
    }
}

# Save results
send("active_users_nyc.json", active_users)
print("Total active NYC users:", len(active_users))
```

### Example 2: File Processing with Error Handling
```dataline
# Load configuration
config = get("config.json")
if (config == null) {
    print("Error: Could not load configuration")
} else {
    # Process data files
    foreach (config["files"] as filename) {
        data = get(filename)
        if (type(data) == "dict") {
            print("Processing:", filename)
            # Transform data
            transformed = {
                "source": filename,
                "record_count": len(data),
                "processed_at": "2024-01-01"
            }
            send("results.json", transformed)
        } else {
            print("Invalid data format in:", filename)
        }
    }
}
```

### Example 3: API Integration and Reporting
```dataline
# Fetch sales data with authentication
sales_data = get("https://api.company.com/sales", headers={"Authorization": "Bearer token123"})
products = get("products.json")

# Generate report
report = {
    "total_sales": 0,
    "top_products": [],
    "date_range": "2024-01-01 to 2024-12-31"
}

foreach (sales_data as sale) {
    report["total_sales"] = report["total_sales"] + sale["amount"]
    
    # Find product details
    foreach (products as product) {
        if (product["id"] == sale["product_id"]) {
            sale["product_name"] = product["name"]
            break
        }
    }
}

# Sort and get top 5 products
if (len(sales_data) > 0) {
    # Simple sorting logic (would need extension for complex sorting)
    foreach (sales_data as sale) {
        if (sale["amount"] > 1000) {
            report["top_products"].append({
                "product": sale["product_name"],
                "amount": sale["amount"]
            })
        }
    }
}

# Send report to dashboard
send("dashboard.company.com/reports", report)
send("sales_report_2024.json", report)
print("Report generated successfully")
```

### Example 4: Data Validation and Cleaning
```dataline
# Load raw data
raw_data = get("user_submissions.json")
clean_data = []
errors = []

foreach (raw_data as submission) {
    # Validate required fields
    if (submission["email"] and submission["name"]) {
        # Clean and normalize data
        clean_entry = {
            "name": submission["name"].strip(),
            "email": submission["email"].lower().strip(),
            "age": submission["age"] or 0,
            "valid": true
        }
        
        # Additional validation
        if (clean_entry["age"] >= 18 and clean_entry["age"] <= 120) {
            clean_data.append(clean_entry)
        } else {
            errors.append({
                "type": "invalid_age",
                "data": clean_entry
            })
        }
    } else {
        errors.append({
            "type": "missing_fields",
            "data": submission
        })
    }
}

# Save results
send("clean_users.json", clean_data)
send("validation_errors.json", errors)
print("Cleaned", len(clean_data), "valid entries")
print("Found", len(errors), "validation errors")
```

## Running the Interpreter

Execute DataLine files from the command line:

```bash
# Basic execution
python dataline.py script.datal

# With log level
python dataline.py script.datal --level=INFO

# Generate code tree and flow graph
python dataline.py script.datal --generate_code_tree --generate_flow_graph

# Silent mode (no logging)
python dataline.py script.datal --level=NONE
```

## Log Levels

- **ALL**: Show all log messages (default)
- **INFO**: Show only informational messages and errors
- **ERROR**: Show only error messages
- **NONE**: Disable all logging output

## Generated Files

- **history.log**: Comprehensive execution log with timestamps
- **filename-code_tree.md**: Hierarchical code structure visualization
- **filename-flow_graph.md**: Control flow graph in Mermaid format
