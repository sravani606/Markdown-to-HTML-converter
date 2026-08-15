#!/usr/bin/env python3
"""
md2html.py
Command-line interface for converting Markdown files to HTML.

Usage:
    python md2html.py input.md
    python md2html.py input.md -o output.html
    python md2html.py input.md --standalone --title "My Page"
    cat input.md | python md2html.py
"""

import argparse
import sys

from converter import markdown_to_html, wrap_html_document

DEFAULT_CSS = """\
body { font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
       max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #222; }
pre { background: #f5f5f5; padding: 12px; overflow-x: auto; border-radius: 6px; }
code { background: #f0f0f0; padding: 2px 4px; border-radius: 4px; font-size: 0.9em; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #ddd; margin: 0; padding-left: 16px; color: #555; }
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2html",
        description="Convert Markdown files to HTML.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the input .md file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to write the HTML output. Prints to stdout if omitted.",
    )
    parser.add_argument(
        "-s", "--standalone",
        action="store_true",
        help="Wrap the output in a full HTML document (with <html>, <head>, styling).",
    )
    parser.add_argument(
        "-t", "--title",
        default="Document",
        help="Title for the HTML document (used with --standalone). Default: 'Document'",
    )
    parser.add_argument(
        "--no-css",
        action="store_true",
        help="Omit the default CSS when using --standalone.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                markdown_text = f.read()
        except OSError as exc:
            print(f"Error: could not read '{args.input}': {exc}", file=sys.stderr)
            return 1
    else:
        markdown_text = sys.stdin.read()

    body_html = markdown_to_html(markdown_text)

    if args.standalone:
        css = None if args.no_css else DEFAULT_CSS
        output = wrap_html_document(body_html, title=args.title, css=css)
    else:
        output = body_html

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
        except OSError as exc:
            print(f"Error: could not write '{args.output}': {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
