#!/usr/bin/env python3
"""Build the Club Treasurer Handbook static site.

Converts docs/*.md and templates/*.md into HTML pages under site/,
copies template data files (CSV) alongside them, and renders every page
with a shared header, navigation, and stylesheet. Standard library only —
no dependencies. Run: python3 build.py
"""

import csv
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
TEMPLATES = ROOT / "templates"
SITE = ROOT / "site"

SITE_TITLE = "The Club Treasurer Handbook"
SITE_TAG = "A friendly, education-only manual for the volunteer treasurer everybody depends on"

CHAPTER_ORDER = [
    "index.md",
    "01-taking-over.md",
    "02-two-accounts.md",
    "03-receipts-and-reimbursements.md",
    "04-monthly-reports.md",
    "05-paying-vendors.md",
    "06-collecting-dues.md",
    "07-year-end-handoff.md",
    "08-fraud-proofing.md",
    "glossary.md",
]

STYLE = """
:root { --ink:#22272e; --soft:#57606a; --line:#d8dee4; --accent:#0b5394;
        --bg:#fdfdfd; --card:#f6f8fa; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
       font:16px/1.65 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
a { color:var(--accent); }
code { background:var(--card); border:1px solid var(--line); border-radius:4px;
       padding:0 4px; font-size:0.92em; }
header.site { background:var(--ink); color:#fff; padding:.9rem 1.2rem; }
header.site a { color:#fff; text-decoration:none; }
header.site .t { font-size:1.2rem; font-weight:700; }
header.site .s { color:#c9d1d9; font-size:.88rem; }
nav.page { background:var(--card); border-bottom:1px solid var(--line);
           padding:.5rem 1.2rem; font-size:.88rem; }
nav.page a { text-decoration:none; margin-right:.9rem; white-space:nowrap; }
nav.page a:hover { text-decoration:underline; }
main { max-width:52rem; margin:0 auto; padding:1.5rem 1.2rem 3rem; }
h1,h2,h3 { line-height:1.25; }
h1 { font-size:1.7rem; border-bottom:2px solid var(--line); padding-bottom:.3rem; }
h2 { font-size:1.3rem; margin-top:2rem; }
table { border-collapse:collapse; margin:1rem 0; max-width:100%;
        font-size:.93rem; }
th,td { border:1px solid var(--line); padding:.4rem .6rem; text-align:left; }
th { background:var(--card); }
blockquote { border-left:4px solid var(--accent); margin:1rem 0; padding:.5rem 1rem;
             background:var(--card); color:var(--soft); }
footer.site { border-top:1px solid var(--line); color:var(--soft);
              font-size:.85rem; padding:1rem 1.2rem 2rem; }
input[type=checkbox] { pointer-events:none; }
"""


# --------------------------------------------------------------------------
# tiny markdown subset (headings, paragraphs, lists, tables, quotes, rules,
# bold/italic/code/links, checkboxes). No external dependencies.
# --------------------------------------------------------------------------

def inline(text: str) -> str:
    """Render inline markdown (bold, italic, code, links) to HTML."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", tc_link, text)
    return text


def tc_link(match: re.Match) -> str:
    label, target = match.group(1), match.group(2)
    if target.endswith(".md"):
        target = target[:-3] + ".html"
    if target.startswith("../templates/"):
        target = target[len("../"):]
    return f'<a href="{html.escape(target, quote=True)}">{label}</a>'


def render_markdown(md_text: str) -> str:
    """Render our controlled markdown subset to an HTML body string."""
    out: list[str] = []
    lines = [ln.rstrip("\n") for ln in md_text.splitlines()]
    i, n = 0, len(lines)

    def flush_paragraph(buf: list[str]) -> None:
        if buf:
            out.append(f"<p>{inline(' '.join(l.strip() for l in buf))}</p>")
            buf.clear()

    para: list[str] = []

    while i < n:
        line = lines[i]

        # html comments: drop entire contiguous comment block
        if line.strip().startswith("<!--"):
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if line.strip().startswith("-->") :
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}", line.strip()):
            flush_paragraph(para)
            out.append("<hr>")
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            flush_paragraph(para)
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # blockquote
        if line.strip().startswith(">"):
            flush_paragraph(para)
            quote: list[str] = []
            while i < n and (lines[i].strip().startswith(">") or
                             (quote and lines[i].strip() and
                              not re.match(r"^\s*(?:[#>*-]|\|)", lines[i]))):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote>{inline(' '.join(q.strip() for q in quote))}</blockquote>")
            continue

        # table
        if line.strip().startswith("|") and i + 1 < n and \
                re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush_paragraph(para)
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                cells += [""] * (len(header) - len(cells))
                rows.append(cells)
                i += 1
            out.append("<table><thead>")
            out.append("<tr>" + "".join(
                f"<th>{inline(h)}</th>" for h in header) + "</tr></thead>")
            if rows:
                out.append("<tbody>")
                for r in rows:
                    out.append("<tr>" + "".join(
                        f"<td>{inline(c)}</td>" for c in r) + "</tr>")
                out.append("</tbody>")
            out.append("</table>")
            continue

        # unordered list (with checkbox support)
        if re.match(r"^\s*[-*]\s+", line):
            flush_paragraph(para)
            checkbox = re.match(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", line)
            if checkbox:
                out.append('<ul class="check">')
                while i < n:
                    cb = re.match(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", lines[i])
                    if not cb:
                        break
                    checked = " checked" if cb.group(1).lower() == "x" else ""
                    out.append(f'<li><input type="checkbox" disabled{checked}> '
                               f"{inline(cb.group(2))}</li>")
                    i += 1
                out.append("</ul>")
            else:
                out.append("<ul>")
                while i < n and re.match(r"^\s*[-*]\s+\S", lines[i]):
                    item = re.sub(r"^\s*[-*]\s+", "", lines[i])
                    # gather wrapped continuation lines
                    while i + 1 < n and lines[i + 1].strip() and \
                            not re.match(r"^\s*(?:[-*]\s|#|>|\|)", lines[i + 1]):
                        item += " " + lines[i + 1].strip()
                        i += 1
                    out.append(f"<li>{inline(item)}</li>")
                    i += 1
                out.append("</ul>")
            continue

        # ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            flush_paragraph(para)
            out.append("<ol>")
            while i < n and re.match(r"^\s*\d+\.\s+\S", lines[i]):
                item = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                while i + 1 < n and lines[i + 1].strip() and \
                        not re.match(r"^\s*(?:[-*\d]|\s*\d\.|#|>|\|)", lines[i + 1]):
                    item += " " + lines[i + 1].strip()
                    i += 1
                out.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append("</ol>")
            continue

        # blank line
        if not line.strip():
            flush_paragraph(para)
            i += 1
            continue

        # paragraph (join wrapped lines)
        para.append(line)
        while i + 1 < n and lines[i + 1].strip() and \
                not re.match(r"^\s*(?:[#>*-]|\||\d+\.\s|\[-\]|<!--)", lines[i + 1]):
            para.append(lines[i + 1])
            i += 1
        i += 1

    flush_paragraph(para)
    return "\n".join(out)


def page(title: str, body_html: str, nav_current: str,
         prefix: str = "") -> str:
    nav_items = []
    for name in CHAPTER_ORDER:
        stem = name[:-3]
        label = {
            "index": "Start Here",
            "01-taking-over": "1. Taking Over",
            "02-two-accounts": "2. Two Accounts",
            "03-receipts-and-reimbursements": "3. Receipts",
            "04-monthly-reports": "4. Monthly Reports",
            "05-paying-vendors": "5. Vendors",
            "06-collecting-dues": "6. Dues",
            "07-year-end-handoff": "7. Handoff",
            "08-fraud-proofing": "8. Fraud-Proofing",
            "glossary": "Glossary",
        }[stem]
        href = f"{prefix}{stem}.html" if stem != "index" else f"{prefix}index.html"
        cls = ' class="cur"' if name == nav_current else ""
        nav_items.append(f'<a href="{href}"{cls}>{label}</a>')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — {SITE_TITLE}</title>
<style>{STYLE}</style>
</head>
<body>
<header class="site">
  <a href="{prefix}index.html"><span class="t">{SITE_TITLE}</span></a>
  <div class="s">{SITE_TAG}</div>
</header>
<nav class="page">{''.join(nav_items)}</nav>
<main>{body_html}</main>
<footer class="site">
  <p>The Club Treasurer Handbook — an education-only project by <strong>Asdale
  Dynamics, LLC</strong>. Never legal or tax advice; 501(c) and similar
  questions belong with qualified professionals. MIT License —
  Copyright (c) 2026 Asdale Dynamics, LLC.</p>
</footer>
</body>
</html>
"""


def build() -> None:
    pages: list[tuple[str, str, str]] = []   # (relpath, title, markdown)

    for name in CHAPTER_ORDER:
        path = DOCS / name
        md = path.read_text(encoding="utf-8")
        title = md.lstrip().splitlines()[0].lstrip("#").strip()
        if name == "index.md":
            title = "Start Here"
        pages.append((name, title, md))

    for path in sorted(TEMPLATES.glob("*.md")):
        md = path.read_text(encoding="utf-8")
        title: str
        for line in md.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("<!--"):
                title = "Template: " + stripped.lstrip("#").strip()
                break
        else:
            title = f"Template: {path.stem}"
        pages.append((f"templates/{path.name}", title, md))

    SITE.mkdir(exist_ok=True)
    (SITE / "templates").mkdir(exist_ok=True)

    for name, title, md in pages:
        rel = name[:-3] + ".html" if name.endswith(".md") else name
        depth = "" if "/" not in rel else "../"
        (SITE / rel).parent.mkdir(parents=True, exist_ok=True)
        (SITE / rel).write_text(
            page(title, render_markdown(md), name, prefix=depth),
            encoding="utf-8")

    for data in sorted(TEMPLATES.glob("*.csv")):
        shutil.copyfile(data, SITE / "templates" / data.name)

    print(f"Built {len(pages) + len(sorted(TEMPLATES.glob('*.csv')))} "
          f"pages into site/")


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:  # make failures loud for tests/CI
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
