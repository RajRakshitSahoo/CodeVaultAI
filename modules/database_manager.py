"""
CodeVault AI - Database Manager
Handles all SQLite database operations
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).parent.parent / "database" / "codevault.db"


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Create all necessary tables if they don't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL,
            language TEXT DEFAULT 'Python',
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            language TEXT DEFAULT 'Python',
            content TEXT DEFAULT '',
            lines INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            language TEXT DEFAULT 'Python',
            description TEXT DEFAULT '',
            code TEXT NOT NULL,
            tags TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS execution_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            language TEXT,
            code TEXT,
            output TEXT,
            error TEXT,
            duration REAL DEFAULT 0,
            status TEXT DEFAULT 'success',
            executed_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT DEFAULT 'Developer',
            theme TEXT DEFAULT 'dark',
            openai_key TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Insert default settings
    defaults = {
        "theme": "dark",
        "font_size": "13",
        "editor_font": "Consolas",
        "auto_save_interval": "30",
        "tab_size": "4",
        "show_line_numbers": "true",
        "word_wrap": "false",
        "openai_key": "",
        "username": "Developer"
    }
    for key, val in defaults.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val)
        )

    # Ensure at least one user
    cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (1, 'Developer')")
    conn.commit()
    conn.close()


# ---------- Settings ----------

def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
        (key, str(value), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


# ---------- Projects ----------

def create_project(name, path, language="Python", description=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO projects (name, path, language, description) VALUES (?, ?, ?, ?)",
            (name, str(path), language, description)
        )
        conn.commit()
        return True, "Project created successfully"
    except sqlite3.IntegrityError:
        return False, "A project with that name already exists"
    finally:
        conn.close()


def get_all_projects():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM projects ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(project_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_project(project_id, name=None, description=None):
    conn = get_connection()
    if name:
        conn.execute(
            "UPDATE projects SET name=?, updated_at=? WHERE id=?",
            (name, datetime.now().isoformat(), project_id)
        )
    if description is not None:
        conn.execute(
            "UPDATE projects SET description=?, updated_at=? WHERE id=?",
            (description, datetime.now().isoformat(), project_id)
        )
    conn.commit()
    conn.close()


def delete_project(project_id):
    conn = get_connection()
    conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()


def touch_project(project_id):
    conn = get_connection()
    conn.execute(
        "UPDATE projects SET updated_at=? WHERE id=?",
        (datetime.now().isoformat(), project_id)
    )
    conn.commit()
    conn.close()


# ---------- Files ----------

def save_file_record(project_id, name, path, language, content):
    lines = len(content.splitlines())
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM files WHERE path=?", (str(path),)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE files SET content=?, lines=?, updated_at=? WHERE path=?",
            (content, lines, datetime.now().isoformat(), str(path))
        )
    else:
        conn.execute(
            "INSERT INTO files (project_id, name, path, language, content, lines) VALUES (?,?,?,?,?,?)",
            (project_id, name, str(path), language, content, lines)
        )
    conn.commit()
    conn.close()


def get_project_files(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM files WHERE project_id=? ORDER BY name", (project_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_files():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM files ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Snippets ----------

def save_snippet(name, category, language, description, code, tags=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO snippets (name, category, language, description, code, tags) VALUES (?,?,?,?,?,?)",
            (name, category, language, description, code, tags)
        )
        conn.commit()
        return True, "Snippet saved"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_all_snippets():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM snippets ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_snippet(snippet_id, name, category, language, description, code, tags=""):
    conn = get_connection()
    conn.execute(
        """UPDATE snippets SET name=?, category=?, language=?, description=?, code=?, tags=?, updated_at=?
           WHERE id=?""",
        (name, category, language, description, code, tags, datetime.now().isoformat(), snippet_id)
    )
    conn.commit()
    conn.close()


def delete_snippet(snippet_id):
    conn = get_connection()
    conn.execute("DELETE FROM snippets WHERE id=?", (snippet_id,))
    conn.commit()
    conn.close()


def search_snippets(query):
    conn = get_connection()
    q = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM snippets WHERE name LIKE ? OR description LIKE ? OR code LIKE ? OR tags LIKE ?",
        (q, q, q, q)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Execution History ----------

def save_execution(file_name, language, code, output, error, duration, status):
    conn = get_connection()
    conn.execute(
        """INSERT INTO execution_history (file_name, language, code, output, error, duration, status)
           VALUES (?,?,?,?,?,?,?)""",
        (file_name, language, code, output, error, duration, status)
    )
    conn.commit()
    conn.close()


def get_execution_history(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM execution_history ORDER BY executed_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Statistics ----------

def get_statistics():
    conn = get_connection()
    stats = {}
    stats["total_projects"] = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    stats["total_files"] = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    stats["total_snippets"] = conn.execute("SELECT COUNT(*) FROM snippets").fetchone()[0]
    stats["total_executions"] = conn.execute("SELECT COUNT(*) FROM execution_history").fetchone()[0]
    stats["total_lines"] = conn.execute("SELECT COALESCE(SUM(lines),0) FROM files").fetchone()[0]

    lang_row = conn.execute(
        "SELECT language, COUNT(*) as cnt FROM files GROUP BY language ORDER BY cnt DESC LIMIT 1"
    ).fetchone()
    stats["top_language"] = lang_row["language"] if lang_row else "None"

    lang_rows = conn.execute(
        "SELECT language, COUNT(*) as cnt FROM files GROUP BY language ORDER BY cnt DESC"
    ).fetchall()
    stats["language_distribution"] = {r["language"]: r["cnt"] for r in lang_rows}

    exec_rows = conn.execute(
        "SELECT status, COUNT(*) as cnt FROM execution_history GROUP BY status"
    ).fetchall()
    stats["execution_stats"] = {r["status"]: r["cnt"] for r in exec_rows}

    conn.close()
    return stats
