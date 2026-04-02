from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def log(message: str) -> None:
    print(f"[fix_subtitles] {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply corrections to subtitle files (SRT/ASS) using a JSON corrections file."
    )
    parser.add_argument(
        "--corrections",
        required=True,
        help='Path to JSON corrections file. Format: [{"old": "原文", "new": "修正"}, ...]',
    )
    parser.add_argument("--srt", help="Path to the SRT file to correct.")
    parser.add_argument("--ass", help="Path to the ASS file to correct.")
    parser.add_argument("--txt", help="Path to the TXT file to correct.")
    return parser.parse_args()


def load_corrections(corrections_path: Path) -> list[dict[str, str]]:
    if not corrections_path.exists():
        raise FileNotFoundError(f"Corrections file not found: {corrections_path}")

    with corrections_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Corrections JSON must be an array of objects.")

    for i, item in enumerate(data):
        if not isinstance(item, dict) or "old" not in item or "new" not in item:
            raise ValueError(
                f'Corrections item {i} is invalid. Each item must have "old" and "new" keys.'
            )

    return data


def apply_corrections(content: str, corrections: list[dict[str, str]]) -> tuple[str, int]:
    total_count = 0
    for item in corrections:
        old = item["old"]
        new = item["new"]
        if old and old in content:
            count = content.count(old)
            content = content.replace(old, new)
            total_count += count
    return content, total_count


def fix_file(file_path: Path, corrections: list[dict[str, str]]) -> int:
    if not file_path.exists():
        log(f"File not found, skipping: {file_path}")
        return 0

    content = file_path.read_text(encoding="utf-8-sig")
    corrected, count = apply_corrections(content, corrections)

    if count > 0:
        file_path.write_text(corrected, encoding="utf-8-sig")
        log(f"Applied {count} replacements to {file_path.name}")
    else:
        log(f"No matches found in {file_path.name}")

    return count


def main() -> int:
    args = parse_args()

    corrections_path = Path(args.corrections).expanduser().resolve()

    try:
        corrections = load_corrections(corrections_path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    log(f"Loaded {len(corrections)} correction rules from {corrections_path.name}")

    total = 0

    if args.srt:
        srt_path = Path(args.srt).expanduser().resolve()
        total += fix_file(srt_path, corrections)

    if args.ass:
        ass_path = Path(args.ass).expanduser().resolve()
        total += fix_file(ass_path, corrections)

    if args.txt:
        txt_path = Path(args.txt).expanduser().resolve()
        total += fix_file(txt_path, corrections)

    if not args.srt and not args.ass and not args.txt:
        print("ERROR: At least one of --srt or --ass must be provided.", file=sys.stderr)
        return 1

    log(f"Done. Total replacements: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
