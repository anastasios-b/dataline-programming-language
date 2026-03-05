# DataLine Programming Language

Data pipelines oriented programming language. The purpose of it is to make data pipeline creation easier and more maintainable for data scientists, by removing complexity and making code creation more deterministic. It runs python on the backend, which is why it's lightweight and easy to modify. Another strong point is that it doesn't depend on external dependencies - it only uses python's embedded functionalities.

## Key Characteristics
- Case-sensitive
- Comprehensive log file (history.log)
- Automatic code tree generation (code_tree.md)
- Automatic flow graph (flow_graph.md)
- Separated by new lines (no ; at the end of each line)

## Commands

### get

Get data from file or api

**Parameters:**
- source #string #required

**Examples:**
```dataline
get("data.csv")
get("https://api.com/data")
```

### send

Send data to an api or file

**Parameters:**
- destination #string #required
- data #any #required

**Examples:**
```dataline
send("output.json", data)
send("https://api.com/data", data)
```

### if / else / elseif

Conditional statements for program flow control.

**Examples:**
```dataline
if (15 > x and y > 10) {
	...
} else if (x > y) {
	...
} else {
	...
}
```

### type

Prints the type of a variable.

**Parameters:**
- variable #required

**Examples:**
```dataline
type(data)
```

### foreach

Loops through array or json items.

**Parameters:**
- data #array_or_json #required
- single item alias #required

**Examples:**
```dataline
foreach (data as dataEntry) {
	print dataEntry.name
}
```

## Variable Assignment

Automatic type detection for variables:
- String: `name = "DataLine"`
- Number: `age = 25`
- Boolean: `active = true`
- Array: `items = [1, 2, 3]`
- Object: Via get() function or JSON parsing

## Comments

Comments start with # and are ignored by the interpreter:
```dataline
# This is a comment
data = get("file.json") # This is also a comment
```

## Code Structure

- Each statement on a new line (no semicolons)
- Code blocks use curly braces `{` and `}`
- Conditions must be enclosed in parentheses `(condition)`
- Case-sensitive language
