"""
CodeVault AI - Code Runner
"""
import subprocess, threading, queue, time, sys, os, tempfile, re
from pathlib import Path

INPUT_MARKER = "\x00INPUT_NEEDED\x00"


class CodeRunner:
    def __init__(self):
        self._process         = None
        self._lock            = threading.Lock()
        self._stdin_queue     = []
        self._stdin_event     = threading.Event()
        self._on_input_needed = None

    def run(self, code, language="Python", timeout=60,
            on_output=None, on_finish=None, on_input_needed=None):
        self._on_input_needed = on_input_needed
        self._stdin_queue.clear()
        self._stdin_event.clear()
        t = threading.Thread(
            target=self._run_thread,
            args=(code, language, timeout, on_output, on_finish),
            daemon=True)
        t.start()
        return t

    def send_input(self, text):
        self._stdin_queue.append(text + "\n")
        self._stdin_event.set()

    def stop(self):
        with self._lock:
            if self._process and self._process.poll() is None:
                try:
                    self._process.terminate()
                    time.sleep(0.2)
                    if self._process.poll() is None:
                        self._process.kill()
                    return True
                except Exception:
                    pass
        return False

    # ──────────────────────────────────────────────────────────────────────
    def _run_thread(self, code, language, timeout, on_output, on_finish):
        start = time.time()
        try:
            if   language == "Python":
                result = self._run_python(code, timeout, on_output)
            elif language == "JavaScript":
                result = self._run_js(code, timeout, on_output)
            elif language == "Java":
                result = self._run_java(code, timeout, on_output)
            elif language in ("C", "C++"):
                result = self._run_c(code, language, timeout, on_output)
            else:
                result = {"output": f"Preview not supported for {language}.\n",
                          "error": "", "duration": 0, "status": "unsupported"}
        except Exception as exc:
            result = {"output": "", "error": f"Runner error: {exc}",
                      "duration": time.time() - start, "status": "error"}
        if on_finish:
            on_finish(result)

    # ══════════════════════════════════════════════════════════════════════
    # PYTHON — marker injected via wrapper
    # ══════════════════════════════════════════════════════════════════════
    def _run_python(self, code, timeout, on_output):
        M   = INPUT_MARKER
        hdr = (
            "import sys, builtins\n"
            "def input(prompt=''):\n"
            "    if prompt:\n"
            "        sys.stdout.write(str(prompt)); sys.stdout.flush()\n"
            "    sys.stdout.write('" + M + "'); sys.stdout.flush()\n"
            "    return sys.stdin.readline().rstrip('\\n')\n"
            "builtins.input = input\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False, encoding="utf-8") as f:
            f.write(hdr + code); tmp = f.name
        try:
            return self._exec_marker([sys.executable, "-u", tmp], timeout, on_output)
        finally:
            try: os.unlink(tmp)
            except Exception: pass

    # ══════════════════════════════════════════════════════════════════════
    # JAVASCRIPT — patches readline.createInterface
    # ══════════════════════════════════════════════════════════════════════
    def _run_js(self, code, timeout, on_output):
        M = INPUT_MARKER
        hdr = (
            "const _rl = require('readline');\n"
            "const _origCI = _rl.createInterface.bind(_rl);\n"
            "_rl.createInterface = function(opts) {\n"
            "    const iface = _origCI(opts);\n"
            "    const _oq = iface.question.bind(iface);\n"
            "    iface.question = function(prompt, cb) {\n"
            "        if (prompt) { process.stdout.write(String(prompt)); }\n"
            "        process.stdout.write('" + M + "');\n"
            "        _oq('', cb);\n"
            "    };\n"
            "    return iface;\n"
            "};\n\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js",
                                          delete=False, encoding="utf-8") as f:
            f.write(hdr + code); tmp = f.name
        try:
            return self._exec_marker(["node", tmp], timeout, on_output)
        finally:
            try: os.unlink(tmp)
            except Exception: pass

    # ══════════════════════════════════════════════════════════════════════
    # JAVA — injects __GUIScanner__ subclass that emits marker
    # ══════════════════════════════════════════════════════════════════════
    def _run_java(self, code, timeout, on_output):
        M     = INPUT_MARKER
        match = re.search(r"public\s+class\s+(\w+)", code)
        cname = match.group(1) if match else "Main"

        scanner = (
            "import java.util.Scanner;\n"
            "import java.io.*;\n\n"
            "class __GUIScanner__ extends Scanner {\n"
            "    public __GUIScanner__(InputStream in){super(in);}\n"
            "    private void _s(){\n"
            '        System.out.print("' + M + '");\n'
            "        System.out.flush();}\n"
            "    @Override public String  nextLine()   {_s();return super.nextLine();}\n"
            "    @Override public String  next()       {_s();return super.next();}\n"
            "    @Override public int     nextInt()    {_s();return super.nextInt();}\n"
            "    @Override public double  nextDouble() {_s();return super.nextDouble();}\n"
            "    @Override public long    nextLong()   {_s();return super.nextLong();}\n"
            "    @Override public float   nextFloat()  {_s();return super.nextFloat();}\n"
            "    @Override public boolean nextBoolean(){_s();return super.nextBoolean();}\n"
            "}\n\n"
        )
        patched = re.sub(r'new\s+Scanner\s*\(\s*System\.in\s*\)',
                         'new __GUIScanner__(System.in)', code)
        patched = re.sub(r'import\s+java\.util\.Scanner\s*;\s*\n?', '', patched)

        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, f"{cname}.java")
            with open(src, "w", encoding="utf-8") as f:
                f.write(scanner + patched)
            cr = self._exec_marker(["javac", src], 15, None)
            if cr["error"] and "error:" in cr["error"].lower():
                return cr
            return self._exec_marker(["java", "-cp", td, cname], timeout, on_output)

    # ══════════════════════════════════════════════════════════════════════
    # C / C++ — compile clean, run via silence detector
    # ══════════════════════════════════════════════════════════════════════
    def _run_c(self, code, language, timeout, on_output):
        ext = ".c" if language == "C" else ".cpp"
        cc  = "gcc" if language == "C" else "g++"
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, f"prog{ext}")
            exe = os.path.join(td, "prog.exe" if sys.platform=="win32" else "prog")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)
            cr = self._exec_marker([cc, src, "-o", exe], 15, None)
            if cr["error"] and "error:" in cr["error"].lower():
                return cr
            return self._exec_silence([exe], timeout, on_output)

    # ══════════════════════════════════════════════════════════════════════
    # EXECUTOR A — marker-based (Python / JS / Java)
    # ══════════════════════════════════════════════════════════════════════
    def _exec_marker(self, cmd, timeout, on_output):
        start = time.time()
        out_lines, err_lines = [], []
        try:
            with self._lock:
                self._process = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    bufsize=0,
                    creationflags=(subprocess.CREATE_NO_WINDOW
                                   if sys.platform=="win32" else 0))

            threading.Thread(
                target=lambda: [err_lines.append(
                    l.decode("utf-8", errors="replace"))
                    for l in self._process.stderr],
                daemon=True).start()

            buf = ""
            while self._process.poll() is None:
                try:
                    ch = self._process.stdout.read(1)
                    if not ch: break
                except Exception: break
                buf += ch.decode("utf-8", errors="replace")

                if INPUT_MARKER in buf:
                    prompt = buf.replace(INPUT_MARKER, "").strip()
                    buf = ""
                    if prompt:
                        out_lines.append(prompt + "\n")
                        if on_output: on_output(prompt + "\n")
                    # Signal GUI with the exact prompt text
                    user_in = self._request_input(prompt)
                    if user_in is None: break
                    echo = user_in + "\n"
                    out_lines.append(echo)
                    if on_output: on_output(echo)
                    try:
                        self._process.stdin.write((user_in+"\n").encode())
                        self._process.stdin.flush()
                    except Exception: break

                elif "\n" in buf:
                    parts = buf.split("\n")
                    for p in parts[:-1]:
                        line = p + "\n"
                        out_lines.append(line)
                        if on_output: on_output(line)
                    buf = parts[-1]
                elif len(buf) > 4096:
                    out_lines.append(buf)
                    if on_output: on_output(buf)
                    buf = ""

            if buf:
                out_lines.append(buf)
                if on_output: on_output(buf)
            try:
                rem = self._process.stdout.read()
                if rem:
                    t = rem.decode("utf-8", errors="replace")\
                           .replace(INPUT_MARKER, "")
                    if t:
                        out_lines.append(t)
                        if on_output: on_output(t)
            except Exception: pass

        except FileNotFoundError:
            return {"output":"","error":f"Command not found: {cmd[0]}",
                    "duration":time.time()-start,"status":"error"}
        except Exception as e:
            return {"output":"","error":str(e),
                    "duration":time.time()-start,"status":"error"}

        return self._build_result(out_lines, err_lines, start)

    # ══════════════════════════════════════════════════════════════════════
    # EXECUTOR B — silence-based (C / C++)
    # A background thread feeds bytes into a queue.Queue.
    # queue.get(timeout=SILENCE) times out when the process stops writing
    # (i.e. it is blocked on scanf/cin waiting for stdin).
    # We then treat the incomplete line in buf as the prompt text.
    # ══════════════════════════════════════════════════════════════════════
    def _exec_silence(self, cmd, timeout, on_output, silence=0.35):
        start = time.time()
        out_lines, err_lines = [], []
        try:
            with self._lock:
                self._process = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    bufsize=0,
                    creationflags=(subprocess.CREATE_NO_WINDOW
                                   if sys.platform=="win32" else 0))

            threading.Thread(
                target=lambda: [err_lines.append(
                    l.decode("utf-8", errors="replace"))
                    for l in self._process.stderr],
                daemon=True).start()

            byte_q = queue.Queue()

            def _reader():
                try:
                    while True:
                        ch = self._process.stdout.read(1)
                        if not ch: break
                        byte_q.put(ch)
                except Exception: pass
                byte_q.put(None)          # sentinel

            threading.Thread(target=_reader, daemon=True).start()

            buf           = ""
            waiting_input = False         # are we currently waiting for user?

            while True:
                try:
                    ch = byte_q.get(timeout=silence)
                except queue.Empty:
                    # ── Silence detected ───────────────────────────────────
                    # Only treat as prompt if:
                    #   • process is still running
                    #   • buf has content (the prompt text)
                    #   • buf has NO trailing newline (incomplete line)
                    #   • we are not already waiting for input
                    if (buf and "\n" not in buf
                            and self._process.poll() is None
                            and not waiting_input):
                        prompt = buf.strip()
                        buf    = ""
                        # Show prompt in console output
                        out_lines.append(prompt + "\n")
                        if on_output: on_output(prompt + "\n")
                        waiting_input = True
                        # Tell GUI exactly what prompt to show
                        user_in = self._request_input(prompt)
                        waiting_input = False
                        if user_in is None: break
                        echo = user_in + "\n"
                        out_lines.append(echo)
                        if on_output: on_output(echo)
                        try:
                            self._process.stdin.write((user_in+"\n").encode())
                            self._process.stdin.flush()
                        except Exception: break
                    continue

                if ch is None: break      # sentinel — stdout closed

                buf += ch.decode("utf-8", errors="replace")

                if "\n" in buf:
                    parts = buf.split("\n")
                    for p in parts[:-1]:
                        line = p + "\n"
                        out_lines.append(line)
                        if on_output: on_output(line)
                    buf = parts[-1]
                elif len(buf) > 4096:
                    out_lines.append(buf)
                    if on_output: on_output(buf)
                    buf = ""

            if buf:
                out_lines.append(buf)
                if on_output: on_output(buf)

        except FileNotFoundError:
            return {"output":"","error":f"Command not found: {cmd[0]}",
                    "duration":time.time()-start,"status":"error"}
        except Exception as e:
            return {"output":"","error":str(e),
                    "duration":time.time()-start,"status":"error"}

        return self._build_result(out_lines, err_lines, start)

    # ──────────────────────────────────────────────────────────────────────
    def _request_input(self, prompt):
        """Block until GUI sends input, showing the prompt in the input bar."""
        self._stdin_event.clear()
        if self._on_input_needed:
            self._on_input_needed(prompt)        # → _enable_input(prompt)
        deadline = time.time() + 300
        while time.time() < deadline:
            if self._process and self._process.poll() is not None:
                return None
            if self._stdin_queue:
                return self._stdin_queue.pop(0).rstrip("\n")
            self._stdin_event.wait(timeout=0.1)
            self._stdin_event.clear()
        return ""

    def _build_result(self, out_lines, err_lines, start):
        rc  = (self._process.returncode
               if self._process and self._process.poll() is not None else -1)
        out = "".join(out_lines)
        err = "".join(err_lines)
        ok  = rc == 0 or rc == -1 or (not err.strip() and out.strip())
        return {"output": out, "error": err,
                "duration": time.time()-start,
                "status": "success" if ok else "error"}


# ── Singleton ──────────────────────────────────────────────────────────────
_runner = CodeRunner()

def run_code(code, language="Python", timeout=60,
             on_output=None, on_finish=None, on_input_needed=None):
    return _runner.run(code, language, timeout,
                       on_output, on_finish, on_input_needed)

def stop_execution():  return _runner.stop()
def send_input(text):  _runner.send_input(text)
