import csv
import io
import json
import os
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from open_research_toolkit.cli import inspect_csv, main


class InspectCSVTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sample.csv'

    def write(self, text):
        self.path.write_text(text, encoding='utf-8')
        return self.path

    def test_counts_missing_and_duplicates(self):
        self.write('name,age\nAda,32\nAda,32\nBob,\n')
        self.assertEqual(inspect_csv(self.path), {
            'rows': 3, 'columns': 2,
            'missing_by_column': {'name': 0, 'age': 1}, 'duplicate_rows': 1,
        })

    def test_invalid_headers_and_widths(self):
        for content in ['', '\n', 'a,a\n1,2\n', 'a, \n1,2\n', 'a,b\n1\n', 'a,b\n1,2,3\n']:
            with self.subTest(content=content), self.assertRaises(ValueError):
                inspect_csv(self.write(content))

    def test_header_only(self):
        self.assertEqual(inspect_csv(self.write('a,b\n')), {
            'rows': 0, 'columns': 2, 'missing_by_column': {'a': 0, 'b': 0}, 'duplicate_rows': 0,
        })

    def test_bom_unicode_quotes_and_multiline(self):
        result = inspect_csv(self.write('\ufeffname,note\nعلي,"a,b\nc"\nعلي,"a,b\nc"\n'))
        self.assertEqual(result['rows'], 2)
        self.assertEqual(result['duplicate_rows'], 1)

    def test_whitespace_missing_and_blank_lines(self):
        result = inspect_csv(self.write('a,b\n\n ,NA\n,null\n,\n'))
        self.assertEqual(result['rows'], 3)
        self.assertEqual(result['missing_by_column'], {'a': 3, 'b': 1})

    def test_duplicates_preserve_whitespace(self):
        result = inspect_csv(self.write('a\nx\n x\nx\n'))
        self.assertEqual(result['duplicate_rows'], 1)

    def test_malformed_quotes(self):
        with self.assertRaises(csv.Error):
            inspect_csv(self.write('a\n"unfinished\n'))

    def test_json_stdout_has_no_record_values(self):
        self.write('name\nprivate-person\n')
        output = io.StringIO()
        with redirect_stdout(output):
            main([str(self.path)])
        self.assertEqual(json.loads(output.getvalue())['rows'], 1)
        self.assertNotIn('private-person', output.getvalue())

    def test_output_file(self):
        self.write('a\n1\n')
        output = self.path.with_suffix('.json')
        main([str(self.path), '--output', str(output)])
        self.assertEqual(json.loads(output.read_text()), inspect_csv(self.path))

    def test_input_cannot_be_overwritten(self):
        content = 'a\n1\n'
        self.write(content)
        aliases = [self.path, self.path.parent / 'symlink.csv', self.path.parent / 'hardlink.csv']
        aliases[1].symlink_to(self.path)
        os.link(self.path, aliases[2])
        for output in aliases:
            with self.subTest(output=output), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                main([str(self.path), '--output', str(output)])
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(self.path.read_text(), content)

    def test_read_and_write_errors(self):
        cases = [[str(self.path)]]
        for args in cases:
            with redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit) as caught:
                main(args)
            self.assertEqual(caught.exception.code, 2)
            self.assertNotIn('Traceback', error.getvalue())
        self.write('a\n1\n')
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main([str(self.path), '--output', str(self.path.parent / 'missing' / 'report.json')])
        self.assertEqual(caught.exception.code, 2)

    def test_invalid_utf8(self):
        self.path.write_bytes(b'a\n\xff')
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main([str(self.path)])
        self.assertEqual(caught.exception.code, 2)
