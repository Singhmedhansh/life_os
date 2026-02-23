import os
import subprocess
import sys
from pathlib import Path
import re
import webbrowser


def find_app_path() -> Path:
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base_dir / "main.py"


def run_streamlit() -> subprocess.Popen:
    app_path = find_app_path()

    env = os.environ.copy()
    if "LIFE_OS_DATA_DIR" not in env:
        env["LIFE_OS_DATA_DIR"] = str(Path.home() / "LifeOS" / "data")

    # Simple: python -m streamlit run main.py (Streamlit opens browser)
    # We also stream logs and open the URL ourselves as a fallback.
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
                # Stream to this console
                print(line, end="")
                if not url_opened:
                    m = url_re.search(line)
                    if m:
                        url = m.group(2)
                        try:
                            webbrowser.open(url, new=1)
                            url_opened = True
                            print(f"\nOpened browser to: {url}\n")
                        except Exception:
                            # If opening fails, just continue streaming logs
                            pass
    except KeyboardInterrupt:
        pass


# Keep pure-browser open (Streamlit will open automatically)


def main():
    print("Starting LifeOS (Streamlit)… streaming logs below. Press Ctrl+C to stop.\n")
    proc = run_streamlit()
    try:
        stream_logs_and_open(proc)
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
    finally:
        # Make sure any remaining output is printed
        try:
            if proc.stdout:
                rest = proc.stdout.read().decode(errors="ignore")
                if rest:
                    print(rest)
        except Exception:
            pass


if __name__ == "__main__":
    main()
