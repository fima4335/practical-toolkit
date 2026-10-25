#!/usr/bin/env python3
"""
Массовое переименование файлов с предварительным просмотром.
"""

import argparse
import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Массовое переименование файлов")
    parser.add_argument("path", type=Path, help="Папка с файлами")
    parser.add_argument("--prefix", help="Добавить префикс")
    parser.add_argument("--suffix", help="Добавить суффикс (перед расширением)")
    parser.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"), help="Заменить текст в имени")
    parser.add_argument("--regex", nargs=2, metavar=("PATTERN", "REPL"), help="Замена по регулярному выражению")
    parser.add_argument("--lower", action="store_true", help="Перевести имена в нижний регистр")
    parser.add_argument("--upper", action="store_true", help="Перевести имена в верхний регистр")
    parser.add_argument("--number", action="store_true", help="Добавить порядковый номер (001, 002...)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Только показать (по умолчанию включено)")
    parser.add_argument("--apply", action="store_true", help="Реально переименовать")

    args = parser.parse_args()

    if not args.path.is_dir():
        console.print(f"[red]Это не папка: {args.path}[/red]")
        return

    files = sorted([f for f in args.path.iterdir() if f.is_file()], key=lambda x: x.name.lower())
    if not files:
        console.print("[yellow]Файлов нет.[/yellow]")
        return

    changes = []

    for i, file in enumerate(files, 1):
        stem = file.stem
        suffix = file.suffix

        new_stem = stem

        if args.replace:
            new_stem = new_stem.replace(args.replace[0], args.replace[1])
        if args.regex:
            new_stem = re.sub(args.regex[0], args.regex[1], new_stem)
        if args.lower:
            new_stem = new_stem.lower()
        if args.upper:
            new_stem = new_stem.upper()
        if args.prefix:
            new_stem = args.prefix + new_stem
        if args.suffix:
            new_stem = new_stem + args.suffix
        if args.number:
            new_stem = f"{i:03d}_{new_stem}"

        new_name = new_stem + suffix
        if new_name != file.name:
            changes.append((file, file.with_name(new_name)))

    if not changes:
        console.print("[green]Нечего переименовывать — все имена уже подходят.[/green]")
        return

    table = Table(title="Превью переименования")
    table.add_column("Было", style="red")
    table.add_column("Станет", style="green")

    for old, new in changes:
        table.add_row(old.name, new.name)

    console.print(table)
    console.print(f"\nВсего изменений: {len(changes)}")

    if args.apply:
        for old, new in changes:
            if new.exists():
                console.print(f"[red]Пропущено (уже существует): {new.name}[/red]")
                continue
            old.rename(new)
        console.print("[bold green]Готово! Файлы переименованы.[/bold green]")
    else:
        console.print("\n[yellow]Это превью. Чтобы применить изменения, добавь флаг --apply[/yellow]")


if __name__ == "__main__":
    main()
