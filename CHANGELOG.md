# Changelog

## 0.2.0

- Configure CSV delimiters and repeatable missing-value markers.
- Add optional missing-value and duplicate quality gates (exit 1 with a report).
- Add `--version`, regression tests, and maintainer/contribution guidance.
- Preserve the default JSON format and duplicate comparison semantics.

## 0.1.0 — Initial implementation

- Local CSV quality inspection and aggregate JSON reports.
- Validate headers, record widths, and CSV quoting.
- Protect input files from accidental report overwrites.
- Handle input and output errors with a concise message and exit status 2.
- Synthetic example, regression tests, and a GitHub Actions build/test workflow.
