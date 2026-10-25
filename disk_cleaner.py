#!/usr/bin/env python3
"""
Очистка диска: поиск дубликатов, больших файлов и временного мусора.
"""

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import track
from send2trash import send2trash

console = Console()

TEMP_PATTERNS = {
    "*.tmp", "*.temp", "*.log", "*.bak", "*.old", "*.swp",
    "Thumbs.db", ".DS_Store", "desktop.ini", "~$*"
}


def file_hash(path: Path, chunk_size: int = 8192) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(root: Path, min_size: int = 1024):
    """Находит дубликаты по содержимому."""
    hashes = defaultdict(list)

    files = [f for f in root.rglob("*") if f.is_file() and f.stat().st_size >= min_size]

    for file in track(files, description="Сканирую файлы..."):
        try:
            h = file_hash(file)
            hashes[h].append(file)
        except (PermissionError, OSError):
            continue

    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}

    if not duplicates:
        console.print("[green]Дубликаты не найдены.[/green]")
        return

    total_waste = 0
    table = Table(title="Найденные дубликаты")
    table.add_column("Размер", justify="right")
    table.add_column("Количество")
    table.add_column("Файлы", style="dim")

    for paths in sorted(duplicates.values(), key=lambda x: -x[0].stat().st_size):
        size = paths[0].stat().st_size
        waste = size * (len(paths) - 1)
        total_waste += waste
        names = "\n".join(str(p.relative_to(root)) for p in paths[:3])
        if len(paths) > 3:
            names += f"\n... и ещё {len(paths) - 3}"
        table.add_row(f"{size / 1024 / 1024:.1f} MB", str(len(paths)), names)

    console.print(table)
    console.print(f"\n[bold yellow]Можно освободить примерно {total_waste / 1024 / 1024:.1f} MB[/bold yellow]")


def find_large_files(root: Path, min_mb: float = 100):
    """Находит самые большие файлы."""
    min_bytes = int(min_mb * 1024 * 1024)
    large = []

    for file in track(list(root.rglob("*")), description="Ищу большие файлы..."):
        if file.is_file():
            try:
                size = file.stat().st_size
                if size >= min_bytes:
                    large.append((size, file))
            except (PermissionError, OSError):
                continue

    large.sort(reverse=True)

    if not large:
        console.print(f"[green]Файлов больше {min_mb} MB не найдено.[/green]")
        return

    table = Table(title=f"Файлы больше {min_mb} MB")
    table.add_column("Размер", justify="right", style="red")
    table.add_column("Путь")

    for size, path in large[:30]:
        table.add_row(f"{size / 1024 / 1024:.1f} MB", str(path.relative_to(root)))

    console.print(table)


def find_temp_files(root: Path):
    """Ищет временные и мусорные файлы."""
    found = []

    for pattern in TEMP_PATTERNS:
        found.extend(root.rglob(pattern))

    # Убираем директории
    found = [f for f in found if f.is_file()]

    if not found:
        console.print("[green]Временные файлы не найдены.[/green]")
        return

    total = sum(f.stat().st_size for f in found)

    table = Table(title="Временные / мусорные файлы")
    table.add_column("Размер", justify="right")
    table.add_column("Файл")

    for f in sorted(found, key=lambda x: -x.stat().st_size)[:40]:
        table.add_row(f"{f.stat().st_size / 1024:.1f} KB", str(f.relative_to(root)))

    console.print(table)
    console.print(f"\nВсего: {len(found)} файлов (~{total / 1024 / 1024:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Поиск мусора и дубликатов на диске")
    parser.add_argument("path", type=Path, nargs="?", default=Path.cwd(), help="Папка для сканирования")
    parser.add_argument("--find-duplicates", action="store_true", help="Искать дубликаты")
    parser.add_argument("--large", type=float, metavar="MB", help="Показать файлы больше N мегабайт")
    parser.add_argument("--temp", action="store_true", help="Искать временные файлы")

    args = parser.parse_args()

    if not args.path.exists():
        console.print(f"[red]Путь не существует: {args.path}[/red]")
        return

    if args.find_duplicates:
        find_duplicates(args.path)
    elif args.large:
        find_large_files(args.path, args.large)
    elif args.temp:
        find_temp_files(args.path)
    else:
        console.print("Укажите действие: --find-duplicates | --large 100 | --temp")
        parser.print_help()


if __name__ == "__main__":
    main()
