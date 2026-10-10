#!/usr/bin/env python3
"""Replace a single Apple Notes note with today's selected workout menu."""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from datetime import date


if __package__:
    from .fitness.paths import CURRENT_MENUS, ROOT
else:
    from fitness.paths import CURRENT_MENUS, ROOT
NOTE_TITLE = "今日のトレーニングメニュー"

SECTION_STARTS = {
    "A": re.compile(r"^# A（"),
    "B": re.compile(r"^# B（"),
    "C": re.compile(r"^# C（"),
}

C_MODE_LABELS = {
    "recovery": "Recovery",
    "standard": "Standard",
    "endurance": "Endurance",
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
        "--c-mode",
        choices=tuple(C_MODE_LABELS),
        help="For Menu C, export only Recovery, Standard, or Endurance.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the snapshot without opening or changing Apple Notes.",
    )
    return parser.parse_args(argv)


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
    return "\n".join(
        line for line in lines[start:end]
        if line not in {
            "<!-- next-session-trial:start -->",
            "<!-- next-session-trial:end -->",
        }
    ).strip()


def extract_c_mode(menu_markdown: str, c_mode: str) -> str:
    lines = menu_markdown.splitlines()
    label = C_MODE_LABELS[c_mode]
    first_section = next(
        (index for index, line in enumerate(lines) if line.startswith("## ")),
        len(lines),
    )
    mode_start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith(f"## {label}（")
        ),
        None,
    )
    if mode_start is None:
        raise SystemExit(f"Menu C mode {label} was not found in {CURRENT_MENUS}")
    mode_end = next(
        (
            index
            for index in range(mode_start + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        len(lines),
    )
    common_start = next(
        (
            index
            for index, line in enumerate(lines)
            if line == "## 共通の実施・中止基準"
        ),
        None,
    )
    if common_start is None:
        raise SystemExit(f"Menu C common rules were not found in {CURRENT_MENUS}")
    common_end = next(
        (
            index
            for index in range(common_start + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        len(lines),
    )
    selected = (
        lines[:first_section]
        + lines[mode_start:mode_end]
        + lines[common_start:common_end]
    )
    return "\n".join(selected).strip()


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


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.c_mode and args.menu != "C":
        raise SystemExit("--c-mode can only be used with --menu C")
    snapshot_date = validate_date(args.date)
    source = CURRENT_MENUS.read_text(encoding="utf-8")
    menu_markdown = extract_menu(source, args.menu)
    menu_label = args.menu
    if args.c_mode:
        menu_markdown = extract_c_mode(menu_markdown, args.c_mode)
        menu_label = f"C / {C_MODE_LABELS[args.c_mode]}"

    if args.dry_run:
        print(build_plaintext_preview(menu_markdown, menu_label, snapshot_date), end="")
        return

    note_body = build_note_body(menu_markdown, menu_label, snapshot_date)
    result = write_apple_note(note_body)
    print(f"Apple Notes: {result} '{NOTE_TITLE}' with Menu {menu_label}")


if __name__ == "__main__":
    main()
