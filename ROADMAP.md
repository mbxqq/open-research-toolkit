# Roadmap

These are proposed tasks, not completed features or scheduled commitments.

- **Schema checks:** validate required columns and basic types; test missing columns,
  invalid values, and a clean dataset without exposing record values in errors.
- **Bounded-memory duplicate checks:** benchmark a disk-backed implementation using
  synthetic data and document memory, disk and runtime tradeoffs.
- **Broader platform validation:** test installation and file behavior on Windows and macOS.
- **User feedback:** invite voluntary trials on non-sensitive datasets; document
  reproducible problems and improve behavior based on actual feedback.

Current 0.2.0 scope: configurable delimiters, missing markers, JSON reports and optional
quality gates. Public development history and CI demonstrate implemented work;
community use and ecosystem importance require separate real-world evidence.
