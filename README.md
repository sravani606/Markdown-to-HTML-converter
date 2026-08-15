# 📝 Markdown to HTML Converter
**Intern ID:** CITS8111

A lightweight command-line tool that converts Markdown files to HTML —
with **zero external dependencies**, just the Python standard library.

## Features

- Headers (`#` through `######`)
- **Bold** and *italic* text
- `Inline code` and fenced ```code blocks``` (with language highlighting class)
- [Links](https://example.com) and images
- Unordered and ordered lists
- Blockquotes
- Horizontal rules
- Read from a file or stdin, write to a file or stdout
- Optional `--standalone` mode to wrap output in a full, styled HTML document

## Installation

```bash
git clone https://github.com/<your-username>/md-to-html.git
cd md-to-html
```

No `pip install` needed — the converter is pure Python standard library.
Requires Python 3.8+.

## Usage

```bash
python md2html.py input.md
```

Prints the converted HTML fragment to the terminal.

### Save to a file

```bash
python md2html.py input.md -o output.html
```

### Standalone HTML document (with styling)

```bash
python md2html.py input.md --standalone --title "My Page" -o output.html
```

### Read from stdin

```bash
cat input.md | python md2html.py
echo "# Hello **world**" | python md2html.py
```

### Options

| Flag | Description |
|---|---|
| `input` | Path to a `.md` file (positional, optional — reads stdin if omitted) |
| `-o`, `--output` | Path to write HTML output (prints to stdout if omitted) |
| `-s`, `--standalone` | Wrap output in a full `<html>` document with basic CSS |
| `-t`, `--title` | Title for the standalone HTML document (default: `Document`) |
| `--no-css` | Skip the default CSS when using `--standalone` |

## Example

Input (`examples/sample.md`):
```markdown
# Welcome to md2html

This is a **sample document**.

- Headers
- **Bold** and *italic* text
- `Inline code`
```

Run:
```bash
python md2html.py examples/sample.md --standalone --title "Sample Page" -o examples/sample.html
```

Output includes:
```html
<h1>Welcome to md2html</h1>
<p>This is a <strong>sample document</strong>.</p>
<ul>
<li>Headers</li>
<li><strong>Bold</strong> and <em>italic</em> text</li>
<li><code>Inline code</code></li>
</ul>
```

A working example is included in [`examples/`](examples/).

## Project structure

```
md-to-html/
├── md2html.py               # CLI entry point
├── converter.py             # Core Markdown -> HTML conversion logic
├── examples/
│   ├── sample.md             # Example input
│   └── sample.html           # Example output
├── tests/
│   └── test_converter.py    # Unit tests (18 tests)
├── .github/workflows/ci.yml # CI: run tests on push/PR
├── .gitignore
├── LICENSE
└── README.md
```

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## Scope & limitations

This is a compact implementation covering the most common Markdown
syntax — it is **not** a full [CommonMark](https://commonmark.org/)
implementation. It doesn't currently support tables, nested lists,
footnotes, or task-list checkboxes.

## Roadmap ideas

- [ ] Table support
- [ ] Nested list support
- [ ] Task list checkboxes (`- [ ]` / `- [x]`)
- [ ] Syntax highlighting via Pygments (optional dependency)
- [ ] Batch-convert a whole directory of `.md` files

## Contributing

Issues and pull requests are welcome. Please run `pytest` before submitting.

## License

MIT — see [LICENSE](LICENSE).
