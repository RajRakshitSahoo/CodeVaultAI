# CodeVault AI 🚀

**Professional Python Coding Workspace** — A lightweight VS Code-inspired desktop IDE built entirely in Python using Tkinter and SQLite.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗂️ **Project Manager** | Create, open, rename, delete projects. File explorer with context menus. |
| 📝 **Multi-tab Editor** | Syntax highlighting (Pygments), line numbers, auto-indent, undo/redo, zoom |
| ▶️ **Code Runner** | Run Python (+ JS/Java/C/C++) with live output, stop button, execution time |
| 🧠 **AI Explainer** | Explains functions, classes, loops, imports — rule-based (no API needed) |
| 🔍 **Code Reviewer** | Complexity score, readability, PEP 8 issues, naming suggestions |
| 🐛 **Error Analyzer** | Parses runtime errors, shows causes, fixes, and code examples |
| 📌 **Snippet Vault** | Save, search, insert, and manage reusable code snippets (12 built-ins included) |
| 🔎 **Global Search** | Search across all project files and snippets instantly |
| 📊 **Statistics** | Dashboard with charts (requires matplotlib) for projects, files, executions |
| ⚙️ **Settings** | Font, font size, auto-save, tab size, OpenAI key, username |
| 💾 **Find & Replace** | Global find and replace with case-sensitivity option |

---

## 🚀 Quick Start (Windows)

### Option A — Double-click launcher (easiest)
```
Double-click launch.bat
```
This auto-installs dependencies and starts the app.

### Option B — PowerShell setup (first time)
```powershell
Right-click setup.ps1 → "Run with PowerShell"
```

### Option C — VS Code
1. Open the `CodeVaultAI` folder in VS Code
2. Open terminal (`Ctrl+\``)
3. Run:
```bash
pip install pygments matplotlib
python main.py
```
Or press **F5** (uses `.vscode/launch.json`)

### Option D — Manual
```bash
cd CodeVaultAI
pip install -r requirements.txt
python main.py
```

---

## 📁 Project Structure

```
CodeVaultAI/
│
├── main.py                    ← Main application (GUI)
├── requirements.txt           ← Python dependencies
├── launch.bat                 ← Windows one-click launcher
├── setup.ps1                  ← PowerShell first-time setup
├── CodeVaultAI.code-workspace ← VS Code workspace
│
├── modules/
│   ├── __init__.py
│   ├── database_manager.py    ← SQLite CRUD (projects, files, snippets, history)
│   ├── project_manager.py     ← File-system project operations
│   ├── snippet_manager.py     ← Snippet CRUD + 12 built-in snippets
│   ├── code_runner.py         ← Subprocess execution engine
│   ├── ai_explainer.py        ← Rule-based + optional OpenAI explainer/reviewer
│   └── error_analyzer.py      ← Error parsing + fix database (16 error types)
│
├── database/                  ← SQLite database (auto-created)
├── projects/                  ← Your projects live here
├── snippets/                  ← (reserved)
├── backups/                   ← Export/backup destination
├── assets/                    ← (reserved for icons)
├── config/                    ← (reserved)
└── .vscode/
    ├── launch.json            ← F5 run config
    └── tasks.json             ← Build tasks
```

---

## 🗄️ Database Tables

| Table | Purpose |
|-------|---------|
| `projects` | Project metadata (name, path, language, description) |
| `files` | File records per project (name, path, content, lines) |
| `snippets` | Reusable code snippets |
| `execution_history` | Code run log (output, errors, duration, status) |
| `settings` | App preferences (key-value store) |
| `users` | User profile |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save current file |
| `Ctrl+W` | Close current tab |
| `Ctrl+F` | Find & Replace |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+A` | Select all |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `F5` | Run code |
| `F6` | Stop execution |
| `Tab` | Indent (4 spaces) |
| `Enter` | Auto-indent |

---

## 🤖 AI Features

### Rule-Based (No API needed)
- Detects functions, classes, imports, variables, loops, conditionals
- Calculates complexity (Simple / Moderate / Complex / Very Complex)
- Readability score (0–100)
- Code review: long lines, missing docstrings, magic numbers, bare excepts, mutable defaults

### OpenAI Enhanced (Optional)
Add your OpenAI API key in **Settings → AI/API → OpenAI API Key**  
Uses `gpt-3.5-turbo` for natural language explanations.

---

## 🐛 Supported Error Types

SyntaxError, IndentationError, NameError, TypeError, ValueError,  
AttributeError, ImportError, ModuleNotFoundError, IndexError, KeyError,  
ZeroDivisionError, FileNotFoundError, RecursionError, MemoryError,  
OverflowError, StopIteration, PermissionError

---

## 📦 Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `pygments` | Syntax highlighting | ✅ Yes |
| `matplotlib` | Statistics charts | ⬜ Optional |
| `openai` | AI-enhanced explanations | ⬜ Optional |

Python stdlib used: `tkinter`, `sqlite3`, `subprocess`, `threading`, `pathlib`, `json`, `re`, `ast`

---

## 💡 Tips

- **Right-click** project/file nodes in Explorer for context menu options
- **Double-click** a snippet to insert it at cursor position
- **Middle-click** a tab to close it
- Run code with **F5**, stop it with **F6**
- Use **AI Tools menu** or toolbar buttons for code analysis
- Statistics window shows language distribution bar chart (needs matplotlib)

---

## 🔧 Troubleshooting

**"No module named pygments"**
```bash
pip install pygments
```

**"No module named tkinter"**  
Tkinter ships with Python on Windows. Re-install Python and check "tcl/tk" option.

**App opens but looks wrong**  
Make sure you're running Python 3.10+:
```bash
python --version
```

**Syntax highlighting not working**  
Install pygments: `pip install pygments`

---

*Built with ❤️ using Python, Tkinter, SQLite, and Pygments*
