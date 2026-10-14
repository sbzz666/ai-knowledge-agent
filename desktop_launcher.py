"""Windows desktop launcher for Knowledge Agent."""

from __future__ import annotations

import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path


APP_NAME = "Knowledge Agent"


def _bundle_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def _user_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    path = base / "KnowledgeAgent"
    path.mkdir(parents=True, exist_ok=True)
    (path / "data").mkdir(exist_ok=True)
    return path


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    from streamlit.web import cli as streamlit_cli

    os.chdir(_user_data_dir())
    port = _free_port()
    threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    script = _bundle_root() / "streamlit_app.py"
    sys.argv = [
        APP_NAME,
        "run",
        str(script),
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
    ]
    streamlit_cli.main()


if __name__ == "__main__":
    main()
