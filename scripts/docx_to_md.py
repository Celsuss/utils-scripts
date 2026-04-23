#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

import mammoth

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "docs" / "Dataiku Flow Documentation - B2C_FEATURE_STORES.docx"


def clean_markdown(text: str) -> str:
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def convert(input_path: Path, output_path: Path) -> None:
    with input_path.open("rb") as f:
        result = mammoth.convert_to_markdown(f)

    if result.messages:
        for msg in result.messages:
            print(f"WARNING: {msg}", file=sys.stderr)
        print(f"{len(result.messages)} warning(s) during conversion.", file=sys.stderr)

    output_path.write_text(clean_markdown(result.value), encoding="utf-8")
    print(f"Written: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a .docx file to Markdown.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    input_path: Path = args.input
    output_path: Path = args.output or input_path.with_suffix(".md")

    if not input_path.exists():
        sys.exit(f"Input file not found: {input_path}")

    convert(input_path, output_path)


if __name__ == "__main__":
    main()
