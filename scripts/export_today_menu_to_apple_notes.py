#!/usr/bin/env python3
"""Replace a single Apple Notes note with today's selected workout menu."""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_MENUS = ROOT / "data/menus/current-menus.md"
NOTE_TITLE = "今日のトレーニングメニュー"

SECTION_STARTS = {
    "A": re.compile(r"^# A（"),
    "B": re.compile(r"^# B（"),
    "C": re.compile(r"^# C（"),
}

APPLE_SCRIPT = r'''
on run argv
    set noteTitle to item 1 of argv
    set noteBody to item 2 of argv

    tell application "Notes"
        set matchingNotes to every note whose name is noteTitle
        set matchCount to count of matchingNotes

        if matchCount > 1 then
            error "同名ノートが複数あります。重複を解消してから再実行してください: " & noteTitle
        else if matchCount = 1 then
            set body of item 1 of matchingNotes to noteBody
            return "updated"
        else
            set targetAccount to default account
            set targetFolder to default folder of targetAccount
            make new note at targetFolder with properties {body:noteBody}
            return "created"
        end if
    end tell
end run
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export an A, B, or C menu to one fixed Apple Notes note. "
            "The existing note body is replaced in full."
        )
    )
    parser.add_argument(
        "--menu",
        required=True,
        choices=tuple(SECTION_STARTS),
        help="Menu to export: A, B, or C.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Snapshot date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the snapshot without opening or changing Apple Notes.",
    )
    return parser.parse_args()


def validate_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise SystemExit(f"Invalid --date value: {value}") from exc


def extract_menu(markdown: str, menu: str) -> str:
    lines = markdown.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if SECTION_STARTS[menu].match(line)),
        None,
    )
    if start is None:
        raise SystemExit(f"Menu {menu} was not found in {CURRENT_MENUS}")

    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("# ")
        ),
        len(lines),
    )
    return "\n".join(lines[start:end]).strip()


def markdown_line_to_html(line: str) -> str:
    escaped = html.escape(line)
    if line.startswith("## "):
        return f"<h3>{html.escape(line[3:])}</h3>"
    if line.startswith("# "):
        return f"<h2>{html.escape(line[2:])}</h2>"
    if line.startswith("- "):
        return f"<div>• {html.escape(line[2:])}</div>"
    if not line:
        return "<br>"
    return f"<div>{escaped}</div>"


def build_note_body(menu_markdown: str, menu: str, snapshot_date: str) -> str:
    menu_html = "\n".join(
        markdown_line_to_html(line) for line in menu_markdown.splitlines()
    )
    return (
        f"<h1>{html.escape(NOTE_TITLE)}</h1>\n"
        f"<div>{html.escape(snapshot_date)} / Menu {html.escape(menu)}</div>\n"
        "<br>\n"
        f"{menu_html}"
    )


def build_plaintext_preview(menu_markdown: str, menu: str, snapshot_date: str) -> str:
    return f"{NOTE_TITLE}\n{snapshot_date} / Menu {menu}\n\n{menu_markdown}\n"


def write_apple_note(note_body: str) -> str:
    completed = subprocess.run(
        ["osascript", "-e", APPLE_SCRIPT, NOTE_TITLE, note_body],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(f"Apple Notes export failed: {detail}")
    return completed.stdout.strip()


def main() -> None:
    args = parse_args()
    snapshot_date = validate_date(args.date)
    source = CURRENT_MENUS.read_text(encoding="utf-8")
    menu_markdown = extract_menu(source, args.menu)

    if args.dry_run:
        print(build_plaintext_preview(menu_markdown, args.menu, snapshot_date), end="")
        return

    note_body = build_note_body(menu_markdown, args.menu, snapshot_date)
    result = write_apple_note(note_body)
    print(f"Apple Notes: {result} '{NOTE_TITLE}' with Menu {args.menu}")


if __name__ == "__main__":
    main()
