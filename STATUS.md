# STATUS — The Club Treasurer Handbook

Last updated: 2026-11-06

## What was built

An education-only manual for volunteer club treasurers, published by
**Asdale Dynamics, LLC** (MIT-licensed). Markdown sources in `docs/` build
into a static HTML site in `site/` via a dependency-free Python script.

Contents:

| Piece | Where | Notes |
| --- | --- | --- |
| Start-here page + full book map | `docs/index.md` | Contains the read-first "not legal or tax advice / 501(c) -> pros" statement |
| Ch.1 Taking Over Without Dread | `docs/01-taking-over.md` | First two weeks, cash count with witness, ledger pick |
| Ch.2 The Two-Account Setup | `docs/02-two-accounts.md` | Operating vs Reserve, signer hygiene, no reserve card |
| Ch.3 Receipts & Reimbursements | `docs/03-receipts-and-reimbursements.md` | Ledger habit, receipt rule, two-eyeballs approvals, petty cash |
| Ch.4 Monthly Reports People Actually Read | `docs/04-monthly-reports.md` | One-pager anatomy, rhythm, anti-patterns |
| Ch.5 Paying Vendors Fairly | `docs/05-paying-vendors.md` | Quotes, invoices, deposits, member-vendors; tax-form questions routed to pros |
| Ch.6 Collecting Dues Kindly | `docs/06-collecting-dues.md` | Reminder rhythm, no public naming, hardship routing |
| Ch.7 Year-End Handoff Binder | `docs/07-year-end-handoff.md` | Binder sections, close-out, access removal; no passwords/full numbers in the binder |
| Ch.8 Fraud-Proofing Basics | `docs/08-fraud-proofing.md` | Four habits, early-warning signs, incident playbook, digital hygiene |
| Glossary | `docs/glossary.md` | Plain-English money words, member-readable |
| Starter ledger sheet | `templates/ledger.csv` | Uniform-width CSV with worked example rows + usage comment rows |
| Monthly report template | `templates/monthly-report-template.md` | One page; footer carries the not-advice note |
| Reimbursement request form | `templates/reimbursement-request.md` | Enforces receipt + separate approver |
| Vendor payment log | `templates/vendor-payment-log.csv` | Five questions a payment must answer |
| Dues tracker | `templates/dues-tracker.md` | Counts-not-names for public reporting |
| Handoff binder checklist | `templates/handoff-binder-checklist.md` | Printable chapter-7 companion |
| Static site builder | `build.py` | Stdlib-only markdown subset -> styled HTML, nav, footer |
| Test suite | `tests/test_build.py` | 21 tests (see Verification) |
| README | `README.md` | Credits Asdale Dynamics, LLC; documents build + test commands; scopes the book against the companion project |
| LICENSE | `LICENSE` | MIT, Copyright (c) 2026 Asdale Dynamics, LLC |

## How to run it

```bash
python3 build.py                 # renders site/ (16 HTML pages + 2 CSVs)
python3 tests/test_build.py      # 21 tests (also: python3 -m unittest discover -s tests)
```

Requires Python 3.8+, nothing else. Open `site/index.html` in a browser.

## Verification results (2026-11-06)

- `python3 build.py` -> exits 0, "Built 16 pages into site/".
- `python3 tests/test_build.py` -> **Ran 21 tests ... OK**, including:
  - build runs and produces all 10 chapter pages + 6 template pages + 2 CSVs;
  - every page is complete HTML with title, nav, LLC credit, and a
    "Never legal or tax advice" footer;
  - chapter-content spot checks survive rendering;
  - all links in every built page resolve to real files (caught and fixed a
    nav path bug for `site/templates/` pages);
  - CSVs parse and are uniform width (caught and fixed ragged comment rows);
  - build is byte-for-byte deterministic across two runs;
  - content policy: education-only phrasing, 501(c)/tax questions point to
    tax professionals, no secret-assignment patterns or long bank-number
    strings in docs;
  - every template referenced by a doc exists on disk.
- Manual render spot-checks (tables, checkboxes, template comment stripping,
  link rewriting `../templates/*` -> `templates/*`) all behave as intended.

## Known gaps / honest limits

- The markdown renderer (`build.py`) supports a *subset* of CommonMark
  (headings, paragraphs, bold/italic/code/links, lists, checkboxes, tables,
  blockquotes, rules, HTML-comment stripping). Tables and inline formatting
  are handled by the parser this repo controls — verified by tests — but
  arbitrary external markdown is out of scope.
- The starter ledger is a CSV, not a live spreadsheet; formulas are not
  included on purpose (works in any spreadsheet program as-is).
- The book deliberately does not answer 501(c)/1099/W-9 questions — that is
  a design decision, not an omission to fix; it routes readers to qualified
  professionals instead.
- `site/` output is committed so the book is browsable without running the
  build; it regenerates cleanly (determinism is tested).
- No print/PDF generation yet; pages print acceptably via the browser.
- Relative-path browsing of `site/` offline works best from `site/index.html`
  if the whole `site/` folder is moved together.

## Housekeeping

- Git initialized; committed locally only. No remote, no push, no publishing.
- No secrets, API keys, or personal data in any file (tested).
- Distinct from `club-and-nonprofit-ai-guide`: this handbook covers only
  club treasurer duties; that project covers AI use in club/nonprofit work.
