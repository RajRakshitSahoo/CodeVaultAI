"""
CodeVault AI - Snippet Manager
"""

from modules import database_manager as db

CATEGORIES = [
    "General", "Data Structures", "Algorithms", "File I/O",
    "Networking", "Database", "GUI", "Web", "Math", "String",
    "Error Handling", "OOP", "Functional", "Testing", "Utilities"
]

LANGUAGES = ["Python", "JavaScript", "Java", "HTML", "CSS", "C", "C++", "SQL", "Bash"]


# ─── CRUD ───────────────────────────────────

def add_snippet(name, category, language, description, code, tags=""):
    return db.save_snippet(name, category, language, description, code, tags)


def get_snippets(search=None):
    if search:
        return db.search_snippets(search)
    return db.get_all_snippets()


def update_snippet(snippet_id, name, category, language, description, code, tags=""):
    db.update_snippet(snippet_id, name, category, language, description, code, tags)
    return True, "Snippet updated"


def delete_snippet(snippet_id):
    db.delete_snippet(snippet_id)
    return True, "Snippet deleted"


def get_snippets_by_category(category):
    all_snips = db.get_all_snippets()
    return [s for s in all_snips if s["category"] == category]


# ─── Built-in starter snippets ──────────────

BUILTIN_SNIPPETS = [
    {
        "name": "Read File",
        "category": "File I/O",
        "language": "Python",
        "description": "Read entire file content safely",
        "code": 'with open("filename.txt", "r", encoding="utf-8") as f:\n    content = f.read()\nprint(content)',
        "tags": "file,read,io"
    },
    {
        "name": "Write File",
        "category": "File I/O",
        "language": "Python",
        "description": "Write text to a file",
        "code": 'with open("output.txt", "w", encoding="utf-8") as f:\n    f.write("Hello, World!")',
        "tags": "file,write,io"
    },
    {
        "name": "List Comprehension",
        "category": "General",
        "language": "Python",
        "description": "Create a filtered/transformed list in one line",
        "code": 'numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\nevens = [n for n in numbers if n % 2 == 0]\nsquares = [n**2 for n in numbers]\nprint(evens)\nprint(squares)',
        "tags": "list,comprehension,functional"
    },
    {
        "name": "Dictionary Default",
        "category": "Data Structures",
        "language": "Python",
        "description": "Use defaultdict for auto-initialised keys",
        "code": 'from collections import defaultdict\n\ncounts = defaultdict(int)\nwords = ["apple", "banana", "apple", "cherry", "banana", "apple"]\nfor word in words:\n    counts[word] += 1\nprint(dict(counts))',
        "tags": "dict,defaultdict,collections"
    },
    {
        "name": "Decorator Template",
        "category": "OOP",
        "language": "Python",
        "description": "Basic function decorator pattern",
        "code": 'import functools\n\ndef my_decorator(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        print(f"Calling {func.__name__}")\n        result = func(*args, **kwargs)\n        print(f"Done: {func.__name__}")\n        return result\n    return wrapper\n\n@my_decorator\ndef greet(name):\n    print(f"Hello, {name}!")\n\ngreet("World")',
        "tags": "decorator,wrapper,functools"
    },
    {
        "name": "Context Manager",
        "category": "OOP",
        "language": "Python",
        "description": "Custom context manager using __enter__/__exit__",
        "code": 'class Timer:\n    import time\n    def __enter__(self):\n        self.start = self.time.time()\n        return self\n\n    def __exit__(self, *args):\n        self.elapsed = self.time.time() - self.start\n        print(f"Elapsed: {self.elapsed:.4f}s")\n\nwith Timer():\n    sum(range(1_000_000))',
        "tags": "context,timer,with"
    },
    {
        "name": "Generator Function",
        "category": "Functional",
        "language": "Python",
        "description": "Infinite generator for memory-efficient iteration",
        "code": 'def fibonacci():\n    a, b = 0, 1\n    while True:\n        yield a\n        a, b = b, a + b\n\nfib = fibonacci()\nfor _ in range(10):\n    print(next(fib), end=" ")',
        "tags": "generator,yield,fibonacci"
    },
    {
        "name": "Try/Except/Finally",
        "category": "Error Handling",
        "language": "Python",
        "description": "Full error handling pattern",
        "code": 'try:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f"Error: {e}")\nexcept Exception as e:\n    print(f"Unexpected error: {e}")\nelse:\n    print(f"Success: {result}")\nfinally:\n    print("This always runs")',
        "tags": "try,except,finally,error"
    },
    {
        "name": "Dataclass",
        "category": "OOP",
        "language": "Python",
        "description": "Python dataclass for clean data models",
        "code": 'from dataclasses import dataclass, field\nfrom typing import List\n\n@dataclass\nclass Student:\n    name: str\n    age: int\n    grades: List[float] = field(default_factory=list)\n\n    @property\n    def average(self):\n        return sum(self.grades) / len(self.grades) if self.grades else 0.0\n\ns = Student("Alice", 20, [85.0, 92.5, 78.0])\nprint(s)\nprint(f"Average: {s.average:.1f}")',
        "tags": "dataclass,oop,typing"
    },
    {
        "name": "SQLite Quick Start",
        "category": "Database",
        "language": "Python",
        "description": "Create table, insert, and query with SQLite",
        "code": 'import sqlite3\n\nconn = sqlite3.connect(":memory:")\ncursor = conn.cursor()\n\ncursor.execute("""CREATE TABLE users (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name TEXT NOT NULL,\n    email TEXT UNIQUE\n)""")\n\ncursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))\nconn.commit()\n\nfor row in cursor.execute("SELECT * FROM users"):\n    print(row)\n\nconn.close()',
        "tags": "sqlite,database,sql"
    },
    {
        "name": "HTTP GET Request",
        "category": "Networking",
        "language": "Python",
        "description": "Simple HTTP GET with urllib (no extra dependencies)",
        "code": 'import urllib.request\nimport json\n\nurl = "https://jsonplaceholder.typicode.com/todos/1"\nwith urllib.request.urlopen(url) as response:\n    data = json.loads(response.read().decode())\nprint(json.dumps(data, indent=2))',
        "tags": "http,get,urllib,networking"
    },
    {
        "name": "Argparse CLI",
        "category": "Utilities",
        "language": "Python",
        "description": "Command-line argument parser template",
        "code": 'import argparse\n\ndef main():\n    parser = argparse.ArgumentParser(description="My CLI tool")\n    parser.add_argument("name", help="Your name")\n    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")\n    parser.add_argument("--count", type=int, default=1, help="Repeat count")\n    args = parser.parse_args()\n\n    for _ in range(args.count):\n        if args.verbose:\n            print(f"Hello, {args.name}! (verbose mode)")\n        else:\n            print(f"Hello, {args.name}!")\n\nif __name__ == "__main__":\n    main()',
        "tags": "argparse,cli,arguments"
    },
]


def seed_builtin_snippets():
    """Add built-in snippets if not already present."""
    existing = db.get_all_snippets()
    existing_names = {s["name"] for s in existing}
    added = 0
    for snip in BUILTIN_SNIPPETS:
        if snip["name"] not in existing_names:
            db.save_snippet(**snip)
            added += 1
    return added
