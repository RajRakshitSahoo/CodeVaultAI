"""
CodeVault AI - AI Code Explainer
Rule-based code analysis and explanation engine.
Optionally uses OpenAI API if configured.
"""

import re
import ast
from modules.database_manager import get_setting


# ─────────────────────────────────────────────
#  Rule-based Explainer
# ─────────────────────────────────────────────

KEYWORD_EXPLANATIONS = {
    "def": "Defines a new function. Functions are reusable blocks of code.",
    "class": "Defines a new class – a blueprint for creating objects (OOP).",
    "import": "Imports an external module or library into the current script.",
    "from": "Imports specific items from a module.",
    "return": "Exits the function and optionally passes a value back to the caller.",
    "if": "Starts a conditional block. Code inside runs only when the condition is True.",
    "elif": "Checks another condition if the previous 'if' or 'elif' was False.",
    "else": "Runs when all preceding conditions are False.",
    "for": "Iterates over each item in a sequence (list, string, range, etc.).",
    "while": "Keeps looping as long as the given condition remains True.",
    "break": "Immediately exits the current loop.",
    "continue": "Skips the rest of the current iteration and moves to the next.",
    "try": "Begins an error-handling block. Exceptions inside are caught by 'except'.",
    "except": "Catches exceptions raised in the corresponding 'try' block.",
    "finally": "Runs this block regardless of whether an exception occurred.",
    "with": "Creates a context manager (e.g. for file handling) – auto-closes the resource.",
    "as": "Creates an alias for an import or gives the exception a local name.",
    "lambda": "Creates a small anonymous (one-line) function inline.",
    "yield": "Pauses a generator function and returns a value to the caller.",
    "async": "Marks a function as asynchronous (used with 'await').",
    "await": "Pauses execution until an async operation completes.",
    "pass": "A placeholder that does nothing – useful for empty blocks.",
    "global": "Declares that a variable refers to the module-level (global) scope.",
    "nonlocal": "Declares that a variable refers to an enclosing (non-global) scope.",
    "del": "Deletes a variable or an element from a data structure.",
    "assert": "Tests a condition and raises AssertionError if it is False.",
    "raise": "Manually raises an exception.",
    "in": "Tests membership or iterates over a sequence.",
    "not": "Logical negation operator.",
    "and": "Logical AND – True only when both operands are True.",
    "or": "Logical OR – True when at least one operand is True.",
    "is": "Identity comparison – checks if two variables point to the same object.",
    "None": "Python's null value – represents the absence of a value.",
    "True": "Boolean literal representing truth.",
    "False": "Boolean literal representing falsehood.",
    "print": "Outputs values to the console / standard output.",
    "len": "Returns the number of items in a container (list, string, dict, etc.).",
    "range": "Generates a sequence of integers – commonly used in for-loops.",
    "list": "Creates or converts to a mutable ordered collection.",
    "dict": "Creates or converts to a key-value mapping (dictionary).",
    "set": "Creates an unordered collection of unique values.",
    "tuple": "Creates an immutable ordered collection.",
    "str": "Creates or converts to a string.",
    "int": "Creates or converts to an integer.",
    "float": "Creates or converts to a floating-point number.",
    "bool": "Creates or converts to a boolean (True/False).",
    "open": "Opens a file and returns a file object.",
    "type": "Returns the data type of an object.",
    "isinstance": "Checks whether an object is an instance of a given class or type.",
    "enumerate": "Returns an enumerate object yielding (index, value) pairs.",
    "zip": "Aggregates items from multiple iterables into tuples.",
    "map": "Applies a function to every item of an iterable.",
    "filter": "Filters items in an iterable by a condition.",
    "sorted": "Returns a new sorted list from an iterable.",
    "sum": "Sums up all values in an iterable.",
    "max": "Returns the largest value in an iterable.",
    "min": "Returns the smallest value in an iterable.",
    "abs": "Returns the absolute value of a number.",
    "round": "Rounds a number to a given number of decimal places.",
    "input": "Reads a line from standard input (keyboard) as a string.",
    "super": "Returns a proxy object that delegates method calls to a parent class.",
    "self": "Refers to the current instance of a class inside its methods.",
    "__init__": "The constructor method – called automatically when an object is created.",
    "__str__": "Defines the human-readable string representation of an object.",
    "__repr__": "Defines the developer-facing string representation of an object.",
    "__main__": "Evaluates to True when the script is run directly (not imported).",
}


def _extract_functions(code):
    funcs = re.findall(r"def\s+(\w+)\s*\(([^)]*)\)\s*:", code)
    return funcs


def _extract_classes(code):
    classes = re.findall(r"class\s+(\w+)(?:\(([^)]*)\))?\s*:", code)
    return classes


def _extract_imports(code):
    imports = re.findall(r"^(?:import|from)\s+.+", code, re.MULTILINE)
    return imports


def _extract_variables(code):
    vars_ = re.findall(r"^(\w+)\s*=\s*(.+)", code, re.MULTILINE)
    return [(v, val) for v, val in vars_ if not v.startswith("_") and v.lower() != v.upper()]


def _count_loops(code):
    for_cnt = len(re.findall(r"\bfor\b", code))
    while_cnt = len(re.findall(r"\bwhile\b", code))
    return for_cnt, while_cnt


def _count_conditionals(code):
    return len(re.findall(r"\bif\b", code))


def _detect_language_features(code):
    features = []
    if "async def" in code:
        features.append("Async/Await (asynchronous programming)")
    if re.search(r"\bwith\b", code):
        features.append("Context managers (with statement)")
    if re.search(r"\byield\b", code):
        features.append("Generators (yield keyword)")
    if re.search(r"\blambda\b", code):
        features.append("Lambda functions (anonymous functions)")
    if re.search(r"\btry\b", code):
        features.append("Exception handling (try/except)")
    if re.search(r"\[.+\s+for\s+.+\s+in\s+.+\]", code):
        features.append("List comprehensions")
    if re.search(r"\{.+\s+for\s+.+\s+in\s+.+\}", code):
        features.append("Set/Dict comprehensions")
    if re.search(r"@\w+", code):
        features.append("Decorators")
    return features


def _estimate_complexity(code):
    lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith("#")]
    n = len(lines)
    branches = len(re.findall(r"\b(if|elif|for|while|except|case)\b", code))
    nesting = max((len(l) - len(l.lstrip())) // 4 for l in lines) if lines else 0

    if n < 20 and branches < 5 and nesting < 3:
        level = "Simple"
    elif n < 80 and branches < 15 and nesting < 5:
        level = "Moderate"
    elif n < 200:
        level = "Complex"
    else:
        level = "Very Complex"
    return level, n, branches, nesting


def _readability_score(code):
    lines = code.splitlines()
    total = len(lines)
    if total == 0:
        return 0
    comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
    blank_lines = sum(1 for l in lines if not l.strip())
    docstrings = len(re.findall(r'"""[\s\S]*?"""', code))
    long_lines = sum(1 for l in lines if len(l) > 79)

    score = 100
    if total > 0:
        score -= min(30, long_lines / total * 100)
    if total > 5:
        score += min(15, comment_lines / total * 100)
    score += min(10, docstrings * 5)
    if blank_lines == 0 and total > 10:
        score -= 10
    return max(0, min(100, int(score)))


def explain_code(code, selected_only=False):
    """Return a structured explanation dict for the given code."""
    lines = code.strip().splitlines()
    if not lines:
        return {"error": "No code provided"}

    funcs = _extract_functions(code)
    classes = _extract_classes(code)
    imports = _extract_imports(code)
    variables = _extract_variables(code)
    for_cnt, while_cnt = _count_loops(code)
    cond_cnt = _count_conditionals(code)
    features = _detect_language_features(code)
    complexity, n_lines, branches, max_nest = _estimate_complexity(code)
    readability = _readability_score(code)

    # Build summary
    parts = []
    if classes:
        parts.append(f"{len(classes)} class(es)")
    if funcs:
        parts.append(f"{len(funcs)} function(s)")
    if imports:
        parts.append(f"{len(imports)} import(s)")

    summary = f"This code contains {', '.join(parts) if parts else 'no major structures'}." if parts else "This is a simple script."

    # Function details
    func_details = []
    for fname, params in funcs:
        param_list = [p.strip() for p in params.split(",") if p.strip()]
        fd = {
            "name": fname,
            "params": param_list,
            "param_count": len(param_list),
            "description": f"Function '{fname}' takes {len(param_list)} parameter(s): {', '.join(param_list) if param_list else 'none'}."
        }
        # Try to find docstring
        doc_match = re.search(rf"def\s+{fname}\s*\([^)]*\)\s*:\s*\n\s+\"\"\"(.*?)\"\"\"", code, re.DOTALL)
        if doc_match:
            fd["docstring"] = doc_match.group(1).strip()
        func_details.append(fd)

    # Class details
    class_details = []
    for cname, bases in classes:
        cd = {
            "name": cname,
            "bases": [b.strip() for b in bases.split(",") if b.strip()],
            "description": f"Class '{cname}'" + (f" inherits from {bases}" if bases else " (no inheritance)")
        }
        class_details.append(cd)

    # Variable details
    var_details = []
    for vname, val in variables[:10]:  # limit
        vtype = "unknown"
        val = val.strip()
        if val.startswith('"') or val.startswith("'") or val.startswith('"""'):
            vtype = "string"
        elif val.replace(".", "").replace("-", "").isdigit():
            vtype = "number"
        elif val.startswith("["):
            vtype = "list"
        elif val.startswith("{"):
            vtype = "dict or set"
        elif val.startswith("("):
            vtype = "tuple"
        elif val.lower() in ("true", "false"):
            vtype = "boolean"
        elif val.lower() == "none":
            vtype = "None"
        var_details.append({"name": vname, "value": val[:40], "type": vtype})

    return {
        "summary": summary,
        "line_count": n_lines,
        "complexity": complexity,
        "readability_score": readability,
        "functions": func_details,
        "classes": class_details,
        "imports": imports,
        "variables": var_details,
        "loops": {"for": for_cnt, "while": while_cnt},
        "conditionals": cond_cnt,
        "features": features,
        "branches": branches,
        "max_nesting": max_nest,
    }


def format_explanation(result):
    """Format the explanation dict into a readable string."""
    if "error" in result:
        return result["error"]

    lines = []
    lines.append("═" * 50)
    lines.append("  📋 CODE ANALYSIS REPORT")
    lines.append("═" * 50)
    lines.append(f"\n📌 SUMMARY\n{result['summary']}")
    lines.append(f"\n📊 METRICS")
    lines.append(f"  Lines of Code  : {result['line_count']}")
    lines.append(f"  Complexity     : {result['complexity']}")
    lines.append(f"  Readability    : {result['readability_score']}/100")
    lines.append(f"  Branches       : {result['branches']}")
    lines.append(f"  Max Nesting    : {result['max_nesting']} level(s)")

    if result["imports"]:
        lines.append(f"\n📦 IMPORTS ({len(result['imports'])})")
        for imp in result["imports"]:
            lines.append(f"  • {imp.strip()}")

    if result["classes"]:
        lines.append(f"\n🏗️  CLASSES ({len(result['classes'])})")
        for c in result["classes"]:
            lines.append(f"  • {c['description']}")

    if result["functions"]:
        lines.append(f"\n⚙️  FUNCTIONS ({len(result['functions'])})")
        for f in result["functions"]:
            lines.append(f"  • {f['description']}")
            if "docstring" in f:
                lines.append(f"    ↳ Doc: {f['docstring'][:80]}")

    if result["variables"]:
        lines.append(f"\n📝 VARIABLES (top {len(result['variables'])})")
        for v in result["variables"]:
            lines.append(f"  • {v['name']} = {v['value']} ({v['type']})")

    loops = result["loops"]
    if loops["for"] or loops["while"]:
        lines.append(f"\n🔄 LOOPS")
        if loops["for"]:
            lines.append(f"  • {loops['for']} for-loop(s)")
        if loops["while"]:
            lines.append(f"  • {loops['while']} while-loop(s)")

    if result["conditionals"]:
        lines.append(f"\n🔀 CONDITIONALS : {result['conditionals']} if-statement(s)")

    if result["features"]:
        lines.append(f"\n✨ ADVANCED FEATURES")
        for feat in result["features"]:
            lines.append(f"  • {feat}")

    lines.append("\n" + "═" * 50)
    return "\n".join(lines)


def explain_keyword(keyword):
    """Return a brief explanation of a Python keyword or built-in."""
    return KEYWORD_EXPLANATIONS.get(keyword, f"'{keyword}' is a user-defined name or identifier.")


# ─────────────────────────────────────────────
#  AI Code Reviewer
# ─────────────────────────────────────────────

def review_code(code):
    """Analyze code quality and return review results."""
    issues = []
    suggestions = []

    lines = code.splitlines()

    # Long lines
    long = [i + 1 for i, l in enumerate(lines) if len(l) > 79]
    if long:
        issues.append(f"Lines exceeding 79 chars (PEP 8): {long[:5]}")
        suggestions.append("Break long lines using parentheses or backslash continuation.")

    # Missing docstrings
    funcs_without_docs = []
    for m in re.finditer(r"def\s+(\w+)\s*\([^)]*\)\s*:\s*\n(\s+)", code):
        fname = m.group(1)
        after = code[m.end():]
        if not after.lstrip().startswith('"""') and not after.lstrip().startswith("'''"):
            funcs_without_docs.append(fname)
    if funcs_without_docs:
        issues.append(f"Functions missing docstrings: {', '.join(funcs_without_docs[:5])}")
        suggestions.append('Add docstrings: """Describe what this function does."""')

    # Magic numbers
    magic = re.findall(r"(?<!\w)(?<!\.)\b([2-9]\d+|[1-9]\d{2,})\b(?!\w)", code)
    if magic:
        issues.append(f"Possible magic numbers found: {', '.join(set(magic[:5]))}")
        suggestions.append("Replace magic numbers with named constants for clarity.")

    # Bare except
    if re.search(r"\bexcept\s*:", code):
        issues.append("Bare 'except:' clause detected – catches all exceptions including system ones.")
        suggestions.append("Use 'except Exception as e:' or a specific exception type.")

    # Single-letter variables (except loop vars)
    singles = re.findall(r"\b([a-zA-Z])\s*=", code)
    bad_singles = [v for v in singles if v not in ("i", "j", "k", "n", "x", "y", "z", "e")]
    if bad_singles:
        issues.append(f"Single-letter variable names (hard to read): {', '.join(set(bad_singles[:5]))}")
        suggestions.append("Use descriptive variable names to improve readability.")

    # Mutable default arguments
    if re.search(r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\})", code):
        issues.append("Mutable default argument (list or dict) found in function signature.")
        suggestions.append("Use None as default and create the mutable object inside the function.")

    # TODO/FIXME comments
    todos = re.findall(r"#.*\b(TODO|FIXME|HACK|XXX)\b.*", code, re.IGNORECASE)
    if todos:
        issues.append(f"{len(todos)} TODO/FIXME comment(s) found.")
        suggestions.append("Resolve outstanding TODO/FIXME items before shipping to production.")

    # Global variables
    globals_ = re.findall(r"^\s*global\s+\w+", code, re.MULTILINE)
    if globals_:
        issues.append(f"{len(globals_)} global variable declaration(s) found.")
        suggestions.append("Minimize use of global state; pass data via parameters and return values.")

    complexity, n_lines, branches, nesting = _estimate_complexity(code)
    readability = _readability_score(code)

    best_practices = [
        "Use type hints for function parameters and return values.",
        "Keep functions short and focused on a single responsibility.",
        "Write unit tests for critical functions.",
        "Follow PEP 8 style guidelines.",
        "Use f-strings instead of % formatting or str.format().",
        "Prefer list/dict comprehensions over explicit loops when readable.",
    ]

    return {
        "issues": issues,
        "suggestions": suggestions,
        "best_practices": best_practices,
        "complexity": complexity,
        "readability_score": readability,
        "line_count": n_lines,
        "issue_count": len(issues),
    }


def format_review(result):
    lines = []
    lines.append("═" * 50)
    lines.append("  🔍 CODE REVIEW REPORT")
    lines.append("═" * 50)
    lines.append(f"\n📊 Complexity    : {result['complexity']}")
    lines.append(f"📖 Readability   : {result['readability_score']}/100")
    lines.append(f"📏 Lines         : {result['line_count']}")
    lines.append(f"⚠️  Issues Found  : {result['issue_count']}")

    if result["issues"]:
        lines.append(f"\n⚠️  ISSUES")
        for issue in result["issues"]:
            lines.append(f"  ✗ {issue}")
    else:
        lines.append("\n✅ No major issues found!")

    if result["suggestions"]:
        lines.append(f"\n💡 SUGGESTIONS")
        for s in result["suggestions"]:
            lines.append(f"  → {s}")

    lines.append(f"\n📚 BEST PRACTICES")
    for bp in result["best_practices"][:4]:
        lines.append(f"  • {bp}")

    lines.append("\n" + "═" * 50)
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  OpenAI-enhanced explanation (optional)
# ─────────────────────────────────────────────

def try_openai_explain(code, api_key):
    """Try to get an AI explanation via OpenAI. Returns None on failure."""
    try:
        import urllib.request
        import json

        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "max_tokens": 500,
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant. Explain code clearly and concisely."},
                {"role": "user", "content": f"Explain this code in simple terms:\n\n```python\n{code[:2000]}\n```"}
            ]
        }).encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None
