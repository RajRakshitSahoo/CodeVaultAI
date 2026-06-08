"""
CodeVault AI - Error Analyzer
Analyzes Python runtime/compile errors and provides fixes.
"""

import re
import traceback


ERROR_DATABASE = {
    "SyntaxError": {
        "causes": [
            "Missing colon (:) at end of if/for/while/def/class",
            "Mismatched parentheses, brackets, or braces",
            "Invalid Python syntax",
            "String not properly closed (missing quote)",
            "Incorrect indentation causing parser confusion",
        ],
        "fixes": [
            "Check for missing colons at the end of compound statements",
            "Count opening vs closing brackets/parentheses",
            "Look at the line number indicated in the error message",
            "Ensure strings are properly quoted",
        ],
        "example": 'if x > 0\n    print(x)  # Missing colon after condition',
        "solution": 'if x > 0:\n    print(x)  # Added colon',
    },
    "IndentationError": {
        "causes": [
            "Mixing tabs and spaces",
            "Incorrect indentation level",
            "Code block not properly indented after a colon",
            "Unexpected indent",
        ],
        "fixes": [
            "Use consistent indentation (4 spaces recommended by PEP 8)",
            "Convert all tabs to spaces (most editors can do this automatically)",
            "Check that code inside if/for/while/def/class is indented",
            "Use an IDE that highlights indentation issues",
        ],
        "example": 'def hello():\nprint("Hi")  # Not indented!',
        "solution": 'def hello():\n    print("Hi")  # Properly indented',
    },
    "NameError": {
        "causes": [
            "Variable used before it was defined",
            "Typo in variable or function name",
            "Variable defined in a different scope",
            "Function called before it was defined (in some cases)",
        ],
        "fixes": [
            "Define the variable before using it",
            "Check for typos in the variable name",
            "Ensure the variable is in the correct scope",
            "Import the module that defines the name",
        ],
        "example": 'print(message)  # message not defined yet',
        "solution": 'message = "Hello"\nprint(message)',
    },
    "TypeError": {
        "causes": [
            "Operation applied to wrong data type",
            "Calling a non-callable object",
            "Wrong number of arguments passed to a function",
            "Mixing incompatible types (e.g. str + int)",
        ],
        "fixes": [
            "Check the types of your variables using type()",
            "Convert types explicitly: str(), int(), float(), list()",
            "Verify function signatures and pass correct number of arguments",
            "Use isinstance() to check types before operations",
        ],
        "example": 'result = "Age: " + 25  # Cannot concatenate str and int',
        "solution": 'result = "Age: " + str(25)  # Convert int to str first',
    },
    "ValueError": {
        "causes": [
            "Function received right type but wrong value",
            "Converting invalid string to number (e.g. int('abc'))",
            "Unpacking wrong number of values",
            "Invalid value for a built-in operation",
        ],
        "fixes": [
            "Validate input data before passing to functions",
            "Use try/except to handle conversion errors",
            "Check that sequences have the expected number of elements",
            "Use conditional checks before risky operations",
        ],
        "example": 'x = int("hello")  # Cannot convert to int',
        "solution": 'try:\n    x = int(input_str)\nexcept ValueError:\n    x = 0  # Default fallback',
    },
    "AttributeError": {
        "causes": [
            "Accessing an attribute that doesn't exist on an object",
            "Calling a method that doesn't exist",
            "Operating on None (e.g. result of a function that returns None)",
            "Typo in attribute/method name",
        ],
        "fixes": [
            "Use dir(object) to see available attributes/methods",
            "Check if the variable is None before accessing attributes",
            "Verify you're using the correct method name",
            "Check the class definition or documentation",
        ],
        "example": 'my_list = [1, 2, 3]\nmy_list.push(4)  # Lists use append(), not push()',
        "solution": 'my_list = [1, 2, 3]\nmy_list.append(4)  # Correct method name',
    },
    "ImportError": {
        "causes": [
            "Module not installed (needs pip install)",
            "Typo in module name",
            "Module not in Python path",
            "Circular imports",
        ],
        "fixes": [
            "Install missing package: pip install <package-name>",
            "Check spelling of the module name",
            "Verify the module is available for your Python version",
            "Check your virtual environment is activated",
        ],
        "example": 'import numpy  # Not installed',
        "solution": '# Run: pip install numpy\nimport numpy',
    },
    "ModuleNotFoundError": {
        "causes": [
            "Module not installed in current environment",
            "Typo in module name",
            "Wrong Python environment activated",
        ],
        "fixes": [
            "Run: pip install <module-name>",
            "Double-check the module name spelling",
            "Ensure you're using the correct Python/venv environment",
        ],
        "example": 'import pandas  # Not installed',
        "solution": '# Run: pip install pandas\nimport pandas as pd',
    },
    "IndexError": {
        "causes": [
            "Accessing list/tuple index that's out of range",
            "Empty list/sequence",
            "Off-by-one error in loop",
        ],
        "fixes": [
            "Check list length before accessing by index: len(my_list)",
            "Use try/except IndexError to handle edge cases",
            "Use negative indexing carefully (-1 = last element)",
            "Ensure loops don't exceed sequence bounds",
        ],
        "example": 'my_list = [1, 2, 3]\nprint(my_list[5])  # Index 5 out of range',
        "solution": 'my_list = [1, 2, 3]\nif len(my_list) > 5:\n    print(my_list[5])',
    },
    "KeyError": {
        "causes": [
            "Accessing dictionary key that doesn't exist",
            "Typo in key name",
            "Assuming a key exists without checking",
        ],
        "fixes": [
            "Use dict.get(key, default) for safe access",
            "Check with 'key in dict' before accessing",
            "Use dict.setdefault() to provide defaults",
            "Verify the key name spelling",
        ],
        "example": 'person = {"name": "Alice"}\nprint(person["age"])  # Key not found',
        "solution": 'person = {"name": "Alice"}\nprint(person.get("age", "Unknown"))  # Safe access',
    },
    "ZeroDivisionError": {
        "causes": [
            "Dividing a number by zero",
            "Modulo operation with zero divisor",
        ],
        "fixes": [
            "Check divisor is not zero before dividing",
            "Use try/except ZeroDivisionError",
            "Provide a fallback value when denominator is zero",
        ],
        "example": 'result = 10 / 0  # Division by zero',
        "solution": 'divisor = 0\nresult = 10 / divisor if divisor != 0 else float("inf")',
    },
    "FileNotFoundError": {
        "causes": [
            "File path doesn't exist",
            "Wrong directory or relative path",
            "File was deleted or moved",
            "Typo in file name",
        ],
        "fixes": [
            "Verify the file path is correct",
            "Use os.path.exists() before opening",
            "Check current working directory: os.getcwd()",
            "Use pathlib.Path for cross-platform paths",
        ],
        "example": 'with open("data.txt") as f:  # File doesn\'t exist\n    pass',
        "solution": 'import os\nif os.path.exists("data.txt"):\n    with open("data.txt") as f:\n        pass',
    },
    "RecursionError": {
        "causes": [
            "Function calls itself infinitely without a base case",
            "Base case condition never reached",
            "Mutually recursive functions without termination",
        ],
        "fixes": [
            "Ensure every recursive function has a proper base case",
            "Verify the base case is reachable given the input",
            "Consider converting deep recursion to iteration",
            "Increase recursion limit: sys.setrecursionlimit(N) (use carefully)",
        ],
        "example": 'def count(n):\n    return count(n - 1)  # No base case!',
        "solution": 'def count(n):\n    if n <= 0:\n        return 0  # Base case\n    return count(n - 1)',
    },
    "MemoryError": {
        "causes": [
            "Program uses more memory than available",
            "Creating very large data structures",
            "Memory leak in long-running code",
        ],
        "fixes": [
            "Use generators instead of lists for large datasets",
            "Process data in chunks instead of loading all at once",
            "Use del to release unused objects",
            "Use memory-efficient data structures",
        ],
        "example": 'huge_list = list(range(10**9))  # Too much memory',
        "solution": 'huge_gen = range(10**9)  # Generator – memory efficient',
    },
    "OverflowError": {
        "causes": [
            "Floating point number too large",
            "Mathematical operation produces result too large to represent",
        ],
        "fixes": [
            "Use Python's arbitrary-precision integers instead of floats",
            "Use the decimal module for precise large number arithmetic",
            "Check for overflow conditions before performing operations",
        ],
        "example": 'import math\nresult = math.exp(1000)  # Too large for float',
        "solution": 'from decimal import Decimal\nresult = Decimal("2.718") ** 1000',
    },
    "StopIteration": {
        "causes": [
            "Calling next() on an exhausted iterator",
            "Generator function reached end without returning",
        ],
        "fixes": [
            "Use a for loop instead of manual next() calls",
            "Provide a default value: next(iterator, default)",
            "Check if iterator is exhausted before calling next()",
        ],
        "example": 'gen = iter([1, 2])\nnext(gen); next(gen); next(gen)  # Exhausted!',
        "solution": 'gen = iter([1, 2])\nvalue = next(gen, None)  # Returns None if exhausted',
    },
    "PermissionError": {
        "causes": [
            "Insufficient file/directory permissions",
            "Trying to write to a read-only file",
            "Process lacks OS-level permissions",
        ],
        "fixes": [
            "Run the program with appropriate permissions",
            "Check file permissions with os.access()",
            "Choose a writable directory for output files",
        ],
        "example": 'open("/etc/hosts", "w")  # Read-only system file',
        "solution": 'import tempfile\nwith tempfile.NamedTemporaryFile(mode="w") as f:\n    f.write("data")',
    },
}


def parse_error(error_output):
    """Parse a Python error string and return structured info."""
    if not error_output or not error_output.strip():
        return None

    error_type = None
    error_message = ""
    error_line = None
    error_file = None
    traceback_lines = []

    lines = error_output.strip().splitlines()

    # Find error type and message on last line
    last_line = lines[-1].strip() if lines else ""
    m = re.match(r"(\w+(?:Error|Warning|Exception|StopIteration|KeyboardInterrupt|SystemExit))\s*:\s*(.*)", last_line)
    if not m:
        m = re.match(r"(\w+(?:Error|Warning|Exception|StopIteration))(.*)", last_line)
    if m:
        error_type = m.group(1)
        error_message = m.group(2).strip().lstrip(":").strip()

    # Find line number
    for line in lines:
        lm = re.search(r'line (\d+)', line)
        if lm:
            error_line = int(lm.group(1))
        fm = re.search(r'File "([^"]+)"', line)
        if fm:
            error_file = fm.group(1)

    # Collect traceback
    for line in lines:
        if line.strip().startswith(("File ", "  ", "Traceback")):
            traceback_lines.append(line)

    if not error_type:
        return {"raw": error_output, "error_type": "Unknown", "message": error_output, "line": error_line}

    return {
        "error_type": error_type,
        "message": error_message,
        "line": error_line,
        "file": error_file,
        "traceback": "\n".join(traceback_lines),
        "raw": error_output,
    }


def analyze_error(error_output):
    """Full error analysis with causes, fixes, and examples."""
    parsed = parse_error(error_output)
    if not parsed:
        return None

    error_type = parsed.get("error_type", "Unknown")
    db_entry = ERROR_DATABASE.get(error_type, {})

    return {
        "error_type": error_type,
        "message": parsed.get("message", ""),
        "line": parsed.get("line"),
        "file": parsed.get("file"),
        "traceback": parsed.get("traceback", ""),
        "causes": db_entry.get("causes", ["Unknown cause"]),
        "fixes": db_entry.get("fixes", ["Check the error message carefully"]),
        "example": db_entry.get("example", ""),
        "solution": db_entry.get("solution", ""),
        "severity": _get_severity(error_type),
    }


def _get_severity(error_type):
    critical = {"RecursionError", "MemoryError", "SystemExit", "KeyboardInterrupt"}
    high = {"SyntaxError", "IndentationError", "ImportError", "ModuleNotFoundError"}
    medium = {"TypeError", "ValueError", "AttributeError", "NameError"}
    if error_type in critical:
        return "Critical"
    if error_type in high:
        return "High"
    if error_type in medium:
        return "Medium"
    return "Low"


def format_error_analysis(analysis):
    """Format the analysis dict into a readable string."""
    if not analysis:
        return "No error detected or unable to parse error."

    lines = []
    lines.append("═" * 50)
    lines.append("  🚨 ERROR ANALYSIS REPORT")
    lines.append("═" * 50)

    severity_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(analysis.get("severity", "Low"), "⚪")

    lines.append(f"\n{severity_icon} Error Type  : {analysis['error_type']}")
    lines.append(f"   Severity   : {analysis.get('severity', 'Unknown')}")
    if analysis.get("line"):
        lines.append(f"   At Line    : {analysis['line']}")
    if analysis.get("message"):
        lines.append(f"   Message    : {analysis['message']}")

    lines.append(f"\n🔎 POSSIBLE CAUSES")
    for cause in analysis.get("causes", []):
        lines.append(f"  • {cause}")

    lines.append(f"\n🔧 SUGGESTED FIXES")
    for fix in analysis.get("fixes", []):
        lines.append(f"  → {fix}")

    if analysis.get("example"):
        lines.append(f"\n❌ PROBLEMATIC CODE PATTERN")
        for eline in analysis["example"].splitlines():
            lines.append(f"  {eline}")

    if analysis.get("solution"):
        lines.append(f"\n✅ CORRECT PATTERN")
        for sline in analysis["solution"].splitlines():
            lines.append(f"  {sline}")

    lines.append("\n" + "═" * 50)
    return "\n".join(lines)
