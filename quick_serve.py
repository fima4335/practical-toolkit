#!/usr/bin/env python3
"""
Красивый и быстрый HTTP-сервер для раздачи файлов.
Просто запусти в любой папке — и она станет доступна по сети.
"""

import argparse
import http.server
import socketserver
import socket
from pathlib import Path
from urllib.parse import unquote

from rich.console import Console
from rich.panel import Panel

console = Console()


class BeautifulHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        # Более аккуратные логи
        console.print(f"[dim]{self.address_string()}[/dim] — {args[0]}")

    def list_directory(self, path):
        try:
            file_list = list(Path(path).iterdir())
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None

        file_list.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

        html = ["""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Directory listing</title>
<style>
  :root { --bg: #0f172a; --card: #1e293b; --text: #e2e8f0; --accent: #38bdf8; --muted: #94a3b8; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); padding: 2rem; }
  h1 { font-size: 1.5rem; margin-bottom: 1.5rem; color: var(--accent); }
  .grid { display: grid; gap: 0.5rem; }
  a { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: var(--card); border-radius: 0.5rem; text-decoration: none; color: var(--text); transition: 0.15s; }
  a:hover { background: #334155; transform: translateX(4px); }
  .icon { font-size: 1.25rem; width: 1.5rem; text-align: center; }
  .name { flex: 1; }
  .size { color: var(--muted); font-size: 0.875rem; }
  .dir { color: var(--accent); }
</style>
</head>
<body>
<h1>📁 """ + Path(path).name + """</h1>
<div class="grid">
"""]

        # Parent directory
        if Path(path).resolve() != Path(self.directory).resolve():
            html.append('<a href="../"><span class="icon">⬆️</span><span class="name dir">..</span></a>')

        for item in file_list:
            name = item.name
            if item.is_dir():
                html.append(f'<a href="{name}/"><span class="icon">📂</span><span class="name dir">{name}/</span></a>')
            else:
                size = item.stat().st_size
                size_str = f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
                icon = "📄"
                if item.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                    icon = "🖼️"
                elif item.suffix.lower() in {".mp4", ".mkv", ".avi"}:
                    icon = "🎬"
                elif item.suffix.lower() in {".mp3", ".wav", ".flac"}:
                    icon = "🎵"
                elif item.suffix.lower() in {".zip", ".rar", ".7z"}:
                    icon = "📦"
                html.append(f'<a href="{name}"><span class="icon">{icon}</span><span class="name">{name}</span><span class="size">{size_str}</span></a>')

        html.append("</div></body></html>")
        encoded = "\n".join(html).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="Красивый быстрый HTTP-сервер")
    parser.add_argument("directory", nargs="?", default=".", help="Папка для раздачи (по умолчанию текущая)")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Порт (по умолчанию 8000)")

    args = parser.parse_args()
    directory = Path(args.directory).resolve()

    if not directory.is_dir():
        console.print(f"[red]Это не папка: {directory}[/red]")
        return

    handler = lambda *a, **kw: BeautifulHandler(*a, directory=str(directory), **kw)

    with socketserver.TCPServer(("", args.port), handler) as httpd:
        local_ip = get_local_ip()
        console.print(Panel.fit(
            f"[bold green]Сервер запущен![/bold green]\n\n"
            f"Локально:   [cyan]http://127.0.0.1:{args.port}[/cyan]\n"
            f"В сети:     [cyan]http://{local_ip}:{args.port}[/cyan]\n\n"
            f"Папка: [dim]{directory}[/dim]\n\n"
            f"Нажми Ctrl+C для остановки",
            title="Quick Serve",
            border_style="green"
        ))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Сервер остановлен.[/yellow]")


if __name__ == "__main__":
    main()
