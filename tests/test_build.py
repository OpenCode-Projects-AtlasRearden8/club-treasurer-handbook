#!/usr/bin/env python3
"""Tests for the Club Treasurer Handbook.

Verifies the site builds, the rendered pages are complete and internally
consistent, templates parse, content policy rules hold (education-only,
no legal/tax advice, credits), and the build is deterministic.

Run:  python3 tests/test_build.py   (or: python3 -m unittest discover tests)
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

LICENSE_TEXT = (ROOT / "LICENSE").read_text(encoding="utf-8")
COPYRIGHT_LINE = "Copyright (c) 2026 Asdale Dynamics, LLC"


def fresh_site(directory: Path) -> Path:
    """Run build.py with SITE pinned to a temp dir; return that dir."""
    original = build.SITE
    build.SITE = directory
    try:
        build.build()
    finally:
        build.SITE = original
    return directory


class TestBuildProduces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cth-test-"))
        cls.site = fresh_site(cls.tmp / "site")

    def test_build_scripts_runs_and_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "build.py")],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Built", result.stdout)

    def test_all_chapter_pages_exist(self):
        for name in build.CHAPTER_ORDER:
            page = self.site / (name[:-3] + ".html")
            self.assertTrue(page.exists(), f"missing page: {page.name}")

    def test_template_pages_and_csvs_exist(self):
        for template_md in build.TEMPLATES.glob("*.md"):
            self.assertTrue(
                (self.site / "templates" / (template_md.stem + ".html")).exists())
        for template_csv in build.TEMPLATES.glob("*.csv"):
            self.assertTrue(
                (self.site / "templates" / template_csv.name).exists())

    def test_every_page_is_complete_html(self):
        for page in self.site.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", text, page.name)
            self.assertIn("</html>", text, page.name)
            self.assertIn("<title>", text, page.name)
            self.assertIn("Asdale Dynamics, LLC", text, page.name)
            self.assertIn("Never legal or tax advice", text, page.name)

    def test_navigation_links_on_every_page(self):
        for page in self.site.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            # full chapter nav present on every page; resolution is checked
            # by test_all_links_in_built_pages_resolve
            self.assertIn('class="page"', text, page.name)
            for chapter in ("01-taking-over.html", "glossary.html"):
                target = f'href="../{chapter}"' if "templates" in \
                    str(page.relative_to(self.site)) else f'href="{chapter}"'
                self.assertIn(target, text, page.name)
            # only real chapter pages highlight their own nav entry
            if page.parent == self.site:
                self.assertIn('class="cur"', text, page.name)

    def test_chapter_content_survived_rendering(self):
        expected = {
            "index.html": ["The one-paragraph version of the whole job"],
            "01-taking-over.html": ["Count the money (with a witness)"],
            "02-two-accounts.html": ["Account A: Operating",
                                     "Account B: Reserve"],
            "03-receipts-and-reimbursements.html": ["No receipt, no payout",
                                                    "Two-eyeballs"],
            "04-monthly-reports.html": ["one-pager", "anti-patterns"],
            "05-paying-vendors.html": ["two quotes", "vendor payment log"],
            "06-collecting-dues.html": ["reminder rhythm", "hardship"],
            "07-year-end-handoff.html": ["handoff binder", "one at a time"],
            "08-fraud-proofing.html": ["Two-eyeballs on every payout",
                                       "Fraud-proofing"],
            "glossary.html": ["Ledger", "Reconcile", "Reserve"],
        }
        for name, needles in expected.items():
            text = (self.site / name).read_text(encoding="utf-8")
            for needle in needles:
                self.assertIn(needle, text, f"{needle!r} missing in {name}")

    def test_no_html_comments_leak_into_pages(self):
        for page in self.site.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("<!--", re.sub(r"<!DOCTYPE[^>]+>", "", text),
                             f"unstripped comment in {page.name}")

    def test_build_is_deterministic(self):
        first = fresh_site(self.tmp / "site-a")
        second = fresh_site(self.tmp / "site-b")
        for page in first.rglob("*.html"):
            self.assertEqual(
                page.read_text(encoding="utf-8").strip(),
                (second / page.relative_to(first)).read_text(
                    encoding="utf-8").strip(),
                f"non-deterministic output: {page.name}")


    def test_all_links_in_built_pages_resolve(self):
        for page in self.site.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            for href in re.findall(r'href="([^"]+)"', text):
                if href.startswith(("http://", "https://", "mailto:",
                                    "#", "data:")):
                    continue
                resolved = (page.parent / href).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"broken link {href!r} in {page}")


class TestContentPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {p.name: p.read_text(encoding="utf-8")
                    for p in (ROOT / "docs").glob("*.md")}
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.everything = "\n".join(cls.docs.values()) + "\n" + cls.readme

    def test_index_disclaims_legal_and_tax_advice(self):
        index = " ".join(self.docs["index.md"].split())  # unwrap line breaks
        self.assertIn("education only", index.lower())
        self.assertIn("never legal advice and never tax advice", index.lower())

    def test_all_documents_reaffirm_disclaimer_or_disclaimer_presence(self):
        # every rendered page (tested above) carries the footer disclaimer;
        # docs must at least never *claim* to provide professional advice.
        self.assertNotIn("this is legal advice", self.everything.lower())
        self.assertNotIn("this is tax advice", self.everything.lower())

    def test_501c_questions_point_to_professionals(self):
        index = " ".join(self.docs["index.md"].split())  # unwrap line breaks
        self.assertIn("501(c)", index)
        self.assertIn("tax professional", index.lower())
        # glossary is the word cheat sheet: also routes to a pro
        self.assertIn(
            "tax professional",
            " ".join(self.docs["glossary.md"].split()).lower())

    def test_readme_credits_the_llc_and_explains_scope(self):
        self.assertIn("Asdale Dynamics, LLC", self.readme)
        self.assertIn("education-only", self.readme.lower())

    def test_readme_documents_how_to_build(self):
        self.assertIn("python3 build.py", self.readme)
        self.assertIn("python3 tests/test_build.py", self.readme)

    def test_separate_from_companion_guide(self):
        self.assertIn("club-and-nonprofit-ai-guide", self.readme)

    def test_no_obvious_secrets_or_full_bank_numbers(self):
        # assignment-style secret leaks and bare 9+ digit account numbers
        pattern = re.compile(
            r"(?:api[_-]?key\s*[:=]|secret\s*[:=]|password\s*[:=]"
            r"|token\s*[:=]|\b\d{9,17}\b)", re.IGNORECASE)
        for name, text in self.docs.items():
            match = pattern.search(text)
            self.assertIsNone(match, f"suspicious token in {name}: {match!r}")
        # (the literal word "secret" is fine — the phrase book even uses it)


class TestTemplatesParse(unittest.TestCase):
    def test_csv_templates_parse(self):
        import csv as csvmod
        for csv_file in (ROOT / "templates").glob("*.csv"):
            with open(csv_file, newline="", encoding="utf-8") as fh:
                rows = list(csvmod.reader(fh))
            self.assertTrue(rows, f"{csv_file.name} is empty")
            self.assertTrue(
                all(len(r) == len(rows[0]) for r in rows if r),
                f"ragged rows in {csv_file.name}")

    def test_report_template_has_required_sections(self):
        report = (ROOT / "templates" / "monthly-report-template.md").read_text(
            encoding="utf-8")
        for section in ["Money in this month", "Money out this month",
                        "Transfers", "health note"]:
            self.assertIn(section, report)

    def test_reimbursement_form_has_two_eyeballs_rule(self):
        form = (ROOT / "templates" / "reimbursement-request.md").read_text(
            encoding="utf-8")
        self.assertIn("other than the spender", form)

    def test_handoff_checklist_covers_binder_sections(self):
        handoff = (ROOT / "templates" / "handoff-binder-checklist.md")
        text = handoff.read_text(encoding="utf-8")
        for section in ["Accounts", "Ledger", "Monthly reports",
                        "Receipts", "Vendors", "Dues", "Access changes"]:
            self.assertIn(section, text)

    def test_documents_reference_only_real_templates(self):
        docs_texts = "\n".join(
            p.read_text(encoding="utf-8") for p in (ROOT / "docs").glob("*.md"))
        referenced = set(re.findall(r"\((?:\.\./)?templates/([^)\"\s]+)\)",
                                    docs_texts))
        on_disk = {p.name for p in (ROOT / "templates").glob("*")
                   if not p.name.startswith(".")}
        self.assertTrue(referenced, "docs reference no templates at all")
        self.assertLessEqual(referenced, on_disk,
                             f"docs reference missing templates: "
                             f"{referenced - on_disk}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
