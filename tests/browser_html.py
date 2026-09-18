#!/usr/bin/env python3
"""Browser smoke tests. Clipboard reads exist only here, never in the website."""
import argparse
import hashlib
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--site', type=Path, default=ROOT / '_site')
parser.add_argument('--url')
parser.add_argument('--require-math', action='store_true')
parser.add_argument('--screenshots', type=Path, default=ROOT / 'test-results')
args = parser.parse_args()
args.screenshots.mkdir(exist_ok=True, parents=True)
server = None
if args.url:
    url = args.url
else:
    server = ThreadingHTTPServer(
        ('127.0.0.1', 0),
        partial(SimpleHTTPRequestHandler, directory=str(args.site)),
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True,
        executable_path=os.getenv('CHROMIUM_PATH') or None,
        args=['--no-sandbox'],
    )
    context = browser.new_context(
        viewport={'width': 1440, 'height': 1100},
        permissions=['clipboard-read', 'clipboard-write'],
    )
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    response = page.goto(url, wait_until='domcontentloaded')
    assert response.status == 200, response.status
    page.wait_for_function(
        "document.querySelector('.paper .copy') && !document.querySelector('.paper .copy').disabled"
    )

    if args.require_math:
        page.wait_for_function(
            "document.documentElement.dataset.mathReady === 'true'",
            timeout=90000,
        )
        assert page.locator('mjx-container').count() > 0
        assert page.locator('mjx-merror, [data-mjx-error]').count() == 0, 'MathJax errors'

    base = url.split('#')[0].split('?')[0]
    manifest = context.request.get(base + 'build-info.json?check=1').json()
    assert page.locator('meta[name="source-revision"]').get_attribute('content') == manifest['source_revision']
    pdf_response = context.request.get(base + manifest['pdf_file'])
    assert pdf_response.status == 200
    assert hashlib.sha256(pdf_response.body()).hexdigest() == manifest['pdf_sha256']

    data = page.locator('#bib-data').evaluate('(element) => JSON.parse(element.textContent)')
    paper_count = page.locator('.paper').count()
    assert paper_count == manifest['paper_count'] and paper_count > 0
    assert page.locator('.topic').count() == manifest['section_count']
    assert page.locator('.subtopic').count() == manifest['subtopic_count']

    # Detailed table of contents: section -> subtopic -> numbered paper.
    assert page.locator('.toc-section').count() == manifest['section_count']
    assert page.locator('.toc-subtopic').count() == manifest['subtopic_count']
    assert page.locator('.toc-paper-link').count() == manifest['paper_count']
    for paper in page.locator('.paper').all():
        paper_id = paper.get_attribute('id')
        toc_link = page.locator(f'.toc-paper-link[href="#{paper_id}"]')
        assert toc_link.count() == 1, paper_id
        number = paper.locator('.paper-number').inner_text().strip()
        assert toc_link.locator('.toc-paper-number').inner_text().strip() == number
        arxiv_link = paper.locator('.actions a[href*="arxiv.org/abs/"]')
        if arxiv_link.count():
            eprint = arxiv_link.first.get_attribute('href').split('/abs/', 1)[1]
            assert eprint.lower() in toc_link.inner_text().lower(), (paper_id, eprint)

    ice_toc = page.locator('.toc-paper-link', has_text='2608.29746')
    assert ice_toc.count() == 1 and 'IceCube' in ice_toc.inner_text()

    first_toc_section = page.locator('.toc-section').first
    section_open = first_toc_section.evaluate('(element) => element.open')
    first_toc_section.locator(':scope > summary').click()
    assert first_toc_section.evaluate('(element) => element.open') != section_open
    first_toc_section.locator(':scope > summary').click()
    assert first_toc_section.evaluate('(element) => element.open') == section_open

    first_toc_subtopic = page.locator('.toc-subtopic').first
    subtopic_open = first_toc_subtopic.evaluate('(element) => element.open')
    first_toc_subtopic.locator(':scope > summary').click()
    assert first_toc_subtopic.evaluate('(element) => element.open') != subtopic_open
    first_toc_subtopic.locator(':scope > summary').click()
    assert first_toc_subtopic.evaluate('(element) => element.open') == subtopic_open

    # Body hierarchy is independently collapsible at all three levels.
    first_section = page.locator('.topic').first
    first_subtopic = first_section.locator(':scope > .subtopic').first
    first_paper = first_subtopic.locator(':scope > .paper').first
    section_toggle = first_section.locator(':scope > h2 > .section-toggle')
    subtopic_toggle = first_subtopic.locator(':scope > h3 > .subtopic-toggle')
    paper_toggle = first_paper.locator(':scope > .paper-heading > .paper-toggle')
    assert section_toggle.count() == subtopic_toggle.count() == paper_toggle.count() == 1
    assert section_toggle.get_attribute('aria-expanded') == 'true'
    assert subtopic_toggle.get_attribute('aria-expanded') == 'true'
    assert paper_toggle.get_attribute('aria-expanded') == 'true'

    paper_toggle.click()
    assert first_paper.get_attribute('data-collapsed') == 'true'
    expect(first_paper.locator('.authors')).to_be_hidden()
    paper_toggle.click()
    expect(first_paper.locator('.authors')).to_be_visible()

    subtopic_toggle.click()
    assert first_subtopic.get_attribute('data-collapsed') == 'true'
    expect(first_paper).to_be_hidden()
    subtopic_toggle.click()
    expect(first_paper).to_be_visible()

    section_toggle.click()
    assert first_section.get_attribute('data-collapsed') == 'true'
    expect(first_subtopic).to_be_hidden()
    section_toggle.click()
    expect(first_subtopic).to_be_visible()

    # Clipboard actions.
    for button in page.locator('[data-copy="bib"]').all():
        key = button.get_attribute('data-key')
        button.click()
        page.wait_for_timeout(30)
        assert page.evaluate('navigator.clipboard.readText()') == data[key], key

    first = page.locator('.paper').first
    key = first.get_attribute('data-key')
    first.locator('[data-copy="key"]').click()
    page.wait_for_function(
        "document.getElementById('toast').textContent === 'Citation keyをコピーしました'"
    )
    assert page.evaluate('navigator.clipboard.readText()') == key
    first.locator('[data-copy="cite"]').click()
    page.wait_for_function("document.getElementById('toast').textContent.includes('cite')")
    assert page.evaluate('navigator.clipboard.readText()') == '\\cite{' + key + '}'
    first.locator('.citation').first.click()
    assert '#ref-' in page.url
    assert page.locator('.reference:target').count() == 1

    # Search and section filtering preserve the hierarchy.
    page.locator('#search').fill('2608.29746')
    ice_search = page.locator('[id="paper-2608.29746"]')
    expect(ice_search).to_be_visible()
    assert 'IceCube' in ice_search.locator('.paper-heading h4').inner_text()
    expect(ice_search.locator('xpath=ancestor::section[contains(@class,"subtopic")]')).to_be_visible()
    page.locator('#search').fill('zzzznonexistentzzzz')
    assert page.locator('#empty').is_visible()
    page.locator('#reset').click()
    page.locator('#topic').select_option('section-extra-dimensional-neutrinos')
    assert page.locator('.topic:visible').count() == 1
    assert page.locator('.subtopic:visible').count() > 1
    assert page.locator('.paper:visible').count() > 0
    page.locator('#reset').click()

    # Resizable desktop contents sidebar, including persistence and reset.
    resizer = page.locator('#sidebar-resizer')
    expect(resizer).to_be_visible()
    sidebar = page.locator('.sidebar')
    initial_width = sidebar.evaluate('(element) => element.getBoundingClientRect().width')
    resizer.press('ArrowRight')
    page.wait_for_timeout(50)
    wider = sidebar.evaluate('(element) => element.getBoundingClientRect().width')
    assert wider > initial_width
    stored = page.evaluate("Number(localStorage.getItem('paper-notes-sidebar-width'))")
    assert abs(stored - wider) <= 2
    resizer.press('Home')
    page.wait_for_timeout(50)
    reset_width = sidebar.evaluate('(element) => element.getBoundingClientRect().width')
    assert abs(reset_width - 245) <= 2

    page.evaluate("history.replaceState(null, '', location.pathname); window.scrollTo(0, 0)")
    page.screenshot(path=str(args.screenshots / 'desktop.png'))

    # Direct paper links reopen paper, subtopic, section and their TOC groups.
    ice = page.locator('[id="paper-2608.29746"]')
    ice_subtopic = ice.locator('xpath=ancestor::section[contains(@class,"subtopic")]')
    ice_section = ice.locator('xpath=ancestor::section[contains(@class,"topic")]')
    if ice.get_attribute('data-collapsed') != 'true':
        ice.locator(':scope > .paper-heading > .paper-toggle').click()
    if ice_subtopic.get_attribute('data-collapsed') != 'true':
        ice_subtopic.locator(':scope > h3 > .subtopic-toggle').click()
    if ice_section.get_attribute('data-collapsed') != 'true':
        ice_section.locator(':scope > h2 > .section-toggle').click()
    page.locator('#search').fill('zzzznonexistentzzzz')
    page.evaluate("location.hash = '#paper-2608.29746'")
    page.wait_for_timeout(100)
    expect(ice).to_be_visible()
    assert ice.get_attribute('data-collapsed') == 'false'
    assert ice_subtopic.get_attribute('data-collapsed') == 'false'
    assert ice_section.get_attribute('data-collapsed') == 'false'
    assert page.locator(
        '.toc-section[data-section="section-extra-dimensional-neutrinos"]'
    ).evaluate('(element) => element.open')
    ice_subtopic_id = ice.get_attribute('data-subtopic')
    assert page.locator(f'.toc-subtopic[data-subtopic="{ice_subtopic_id}"]').evaluate(
        '(element) => element.open'
    )
    page.screenshot(path=str(args.screenshots / 'icecube.png'))

    # Clipboard fallback.
    page.evaluate(
        "() => { navigator.clipboard.writeText = () => "
        "Promise.reject(new DOMException('Denied', 'NotAllowedError')); }"
    )
    ice.locator('[data-copy="bib"]').click()
    expect(page.locator('#copy-dialog')).to_be_visible()
    assert page.locator('#copy-text').input_value() == data[ice.get_attribute('data-key')]
    page.locator('#copy-dialog button').click()

    # Responsive layouts must not overflow horizontally.
    for width in [375, 390, 768]:
        page.set_viewport_size({'width': width, 'height': 844})
        page.locator('#reset').click()
        page.evaluate('window.scrollTo(0, 0)')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), width
        if width <= 760:
            expect(page.locator('#sidebar-resizer')).to_be_hidden()
        page.screenshot(path=str(args.screenshots / f'mobile-{width}.png'))

    assert not errors, errors
    (args.screenshots / 'report.json').write_text(
        json.dumps(
            {
                'papers': paper_count,
                'sections': manifest['section_count'],
                'subtopics': manifest['subtopic_count'],
                'references': len(data),
                'bib_copy_checks': paper_count + len(data),
                'math_verified': args.require_math,
                'pdf_sha256_verified': manifest['pdf_sha256'],
                'url': url,
                'javascript_errors': errors,
                'source_revision': manifest['source_revision'],
            },
            indent=2,
        )
    )
    print(
        'Browser checks passed:',
        paper_count,
        'cards,',
        manifest['subtopic_count'],
        'subtopics and',
        len(data),
        'references',
    )
    browser.close()

if server:
    server.shutdown()
