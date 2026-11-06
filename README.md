# The Club Treasurer Handbook

*A friendly, education-only manual for the volunteer treasurer everybody
depends on — taking over without dread, two accounts, receipts and
reimbursements, monthly reports people actually read, fair-pay-for-vendors
paperwork, kind dues collection, a year-end handoff binder, and
fraud-proofing basics.*

## Why this exists

Small clubs run on volunteer treasurers, and volunteer treasurers are usually
handed a shoebox and a login and told "good luck." This handbook is the
"good luck" replacement: eight short chapters and six plain templates that
turn the role from dreaded into *boring* — where boring means trusted,
consistent, and hand-off-able.

- **Plain English, step by step, never condescending** — written like a
  friend would explain it.
- **No special software.** Paper, a spreadsheet, whatever your club has.
- **Education only.** It is never legal or tax advice; questions about
  501(c) status and tax forms are pointed to qualified professionals
  (CPAs, enrolled agents, lawyers) — early, and on purpose.

## Read it

- Start with [docs/index.md](docs/index.md) — the start-here page with the
  whole book mapped out.
- [Chapter 1: Taking Over Without Dread](docs/01-taking-over.md) — your first
  two weeks, calmly.
- [Chapter 2: The Two-Account Setup](docs/02-two-accounts.md) — one wallet,
  one savings, two clear jobs.
- [Chapter 3: Receipts and Reimbursements](docs/03-receipts-and-reimbursements.md),
  [Chapter 4: Monthly Reports](docs/04-monthly-reports.md),
  [Chapter 5: Paying Vendors Fairly](docs/05-paying-vendors.md),
  [Chapter 6: Collecting Dues Kindly](docs/06-collecting-dues.md),
  [Chapter 7: The Year-End Handoff Binder](docs/07-year-end-handoff.md),
  [Chapter 8: Fraud-Proofing Basics](docs/08-fraud-proofing.md).
- [Glossary](docs/glossary.md) — every money word, in plain English.

## Build the static site

`build.py` renders the whole book into a self-contained static HTML site
(`site/`) — no dependencies, standard library only:

```bash
python3 build.py
```

Then open `site/index.html` in any browser (double-clicking works; no server
needed).

## The starter templates

In [`templates/`](templates/): a starter ledger sheet
([ledger.csv](templates/ledger.csv)), a one-page monthly report template
([monthly-report-template.md](templates/monthly-report-template.md)), a
reimbursement request form, a vendor payment log, a dues tracker, and a
handoff binder checklist. Copy them, rename them, make them yours.

## Run the tests

The build is tested — rendered pages, content policy (education-only, no
advice), template integrity, and deterministic output:

```bash
python3 tests/test_build.py
```

## Requirements

- Python 3.8+ for the build script and tests. Nothing else.
- Markdown source lives in `docs/`; the site is plain HTML you can host
  anywhere static files live.

## What this is not

- **Not legal or tax advice.** For questions about 501(c) status, forms,
  insurance, or your club's structure, ask a qualified professional — the
  handbook says so again and again, on purpose.
- **Not accounting software.** There is nothing to install.

## Related projects

This handbook is deliberately scoped to *treasurer duties only*, and is
distinct from the companion project **club-and-nonprofit-ai-guide**, which
covers different ground (using AI tools in club and nonprofit work). One is
about running the money; the other is about the tech. They don't overlap
except in spirit.

## Credits and license

Published by **Asdale Dynamics, LLC** as part of its beginner-friendly
books, guides, and practical tools collection — AI and life-admin education
explained like a friend would, local-first, tested. Licensed under the
MIT License — see [LICENSE](LICENSE) (Copyright (c) 2026 Asdale Dynamics,
LLC). Use it, copy it, adapt it for your club; the next treasurer thanks you.
