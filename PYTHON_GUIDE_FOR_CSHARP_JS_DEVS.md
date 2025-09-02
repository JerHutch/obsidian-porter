# Python Guide for C# and JavaScript Developers

This guide helps C# and JavaScript developers understand Python language features and patterns used in this SimpleNote to Obsidian importer codebase.

## Language Feature Mappings

### Classes and Objects

**Python:**
```python
class MetadataParser:
    def __init__(self, config):  # Constructor
        self.config = config     # Instance variable (like C# field)
    
    def parse_json(self, json_path):  # Instance method
        return {"data": "value"}
```

**C# Equivalent:**
```csharp
public class MetadataParser
{
    private Config config;       // Field
    
    public MetadataParser(Config config)  // Constructor
    {
        this.config = config;
    }
    
    public Dictionary<string, object> ParseJson(string jsonPath)  // Method
    {
        return new Dictionary<string, object> { {"data", "value"} };
    }
}
```

**JavaScript Equivalent:**
```javascript
class MetadataParser {
    constructor(config) {
        this.config = config;    // Instance property
    }
    
    parseJson(jsonPath) {        // Method
        return {"data": "value"};
    }
}
```

### Properties and Data Access

**Python (using @property decorator):**
```python
class ImportConfig:
    def __init__(self):
        self._auto_tag = True    # Private-ish (convention only)
    
    @property
    def auto_tag(self):          # Getter
        return self._auto_tag
    
    @auto_tag.setter
    def auto_tag(self, value):   # Setter
        self._auto_tag = value
```

**C# Equivalent:**
```csharp
public class ImportConfig
{
    private bool _autoTag = true;
    
    public bool AutoTag
    {
        get { return _autoTag; }
        set { _autoTag = value; }
    }
}
```

### Dictionary Access and Operations

**Python:**
```python
# Dictionary creation
config = {"auto_tag": True, "folders": ["inbox", "archive"]}

# Access with default
enabled = config.get("auto_tag", False)  # Returns False if key missing

# Safe access pattern
if "auto_tag" in config:
    enabled = config["auto_tag"]

# Dictionary comprehension (like LINQ)
tagged_notes = {k: v for k, v in notes.items() if v.get("tags")}
```

**C# Equivalent:**
```csharp
// Dictionary creation
var config = new Dictionary<string, object>
{
    {"auto_tag", true},
    {"folders", new[] {"inbox", "archive"}}
};

// Access with default
bool enabled = config.ContainsKey("auto_tag") ? (bool)config["auto_tag"] : false;

// Safe access pattern
if (config.ContainsKey("auto_tag"))
{
    enabled = (bool)config["auto_tag"];
}

// LINQ equivalent
var taggedNotes = notes.Where(kv => ((dynamic)kv.Value).tags != null)
                      .ToDictionary(kv => kv.Key, kv => kv.Value);
```

**JavaScript Equivalent:**
```javascript
// Object creation
const config = {"auto_tag": true, "folders": ["inbox", "archive"]};

// Access with default (modern)
const enabled = config.auto_tag ?? false;

// Safe access pattern
if ("auto_tag" in config) {
    enabled = config.auto_tag;
}

// Filter and transform
const taggedNotes = Object.fromEntries(
    Object.entries(notes).filter(([k, v]) => v.tags)
);
```

### List/Array Operations

**Python:**
```python
# List creation and operations
tags = ["work", "important", "project"]
tags.append("urgent")           # Add item
tags.extend(["meeting", "todo"]) # Add multiple items
tags.remove("work")             # Remove specific item
filtered = [tag for tag in tags if len(tag) > 4]  # List comprehension

# Slicing
first_three = tags[:3]          # First 3 items
last_two = tags[-2:]            # Last 2 items
```

**C# Equivalent:**
```csharp
// List creation and operations
var tags = new List<string> {"work", "important", "project"};
tags.Add("urgent");                    // Add item
tags.AddRange(new[] {"meeting", "todo"}); // Add multiple
tags.Remove("work");                   // Remove specific item
var filtered = tags.Where(tag => tag.Length > 4).ToList(); // LINQ

// Slicing equivalent
var firstThree = tags.Take(3).ToList();
var lastTwo = tags.Skip(Math.Max(0, tags.Count - 2)).ToList();
```

### String Operations

**Python:**
```python
# String formatting (multiple ways)
name = "SimpleNote"
count = 42

# f-strings (preferred, like C# interpolation)
message = f"Processing {count} notes from {name}"

# format method
message = "Processing {} notes from {}".format(count, name)

# String methods
filename = "  My Note Title  "
clean = filename.strip()           # Remove whitespace
safe = filename.replace(" ", "_")  # Replace characters
parts = "tag1,tag2,tag3".split(",") # Split string
```

**C# Equivalent:**
```csharp
// String interpolation
string name = "SimpleNote";
int count = 42;
string message = $"Processing {count} notes from {name}";

// String methods
string filename = "  My Note Title  ";
string clean = filename.Trim();
string safe = filename.Replace(" ", "_");
string[] parts = "tag1,tag2,tag3".Split(',');
```

### File and Path Operations

**Python:**
```python
from pathlib import Path
import os

# Path operations (modern Python way)
path = Path("data/source/notes.json")
parent = path.parent               # Get directory
name = path.name                   # Get filename
stem = path.stem                   # Filename without extension
exists = path.exists()             # Check if exists

# File operations
with open(path, 'r', encoding='utf-8') as file:
    content = file.read()          # Auto-closes file

# Directory operations
path.mkdir(parents=True, exist_ok=True)  # Create directory
```

**C# Equivalent:**
```csharp
using System.IO;

// Path operations
string path = Path.Combine("data", "source", "notes.json");
string parent = Path.GetDirectoryName(path);
string name = Path.GetFileName(path);
string stem = Path.GetFileNameWithoutExtension(path);
bool exists = File.Exists(path);

// File operations
using (var reader = new StreamReader(path, Encoding.UTF8))
{
    string content = reader.ReadToEnd();
}

// Directory operations
Directory.CreateDirectory(Path.GetDirectoryName(path));
```

## Python-Specific Gotchas for C#/JS Developers

### 1. Indentation is Syntax
**Python:** Indentation defines code blocks (no braces)
```python
if condition:
    do_something()    # 4 spaces indentation
    do_another()
else:
    do_different()
```

**C#/JS:** Braces define blocks
```csharp
if (condition) {
    DoSomething();
    DoAnother();
} else {
    DoDifferent();
}
```

### 2. No True Private Members
**Python:**
```python
class Example:
    def __init__(self):
        self.public = "anyone can access"
        self._protected = "convention: internal use"  # Still accessible!
        self.__private = "name mangling, harder to access"  # Still not truly private
```

**C#:** Has true access modifiers (`private`, `protected`, `public`)

### 3. Dynamic Typing vs Static
**Python:**
```python
# Variable can change type
value = "string"
value = 42          # Now it's an integer
value = [1, 2, 3]   # Now it's a list
```

**C#:** Static typing prevents this
**JavaScript:** Similar dynamic behavior

### 4. None vs null/undefined
**Python:**
```python
result = None                    # Python's null equivalent
if result is None:               # Use 'is' for None comparison
    handle_empty_case()

# Default parameter values
def process_note(content, tags=None):
    if tags is None:
        tags = []                # Don't use [] as default!
```

**C# equivalent:** `null`
**JS equivalent:** `null` or `undefined`

### 5. List/Dict Comprehensions
**Python:**
```python
# List comprehension - very common pattern
numbers = [1, 2, 3, 4, 5]
squares = [n * n for n in numbers if n % 2 == 0]  # [4, 16]

# Dict comprehension
word_lengths = {word: len(word) for word in ["hello", "world"]}
```

**C# LINQ equivalent:**
```csharp
var numbers = new[] {1, 2, 3, 4, 5};
var squares = numbers.Where(n => n % 2 == 0).Select(n => n * n).ToList();
```

### 6. Multiple Assignment and Tuple Unpacking
**Python:**
```python
# Multiple assignment
x, y = 10, 20
x, y = y, x          # Swap values

# Tuple unpacking
point = (3, 4)
x, y = point

# Function returning multiple values
def get_name_age():
    return "John", 25

name, age = get_name_age()
```

**C#:** Requires tuples or out parameters
```csharp
// C# 7+ tuples
(string name, int age) = GetNameAge();

// Traditional out parameters
int age;
string name = GetNameAge(out age);
```

### 7. Exception Handling
**Python:**
```python
try:
    risky_operation()
except FileNotFoundError as e:    # Specific exception type
    handle_missing_file(e)
except Exception as e:            # Catch-all
    handle_any_error(e)
finally:                          # Always runs
    cleanup()
```

**C# Equivalent:**
```csharp
try
{
    RiskyOperation();
}
catch (FileNotFoundException e)    // Specific exception
{
    HandleMissingFile(e);
}
catch (Exception e)                // Catch-all
{
    HandleAnyError(e);
}
finally                            // Always runs
{
    Cleanup();
}
```

### 8. Import System
**Python:**
```python
# Import entire module
import os
os.path.join("a", "b")

# Import specific items
from pathlib import Path
Path("myfile.txt")

# Import with alias
import simplenote_importer as importer
```

**C# Equivalent:**
```csharp
using System.IO;          // Import namespace
using Path = System.IO.Path;  // Alias

Path.Combine("a", "b");
```

### 9. Context Managers (with statement)
**Python:**
```python
# Automatic resource management
with open("file.txt", "r") as file:
    content = file.read()
# File automatically closed here

# Custom context manager
with timer() as t:
    do_expensive_operation()
    print(f"Took {t.elapsed} seconds")
```

**C# Equivalent:**
```csharp
// using statement
using (var file = new StreamReader("file.txt"))
{
    string content = file.ReadToEnd();
} // Automatically disposed

// Custom using
using (var timer = new Timer())
{
    DoExpensiveOperation();
    Console.WriteLine($"Took {timer.Elapsed} seconds");
}
```

## Common Patterns in This Codebase

### 1. Configuration Injection
```python
class MetadataParser:
    def __init__(self, config: ImportConfig):
        self.config = config
```
Similar to C# dependency injection.

### 2. Factory Methods
```python
@classmethod
def from_file(cls, file_path):
    return cls(load_config(file_path))
```
Like C# static factory methods.

### 3. Type Hints (Optional but Recommended)
```python
def process_notes(notes: List[Dict[str, Any]]) -> Dict[str, str]:
    return {"result": "success"}
```
Similar to C# method signatures.

### 4. Dataclasses (Python 3.7+)
```python
from dataclasses import dataclass

@dataclass
class NoteMetadata:
    title: str
    created: datetime
    tags: List[str]
```
Similar to C# records or plain data classes.

This guide covers the key concepts you'll encounter in the codebase. Python's philosophy emphasizes readability and simplicity, so most patterns should feel familiar once you understand these core differences.