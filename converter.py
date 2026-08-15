"""
converter.py
A lightweight Markdown -> HTML converter with no external dependencies.

Supports:
- Headers (# through ######)
- Bold (**text** or __text__) and italic (*text* or _text_)
- Inline code (`code`) and fenced code blocks (```lang ... ```)
- Links [text](url) and images ![alt](url)
- Unordered lists (-, *, +) and ordered lists (1. 2. ...)
- Blockquotes (> text)
- Horizontal rules (---, ***, ___)
- Paragraphs (blank-line separated)

This is a deliberately compact implementation covering common Markdown
syntax — not a full CommonMark implementation.
"""

import html
import re
from typing import List

HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
HR_RE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
UL_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
OL_RE = re.compile(r"^(\s*)\d+\.\s+(.*)$")
BLOCKQUOTE_RE = re.compile(r"^>\s?(.*)$")
FENCE_RE = re.compile(r"^```(\w*)\s*$")

INLINE_CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"(\*\*|__)(.+?)\1")
ITALIC_RE = re.compile(r"(\*|_)(.+?)\1")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")


def _escape(text: str) -> str:
    return html.escape(text, quote=False)


def _inline(text: str) -> str:
    """Apply inline-level transformations: code, images, links, bold, italic."""
    # Protect inline code first so its contents aren't touched by other rules
    placeholders = []

    def stash_code(match: "re.Match") -> str:
        placeholders.append(_escape(match.group(1)))
        return f"\x00{len(placeholders) - 1}\x00"

    text = INLINE_CODE_RE.sub(stash_code, text)
    text = _escape(text)

    text = IMAGE_RE.sub(
        lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}"'
        + (f' title="{m.group(3)}"' if m.group(3) else "")
        + ">",
        text,
    )
    text = LINK_RE.sub(
        lambda m: f'<a href="{m.group(2)}"'
        + (f' title="{m.group(3)}"' if m.group(3) else "")
        + f">{m.group(1)}</a>",
        text,
    )
    text = BOLD_RE.sub(r"<strong>\2</strong>", text)
    text = ITALIC_RE.sub(r"<em>\2</em>", text)

    # Restore protected inline code
    def restore_code(match: "re.Match") -> str:
        idx = int(match.group(1))
        return f"<code>{placeholders[idx]}</code>"

    text = re.sub(r"\x00(\d+)\x00", restore_code, text)
    return text


def markdown_to_html(markdown_text: str) -> str:
    """Convert a Markdown string to an HTML fragment."""
    lines = markdown_text.splitlines()
    html_lines: List[str] = []

    i = 0
    paragraph_buffer: List[str] = []
    list_stack: List[str] = []  # tracks open <ul>/<ol> tags

    def flush_paragraph():
        if paragraph_buffer:
            joined = " ".join(paragraph_buffer)
            html_lines.append(f"<p>{_inline(joined)}</p>")
            paragraph_buffer.clear()

    def close_lists():
        while list_stack:
            html_lines.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        fence_match = FENCE_RE.match(line)
        if fence_match:
            flush_paragraph()
            close_lists()
            lang = fence_match.group(1)
            code_lines = []
            i += 1
            while i < len(lines) and not FENCE_RE.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            code_html = _escape("\n".join(code_lines))
            lang_attr = f' class="language-{lang}"' if lang else ""
            html_lines.append(f"<pre><code{lang_attr}>{code_html}</code></pre>")
            i += 1  # skip closing fence
            continue

        # Blank line -> paragraph/list break
        if line.strip() == "":
            flush_paragraph()
            close_lists()
            i += 1
            continue

        # Horizontal rule
        if HR_RE.match(line):
            flush_paragraph()
            close_lists()
            html_lines.append("<hr>")
            i += 1
            continue

        # Header
        header_match = HEADER_RE.match(line)
        if header_match:
            flush_paragraph()
            close_lists()
            level = len(header_match.group(1))
            content = _inline(header_match.group(2).strip())
            html_lines.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # Blockquote
        bq_match = BLOCKQUOTE_RE.match(line)
        if bq_match:
            flush_paragraph()
            close_lists()
            quote_lines = [bq_match.group(1)]
            i += 1
            while i < len(lines) and BLOCKQUOTE_RE.match(lines[i]):
                quote_lines.append(BLOCKQUOTE_RE.match(lines[i]).group(1))
                i += 1
            inner = markdown_to_html("\n".join(quote_lines))
            html_lines.append(f"<blockquote>{inner}</blockquote>")
            continue

        # Unordered list
        ul_match = UL_RE.match(line)
        if ul_match:
            flush_paragraph()
            if not list_stack or list_stack[-1] != "ul":
                close_lists()
                html_lines.append("<ul>")
                list_stack.append("ul")
            html_lines.append(f"<li>{_inline(ul_match.group(2))}</li>")
            i += 1
            continue

        # Ordered list
        ol_match = OL_RE.match(line)
        if ol_match:
            flush_paragraph()
            if not list_stack or list_stack[-1] != "ol":
                close_lists()
                html_lines.append("<ol>")
                list_stack.append("ol")
            html_lines.append(f"<li>{_inline(ol_match.group(2))}</li>")
            i += 1
            continue

        # Otherwise: part of a paragraph
        close_lists()
        paragraph_buffer.append(line.strip())
        i += 1

    flush_paragraph()
    close_lists()

    return "\n".join(html_lines)


def wrap_html_document(body: str, title: str = "Document", css: str = None) -> str:
    """Wrap an HTML fragment in a full standalone HTML document."""
    style_tag = f"<style>\n{css}\n</style>" if css else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_escape(title)}</title>
{style_tag}
</head>
<body>
{body}
</body>
</html>
"""
