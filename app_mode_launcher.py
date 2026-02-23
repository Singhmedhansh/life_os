import os
import re
import subprocess
import sys
from pathlib import Path
from shutil import which
import webbrowser


def find_app_path() -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base_dir / "main.py"


def get_app_mode_command(url: str):
    # Prefer Edge (ships with Windows), then Chrome
    edge_candidates = [
        which("msedge"),
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    chrome_candidates = [
        which("chrome"),
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
    ]

    for p in edge_candidates:
        if p and Path(p).exists():
            return (p, [p, f"--app={url}"])
    for p in chrome_candidates:
        if p and Path(p).exists():
            return (p, [p, f"--app={url}"])
    return None


def run_streamlit() -> subprocess.Popen:
    app_path = find_app_path()

    env = os.environ.copy()
    if "LIFE_OS_DATA_DIR" not in env:
        env["LIFE_OS_DATA_DIR"] = str(Path.home() / "LifeOS" / "data")

    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW

    return subprocess.Popen(
        cmd,
        cwd=str(app_path.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=creationflags,
    )


def stream_logs_and_open(proc: subprocess.Popen) -> None:
    url_opened = False
    url_re = re.compile(r"(Local|Network) URL:\s*(http://\S+)")
    try:
        if proc.stdout:
            while True:
                chunk = proc.stdout.readline()
                if not chunk:
                    break
                line = chunk.decode(errors="ignore")
                print(line, end="")
                if not url_opened:
                    m = url_re.search(line)
                    if m:
                        url = m.group(2)
                        # Try app-mode window first
                        result = get_app_mode_command(url)
                        if result:
                            browser_name, cmd = result
                            try:
                                subprocess.Popen(cmd, shell=False)
                                print(f"\nOpened app window using {Path(browser_name).name}: {url}\n")
                                url_opened = True
                                continue
                            except Exception as e:
                                print(f"\nFailed to open app window: {e}")
                        # Fallback to default browser
                        if not url_opened:
                            try:
                                webbrowser.open(url, new=1)
                                print(f"\nOpened default browser to: {url}\n")
                                url_opened = True
                            except Exception as e:
                                print(f"\nFailed to open browser: {e}")
    except KeyboardInterrupt:
        pass


def main():
    print("Starting LifeOS in app-mode… streaming logs below. Press Ctrl+C to stop.\n")
    proc = run_streamlit()
    try:
        stream_logs_and_open(proc)
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
    finally:
        try:
            if proc.stdout:
                rest = proc.stdout.read().decode(errors="ignore")
                if rest:
                    print(rest)
        except Exception:
            pass


if __name__ == "__main__":
    main()
