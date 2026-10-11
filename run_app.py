from __future__ import annotations

import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PORT = 8000


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> None:
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(ROOT), **kwargs)
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as server:
        url = f"http://127.0.0.1:{PORT}/app/index.html?v=tentec-layers"
        print(f"TEN-T simulation running at {url}")
        print("Press Ctrl+C to stop the server.")
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        server.serve_forever()


if __name__ == "__main__":
    main()
