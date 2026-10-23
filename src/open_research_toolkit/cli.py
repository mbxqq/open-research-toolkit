"""CLI for privacy-friendly, local CSV dataset quality checks."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from . import __version__


def inspect_csv(path, *, delimiter=",", missing_values=()):
    """Return aggregate quality metrics; never return individual record values."""
    if len(delimiter) != 1 or delimiter in "\r\n\0":
        raise ValueError("Delimiter must be one character other than newline or NUL")
    markers = {value.strip() for value in missing_values}
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle, strict=True, delimiter=delimiter)
        fields = next(reader, None)
        if not fields:
            raise ValueError("CSV must have a header row")
        if any(not field.strip() for field in fields):
            raise ValueError("CSV column names must not be blank")
        if len(set(fields)) != len(fields):
            raise ValueError("CSV column names must be unique")
        missing = Counter({field: 0 for field in fields})
        seen = set()
        duplicates = 0
        count = 0
        for row in reader:
            if not row:
                continue
            if len(row) != len(fields):
                raise ValueError(f"CSV record ending at line {reader.line_num} has an unexpected number of fields")
            count += 1
            values = tuple(row)
            if values in seen:
                duplicates += 1
            seen.add(values)
            for field, value in zip(fields, values):
                if not value.strip() or value.strip() in markers:
                    missing[field] += 1
    return {"rows": count, "columns": len(fields), "missing_by_column": dict(missing), "duplicate_rows": duplicates}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect local CSV quality without uploading data")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--delimiter", default=",", help="Single field separator (default: comma)")
    parser.add_argument("--missing-value", action="append", default=[], help="Additional missing marker; repeatable, case-sensitive, whitespace-trimmed")
    parser.add_argument("--fail-on-missing", action="store_true", help="Exit 1 if any missing values are found")
    parser.add_argument("--fail-on-duplicates", action="store_true", help="Exit 1 if duplicate records are found")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--output", type=Path, help="Write aggregate report as JSON")
    args = parser.parse_args(argv)
    try:
        if args.output and (
            args.output.resolve() == args.csv_file.resolve()
            or (args.output.exists() and args.output.samefile(args.csv_file))
        ):
            raise ValueError("Output must not overwrite the input CSV")
        result = inspect_csv(args.csv_file, delimiter=args.delimiter, missing_values=args.missing_value)
        report = json.dumps(result, indent=2)
        if args.output:
            args.output.write_text(report + "\n", encoding="utf-8")
        else:
            print(report)
        if (args.fail_on_missing and any(result["missing_by_column"].values())) or (
            args.fail_on_duplicates and result["duplicate_rows"] > 0
        ):
            parser.exit(1)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        parser.exit(2, f"ort-check: error: {error}\n")


if __name__ == "__main__":
    main()
