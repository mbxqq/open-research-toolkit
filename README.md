# Open Research Toolkit

An initial, local command-line tool for reproducible CSV data-quality checks.
The tool makes no network requests and processes your CSV on your computer.

## Features

- Count data rows and columns.
- Count empty or whitespace-only values per column.
- Count exact duplicate records beyond their first occurrence.
- Write aggregate metrics as JSON, including column names but no individual record values.
- Reject blank or repeated column names, inconsistent row widths, and malformed CSV quoting.

## Install from source

Requires Python 3.10 or newer. This project is not currently published on PyPI.

```bash
git clone https://github.com/mbxqq/open-research-toolkit.git
cd open-research-toolkit
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Usage

```bash
ort-check examples/sample.csv
ort-check examples/sample.csv --output report.json
```

The included data is synthetic. Expected report:

```json
{
  "rows": 3,
  "columns": 3,
  "missing_by_column": {
    "sample_id": 0,
    "group": 0,
    "value": 1
  },
  "duplicate_rows": 1
}
```

Errors exit with status 2. The output cannot be the input CSV or a link to it.
An existing report file is replaced when `--output` is used.

## Tests and automated checks

After installing the package:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions is configured to build a source archive and wheel, install the wheel,
and run the tests and example on Python 3.10, 3.13, and 3.14 for pushes and pull requests.
A configured workflow is not evidence that a remote run has passed.

## Limitations and privacy

- Input must be comma-delimited UTF-8 CSV; a UTF-8 byte order mark is accepted.
- Completely blank lines are skipped; quoted multiline fields are supported.
- Whitespace-only fields count as missing. `NA` and `null` remain literal values.
- Duplicate matching compares parsed strings exactly, without trimming whitespace.
- Duplicate detection retains unique rows in memory; large datasets may need substantial memory.
- Reports include column names, which can themselves be sensitive. Review reports before sharing.
- Quality metrics do not validate scientific conclusions or establish suitability for clinical decisions.

## Development status

Version 0.1.0 is an initial implementation. No adoption, user counts, or external
program eligibility are claimed. Future possibilities include configurable missing
markers, schema checks, and additional report formats; these are not implemented.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance.

## License

[MIT](LICENSE). The existing copyright notice is retained.
