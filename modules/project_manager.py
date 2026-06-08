"""
CodeVault AI - Project Manager
File-system and database operations for projects.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path
from datetime import datetime
from modules import database_manager as db

# Base projects directory – sits alongside CodeVaultAI folder
BASE_DIR = Path(__file__).parent.parent / "projects"


def _ensure_base():
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def create_project(name, language="Python", description=""):
    """Create a project folder and register it in the DB."""
    _ensure_base()
    safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    if not safe_name:
        return False, "Invalid project name"
    project_path = BASE_DIR / safe_name
    if project_path.exists():
        return False, "Project folder already exists"
    project_path.mkdir(parents=True)

    # Create starter file
    ext = _default_ext(language)
    starter = project_path / f"main{ext}"
    starter.write_text(_starter_code(language, name), encoding="utf-8")

    ok, msg = db.create_project(name, str(project_path), language, description)
    if ok:
        # Register the starter file
        projects = db.get_all_projects()
        for p in projects:
            if p["name"] == name:
                db.save_file_record(p["id"], starter.name, str(starter), language,
                                    _starter_code(language, name))
                break
    return ok, msg


def open_project(project_id):
    """Return project info dict (for loading into the editor)."""
    project = db.get_project(project_id)
    if not project:
        return None, "Project not found"
    path = Path(project["path"])
    if not path.exists():
        return None, f"Project folder missing: {path}"
    db.touch_project(project_id)
    files = _scan_files(path, project_id)
    return {**project, "files": files}, "OK"


def _scan_files(path, project_id):
    """Scan folder and sync files to DB. Return list of file info dicts."""
    result = []
    for fpath in sorted(path.iterdir()):
        if fpath.is_file() and not fpath.name.startswith("."):
            lang = _detect_language(fpath.suffix)
            content = ""
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
            db.save_file_record(project_id, fpath.name, str(fpath), lang, content)
            result.append({"name": fpath.name, "path": str(fpath), "language": lang})
    return result


def delete_project(project_id):
    project = db.get_project(project_id)
    if not project:
        return False, "Project not found"
    try:
        shutil.rmtree(project["path"], ignore_errors=True)
    except Exception as e:
        return False, str(e)
    db.delete_project(project_id)
    return True, "Project deleted"


def rename_project(project_id, new_name):
    project = db.get_project(project_id)
    if not project:
        return False, "Project not found"
    old_path = Path(project["path"])
    new_path = old_path.parent / new_name
    if new_path.exists():
        return False, "A folder with that name already exists"
    old_path.rename(new_path)
    db.update_project(project_id, name=new_name)
    conn = __import__("sqlite3").connect(str(db.DB_PATH))
    conn.execute("UPDATE projects SET path=? WHERE id=?", (str(new_path), project_id))
    conn.commit()
    conn.close()
    return True, "Project renamed"


def create_file_in_project(project_id, file_name, language="Python"):
    project = db.get_project(project_id)
    if not project:
        return None, "Project not found"
    path = Path(project["path"]) / file_name
    if path.exists():
        return None, "File already exists"
    content = _starter_code(language, file_name)
    path.write_text(content, encoding="utf-8")
    db.save_file_record(project_id, file_name, str(path), language, content)
    return str(path), "File created"


def delete_file_from_project(file_path):
    try:
        Path(file_path).unlink(missing_ok=True)
        return True, "File deleted"
    except Exception as e:
        return False, str(e)


def export_project_zip(project_id, dest_dir):
    project = db.get_project(project_id)
    if not project:
        return None, "Project not found"
    project_path = Path(project["path"])
    zip_name = f"{project['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = Path(dest_dir) / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in project_path.rglob("*"):
            if fpath.is_file():
                zf.write(fpath, fpath.relative_to(project_path.parent))
    return str(zip_path), "Exported successfully"


def backup_database(dest_dir):
    src = db.DB_PATH
    backup_name = f"codevault_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    dest = Path(dest_dir) / backup_name
    shutil.copy2(str(src), str(dest))
    return str(dest)


# ─── helpers ────────────────────────────────

def _default_ext(language):
    return {
        "Python": ".py", "JavaScript": ".js", "Java": ".java",
        "HTML": ".html", "CSS": ".css", "C": ".c", "C++": ".cpp"
    }.get(language, ".txt")


def _detect_language(suffix):
    return {
        ".py": "Python", ".js": "JavaScript", ".java": "Java",
        ".html": "HTML", ".htm": "HTML", ".css": "CSS",
        ".c": "C", ".cpp": "C++", ".h": "C", ".txt": "Text",
        ".md": "Markdown", ".json": "JSON", ".xml": "XML",
    }.get(suffix.lower(), "Text")


def _starter_code(language, name="main"):
    py_template = ('"""\n' + name + '\nCreated with CodeVault AI\n"""\n\n'
                   'def main():\n    print("Hello from ' + name + '!")\n\n'
                   'if __name__ == "__main__":\n    main()\n')
    templates = {
        "Python": py_template,
        "JavaScript": f'// {name} - Created with CodeVault AI\n\nfunction main() {{\n    console.log("Hello from {name}!");\n}}\n\nmain();\n',
        "Java": f'public class Main {{\n    public static void main(String[] args) {{\n        System.out.println("Hello from {name}!");\n    }}\n}}\n',
        "HTML": f'<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <title>{name}</title>\n</head>\n<body>\n    <h1>Hello from {name}!</h1>\n</body>\n</html>\n',
        "CSS": f'/* {name} - Created with CodeVault AI */\n\nbody {{\n    font-family: sans-serif;\n    margin: 0;\n    padding: 0;\n}}\n',
        "C": f'#include <stdio.h>\n\nint main() {{\n    printf("Hello from {name}!\\n");\n    return 0;\n}}\n',
        "C++": f'#include <iostream>\nusing namespace std;\n\nint main() {{\n    cout << "Hello from {name}!" << endl;\n    return 0;\n}}\n',
    }
    return templates.get(language, f"// {name}\n")
