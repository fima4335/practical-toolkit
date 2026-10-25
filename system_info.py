#!/usr/bin/env python3
"""
Красивый отчёт о системе.
"""

import platform
import socket
import os
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

console = Console()


def get_size(bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} PB"


def main():
    # Основная информация
    uname = platform.uname()

    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="bold cyan")
    info_table.add_column()

    info_table.add_row("Система", f"{uname.system} {uname.release}")
    info_table.add_row("Версия", uname.version)
    info_table.add_row("Машина", uname.machine)
    info_table.add_row("Процессор", uname.processor or platform.processor() or "—")
    info_table.add_row("Имя хоста", socket.gethostname())
    info_table.add_row("Python", platform.python_version())

    # Диски
    disk_table = Table(title="Диски", show_header=True)
    disk_table.add_column("Точка монтирования")
    disk_table.add_column("Всего", justify="right")
    disk_table.add_column("Занято", justify="right")
    disk_table.add_column("Свободно", justify="right")
    disk_table.add_column("Использовано", justify="right")

    try:
        import shutil
        # Для простоты показываем корневой диск и домашнюю папку
        for path in [Path("/"), Path.home()]:
            try:
                usage = shutil.disk_usage(path)
                percent = usage.used / usage.total * 100
                disk_table.add_row(
                    str(path),
                    get_size(usage.total),
                    get_size(usage.used),
                    get_size(usage.free),
                    f"{percent:.1f}%"
                )
            except Exception:
                continue
    except Exception:
        disk_table.add_row("—", "—", "—", "—", "—")

    # Время
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    console.print(Panel(info_table, title="[bold]Информация о системе[/bold]", border_style="blue"))
    console.print(disk_table)
    console.print(f"\n[dim]Сформировано: {now}[/dim]")


if __name__ == "__main__":
    main()
