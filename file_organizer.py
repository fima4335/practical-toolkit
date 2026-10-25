#!/usr/bin/env python3
"""
Умный организатор файлов.
Сортирует файлы по типу, дате создания или размеру.
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

# Категории по расширениям
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic", ".raw"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".rtf", ".odt"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".php", ".rb", ".json", ".xml", ".yaml", ".yml"},
    "Executables": {".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".AppImage"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2"},
}


def get_category(path: Path) -> str:
    ext = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def organize_by_type(source: Path, dry_run: bool = False):
    stats = defaultdict(int)

    files = [f for f in source.iterdir() if f.is_file()]
    if not files:
        console.print("[yellow]Нет файлов для сортировки.[/yellow]")
        return

    for file in track(files, description="Сортирую по типу..."):
        category = get_category(file)
        target_dir = source / category
        target = target_dir / file.name

        if dry_run:
            console.print(f"  {file.name} → {category}/")
        else:
            target_dir.mkdir(exist_ok=True)
            # Избегаем перезаписи
            counter = 1
            while target.exists():
                target = target_dir / f"{file.stem}_{counter}{file.suffix}"
                counter += 1
            shutil.move(str(file), str(target))
        stats[category] += 1

    show_stats(stats, dry_run)


def organize_by_date(source: Path, dry_run: bool = False):
    stats = defaultdict(int)

    files = [f for f in source.iterdir() if f.is_file()]
    if not files:
        console.print("[yellow]Нет файлов для сортировки.[/yellow]")
        return

    for file in track(files, description="Сортирую по дате..."):
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        folder_name = mtime.strftime("%Y-%m")
        target_dir = source / folder_name
        target = target_dir / file.name

        if dry_run:
            console.print(f"  {file.name} → {folder_name}/")
        else:
            target_dir.mkdir(exist_ok=True)
            counter = 1
            while target.exists():
                target = target_dir / f"{file.stem}_{counter}{file.suffix}"
                counter += 1
            shutil.move(str(file), str(target))
        stats[folder_name] += 1

    show_stats(stats, dry_run)


def show_stats(stats: dict, dry_run: bool):
    table = Table(title="Результат" + (" (dry-run)" if dry_run else ""))
    table.add_column("Папка", style="cyan")
    table.add_column("Файлов", justify="right", style="green")

    for name, count in sorted(stats.items()):
        table.add_row(name, str(count))

    console.print(table)
    if dry_run:
        console.print("\n[bold yellow]Это был dry-run. Файлы не перемещались.[/bold yellow]")


def main():
    parser = argparse.ArgumentParser(description="Умный организатор файлов")
    parser.add_argument("path", type=Path, help="Путь к папке")
    parser.add_argument("--by", choices=["type", "date"], default="type", help="Критерий сортировки")
    parser.add_argument("--dry-run", action="store_true", help="Показать, что будет сделано, без реальных изменений")

    args = parser.parse_args()

    if not args.path.exists() or not args.path.is_dir():
        console.print(f"[red]Ошибка: {args.path} не является папкой[/red]")
        return

    console.print(f"\n[bold]Организация:[/bold] {args.path}")
    console.print(f"[bold]Режим:[/bold] по {'типу' if args.by == 'type' else 'дате'}\n")

    if args.by == "type":
        organize_by_type(args.path, args.dry_run)
    else:
        organize_by_date(args.path, args.dry_run)


if __name__ == "__main__":
    main()
