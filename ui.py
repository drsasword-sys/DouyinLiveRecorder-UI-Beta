# -*- coding: utf-8 -*-
"""Local browser UI for DouyinLiveRecorder.

The existing recorder remains the source of truth. This module only edits
URL_config.ini and starts/stops one recorder process.
"""
from __future__ import annotations

import atexit
import json
import os
import re
import subprocess
import sys
import threading
import traceback
import webbrowser
import shutil
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


IS_FROZEN = bool(getattr(sys, "frozen", False))
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DIR = Path(sys.executable).resolve().parent if IS_FROZEN else Path(__file__).resolve().parent
MAIN_FILE = RESOURCE_DIR / "main.py"
URL_CONFIG = APP_DIR / "config" / "URL_config.ini"
OUTPUT_DIR = APP_DIR / "downloads"
CONFIG_TEMPLATE = RESOURCE_DIR / "config" / "config.example.ini"
URL_CONFIG_TEMPLATE = RESOURCE_DIR / "config" / "URL_config.example.ini"
HOST = "127.0.0.1"
try:
    PORT = int(os.environ.get("DOUYIN_RECORDER_PORT", "8765"))
except ValueError:
    PORT = 8765
if not 1024 <= PORT <= 65535:
    PORT = 8765
APP_VERSION = "0.1.0-beta.3"
ALLOWED_HOSTS = {
    "live.douyin.com",
    "v.douyin.com",
    "www.douyin.com",
    "www.tiktok.com",
    "tiktok.com",
}
CONFIG_LOCK = threading.Lock()
recorder_process: subprocess.Popen | None = None
recorder_log = None


class LocalHTTPServer(ThreadingHTTPServer):
    """Prevent multiple recorder UIs from sharing the same Windows port."""

    allow_reuse_address = False


def ensure_runtime_files() -> None:
    """Create user-editable runtime files without overwriting existing data."""
    config_dir = APP_DIR / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.ini"
    if not config_file.exists():
        shutil.copy2(CONFIG_TEMPLATE, config_file)
    if not URL_CONFIG.exists():
        if URL_CONFIG_TEMPLATE.exists():
            shutil.copy2(URL_CONFIG_TEMPLATE, URL_CONFIG)
        else:
            URL_CONFIG.write_text("", encoding="utf-8-sig")


def ensure_console_streams(log_name: str) -> None:
    """Provide log sinks when running as a windowed PyInstaller executable."""
    invalid_streams = []
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            invalid_streams.append(stream_name)

    if not invalid_streams:
        return

    console_log_path = APP_DIR / "logs" / log_name
    console_log_path.parent.mkdir(parents=True, exist_ok=True)
    console_log = console_log_path.open("a", encoding="utf-8", errors="replace")
    for stream_name in invalid_streams:
        setattr(sys, stream_name, console_log)


def prepare_recorder_runtime() -> None:
    """Prepare writable config and UTF-8 output before importing the recorder."""
    ensure_runtime_files()
    ensure_console_streams("recorder-console.log")


def validate_url(value: str) -> str:
    """Validate and normalize a supported public live URL."""
    url = value.strip()
    if re.search(r"[\x00-\x20<>\"'\\]", url):
        raise ValueError("Link chứa ký tự không an toàn.")
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or hostname not in ALLOWED_HOSTS:
        raise ValueError("Chỉ hỗ trợ link live Douyin hoặc TikTok hợp lệ.")
    if parsed.username or parsed.password or not parsed.path:
        raise ValueError("Link không hợp lệ.")
    return url.split("#", 1)[0]


def _line_url(line: str) -> str:
    match = re.search(r"https?://[^,\s]+", line)
    return match.group(0) if match else ""


def _read_lines() -> list[str]:
    if not URL_CONFIG.exists():
        return []
    return URL_CONFIG.read_text(encoding="utf-8-sig").splitlines()


def _write_lines(lines: list[str]) -> None:
    URL_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    if lines:
        content += "\n"
    URL_CONFIG.write_text(content, encoding="utf-8-sig")


def add_url(url: str, name: str = "") -> str:
    url = validate_url(url)
    clean_name = re.sub(r"[\r\n,]", " ", name.strip())[:120]
    with CONFIG_LOCK:
        lines = _read_lines()
        for index, line in enumerate(lines):
            if _line_url(line) == url:
                lines[index] = line.lstrip("#")
                _write_lines(lines)
                return url
        suffix = f",主播: {clean_name}" if clean_name else ""
        lines.append(f"{url}{suffix}")
        _write_lines(lines)
    return url


def stop_url(url: str) -> str:
    url = validate_url(url)
    changed = False
    with CONFIG_LOCK:
        lines = _read_lines()
        for index, line in enumerate(lines):
            if _line_url(line) == url and not line.lstrip().startswith("#"):
                lines[index] = "#" + line
                changed = True
        if changed:
            _write_lines(lines)
    return url


def configured_urls() -> list[dict[str, object]]:
    result = []
    with CONFIG_LOCK:
        for line in _read_lines():
            url = _line_url(line)
            if url:
                result.append({"url": url, "enabled": not line.lstrip().startswith("#")})
    return result


def ensure_recorder_started() -> None:
    global recorder_process, recorder_log
    if recorder_process and recorder_process.poll() is None:
        return
    if IS_FROZEN:
        recorder_command = [sys.executable, "--recorder"]
    else:
        recorder_python = Path(getattr(sys, "_base_executable", sys.executable))
        recorder_command = [str(recorder_python), str(MAIN_FILE)]
    log_path = APP_DIR / "logs" / "ui-recorder.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    recorder_log = log_path.open("a", encoding="utf-8", errors="replace")
    recorder_env = os.environ.copy()
    recorder_env["PYTHONIOENCODING"] = "utf-8"
    recorder_env["PYTHONUTF8"] = "1"
    if not IS_FROZEN:
        recorder_env["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
    recorder_process = subprocess.Popen(
        recorder_command,
        cwd=str(APP_DIR),
        stdin=subprocess.DEVNULL,
        stdout=recorder_log,
        stderr=subprocess.STDOUT,
        env=recorder_env,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def stop_recorder_process() -> None:
    if recorder_process and recorder_process.poll() is None:
        recorder_process.terminate()


def run_self_test() -> bool:
    """Verify packaged runtime dependencies without making network requests."""
    ensure_runtime_files()
    ensure_console_streams("self-test-console.log")
    errors: dict[str, str] = {}
    checks: dict[str, bool] = {
        "config_template": CONFIG_TEMPLATE.exists(),
        "url_template": URL_CONFIG_TEMPLATE.exists(),
        "ffmpeg": False,
        "node": False,
        "python_modules": False,
        "javascript_assets": (RESOURCE_DIR / "src" / "javascript" / "x-bogus.js").exists(),
    }
    try:
        import httpx  # noqa: F401
        import execjs  # noqa: F401
        from Crypto.Cipher import AES  # noqa: F401
        from src import spider, stream  # noqa: F401

        checks["python_modules"] = True
    except Exception as exc:
        checks["python_modules"] = False
        errors["python_modules"] = traceback.format_exc()

    ffmpeg_binary = APP_DIR / "ffmpeg" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    node_binary = APP_DIR / "node" / ("node.exe" if os.name == "nt" else "node")
    for key, binary, argument in (
        ("ffmpeg", ffmpeg_binary, "-version"),
        ("node", node_binary, "--version"),
    ):
        try:
            result = subprocess.run([str(binary), argument], capture_output=True, timeout=15)
            checks[key] = result.returncode == 0
        except (OSError, subprocess.SubprocessError) as exc:
            checks[key] = False
            errors[key] = f"{type(exc).__name__}: {exc}"

    report = {
        "version": APP_VERSION,
        "passed": all(checks.values()),
        "checks": checks,
        "errors": errors,
    }
    report_path = APP_DIR / "logs" / "self-test.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return bool(report["passed"])


atexit.register(stop_recorder_process)


HTML = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Douyin Live Recorder Beta</title>
<style>
:root{color-scheme:dark;font-family:Segoe UI,Arial,sans-serif;background:#101318;color:#eef2f7}
body{max-width:900px;margin:0 auto;padding:28px 16px}h1{margin:0 0 8px;font-size:26px}
.muted{color:#9ba7b5;margin:0 0 24px}.card{background:#1a2029;border:1px solid #2c3644;border-radius:16px;padding:16px;margin:12px 0}
input{box-sizing:border-box;width:100%;padding:12px;border-radius:10px;border:1px solid #435064;background:#0e131a;color:#fff;font-size:15px;margin:6px 0}
.row{display:flex;gap:8px;align-items:center}.row input{flex:1}.button{border:0;border-radius:10px;padding:11px 14px;cursor:pointer;font-weight:600;white-space:nowrap}
.start{background:#20c997;color:#07130f}.stop{background:#ff647c;color:#24070c}.live{background:#5b8cff;color:#fff}.ghost{background:#2a3442;color:#dbe5f2}
.item{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:12px 0;border-top:1px solid #2c3644}.item:first-child{border-top:0}
.url{word-break:break-all;color:#dbe5f2}.badge{font-size:12px;color:#9ba7b5;margin-top:4px}.off{opacity:.55}
#message{min-height:22px;color:#8ee6bd;margin:12px 0}@media(max-width:600px){.item{grid-template-columns:1fr}.row{flex-wrap:wrap}.row .button{flex:1}}
</style></head>
<body>
<h1>Douyin / TikTok Live Recorder <small>Beta 0.1.0</small></h1>
<p class="muted">Chạy local trên máy này · video lưu trong thư mục downloads</p>
<div class="card"><input id="url" placeholder="Dán link live Douyin/TikTok..."><input id="name" placeholder="Tên主播 (không bắt buộc)">
<div class="row"><button class="button start" onclick="startRecord()">▶ Bắt đầu ghi</button><button class="button ghost" onclick="refresh()">↻ Làm mới</button><button class="button live" onclick="openOutput()">📁 Mở output</button></div></div>
<div id="message"></div><div class="card"><h3>Danh sách phòng</h3><div id="rooms">Đang tải...</div></div>
<script>
const $=id=>document.getElementById(id); const msg=t=>{$('message').textContent=t;};
async function call(path,body){try{const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw Error(d.error||'Có lỗi');return d;}catch(e){if(e instanceof TypeError)throw Error('UI recorder chưa chạy. Hãy mở lại start_ui.bat.');throw e;}}
async function startRecord(){try{const url=$('url').value.trim();const name=$('name').value.trim();await call('/api/start',{url,name});$('url').value='';$('name').value='';msg('Đã bật theo dõi. Nếu live đang phát, recorder sẽ tạo file mới.');refresh();}catch(e){msg(e.message)}}
async function resumeRecord(url){try{await call('/api/start',{url});msg('Đã bật lại ghi cho phòng này; phiên mới sẽ được tạo.');refresh();}catch(e){msg(e.message)}}
async function stopRecord(url){try{await call('/api/stop',{url});msg('Đã dừng phòng này. File hiện tại sẽ được đóng/lưu; bấm Bắt đầu ghi để ghi phiên mới.');refresh();}catch(e){msg(e.message)}}
async function openOutput(){try{await call('/api/open-output',{});msg('Đã mở thư mục downloads.');}catch(e){msg(e.message)}}
function render(rooms){$('rooms').innerHTML=rooms.length?rooms.map(x=>`<div class="item ${x.enabled?'':'off'}"><div><div class="url">${escapeHtml(x.url)}</div><div class="badge">${x.enabled?'Đang theo dõi':'Đã tạm dừng'}</div></div><div class="row"><button class="button start" onclick="resumeRecord('${escapeJs(x.url)}')">▶</button><a class="button live" target="_blank" rel="noopener" href="${encodeURI(x.url)}">Go Live</a>${x.enabled?`<button class="button stop" onclick="stopRecord('${escapeJs(x.url)}')">Ⅱ Dừng</button>`:''}</div></div>`).join(''):'Chưa có phòng nào.'}
function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function escapeJs(s){return s.replace(/\\/g,'\\\\').replace(/'/g,"\\'")}
async function refresh(){try{const r=await fetch('/api/status');const d=await r.json();render(d.rooms)}catch(e){msg('Không kết nối được UI.')}} refresh();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _security_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'")

    def _json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 4096:
            raise ValueError("Dữ liệu yêu cầu quá lớn.")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:
        if self.path == "/":
            data = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/api/status":
            self._json({"rooms": configured_urls(), "recorder_running": bool(recorder_process and recorder_process.poll() is None)})
        else:
            self._json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        try:
            data = self._body()
            url = data.get("url", "")
            if self.path == "/api/start":
                normalized = add_url(url, data.get("name", ""))
                ensure_recorder_started()
                self._json({"url": normalized})
            elif self.path == "/api/stop":
                self._json({"url": stop_url(url)})
            elif self.path == "/api/open-output":
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                if os.name == "nt":
                    os.startfile(str(OUTPUT_DIR))
                else:
                    subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])
                self._json({"opened": True})
            else:
                self._json({"error": "Not found"}, 404)
        except (ValueError, json.JSONDecodeError, TypeError) as error:
            self._json({"error": str(error) or "Dữ liệu không hợp lệ."}, 400)
        except Exception:
            self._json({"error": "Không thể xử lý yêu cầu."}, 500)

    def log_message(self, _format: str, *_args: object) -> None:
        return


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(0 if run_self_test() else 1)
    elif "--recorder" in sys.argv:
        prepare_recorder_runtime()
        import main  # noqa: F401 - importing starts the upstream recorder loop
    else:
        ensure_runtime_files()
        try:
            server = LocalHTTPServer((HOST, PORT), Handler)
        except OSError:
            webbrowser.open(f"http://{HOST}:{PORT}")
            raise SystemExit(0)
        if sys.stdout is not None:
            print(f"UI đang chạy tại http://{HOST}:{PORT}")
            print("Đóng cửa sổ này sẽ dừng recorder do UI quản lý.")
        webbrowser.open(f"http://{HOST}:{PORT}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
            stop_recorder_process()
