"""
╔══════════════════════════════════════════════════════╗
║            CodeVault AI  –  main.py                 ║
║  Professional Python Coding Workspace (Tkinter)     ║
╚══════════════════════════════════════════════════════╝
"""
 
import sys
import os
import re
import threading
import json
import shutil
import time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, font as tkfont

# ── optional deps ──────────────────────────────────────────────────────────────
try:
    from pygments import lex
    from pygments.lexers import (PythonLexer, JavascriptLexer, JavaLexer,
                                  HtmlLexer, CssLexer, CLexer, CppLexer,
                                  TextLexer)
    from pygments.token import Token
    PYGMENTS_OK = True
except ImportError:
    PYGMENTS_OK = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

# ── internal modules ───────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from modules import database_manager as db
from modules import project_manager as pm
from modules import snippet_manager as sm
from modules import code_runner as cr
from modules import ai_explainer as ai
from modules import error_analyzer as ea


# ══════════════════════════════════════════════════════════════════════════════
#  THEME / PALETTE
# ══════════════════════════════════════════════════════════════════════════════

DARK = {
    "bg":         "#0d1117",
    "bg2":        "#161b22",
    "bg3":        "#21262d",
    "bg4":        "#30363d",
    "border":     "#30363d",
    "accent":     "#58a6ff",
    "accent2":    "#1f6feb",
    "green":      "#3fb950",
    "red":        "#f85149",
    "yellow":     "#d29922",
    "orange":     "#db6d28",
    "purple":     "#bc8cff",
    "cyan":       "#39c5cf",
    "fg":         "#c9d1d9",
    "fg2":        "#8b949e",
    "fg3":        "#6e7681",
    "selected":   "#1f2937",
    "highlight":  "#264f78",
    "editor_bg":  "#0d1117",
    "lineno_bg":  "#0d1117",
    "lineno_fg":  "#3d444d",
    "tab_active": "#161b22",
    "tab_bg":     "#0d1117",
    "scrollbar":  "#30363d",
}

SYNTAX = {
    Token.Keyword:              "#ff7b72",
    Token.Keyword.Constant:     "#79c0ff",
    Token.Keyword.Namespace:    "#ff7b72",
    Token.Name.Builtin:         "#ffa657",
    Token.Name.Function:        "#d2a8ff",
    Token.Name.Class:           "#ffa657",
    Token.Name.Decorator:       "#d2a8ff",
    Token.Name.Exception:       "#ffa657",
    Token.Literal.String:       "#a5d6ff",
    Token.Literal.String.Doc:   "#8b949e",
    Token.Literal.Number:       "#79c0ff",
    Token.Comment:              "#8b949e",
    Token.Comment.Single:       "#8b949e",
    Token.Operator:             "#ff7b72",
    Token.Punctuation:          "#c9d1d9",
    Token.Name.Attribute:       "#79c0ff",
    Token.Name.Namespace:       "#ffa657",
    Token.Name:                 "#c9d1d9",
    Token.Text:                 "#c9d1d9",
    Token.Error:                "#f85149",
}

LEXER_MAP = {}
if PYGMENTS_OK:
    LEXER_MAP = {
        "Python":     PythonLexer(),
        "JavaScript": JavascriptLexer(),
        "Java":       JavaLexer(),
        "HTML":       HtmlLexer(),
        "CSS":        CssLexer(),
        "C":          CLexer(),
        "C++":        CppLexer(),
    }

LANGUAGE_EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".java": "Java",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS",
    ".c": "C", ".cpp": "C++", ".h": "C", ".txt": "Text",
    ".md": "Text", ".json": "Text",
}

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def detect_language(path):
    ext = Path(path).suffix.lower()
    return LANGUAGE_EXTENSIONS.get(ext, "Python")


def apply_ttk_theme():
    """Apply a custom dark ttk style."""
    style = ttk.Style()
    style.theme_use("clam")
    C = DARK

    style.configure(".",
        background=C["bg2"], foreground=C["fg"],
        bordercolor=C["border"], relief="flat",
        font=("Segoe UI", 10))

    style.configure("TFrame", background=C["bg2"])
    style.configure("TLabel", background=C["bg2"], foreground=C["fg"])
    style.configure("TButton",
        background=C["bg3"], foreground=C["fg"],
        borderwidth=0, relief="flat", padding=(10, 5))
    style.map("TButton",
        background=[("active", C["bg4"]), ("pressed", C["accent2"])],
        foreground=[("active", C["fg"])])

    style.configure("Accent.TButton",
        background=C["accent2"], foreground="#ffffff",
        borderwidth=0, relief="flat", padding=(10, 5))
    style.map("Accent.TButton",
        background=[("active", C["accent"]), ("pressed", C["bg4"])])

    style.configure("TNotebook", background=C["tab_bg"], borderwidth=0)
    style.configure("TNotebook.Tab",
        background=C["tab_bg"], foreground=C["fg2"],
        padding=(14, 5), borderwidth=0)
    style.map("TNotebook.Tab",
        background=[("selected", C["tab_active"])],
        foreground=[("selected", C["fg"])])

    style.configure("TEntry",
        fieldbackground=C["bg3"], foreground=C["fg"],
        bordercolor=C["border"], relief="flat", padding=5)

    style.configure("TCombobox",
        fieldbackground=C["bg3"], background=C["bg3"],
        foreground=C["fg"], bordercolor=C["border"],
        arrowcolor=C["fg2"], relief="flat")
    style.map("TCombobox",
        fieldbackground=[("readonly", C["bg3"])],
        selectbackground=[("readonly", C["bg3"])],
        selectforeground=[("readonly", C["fg"])])

    style.configure("Treeview",
        background=C["bg2"], foreground=C["fg"],
        fieldbackground=C["bg2"], borderwidth=0,
        rowheight=24)
    style.map("Treeview", background=[("selected", C["accent2"])],
              foreground=[("selected", "#fff")])
    style.configure("Treeview.Heading",
        background=C["bg3"], foreground=C["fg2"],
        borderwidth=0, relief="flat")

    style.configure("Vertical.TScrollbar",
        background=C["bg3"], troughcolor=C["bg2"],
        bordercolor=C["bg2"], arrowcolor=C["fg3"],
        width=8, relief="flat")
    style.configure("Horizontal.TScrollbar",
        background=C["bg3"], troughcolor=C["bg2"],
        bordercolor=C["bg2"], arrowcolor=C["fg3"],
        height=8, relief="flat")

    style.configure("TScale",
        background=C["bg2"], troughcolor=C["bg4"])

    return style


# ══════════════════════════════════════════════════════════════════════════════
#  CODE EDITOR TAB
# ══════════════════════════════════════════════════════════════════════════════


class ClosableNotebook(ttk.Notebook):
    """A Notebook where every tab has an ✕ close button and a right-click menu."""

    def __init__(self, parent, on_close=None, **kw):
        super().__init__(parent, **kw)
        self._on_close = on_close          # callback(tab_id)
        self._tab_close_btns = {}          # tab_id -> btn widget (unused, label-based)
        self.bind("<ButtonPress-1>", self._on_click)
        self.bind("<Button-3>",      self._on_right_click)

    # ── public: override add/insert to inject ✕ into tab text ──
    def add(self, child, **kw):
        if "text" in kw:
            kw["text"] = kw["text"].rstrip() + "  ✕"
        super().add(child, **kw)

    # ── detect click on ✕ symbol in tab label ──
    def _on_click(self, event):
        try:
            idx = self.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        tab_id = self.tabs()[idx]
        label  = self.tab(tab_id, "text")
        # ✕ occupies the last 2 chars "  ✕"
        # Estimate if click is in the rightmost ~20px of the tab
        tab_bbox = self._tab_bbox(idx)
        if tab_bbox and event.x >= tab_bbox[2] - 22:
            if self._on_close:
                self._on_close(tab_id)

    def _tab_bbox(self, idx):
        """Return (x0,y0,x1,y1) of tab idx, or None."""
        try:
            return self.bbox(idx)          # works on some platforms
        except Exception:
            pass
        try:
            result = self.tk.call(self._w, "identify", "tab", 0, 10)
            # fallback: just allow close on rightmost area
            return None
        except Exception:
            return None

    # ── right-click context menu ──
    def _on_right_click(self, event):
        try:
            idx = self.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        tab_id = self.tabs()[idx]
        menu = tk.Menu(self, tearoff=0,
                       bg=DARK["bg2"], fg=DARK["fg"],
                       activebackground=DARK["accent"],
                       activeforeground="#fff",
                       relief="flat", bd=0)
        menu.add_command(label="Close",
                         command=lambda: self._on_close and self._on_close(tab_id))
        menu.add_command(label="Close Others",
                         command=lambda: self._close_others(tab_id))
        menu.add_command(label="Close All",
                         command=self._close_all)
        menu.tk_popup(event.x_root, event.y_root)

    def _close_others(self, keep_id):
        for tid in list(self.tabs()):
            if tid != keep_id and self._on_close:
                self._on_close(tid)

    def _close_all(self):
        for tid in list(self.tabs()):
            if self._on_close:
                self._on_close(tid)

    # ── update label (keep ✕ suffix) ──
    def set_tab_title(self, tab_id, title):
        """Set tab title ensuring ✕ suffix is always present."""
        self.tab(tab_id, text=title.rstrip() + "  ✕")


class EditorTab(tk.Frame):
    """A single editor tab: line numbers + text widget + syntax highlighting."""

    def __init__(self, parent, app, file_path=None, language="Python", **kwargs):
        super().__init__(parent, bg=DARK["editor_bg"], **kwargs)
        self.app = app
        self.file_path = file_path
        self.language = language
        self._modified = False
        self._highlight_job = None
        self._autosave_job = None
        self._undo_stack = []
        self._redo_stack = []

        self._build()
        if file_path and Path(file_path).exists():
            self._load_file()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        C = DARK
        fs = int(db.get_setting("font_size", "13"))
        ef = db.get_setting("editor_font", "Consolas")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Line numbers
        self.lineno = tk.Text(self, width=4, bg=C["lineno_bg"], fg=C["lineno_fg"],
                               font=(ef, fs), state="disabled", cursor="arrow",
                               borderwidth=0, highlightthickness=0, relief="flat",
                               takefocus=False, selectbackground=C["lineno_bg"])
        self.lineno.grid(row=0, column=0, sticky="ns")

        # Main editor
        # Calculate tab stop in pixels (4 spaces) - required for Windows Tkinter
        try:
            _mf = tkfont.Font(family=ef, size=fs)
            tab_width = _mf.measure("    ")
        except Exception:
            tab_width = 32
        self.text = tk.Text(self,
            bg=C["editor_bg"], fg=C["fg"],
            font=(ef, fs),
            insertbackground=C["accent"],
            selectbackground=C["highlight"],
            borderwidth=0, relief="flat",
            undo=True, maxundo=200,
            wrap="none",
            spacing1=1, spacing3=1,
            highlightthickness=0,
            tabs=(tab_width,))
        self.text.grid(row=0, column=1, sticky="nsew")

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical",
                             command=self._on_vscroll)
        vsb.grid(row=0, column=2, sticky="ns")
        hsb = ttk.Scrollbar(self, orient="horizontal",
                             command=self.text.xview)
        hsb.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.lineno.configure(yscrollcommand=lambda *a: None)

        # Tag colours for syntax
        for tok, colour in SYNTAX.items():
            tag = str(tok).replace(".", "_")
            self.text.tag_configure(tag, foreground=colour)

        # Special tags
        self.text.tag_configure("match", background="#264f78")
        self.text.tag_configure("error_line", background="#3a1a1a")

        # Bindings
        self.text.bind("<KeyRelease>", self._on_key)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Control-s>", lambda e: self.save())
        self.text.bind("<Control-z>", lambda e: self._undo())
        self.text.bind("<Control-y>", lambda e: self._redo())
        self.text.bind("<Control-f>", lambda e: self.app.show_find_replace())
        self.text.bind("<Control-a>", lambda e: self._select_all())

        # Cursor
        self.text.bind("<ButtonRelease-1>", lambda e: self._update_status())
        self.text.bind("<KeyRelease>", self._on_key, add=True)

    # ── File ops ──────────────────────────────────────────────────────────────

    def _load_file(self):
        try:
            content = Path(self.file_path).read_text(encoding="utf-8", errors="replace")
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self._modified = False
            self._schedule_highlight()
            self._update_line_numbers()
        except Exception as e:
            self.text.insert("1.0", f"# Error loading file: {e}\n")

    def save(self):
        if not self.file_path:
            self.save_as()
            return
        content = self.get_content()
        try:
            Path(self.file_path).write_text(content, encoding="utf-8")
            self._modified = False
            self.app._update_tab_title(self)
            proj = self.app.current_project
            if proj:
                db.save_file_record(proj["id"], Path(self.file_path).name,
                                    self.file_path, self.language, content)
            self.app.status(f"Saved: {Path(self.file_path).name}", "green")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("All Files", "*.*")])
        if path:
            self.file_path = path
            self.language = detect_language(path)
            self.save()

    def get_content(self):
        return self.text.get("1.0", "end-1c")

    def get_selected(self):
        try:
            return self.text.get("sel.first", "sel.last")
        except tk.TclError:
            return ""

    # ── Key handlers ─────────────────────────────────────────────────────────

    def _on_key(self, event=None):
        self._modified = True
        self.app._update_tab_title(self)
        self._update_line_numbers()
        self._update_status()
        # Debounced highlighting
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(400, self._do_highlight)
        # Auto-save
        interval = int(db.get_setting("auto_save_interval", "30")) * 1000
        if self._autosave_job:
            self.after_cancel(self._autosave_job)
        if self.file_path:
            self._autosave_job = self.after(interval, self.save)

    def _on_return(self, event):
        """Auto-indent on Enter."""
        line = self.text.get("insert linestart", "insert")
        indent = len(line) - len(line.lstrip())
        if line.rstrip().endswith(":"):
            indent += 4
        self.text.insert("insert", "\n" + " " * indent)
        return "break"

    def _on_tab(self, event):
        """Insert 4 spaces instead of a tab character."""
        self.text.insert("insert", "    ")
        return "break"

    def _on_vscroll(self, *args):
        self.text.yview(*args)
        self.lineno.yview(*args)

    def _select_all(self):
        self.text.tag_add("sel", "1.0", "end")

    # ── Line numbers ──────────────────────────────────────────────────────────

    def _update_line_numbers(self):
        total = int(self.text.index("end-1c").split(".")[0])
        content = "\n".join(str(i) for i in range(1, total + 1))
        self.lineno.configure(state="normal")
        self.lineno.delete("1.0", "end")
        self.lineno.insert("1.0", content)
        self.lineno.configure(state="disabled")
        digits = len(str(total)) + 1
        self.lineno.configure(width=max(3, digits))

    # ── Syntax Highlighting ───────────────────────────────────────────────────

    def _schedule_highlight(self):
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(300, self._do_highlight)

    def _do_highlight(self):
        if not PYGMENTS_OK:
            return
        lexer = LEXER_MAP.get(self.language)
        if not lexer:
            return
        code = self.get_content()
        # Remove existing syntax tags
        for tok in SYNTAX:
            self.text.tag_remove(str(tok).replace(".", "_"), "1.0", "end")

        line, col = 1, 0
        for tok_type, tok_val in lex(code, lexer):
            tag = None
            for key in SYNTAX:
                if tok_type in key or tok_type is key:
                    tag = str(key).replace(".", "_")
                    break
            lines = tok_val.split("\n")
            for i, part in enumerate(lines):
                if i > 0:
                    line += 1
                    col = 0
                if tag and part:
                    start = f"{line}.{col}"
                    end = f"{line}.{col + len(part)}"
                    self.text.tag_add(tag, start, end)
                col += len(part)

    # ── Status ────────────────────────────────────────────────────────────────

    def _update_status(self):
        pos = self.text.index("insert")
        row, col = pos.split(".")
        self.app.status_pos.set(f"Ln {row}, Col {int(col)+1}")

    def _update_status(self):
        try:
            pos = self.text.index("insert")
            row, col = pos.split(".")
            self.app.status_pos.set(f"Ln {row}, Col {int(col)+1}")
            self.app.status_lang.set(self.language)
        except Exception:
            pass

    # ── Undo / Redo ───────────────────────────────────────────────────────────

    def _undo(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def _redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    # ── Find/Replace ──────────────────────────────────────────────────────────

    def find(self, query, case_sensitive=False, replace=None):
        self.text.tag_remove("match", "1.0", "end")
        if not query:
            return 0
        count = 0
        start = "1.0"
        flags = {} if case_sensitive else {"nocase": True}
        while True:
            pos = self.text.search(query, start, "end", **flags)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self.text.tag_add("match", pos, end)
            if replace is not None:
                self.text.delete(pos, end)
                self.text.insert(pos, replace)
                end = f"{pos}+{len(replace)}c"
            count += 1
            start = end
        if count:
            # Scroll to first match
            first = self.text.tag_ranges("match")
            if first:
                self.text.see(first[0])
        return count

    def zoom(self, delta):
        current = self.text.cget("font")
        try:
            f = tkfont.Font(font=current)
            size = f.actual()["size"] + delta
            size = max(8, min(40, size))
            ef = db.get_setting("editor_font", "Consolas")
            new_font = (ef, size)
            self.text.configure(font=new_font)
            self.lineno.configure(font=new_font)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  FIND / REPLACE DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class FindReplaceDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Find & Replace")
        self.resizable(False, False)
        self.configure(bg=DARK["bg2"])
        self._build()
        self.transient(parent)
        self.grab_set()

    def _build(self):
        C = DARK
        pad = {"padx": 10, "pady": 5}

        tk.Label(self, text="Find:", bg=C["bg2"], fg=C["fg"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", **pad)
        self.find_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.find_var, width=30).grid(row=0, column=1, **pad)

        tk.Label(self, text="Replace:", bg=C["bg2"], fg=C["fg"],
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="e", **pad)
        self.replace_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.replace_var, width=30).grid(row=1, column=1, **pad)

        self.case_var = tk.BooleanVar()
        ttk.Checkbutton(self, text="Case sensitive", variable=self.case_var).grid(
            row=2, column=1, sticky="w", **pad)

        btn_frame = tk.Frame(self, bg=C["bg2"])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Find All", command=self._find).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Replace All", command=self._replace).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="left", padx=5)

    def _find(self):
        editor = self.app.current_editor()
        if editor:
            n = editor.find(self.find_var.get(), self.case_var.get())
            self.app.status(f"Found {n} match(es)", "green" if n else "red")

    def _replace(self):
        editor = self.app.current_editor()
        if editor:
            n = editor.find(self.find_var.get(), self.case_var.get(), self.replace_var.get())
            self.app.status(f"Replaced {n} occurrence(s)", "green")


# ══════════════════════════════════════════════════════════════════════════════
#  SNIPPET DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class SnippetDialog(tk.Toplevel):
    def __init__(self, parent, app, snippet=None):
        super().__init__(parent)
        self.app = app
        self.snippet = snippet
        self.title("Edit Snippet" if snippet else "New Snippet")
        self.configure(bg=DARK["bg2"])
        self.resizable(True, True)
        self._build()
        self.transient(parent)
        self.grab_set()

    def _build(self):
        C = DARK
        pad = {"padx": 10, "pady": 4}

        fields = tk.Frame(self, bg=C["bg2"])
        fields.pack(fill="x", padx=10, pady=10)

        def row(label, widget_factory, r):
            tk.Label(fields, text=label, bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 9), anchor="w").grid(
                row=r, column=0, sticky="ew", padx=5, pady=3)
            w = widget_factory(fields)
            w.grid(row=r, column=1, sticky="ew", padx=5, pady=3)
            return w

        fields.columnconfigure(1, weight=1)

        self.name_var = tk.StringVar(value=self.snippet["name"] if self.snippet else "")
        row("Name", lambda p: ttk.Entry(p, textvariable=self.name_var, width=40), 0)

        self.cat_var = tk.StringVar(value=self.snippet.get("category", "General") if self.snippet else "General")
        row("Category", lambda p: ttk.Combobox(p, textvariable=self.cat_var,
            values=sm.CATEGORIES, state="readonly", width=38), 1)

        self.lang_var = tk.StringVar(value=self.snippet.get("language", "Python") if self.snippet else "Python")
        row("Language", lambda p: ttk.Combobox(p, textvariable=self.lang_var,
            values=sm.LANGUAGES, state="readonly", width=38), 2)

        self.desc_var = tk.StringVar(value=self.snippet.get("description", "") if self.snippet else "")
        row("Description", lambda p: ttk.Entry(p, textvariable=self.desc_var, width=40), 3)

        self.tags_var = tk.StringVar(value=self.snippet.get("tags", "") if self.snippet else "")
        row("Tags", lambda p: ttk.Entry(p, textvariable=self.tags_var, width=40), 4)

        tk.Label(self, text="Code:", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        code_frame = tk.Frame(self, bg=C["bg3"], relief="flat")
        code_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.code_text = tk.Text(code_frame, bg=C["editor_bg"], fg=C["fg"],
                                  font=("Consolas", 11), insertbackground=C["accent"],
                                  relief="flat", borderwidth=0, wrap="none",
                                  height=16)
        vsb = ttk.Scrollbar(code_frame, orient="vertical", command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=vsb.set)
        self.code_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        vsb.pack(side="right", fill="y")

        if self.snippet:
            self.code_text.insert("1.0", self.snippet.get("code", ""))

        btn_frame = tk.Frame(self, bg=C["bg2"])
        btn_frame.pack(fill="x", padx=10, pady=8)
        ttk.Button(btn_frame, text="Save Snippet", style="Accent.TButton",
                   command=self._save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel",
                   command=self.destroy).pack(side="right", padx=5)

    def _save(self):
        name = self.name_var.get().strip()
        code = self.code_text.get("1.0", "end-1c")
        if not name or not code:
            messagebox.showwarning("Missing Fields", "Name and Code are required.")
            return
        if self.snippet:
            sm.update_snippet(
                self.snippet["id"], name, self.cat_var.get(), self.lang_var.get(),
                self.desc_var.get(), code, self.tags_var.get())
        else:
            sm.add_snippet(name, self.cat_var.get(), self.lang_var.get(),
                           self.desc_var.get(), code, self.tags_var.get())
        self.app.refresh_snippets()
        self.app.status("Snippet saved", "green")
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Settings")
        self.configure(bg=DARK["bg2"])
        self.resizable(False, False)
        self._build()
        self.transient(parent)
        self.grab_set()

    def _build(self):
        C = DARK
        settings = db.get_all_settings()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Editor tab
        ef = tk.Frame(nb, bg=C["bg2"])
        nb.add(ef, text="  Editor  ")

        def lbl(parent, text, r, c):
            tk.Label(parent, text=text, bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 10)).grid(row=r, column=c, sticky="w", padx=10, pady=6)

        ef.columnconfigure(1, weight=1)

        lbl(ef, "Font Size", 0, 0)
        self.fs_var = tk.StringVar(value=settings.get("font_size", "13"))
        ttk.Spinbox(ef, from_=8, to=40, textvariable=self.fs_var, width=8).grid(
            row=0, column=1, sticky="w", padx=10, pady=6)

        lbl(ef, "Editor Font", 1, 0)
        self.font_var = tk.StringVar(value=settings.get("editor_font", "Consolas"))
        ttk.Combobox(ef, textvariable=self.font_var, width=20,
                     values=["Consolas", "Courier New", "Fira Code", "JetBrains Mono",
                             "Cascadia Code", "Source Code Pro", "Lucida Console"]).grid(
            row=1, column=1, sticky="w", padx=10, pady=6)

        lbl(ef, "Tab Size", 2, 0)
        self.tab_var = tk.StringVar(value=settings.get("tab_size", "4"))
        ttk.Combobox(ef, textvariable=self.tab_var, values=["2", "4", "8"], width=8,
                     state="readonly").grid(row=2, column=1, sticky="w", padx=10, pady=6)

        lbl(ef, "Auto-save Interval (sec)", 3, 0)
        self.as_var = tk.StringVar(value=settings.get("auto_save_interval", "30"))
        ttk.Spinbox(ef, from_=5, to=300, textvariable=self.as_var, width=8).grid(
            row=3, column=1, sticky="w", padx=10, pady=6)

        lbl(ef, "Word Wrap", 4, 0)
        self.wrap_var = tk.BooleanVar(value=settings.get("word_wrap", "false") == "true")
        ttk.Checkbutton(ef, variable=self.wrap_var).grid(
            row=4, column=1, sticky="w", padx=10, pady=6)

        # ── AI tab
        af = tk.Frame(nb, bg=C["bg2"])
        nb.add(af, text="  AI / API  ")
        af.columnconfigure(1, weight=1)

        tk.Label(af, text="OpenAI API Key (optional):", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, columnspan=2, sticky="w",
                                              padx=10, pady=(15, 4))
        self.key_var = tk.StringVar(value=settings.get("openai_key", ""))
        ttk.Entry(af, textvariable=self.key_var, width=45, show="*").grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=4)
        tk.Label(af, text="Leave blank to use rule-based AI analysis.",
                 bg=C["bg2"], fg=C["fg3"], font=("Segoe UI", 9, "italic")).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=10)

        lbl(af, "Username", 3, 0)
        self.user_var = tk.StringVar(value=settings.get("username", "Developer"))
        ttk.Entry(af, textvariable=self.user_var, width=25).grid(
            row=3, column=1, sticky="w", padx=10, pady=6)

        # Buttons
        btn_frame = tk.Frame(self, bg=C["bg2"])
        btn_frame.pack(fill="x", padx=10, pady=8)
        ttk.Button(btn_frame, text="Save Settings", style="Accent.TButton",
                   command=self._save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel",
                   command=self.destroy).pack(side="right", padx=5)

    def _save(self):
        db.set_setting("font_size", self.fs_var.get())
        db.set_setting("editor_font", self.font_var.get())
        db.set_setting("tab_size", self.tab_var.get())
        db.set_setting("auto_save_interval", self.as_var.get())
        db.set_setting("word_wrap", "true" if self.wrap_var.get() else "false")
        db.set_setting("openai_key", self.key_var.get())
        db.set_setting("username", self.user_var.get())
        self.app.status("Settings saved – restart tabs to apply font changes", "green")
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  STATISTICS PANEL
# ══════════════════════════════════════════════════════════════════════════════

class StatisticsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("CodeVault AI – Statistics")
        self.configure(bg=DARK["bg"])
        self.geometry("800x600")
        self._build()

    def _build(self):
        C = DARK
        stats = db.get_statistics()

        # Header
        hdr = tk.Frame(self, bg=C["bg2"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="📊  Statistics Dashboard", bg=C["bg2"], fg=C["fg"],
                 font=("Segoe UI", 16, "bold"), pady=12).pack(side="left", padx=20)

        # Cards row
        cards_frame = tk.Frame(self, bg=C["bg"])
        cards_frame.pack(fill="x", padx=20, pady=15)

        card_data = [
            ("Projects", stats["total_projects"], C["accent"]),
            ("Files", stats["total_files"], C["green"]),
            ("Snippets", stats["total_snippets"], C["purple"]),
            ("Executions", stats["total_executions"], C["orange"]),
            ("Lines Written", stats["total_lines"], C["cyan"]),
        ]
        for label, value, color in card_data:
            card = tk.Frame(cards_frame, bg=C["bg2"], relief="flat",
                            highlightbackground=color, highlightthickness=1)
            card.pack(side="left", expand=True, fill="both", padx=5)
            tk.Label(card, text=str(value), bg=C["bg2"], fg=color,
                     font=("Segoe UI", 24, "bold")).pack(pady=(15, 0))
            tk.Label(card, text=label, bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 10)).pack(pady=(0, 15))

        # Most-used language
        tk.Label(self, text=f"⭐  Top Language: {stats['top_language']}",
                 bg=C["bg"], fg=C["yellow"],
                 font=("Segoe UI", 12)).pack(anchor="w", padx=25, pady=5)

        if MATPLOTLIB_OK and stats["language_distribution"]:
            fig = Figure(figsize=(7, 3.5), dpi=90, facecolor=C["bg2"])
            ax = fig.add_subplot(111, facecolor=C["bg2"])
            langs = list(stats["language_distribution"].keys())
            counts = list(stats["language_distribution"].values())
            colors = [C["accent"], C["green"], C["purple"], C["orange"],
                      C["cyan"], C["yellow"], C["red"]]
            ax.barh(langs, counts, color=colors[:len(langs)], edgecolor="none")
            ax.set_xlabel("Files", color=C["fg2"])
            ax.tick_params(colors=C["fg2"])
            ax.spines[:].set_color(C["border"])
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
        else:
            if stats["language_distribution"]:
                txt = tk.Text(self, bg=C["bg2"], fg=C["fg"], font=("Consolas", 11),
                              relief="flat", borderwidth=0, height=8)
                txt.pack(fill="both", expand=True, padx=20, pady=10)
                for lang, cnt in stats["language_distribution"].items():
                    bar = "█" * cnt
                    txt.insert("end", f"  {lang:<15} {bar} {cnt}\n")
                txt.configure(state="disabled")
            tk.Label(self, text="Install matplotlib for charts: pip install matplotlib",
                     bg=C["bg"], fg=C["fg3"],
                     font=("Segoe UI", 9, "italic")).pack(pady=5)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class CodeVaultApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("CodeVault AI")
        self.geometry("1400x860")
        self.minsize(1000, 600)
        self.configure(bg=DARK["bg"])
        apply_ttk_theme()

        # State
        self.current_project = None
        self._tabs = {}          # notebook_tab_id -> EditorTab
        self._tab_paths = {}     # path -> notebook_tab_id
        self._execution_running = False

        # Status vars
        self.status_pos = tk.StringVar(value="Ln 1, Col 1")
        self.status_lang = tk.StringVar(value="Python")
        self.status_msg = tk.StringVar(value="Welcome to CodeVault AI")
        self.status_color = DARK["fg2"]

        # Input bar vars (populated in _build_center)
        self._input_var = None
        self._input_entry = None
        self._input_send_btn = None
        self._input_hint = None

        self._build_ui()
        self._bind_menu_shortcuts()
        self.refresh_projects()
        self.refresh_snippets()

        # Auto-welcome tab
        self._open_welcome()

    # ══════════════════════════════════════════════════════════════════════
    #  UI Build
    # ══════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        self._build_menubar()
        self._build_toolbar()
        self._build_main_area()
        self._build_statusbar()

    def _build_menubar(self):
        C = DARK
        menu = tk.Menu(self, bg=C["bg2"], fg=C["fg"],
                       activebackground=C["accent2"], activeforeground="#fff",
                       borderwidth=0, relief="flat")
        self.configure(menu=menu)

        # File
        fm = tk.Menu(menu, tearoff=0, bg=C["bg2"], fg=C["fg"],
                     activebackground=C["accent2"], activeforeground="#fff")
        menu.add_cascade(label="File", menu=fm)
        fm.add_command(label="New File          Ctrl+N", command=self.new_file)
        fm.add_command(label="Open File         Ctrl+O", command=self.open_file)
        fm.add_command(label="Save              Ctrl+S", command=self.save_current)
        fm.add_command(label="Save As", command=self.save_as_current)
        fm.add_separator()
        fm.add_command(label="New Project", command=self.new_project_dialog)
        fm.add_command(label="Open Project Folder", command=self.open_project_folder)
        fm.add_separator()
        fm.add_command(label="Exit", command=self.quit)

        # Edit
        em = tk.Menu(menu, tearoff=0, bg=C["bg2"], fg=C["fg"],
                     activebackground=C["accent2"], activeforeground="#fff")
        menu.add_cascade(label="Edit", menu=em)
        em.add_command(label="Find & Replace    Ctrl+F", command=self.show_find_replace)
        em.add_command(label="Select All        Ctrl+A",
                       command=lambda: self.current_editor() and
                       self.current_editor().text.tag_add("sel", "1.0", "end"))
        em.add_separator()
        em.add_command(label="Zoom In           Ctrl++",
                       command=lambda: self.current_editor() and
                       self.current_editor().zoom(+1))
        em.add_command(label="Zoom Out          Ctrl+-",
                       command=lambda: self.current_editor() and
                       self.current_editor().zoom(-1))

        # Run
        rm = tk.Menu(menu, tearoff=0, bg=C["bg2"], fg=C["fg"],
                     activebackground=C["accent2"], activeforeground="#fff")
        menu.add_cascade(label="Run", menu=rm)
        rm.add_command(label="Run Code          F5", command=self.run_code)
        rm.add_command(label="Stop Execution    F6", command=self.stop_execution)

        # AI
        am = tk.Menu(menu, tearoff=0, bg=C["bg2"], fg=C["fg"],
                     activebackground=C["accent2"], activeforeground="#fff")
        menu.add_cascade(label="AI Tools", menu=am)
        am.add_command(label="Explain Code", command=self.explain_code)
        am.add_command(label="Review Code", command=self.review_code)
        am.add_command(label="Analyze Error", command=self.analyze_last_error)

        # View
        vm = tk.Menu(menu, tearoff=0, bg=C["bg2"], fg=C["fg"],
                     activebackground=C["accent2"], activeforeground="#fff")
        menu.add_cascade(label="View", menu=vm)
        vm.add_command(label="Statistics", command=self.show_statistics)
        vm.add_command(label="Settings", command=self.show_settings)
        vm.add_command(label="Clear Console", command=self.clear_console)

        # Help
        hm = tk.Menu(menu, tearoff=0, bg=C["bg2"], fg=C["fg"],
                     activebackground=C["accent2"], activeforeground="#fff")
        menu.add_cascade(label="Help", menu=hm)
        hm.add_command(label="About", command=self._show_about)
        hm.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)

    def _build_toolbar(self):
        C = DARK
        tb = tk.Frame(self, bg=C["bg2"], height=42,
                      highlightbackground=C["border"], highlightthickness=1)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)

        def btn(text, cmd, tip="", accent=False):
            b = tk.Button(tb, text=text, command=cmd,
                          bg=C["accent2"] if accent else C["bg3"],
                          fg="#fff" if accent else C["fg"],
                          font=("Segoe UI", 9), relief="flat",
                          borderwidth=0, padx=10, pady=4,
                          activebackground=C["accent"] if accent else C["bg4"],
                          activeforeground="#fff",
                          cursor="hand2")
            b.pack(side="left", padx=2, pady=6)
            return b

        btn("＋ New", self.new_file)
        btn("📂 Open", self.open_file)
        btn("💾 Save", self.save_current)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", padx=6, pady=8)

        btn("▶ Run", self.run_code, accent=True)
        btn("■ Stop", self.stop_execution)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", padx=6, pady=8)

        btn("🧠 Explain", self.explain_code)
        btn("🔍 Review", self.review_code)
        btn("🐛 Errors", self.analyze_last_error)

        tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", padx=6, pady=8)
        btn("📊 Stats", self.show_statistics)
        btn("⚙ Settings", self.show_settings)

        # Language selector (right side)
        tk.Label(tb, text="Language:", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="right", padx=(0, 4))
        self.lang_var = tk.StringVar(value="Python")
        lang_cb = ttk.Combobox(tb, textvariable=self.lang_var, width=14,
                                values=["Python", "JavaScript", "Java", "HTML",
                                        "CSS", "C", "C++"],
                                state="readonly", font=("Segoe UI", 9))
        lang_cb.pack(side="right", pady=8, padx=(0, 10))
        lang_cb.bind("<<ComboboxSelected>>", self._on_lang_change)

    def _build_main_area(self):
        """PanedWindow: left sidebar | center editor | right panel."""
        C = DARK
        self._paned = tk.PanedWindow(self, orient="horizontal",
                                      bg=C["bg"], sashwidth=4,
                                      sashrelief="flat", sashpad=0)
        self._paned.pack(fill="both", expand=True)

        # ── LEFT SIDEBAR ─────────────────────────────────────────────────────
        left = tk.Frame(self._paned, bg=C["bg2"], width=220)
        self._paned.add(left, minsize=180)

        # Sidebar tabs
        sidebar_nb = ttk.Notebook(left, style="TNotebook")
        sidebar_nb.pack(fill="both", expand=True)

        # Project Explorer
        proj_frame = tk.Frame(sidebar_nb, bg=C["bg2"])
        sidebar_nb.add(proj_frame, text=" Explorer ")
        self._build_project_explorer(proj_frame)

        # Snippets
        snip_frame = tk.Frame(sidebar_nb, bg=C["bg2"])
        sidebar_nb.add(snip_frame, text=" Snippets ")
        self._build_snippet_panel(snip_frame)

        # Search
        search_frame = tk.Frame(sidebar_nb, bg=C["bg2"])
        sidebar_nb.add(search_frame, text=" Search ")
        self._build_search_panel(search_frame)

        # ── CENTER ───────────────────────────────────────────────────────────
        center = tk.Frame(self._paned, bg=C["bg"])
        self._paned.add(center, minsize=400)

        self._build_center(center)

        # ── RIGHT PANEL ──────────────────────────────────────────────────────
        right = tk.Frame(self._paned, bg=C["bg2"], width=280)
        self._paned.add(right, minsize=220)
        self._build_right_panel(right)

    def _build_project_explorer(self, parent):
        C = DARK

        # Search bar
        sf = tk.Frame(parent, bg=C["bg2"])
        sf.pack(fill="x", padx=5, pady=5)
        self.proj_search_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.proj_search_var,
                  font=("Segoe UI", 9)).pack(fill="x")
        self.proj_search_var.trace("w", lambda *a: self.refresh_projects())

        # Buttons
        bf = tk.Frame(parent, bg=C["bg2"])
        bf.pack(fill="x", padx=5, pady=(0, 5))
        tk.Button(bf, text="+ New Project", command=self.new_project_dialog,
                  bg=C["accent2"], fg="#fff", relief="flat", borderwidth=0,
                  font=("Segoe UI", 9), padx=6, pady=3,
                  activebackground=C["accent"], cursor="hand2").pack(fill="x")

        # Tree
        tree_frame = tk.Frame(parent, bg=C["bg2"])
        tree_frame.pack(fill="both", expand=True)

        self.proj_tree = ttk.Treeview(tree_frame, show="tree",
                                       selectmode="browse")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.proj_tree.yview)
        self.proj_tree.configure(yscrollcommand=vsb.set)
        self.proj_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.proj_tree.bind("<<TreeviewSelect>>", self._on_proj_select)
        self.proj_tree.bind("<Double-1>", self._on_tree_double_click)
        self.proj_tree.bind("<Button-3>", self._on_proj_right_click)

        # Context menu
        self._proj_ctx = tk.Menu(self, tearoff=0, bg=C["bg2"], fg=C["fg"],
                                   activebackground=C["accent2"],
                                   activeforeground="#fff")
        self._proj_ctx.add_command(label="Open Project", command=self._ctx_open_project)
        self._proj_ctx.add_command(label="Rename Project", command=self._ctx_rename_project)
        self._proj_ctx.add_command(label="New File in Project", command=self._ctx_new_file)
        self._proj_ctx.add_separator()
        self._proj_ctx.add_command(label="Export as ZIP", command=self._ctx_export_project)
        self._proj_ctx.add_separator()
        self._proj_ctx.add_command(label="Delete Project", command=self._ctx_delete_project)

        self._selected_proj_id = None
        self._selected_file_path = None

    def _build_snippet_panel(self, parent):
        C = DARK

        sf = tk.Frame(parent, bg=C["bg2"])
        sf.pack(fill="x", padx=5, pady=5)
        self.snip_search_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.snip_search_var,
                  font=("Segoe UI", 9)).pack(fill="x")
        self.snip_search_var.trace("w", lambda *a: self.refresh_snippets())

        bf = tk.Frame(parent, bg=C["bg2"])
        bf.pack(fill="x", padx=5, pady=(0, 5))
        tk.Button(bf, text="+ New Snippet", command=lambda: SnippetDialog(self, self),
                  bg=C["green"], fg="#000", relief="flat", borderwidth=0,
                  font=("Segoe UI", 9), padx=6, pady=3,
                  activebackground="#2ea043", cursor="hand2").pack(fill="x")

        tree_frame = tk.Frame(parent, bg=C["bg2"])
        tree_frame.pack(fill="both", expand=True)

        self.snip_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self.snip_tree.yview)
        self.snip_tree.configure(yscrollcommand=vsb.set)
        self.snip_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.snip_tree.bind("<Double-1>", self._on_snip_double_click)
        self.snip_tree.bind("<Button-3>", self._on_snip_right_click)

        self._snip_ctx = tk.Menu(self, tearoff=0, bg=C["bg2"], fg=C["fg"],
                                  activebackground=C["accent2"],
                                  activeforeground="#fff")
        self._snip_ctx.add_command(label="Insert into Editor", command=self._ctx_insert_snippet)
        self._snip_ctx.add_command(label="Copy to Clipboard", command=self._ctx_copy_snippet)
        self._snip_ctx.add_command(label="Edit Snippet", command=self._ctx_edit_snippet)
        self._snip_ctx.add_separator()
        self._snip_ctx.add_command(label="Delete Snippet", command=self._ctx_delete_snippet)

        self._snip_items = {}  # tree_id -> snippet dict

    def _build_search_panel(self, parent):
        C = DARK
        tk.Label(parent, text="Global Search", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 4))

        sf = tk.Frame(parent, bg=C["bg2"])
        sf.pack(fill="x", padx=5, pady=5)
        self.global_search_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.global_search_var,
                  font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
        tk.Button(sf, text="Go", command=self._do_global_search,
                  bg=C["accent2"], fg="#fff", relief="flat", borderwidth=0,
                  padx=8, pady=3, font=("Segoe UI", 9), cursor="hand2").pack(side="right", padx=(4, 0))

        self.search_results = tk.Text(parent, bg=C["bg2"], fg=C["fg"],
                                       font=("Consolas", 9), relief="flat",
                                       borderwidth=0, wrap="word", state="disabled",
                                       highlightthickness=0)
        self.search_results.pack(fill="both", expand=True, padx=5, pady=5)
        self.search_results.bind("<Double-1>", self._on_search_result_click)
        self._search_result_map = {}  # line_no -> file_path

    def _build_center(self, parent):
        C = DARK
        # Vertical pane: editor top, console bottom
        pv = tk.PanedWindow(parent, orient="vertical",
                             bg=C["bg"], sashwidth=4,
                             sashrelief="flat")
        pv.pack(fill="both", expand=True)

        # Editor notebook
        editor_frame = tk.Frame(pv, bg=C["bg"])
        pv.add(editor_frame, minsize=200)

        self.editor_nb = ClosableNotebook(
            editor_frame, on_close=self._close_tab)
        self.editor_nb.pack(fill="both", expand=True)
        self.editor_nb.bind("<<NotebookTabChanged>>", self._on_tab_change)
        self.editor_nb.bind("<Button-2>", self._on_tab_middle_click)

        # Console
        console_frame = tk.Frame(pv, bg=C["bg2"])
        pv.add(console_frame, minsize=120)

        # ── Interactive Input Bar ── (must be packed BEFORE the notebook so it
        #    isn't swallowed when the notebook claims all remaining space)
        self._input_var = tk.StringVar()

        _input_bar = tk.Frame(console_frame, bg=DARK["bg3"],
                              highlightbackground=DARK["border"],
                              highlightthickness=1)
        _input_bar.pack(fill="x", side="bottom")

        tk.Label(_input_bar, text=" ▶ Input:", bg=DARK["bg3"],
                 fg=DARK["yellow"], font=("Segoe UI", 9, "bold")).pack(
            side="left", padx=(6, 2), pady=4)

        self._input_entry = ttk.Entry(_input_bar, textvariable=self._input_var,
                                      font=("Consolas", 11))
        self._input_entry.pack(side="left", fill="x", expand=True, pady=4, padx=4)
        self._input_entry.bind("<Return>", self._on_input_submit)
        self._input_entry.configure(state="disabled")

        self._input_send_btn = tk.Button(
            _input_bar, text="Send",
            bg=DARK["accent2"], fg="#fff",
            font=("Segoe UI", 9), relief="flat", borderwidth=0,
            padx=12, pady=4,
            activebackground=DARK["accent"],
            cursor="hand2",
            command=self._on_input_submit,
            state="disabled")
        self._input_send_btn.pack(side="right", padx=(4, 8), pady=4)

        self._input_hint = tk.Label(
            _input_bar,
            text="Run a program with input() to activate",
            bg=DARK["bg3"], fg=DARK["fg3"],
            font=("Segoe UI", 8, "italic"))
        self._input_hint.pack(side="right", padx=8)

        # Notebook goes AFTER the input bar so it fills remaining space
        console_nb = ttk.Notebook(console_frame)
        console_nb.pack(fill="both", expand=True)

        # Output
        out_frame = tk.Frame(console_nb, bg=C["bg2"])
        console_nb.add(out_frame, text="  Output  ")
        out_frame.rowconfigure(0, weight=1)
        out_frame.columnconfigure(0, weight=1)

        self.output_text = tk.Text(out_frame, bg=C["bg"], fg="#e0e0e0",
                                    font=("Consolas", 11), relief="flat",
                                    borderwidth=0, wrap="word", state="disabled",
                                    highlightthickness=0)
        vsb_out = ttk.Scrollbar(out_frame, orient="vertical",
                                 command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=vsb_out.set)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        vsb_out.grid(row=0, column=1, sticky="ns")

        # Tag colours for console
        self.output_text.tag_configure("stdout",  foreground="#e0e0e0")
        self.output_text.tag_configure("stderr",  foreground=DARK["red"])
        self.output_text.tag_configure("system",  foreground=DARK["fg2"])
        self.output_text.tag_configure("success", foreground=DARK["green"])
        self.output_text.tag_configure("timing",  foreground=DARK["cyan"])
        self.output_text.tag_configure("input",   foreground=DARK["cyan"])
        self.output_text.tag_configure("prompt",  foreground=DARK["yellow"])

        # Error console
        err_frame = tk.Frame(console_nb, bg=C["bg2"])
        console_nb.add(err_frame, text="  Errors  ")
        err_frame.rowconfigure(0, weight=1)
        err_frame.columnconfigure(0, weight=1)

        self.error_text = tk.Text(err_frame, bg=C["bg"], fg=DARK["red"],
                                   font=("Consolas", 11), relief="flat",
                                   borderwidth=0, wrap="word", state="disabled",
                                   highlightthickness=0)
        vsb_err = ttk.Scrollbar(err_frame, orient="vertical",
                                 command=self.error_text.yview)
        self.error_text.configure(yscrollcommand=vsb_err.set)
        self.error_text.grid(row=0, column=0, sticky="nsew")
        vsb_err.grid(row=0, column=1, sticky="ns")

        # Exec log
        log_frame = tk.Frame(console_nb, bg=C["bg2"])
        console_nb.add(log_frame, text="  Log  ")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, bg=C["bg"], fg=DARK["fg2"],
                                 font=("Consolas", 10), relief="flat",
                                 borderwidth=0, wrap="word", state="disabled",
                                 highlightthickness=0)
        vsb_log = ttk.Scrollbar(log_frame, orient="vertical",
                                 command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=vsb_log.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        vsb_log.grid(row=0, column=1, sticky="ns")

        self._last_error = ""

    def _build_right_panel(self, parent):
        C = DARK
        right_nb = ttk.Notebook(parent)
        right_nb.pack(fill="both", expand=True)

        # AI Analysis
        ai_frame = tk.Frame(right_nb, bg=C["bg2"])
        right_nb.add(ai_frame, text=" AI Analysis ")
        self._build_ai_panel(ai_frame)

        # Error Analysis
        err_frame = tk.Frame(right_nb, bg=C["bg2"])
        right_nb.add(err_frame, text=" Error Insight ")
        self._build_error_panel(err_frame)

        # Project Stats
        stat_frame = tk.Frame(right_nb, bg=C["bg2"])
        right_nb.add(stat_frame, text=" Project Info ")
        self._build_project_info_panel(stat_frame)

    def _build_ai_panel(self, parent):
        C = DARK
        hdr = tk.Frame(parent, bg=C["bg2"])
        hdr.pack(fill="x", padx=8, pady=8)
        tk.Label(hdr, text="🧠 AI Code Analysis", bg=C["bg2"], fg=C["accent"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")

        btn_frame = tk.Frame(parent, bg=C["bg2"])
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))

        for text, cmd in [("Explain", self.explain_code), ("Review", self.review_code)]:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg=C["accent2"], fg="#fff", relief="flat", borderwidth=0,
                      font=("Segoe UI", 9), padx=10, pady=4,
                      activebackground=C["accent"], cursor="hand2").pack(
                side="left", padx=(0, 6))

        self.ai_text = tk.Text(parent, bg=C["bg"], fg=C["fg"],
                                font=("Consolas", 10), relief="flat",
                                borderwidth=0, wrap="word", state="disabled",
                                highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.ai_text.yview)
        self.ai_text.configure(yscrollcommand=vsb.set)
        self.ai_text.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        vsb.pack(side="right", fill="y", pady=(0, 8), padx=(0, 4))

        self.ai_text.tag_configure("header", foreground=DARK["accent"],
                                    font=("Segoe UI", 11, "bold"))
        self.ai_text.tag_configure("key", foreground=DARK["yellow"],
                                    font=("Consolas", 10, "bold"))
        self.ai_text.tag_configure("value", foreground=DARK["fg"])
        self.ai_text.tag_configure("good", foreground=DARK["green"])
        self.ai_text.tag_configure("warn", foreground=DARK["orange"])
        self.ai_text.tag_configure("sep", foreground=DARK["fg3"])

        self._set_ai_text("Click 'Explain' or 'Review' to analyze your code.")

    def _build_error_panel(self, parent):
        C = DARK
        tk.Label(parent, text="🐛 Error Analyzer", bg=C["bg2"], fg=DARK["red"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=8)

        tk.Button(parent, text="Analyze Last Error", command=self.analyze_last_error,
                  bg=DARK["red"], fg="#fff", relief="flat", borderwidth=0,
                  font=("Segoe UI", 9), padx=10, pady=4,
                  activebackground="#da3633", cursor="hand2").pack(
            anchor="w", padx=8, pady=(0, 8))

        self.err_analysis_text = tk.Text(parent, bg=C["bg"], fg=C["fg"],
                                          font=("Consolas", 10), relief="flat",
                                          borderwidth=0, wrap="word", state="disabled",
                                          highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical",
                             command=self.err_analysis_text.yview)
        self.err_analysis_text.configure(yscrollcommand=vsb.set)
        self.err_analysis_text.pack(side="left", fill="both", expand=True,
                                     padx=(8, 0), pady=(0, 8))
        vsb.pack(side="right", fill="y", pady=(0, 8), padx=(0, 4))

        self._set_err_text("Run your code first, then click 'Analyze Last Error'.")

    def _build_project_info_panel(self, parent):
        C = DARK
        self.proj_info_text = tk.Text(parent, bg=C["bg"], fg=C["fg"],
                                       font=("Consolas", 10), relief="flat",
                                       borderwidth=0, wrap="word", state="disabled",
                                       highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical",
                             command=self.proj_info_text.yview)
        self.proj_info_text.configure(yscrollcommand=vsb.set)
        self.proj_info_text.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        vsb.pack(side="right", fill="y", pady=8, padx=(0, 4))
        self._update_project_info()

    def _build_statusbar(self):
        C = DARK
        sb = tk.Frame(self, bg=C["bg3"], height=24,
                      highlightbackground=C["border"], highlightthickness=1)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

        self._status_label = tk.Label(sb, textvariable=self.status_msg,
                                       bg=C["bg3"], fg=C["fg2"],
                                       font=("Segoe UI", 9), anchor="w")
        self._status_label.pack(side="left", padx=10)

        tk.Label(sb, textvariable=self.status_lang,
                 bg=C["bg3"], fg=C["accent"],
                 font=("Segoe UI", 9)).pack(side="right", padx=10)
        tk.Label(sb, textvariable=self.status_pos,
                 bg=C["bg3"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="right", padx=10)

    # ══════════════════════════════════════════════════════════════════════
    #  Keyboard shortcuts
    # ══════════════════════════════════════════════════════════════════════

    def _bind_menu_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_current())
        self.bind("<F5>", lambda e: self.run_code())
        self.bind("<F6>", lambda e: self.stop_execution())
        self.bind("<Control-equal>", lambda e: self.current_editor() and
                  self.current_editor().zoom(+1))
        self.bind("<Control-minus>", lambda e: self.current_editor() and
                  self.current_editor().zoom(-1))
        self.bind("<Control-w>", lambda e: self._close_current_tab())

    # ══════════════════════════════════════════════════════════════════════
    #  File / Tab management
    # ══════════════════════════════════════════════════════════════════════

    def _open_welcome(self):
        welcome = (
            '"""\n'
            '╔══════════════════════════════════════╗\n'
            '║       Welcome to CodeVault AI        ║\n'
            '║  Professional Python Coding Workspace║\n'
            '╚══════════════════════════════════════╝\n\n'
            '  ► New Project  : File > New Project\n'
            '  ► Open File    : File > Open File  (Ctrl+O)\n'
            '  ► Run Code     : Run > Run Code    (F5)\n'
            '  ► AI Explain   : AI Tools > Explain Code\n'
            '  ► Snippets     : Left sidebar > Snippets\n'
            '"""\n\n'
            'def greet(name):\n'
            '    """A friendly greeting function."""\n'
            '    return f"Hello, {name}! Welcome to CodeVault AI."\n\n'
            'if __name__ == "__main__":\n'
            '    print(greet("Developer"))\n'
        )
        tab = EditorTab(self.editor_nb, self, language="Python")
        tab.text.insert("1.0", welcome)
        tab._modified = False
        tab._schedule_highlight()
        tab._update_line_numbers()
        self.editor_nb.add(tab, text="  welcome.py  ")  # ✕ appended by ClosableNotebook
        self.editor_nb.select(tab)
        tab_id = self.editor_nb.select()
        self._tabs[tab_id] = tab

    def new_file(self, file_path=None, language=None, content=None):
        if file_path and file_path in self._tab_paths:
            self.editor_nb.select(self._tab_paths[file_path])
            return
        lang = language or self.lang_var.get()
        if file_path:
            lang = detect_language(file_path)
        tab = EditorTab(self.editor_nb, self,
                        file_path=file_path, language=lang)
        if content:
            tab.text.delete("1.0", "end")
            tab.text.insert("1.0", content)
            tab._modified = False
            tab._schedule_highlight()
            tab._update_line_numbers()
        name = Path(file_path).name if file_path else "untitled.py"
        display = f"  {name}  "
        self.editor_nb.add(tab, text=display)
        self.editor_nb.select(tab)
        tab_id = self.editor_nb.select()
        self._tabs[tab_id] = tab
        if file_path:
            self._tab_paths[file_path] = tab_id
        self.lang_var.set(lang)

    def open_file(self, path=None):
        if not path:
            path = filedialog.askopenfilename(
                filetypes=[
                    ("Code Files", "*.py *.js *.java *.html *.css *.c *.cpp *.h"),
                    ("All Files", "*.*")
                ])
        if not path:
            return
        if path in self._tab_paths:
            self.editor_nb.select(self._tab_paths[path])
            return
        lang = detect_language(path)
        tab = EditorTab(self.editor_nb, self, file_path=path, language=lang)
        name = Path(path).name
        self.editor_nb.add(tab, text=f"  {name}  ")
        self.editor_nb.select(tab)
        tab_id = self.editor_nb.select()
        self._tabs[tab_id] = tab
        self._tab_paths[path] = tab_id
        self.lang_var.set(lang)
        self.status(f"Opened: {name}")

    def save_current(self):
        editor = self.current_editor()
        if editor:
            editor.save()

    def save_as_current(self):
        editor = self.current_editor()
        if editor:
            editor.save_as()

    def current_editor(self):
        tab_id = self.editor_nb.select()
        return self._tabs.get(tab_id)

    def _update_tab_title(self, tab):
        for tab_id, t in self._tabs.items():
            if t is tab:
                name = Path(tab.file_path).name if tab.file_path else "untitled"
                mark = " ●" if tab._modified else ""
                self.editor_nb.set_tab_title(tab_id, f"  {name}{mark}  ")
                return

    def _on_tab_change(self, event):
        editor = self.current_editor()
        if editor:
            self.lang_var.set(editor.language)
            editor._update_status()

    def _on_tab_middle_click(self, event):
        clicked = self.editor_nb.tk.call(self.editor_nb._w, "identify", "tab",
                                          event.x, event.y)
        if clicked != "":
            self._close_tab(clicked)

    def _close_current_tab(self):
        tab_id = self.editor_nb.select()
        if tab_id:
            self._close_tab(tab_id)

    def _close_tab(self, tab_id):
        tab = self._tabs.get(tab_id)
        if tab and tab._modified:
            ans = messagebox.askyesnocancel("Unsaved Changes",
                                             "Save before closing?")
            if ans is None:
                return
            if ans:
                tab.save()
        if tab and tab.file_path and tab.file_path in self._tab_paths:
            del self._tab_paths[tab.file_path]
        if tab_id in self._tabs:
            del self._tabs[tab_id]
        self.editor_nb.forget(tab_id)

    def _on_lang_change(self, event=None):
        editor = self.current_editor()
        if editor:
            editor.language = self.lang_var.get()
            editor._schedule_highlight()

    # ══════════════════════════════════════════════════════════════════════
    #  Project tree
    # ══════════════════════════════════════════════════════════════════════

    def refresh_projects(self, *args):
        self.proj_tree.delete(*self.proj_tree.get_children())
        query = self.proj_search_var.get().lower() if hasattr(self, "proj_search_var") else ""
        projects = db.get_all_projects()
        for p in projects:
            if query and query not in p["name"].lower():
                continue
            pid = self.proj_tree.insert("", "end",
                                         text=f"📁  {p['name']}",
                                         values=(p["id"], "project"),
                                         tags=("project",))
            # Files
            files = db.get_project_files(p["id"])
            for f in files:
                icon = _lang_icon(f["language"])
                self.proj_tree.insert(pid, "end",
                                      text=f"  {icon}  {f['name']}",
                                      values=(f["path"], "file"),
                                      tags=("file",))

    def _on_proj_select(self, event):
        sel = self.proj_tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.proj_tree.item(item, "values")
        if not vals:
            return
        tag = vals[1] if len(vals) > 1 else ""
        if tag == "project":
            self._selected_proj_id = int(vals[0])
            self._selected_file_path = None
        elif tag == "file":
            self._selected_file_path = vals[0]

    def _on_tree_double_click(self, event):
        sel = self.proj_tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.proj_tree.item(item, "values")
        if not vals:
            return
        tag = vals[1] if len(vals) > 1 else ""
        if tag == "file":
            self.open_file(vals[0])
        elif tag == "project":
            proj_id = int(vals[0])
            proj, msg = pm.open_project(proj_id)
            if proj:
                self.current_project = proj
                self._update_project_info()
                self.status(f"Project loaded: {proj['name']}", "green")
                # Expand
                self.proj_tree.item(sel[0], open=True)

    def _on_proj_right_click(self, event):
        item = self.proj_tree.identify_row(event.y)
        if item:
            self.proj_tree.selection_set(item)
            self._on_proj_select(None)
            self._proj_ctx.post(event.x_root, event.y_root)

    def _ctx_open_project(self):
        if self._selected_proj_id:
            proj, msg = pm.open_project(self._selected_proj_id)
            if proj:
                self.current_project = proj
                self._update_project_info()
                self.refresh_projects()
                self.status(f"Project: {proj['name']}", "green")

    def _ctx_rename_project(self):
        if not self._selected_proj_id:
            return
        new_name = simpledialog.askstring("Rename Project", "New name:")
        if new_name:
            ok, msg = pm.rename_project(self._selected_proj_id, new_name)
            self.status(msg, "green" if ok else "red")
            self.refresh_projects()

    def _ctx_new_file(self):
        if not self._selected_proj_id:
            messagebox.showinfo("No Project", "Select a project first.")
            return
        file_name = simpledialog.askstring("New File", "File name (e.g. utils.py):")
        if file_name:
            lang = detect_language(file_name)
            path, msg = pm.create_file_in_project(self._selected_proj_id, file_name, lang)
            if path:
                self.refresh_projects()
                self.open_file(path)
                self.status(f"Created: {file_name}", "green")
            else:
                self.status(msg, "red")

    def _ctx_export_project(self):
        if not self._selected_proj_id:
            return
        dest = filedialog.askdirectory(title="Select export destination")
        if dest:
            path, msg = pm.export_project_zip(self._selected_proj_id, dest)
            self.status(msg, "green" if path else "red")
            if path:
                messagebox.showinfo("Export Complete", f"Saved to:\n{path}")

    def _ctx_delete_project(self):
        if not self._selected_proj_id:
            return
        proj = db.get_project(self._selected_proj_id)
        if not proj:
            return
        if messagebox.askyesno("Delete Project",
                                f"Delete '{proj['name']}' permanently?\n(Files will be deleted!)"):
            ok, msg = pm.delete_project(self._selected_proj_id)
            self.status(msg, "green" if ok else "red")
            if ok and self.current_project and \
               self.current_project["id"] == self._selected_proj_id:
                self.current_project = None
                self._update_project_info()
            self.refresh_projects()

    def new_project_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Project")
        dialog.configure(bg=DARK["bg2"])
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        C = DARK
        pad = {"padx": 12, "pady": 6}

        tk.Label(dialog, text="Project Name:", bg=C["bg2"], fg=C["fg"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", **pad)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=32).grid(row=0, column=1, **pad)

        tk.Label(dialog, text="Language:", bg=C["bg2"], fg=C["fg"],
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", **pad)
        lang_var = tk.StringVar(value="Python")
        ttk.Combobox(dialog, textvariable=lang_var, width=30,
                     values=["Python", "JavaScript", "Java", "HTML", "CSS", "C", "C++"],
                     state="readonly").grid(row=1, column=1, **pad)

        tk.Label(dialog, text="Description:", bg=C["bg2"], fg=C["fg"],
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", **pad)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=32).grid(row=2, column=1, **pad)

        def create():
            n = name_var.get().strip()
            if not n:
                messagebox.showwarning("Missing Name", "Project name is required.")
                return
            ok, msg = pm.create_project(n, lang_var.get(), desc_var.get())
            if ok:
                self.refresh_projects()
                self.status(f"Project '{n}' created", "green")
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)

        btn_frame = tk.Frame(dialog, bg=C["bg2"])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Create", style="Accent.TButton",
                   command=create).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel",
                   command=dialog.destroy).pack(side="left", padx=6)

    def open_project_folder(self):
        folder = filedialog.askdirectory(title="Open Project Folder")
        if not folder:
            return
        name = Path(folder).name
        ok, msg = db.create_project(name, folder, "Python", "")
        if not ok and "already" not in msg.lower():
            messagebox.showerror("Error", msg)
            return
        projects = db.get_all_projects()
        for p in projects:
            if p["path"] == folder:
                proj, _ = pm.open_project(p["id"])
                if proj:
                    self.current_project = proj
                    self._update_project_info()
                    self.refresh_projects()
                    self.status(f"Opened folder: {name}", "green")
                break

    def _update_project_info(self):
        C = DARK
        self.proj_info_text.configure(state="normal")
        self.proj_info_text.delete("1.0", "end")
        if not self.current_project:
            self.proj_info_text.insert("1.0", "No project loaded.\n\nCreate or open a project to see info here.")
        else:
            p = self.current_project
            info = (
                f"Project: {p['name']}\n"
                f"Language: {p.get('language', 'N/A')}\n"
                f"Created: {p.get('created_at', 'N/A')[:10]}\n"
                f"Path: {p.get('path', 'N/A')}\n\n"
                f"Description:\n{p.get('description', 'No description')}\n\n"
                f"Files: {len(p.get('files', []))}\n"
            )
            self.proj_info_text.insert("1.0", info)
        self.proj_info_text.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════
    #  Snippet tree
    # ══════════════════════════════════════════════════════════════════════

    def refresh_snippets(self, *args):
        self.snip_tree.delete(*self.snip_tree.get_children())
        self._snip_items.clear()
        query = self.snip_search_var.get() if hasattr(self, "snip_search_var") else ""
        snippets = sm.get_snippets(query if query else None)
        cats = {}
        for s in snippets:
            cat = s["category"]
            if cat not in cats:
                cats[cat] = self.snip_tree.insert("", "end", text=f"📂  {cat}",
                                                   tags=("cat",))
            iid = self.snip_tree.insert(cats[cat], "end",
                                         text=f"  {_lang_icon(s['language'])}  {s['name']}",
                                         tags=("snippet",))
            self._snip_items[iid] = s

    def _get_selected_snippet(self):
        sel = self.snip_tree.selection()
        if sel:
            return self._snip_items.get(sel[0])
        return None

    def _on_snip_double_click(self, event):
        snip = self._get_selected_snippet()
        if snip:
            self._insert_snippet(snip)

    def _on_snip_right_click(self, event):
        item = self.snip_tree.identify_row(event.y)
        if item and item in self._snip_items:
            self.snip_tree.selection_set(item)
            self._snip_ctx.post(event.x_root, event.y_root)

    def _insert_snippet(self, snip):
        editor = self.current_editor()
        if not editor:
            self.new_file()
            editor = self.current_editor()
        if editor:
            editor.text.insert("insert", snip["code"])
            self.status(f"Inserted snippet: {snip['name']}", "green")

    def _ctx_insert_snippet(self):
        snip = self._get_selected_snippet()
        if snip:
            self._insert_snippet(snip)

    def _ctx_copy_snippet(self):
        snip = self._get_selected_snippet()
        if snip:
            self.clipboard_clear()
            self.clipboard_append(snip["code"])
            self.status("Snippet copied to clipboard", "green")

    def _ctx_edit_snippet(self):
        snip = self._get_selected_snippet()
        if snip:
            SnippetDialog(self, self, snippet=snip)

    def _ctx_delete_snippet(self):
        snip = self._get_selected_snippet()
        if snip:
            if messagebox.askyesno("Delete Snippet",
                                    f"Delete snippet '{snip['name']}'?"):
                sm.delete_snippet(snip["id"])
                self.refresh_snippets()
                self.status("Snippet deleted", "green")

    # ══════════════════════════════════════════════════════════════════════
    #  Global Search
    # ══════════════════════════════════════════════════════════════════════

    def _do_global_search(self):
        query = self.global_search_var.get().strip()
        self.search_results.configure(state="normal")
        self.search_results.delete("1.0", "end")
        self._search_result_map.clear()
        if not query:
            self.search_results.configure(state="disabled")
            return

        results = []
        # Search files
        files = db.get_all_files()
        for f in files:
            content = f.get("content", "")
            if query.lower() in content.lower() or query.lower() in f["name"].lower():
                results.append(("file", f["name"], f["path"], content))

        # Search snippets
        snips = db.search_snippets(query)
        for s in snips:
            results.append(("snippet", s["name"], s.get("code", "")[:60], ""))

        line_num = 1
        if results:
            for kind, name, loc, _ in results:
                icon = "📄" if kind == "file" else "📌"
                self.search_results.insert("end", f"{icon} {name}\n")
                if kind == "file":
                    self._search_result_map[line_num] = loc
                self.search_results.insert("end", f"   {str(loc)[:50]}\n\n")
                line_num += 3
        else:
            self.search_results.insert("end", "No results found.")
        self.search_results.configure(state="disabled")
        self.status(f"Found {len(results)} result(s) for '{query}'")

    def _on_search_result_click(self, event):
        line_num = int(self.search_results.index("@%d,%d" % (event.x, event.y)).split(".")[0])
        for ln, path in self._search_result_map.items():
            if abs(ln - line_num) <= 1 and Path(path).exists():
                self.open_file(path)
                break

    # ══════════════════════════════════════════════════════════════════════
    #  Code Runner
    # ══════════════════════════════════════════════════════════════════════

    def run_code(self):
        editor = self.current_editor()
        if not editor:
            self.status("No editor open", "red")
            return
        if self._execution_running:
            self.status("Already running – press Stop first", "yellow")
            return

        code = editor.get_content()
        language = editor.language
        self._execution_running = True
        self._last_error = ""

        self._console_write(f"▶ Running [{language}]  {datetime.now().strftime('%H:%M:%S')}\n",
                            "system")
        self._console_write("─" * 50 + "\n", "system")
        # Enable input bar immediately so user can send stdin any time
        self._enable_input()

        def on_output(line):
            self.after(0, self._console_write, line, "stdout")

        def on_input_needed(prompt):
            """Called from worker thread when input() is waiting."""
            self.after(0, self._enable_input, prompt)

        def on_finish(result):
            self._execution_running = False
            output = result.get("output", "")
            error  = result.get("error",  "")
            duration = result.get("duration", 0)
            status   = result.get("status",   "error")

            def _finish_ui():
                self._disable_input()
                if error:
                    self._last_error = error
                    self._console_write(error, "stderr", console="error")
                self._console_write("─" * 50 + "\n", "system")
                self._console_write(
                    f"{'✅ Done' if status == 'success' else '❌ Failed'} in {duration:.3f}s\n",
                    "success" if status == "success" else "stderr")
                self._log_write(
                    f"[{datetime.now().strftime('%H:%M:%S')}] {language} | "
                    f"{duration:.3f}s | {status}\n")
                fname = Path(editor.file_path).name if editor.file_path else "untitled"
                db.save_execution(fname, language, code[:500], output[:500],
                                   error[:500], duration, status)

            self.after(0, _finish_ui)

        # HTML/CSS: open in system browser instead of terminal runner
        if language in ("HTML", "CSS"):
            import tempfile, webbrowser, os
            if language == "CSS":
                # Wrap bare CSS in a minimal HTML page
                html_content = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CSS Preview</title>
<style>\n{code}\n</style></head>
<body><p style="font-family:sans-serif;color:#888;padding:20px">
CSS Preview — add HTML elements to see styles applied.</p></body></html>"""
            else:
                html_content = code
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8")
            tmp.write(html_content)
            tmp.close()
            webbrowser.open(f"file:///{tmp.name.replace(chr(92), '/')}")
            self._console_write("\n🌐 Opened in browser for preview.\n", "success")
            self._console_write("─" * 50 + "\n", "system")
            self._console_write("✅ Done in 0.000s\n", "success")
            self._execution_running = False
            self._disable_input()
            return


        # HTML/CSS: open in system browser instead of terminal runner
        if language in ("HTML", "CSS"):
            import tempfile as _tf, webbrowser, os
            if language == "CSS":
                html_content = f"""<!DOCTYPE html>\n<html><head><meta charset=\"UTF-8\"><title>CSS Preview</title>\n<style>\n{code}\n</style></head>\n<body><p style=\"font-family:sans-serif;color:#888;padding:20px\">CSS Preview</p></body></html>"""
            else:
                html_content = code
            _tmp = _tf.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
            _tmp.write(html_content)
            _tmp.close()
            webbrowser.open("file:///" + _tmp.name.replace("\\", "/"))
            self._console_write("\n\U0001f310 Opened in browser for preview.\n", "success")
            self._console_write("\u2500" * 50 + "\n", "system")
            self._console_write("\u2705 Done in 0.000s\n", "success")
            self._execution_running = False
            self._disable_input()
            return

        cr.run_code(code, language, timeout=120,
                    on_output=on_output, on_finish=on_finish,
                    on_input_needed=on_input_needed)

    def _enable_input(self, prompt=""):
        """Enable the input bar — show exact prompt so user knows what to type."""
        self._input_entry.configure(state="normal")
        self._input_send_btn.configure(state="normal")
        self._input_var.set("")
        self._input_entry.focus_set()
        if prompt and prompt.strip():
            label = prompt.strip()
            # Truncate very long prompts for display
            display = label if len(label) <= 60 else label[:57] + "…"
            self._input_hint.configure(
                text=f"▶  {display}",
                fg=DARK["yellow"])
            self.status(f"⌨  {display}  — type below and press Enter", "yellow")
        else:
            self._input_hint.configure(
                text="⌨  Program running — type input and press Enter",
                fg=DARK["cyan"])
            self.status("▶ Running — input bar active", "cyan")

    def _disable_input(self):
        """Disable the input bar when program is not waiting."""
        self._input_entry.configure(state="disabled")
        self._input_send_btn.configure(state="disabled")
        self._input_hint.configure(
            text="Run a program with input() to activate",
            fg=DARK["fg3"])

    def _on_input_submit(self, event=None):
        """Send typed input to the running process."""
        if not self._execution_running:
            return
        text = self._input_var.get().strip()
        if not text and self._input_entry.cget("state") == "disabled":
            return
        self._input_var.set("")
        # Keep bar enabled for C/C++ (silence-based) — disable only briefly
        # to show "sent" feedback; on_input_needed re-enables for next prompt
        self._input_entry.configure(state="disabled")
        self._input_send_btn.configure(state="disabled")
        self._input_hint.configure(
            text="⏳  Input sent — waiting for next prompt…",
            fg=DARK["fg3"])
        # Echo what the user typed in the console
        self._console_write(text + "\n", "input")
        # Send to process
        cr.send_input(text)

    def stop_execution(self):
        if cr.stop_execution():
            self._execution_running = False
            self._disable_input()
            self._console_write("\n⏹ Execution stopped.\n", "system")
            self.status("Execution stopped", "yellow")
        # Also send empty input to unblock any waiting input() call
        cr.send_input("")

    def _console_write(self, text, tag="stdout", console="output"):
        target = self.output_text if console == "output" else self.error_text
        target.configure(state="normal")
        target.insert("end", text, (tag,))
        target.see("end")
        target.configure(state="disabled")

    def _log_write(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_console(self):
        for t in (self.output_text, self.error_text, self.log_text):
            t.configure(state="normal")
            t.delete("1.0", "end")
            t.configure(state="disabled")
        self.status("Console cleared")

    # ══════════════════════════════════════════════════════════════════════
    #  AI Tools
    # ══════════════════════════════════════════════════════════════════════

    def explain_code(self):
        editor = self.current_editor()
        if not editor:
            return
        code = editor.get_selected() or editor.get_content()
        if not code.strip():
            return

        # Try OpenAI first
        api_key = db.get_setting("openai_key", "")
        if api_key:
            result = ai.try_openai_explain(code, api_key)
            if result:
                self._set_ai_text(result)
                return

        result = ai.explain_code(code)
        self._set_ai_text(ai.format_explanation(result))
        self.status("Code explained", "green")

    def review_code(self):
        editor = self.current_editor()
        if not editor:
            return
        code = editor.get_content()
        if not code.strip():
            return
        result = ai.review_code(code)
        self._set_ai_text(ai.format_review(result))
        self.status("Code reviewed", "green")

    def analyze_last_error(self):
        if not self._last_error:
            self._set_err_text("No error captured yet. Run some code first.")
            return
        analysis = ea.analyze_error(self._last_error)
        text = ea.format_error_analysis(analysis)
        self._set_err_text(text)
        self.status("Error analyzed", "green")

    def _set_ai_text(self, text):
        self.ai_text.configure(state="normal")
        self.ai_text.delete("1.0", "end")
        self.ai_text.insert("1.0", text)
        self.ai_text.configure(state="disabled")

    def _set_err_text(self, text):
        self.err_analysis_text.configure(state="normal")
        self.err_analysis_text.delete("1.0", "end")
        self.err_analysis_text.insert("1.0", text)
        self.err_analysis_text.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════
    #  Dialogs
    # ══════════════════════════════════════════════════════════════════════

    def show_find_replace(self):
        FindReplaceDialog(self, self)

    def show_settings(self):
        SettingsDialog(self, self)

    def show_statistics(self):
        StatisticsWindow(self)

    def _show_about(self):
        messagebox.showinfo(
            "About CodeVault AI",
            "CodeVault AI\nVersion 1.0\n\n"
            "Professional Python Coding Workspace\n"
            "Built with Tkinter, SQLite, and Pygments\n\n"
            "Features:\n"
            "  • Multi-tab code editor with syntax highlighting\n"
            "  • Project manager\n"
            "  • Snippet vault\n"
            "  • Code runner (Python + more)\n"
            "  • AI code explainer & reviewer\n"
            "  • Error analyzer with fix suggestions\n"
            "  • Statistics dashboard"
        )

    def _show_shortcuts(self):
        shortcuts = (
            "Keyboard Shortcuts\n"
            "══════════════════\n"
            "Ctrl+N    New File\n"
            "Ctrl+O    Open File\n"
            "Ctrl+S    Save\n"
            "Ctrl+W    Close Tab\n"
            "Ctrl+F    Find & Replace\n"
            "Ctrl+Z    Undo\n"
            "Ctrl+Y    Redo\n"
            "Ctrl+A    Select All\n"
            "Ctrl++    Zoom In\n"
            "Ctrl+-    Zoom Out\n"
            "F5        Run Code\n"
            "F6        Stop Execution\n"
            "Tab       Indent (4 spaces)\n"
            "Enter     Auto-indent\n"
        )
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    # ══════════════════════════════════════════════════════════════════════
    #  Status bar
    # ══════════════════════════════════════════════════════════════════════

    def status(self, msg, color=""):
        self.status_msg.set(msg)
        color_map = {
            "green": DARK["green"],
            "red": DARK["red"],
            "yellow": DARK["yellow"],
            "": DARK["fg2"]
        }
        self._status_label.configure(fg=color_map.get(color, DARK["fg2"]))
        # Reset after 5 seconds
        self.after(5000, lambda: self.status_msg.set("Ready"))


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _lang_icon(lang):
    icons = {
        "Python": "🐍", "JavaScript": "𝙅𝙎", "Java": "☕",
        "HTML": "🌐", "CSS": "🎨", "C": "⚙", "C++": "⚙",
        "Text": "📄", "Markdown": "📝", "JSON": "{}",
    }
    return icons.get(lang, "📄")


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Initialize DB
    db.initialize_database()

    # Seed snippets
    sm.seed_builtin_snippets()

    # Ensure directories
    for d in ("projects", "snippets", "backups", "assets", "config"):
        Path(d).mkdir(exist_ok=True)

    # Launch app
    app = CodeVaultApp()
    app.mainloop()


if __name__ == "__main__":
    main()
