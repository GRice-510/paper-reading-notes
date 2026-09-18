"""Fast tests for source fidelity, hierarchy, BibTeX extraction and internal links."""
import importlib.util
import json
import re
import tempfile
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_html', ROOT / 'scripts/build_html.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.buttons = [], [], []
        self.classes = Counter()

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if 'id' in attr:
            self.ids.append(attr['id'])
        if tag == 'a' and attr.get('href', '').startswith('#'):
            self.hrefs.append(unquote(attr['href'][1:]))
        if tag == 'button' and 'data-copy' in attr:
            self.buttons.append(attr)
        for name in attr.get('class', '').split():
            self.classes[name] += 1


class SourceTests(unittest.TestCase):
    def test_bib_round_trip(self):
        raw = '@article{Test:2026,\n title = "{A {nested} title}",\n author = {G\\\"{o}del, K.},\n year = 2026\n}\n'
        got = build.bib_entries(raw)['Test:2026']
        self.assertEqual(got['raw'], raw)
        self.assertEqual(got['fields']['title'], '{A {nested} title}')

    def test_bib_quoted_brace(self):
        self.assertIn('A', build.bib_entries('@article{A, title="a } quoted brace", year=2026}'))

    def test_bib_duplicates_fail(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            build.bib_entries('@article{A, year=2026}\n@article{A, year=2026}')

    def test_unterminated_fails(self):
        with self.assertRaisesRegex(ValueError, 'Unterminated'):
            build.bib_entries('@article{A, title={hello}')

    def test_unsupported_strings_fail(self):
        with self.assertRaises(ValueError):
            build.bib_entries('@string{j="Journal"}\n@article{A,journal=j}')

    def test_comment_handling(self):
        self.assertEqual(build.uncomment('hello % comment\n90\\% yes'), 'hello \n90\\% yes')

    def test_legacy_arxiv(self):
        self.assertEqual(build.norm_arxiv('hep-ph/9811448v2'), build.norm_arxiv('hep-ph_9811448'))

    def test_missing_input_and_path_escape_fail(self):
        for path in ['papers/not-existing.tex', '../../etc/passwd']:
            with self.assertRaises(ValueError):
                build.resolve(path)

    def test_generated_site(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            manifest = build.generate(dest, 'test-revision', '', ROOT / 'paper-reading-notes.pdf')
            text = (dest / 'index.html').read_text()
            parsed = Tags()
            parsed.feed(text)

            self.assertFalse([key for key, count in Counter(parsed.ids).items() if count > 1])
            self.assertFalse(set(parsed.hrefs) - set(parsed.ids))
            self.assertEqual(parsed.classes['topic'], manifest['section_count'])
            self.assertEqual(parsed.classes['subtopic'], manifest['subtopic_count'])
            self.assertEqual(parsed.classes['paper'], manifest['paper_count'])
            self.assertGreaterEqual(manifest['subtopic_count'], manifest['section_count'])

            data = json.loads(
                re.search(r'<script id="bib-data" type="application/json">(.*?)</script>', text, re.S)[1]
            )
            expected = {}
            for path in manifest['inputs']:
                if path.endswith('.bib'):
                    expected.update(build.bib_entries((ROOT / path).read_text()))
            for key, raw in data.items():
                self.assertEqual(raw, expected[key]['raw'])
            for button in parsed.buttons:
                self.assertIn(button['data-key'], data)

            actual = {paper['path'] for paper in manifest['papers']}
            all_papers = {
                paper.relative_to(ROOT).as_posix()
                for paper in (ROOT / 'papers').glob('*.tex')
                if not paper.name.startswith('_')
            }
            self.assertEqual(actual, all_papers)
            self.assertTrue(all(paper['subtopic'].startswith('subtopic-') for paper in manifest['papers']))
            self.assertEqual(
                len(parsed.buttons),
                3 * (manifest['paper_count'] + manifest['reference_count']),
            )
            self.assertEqual(
                (dest / manifest['pdf_file']).read_bytes(),
                (ROOT / 'paper-reading-notes.pdf').read_bytes(),
            )
            self.assertNotIn('http-equiv="refresh"', text)
            self.assertNotIn('@@', text)


if __name__ == '__main__':
    unittest.main()
