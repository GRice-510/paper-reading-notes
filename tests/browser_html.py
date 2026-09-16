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
from playwright.sync_api import sync_playwright, expect

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
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(args.site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1100}, permissions=['clipboard-read', 'clipboard-write'])
    page = context.new_page()
    errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    response = page.goto(url, wait_until='domcontentloaded')
    assert response.status == 200, response.status
    page.wait_for_function("document.querySelector('.paper .copy') && !document.querySelector('.paper .copy').disabled")
    if args.require_math:
        page.wait_for_function("document.documentElement.dataset.mathReady === 'true'", timeout=90000)
        assert page.locator('mjx-container').count() > 0
        assert page.locator('mjx-merror, [data-mjx-error]').count() == 0, 'MathJax errors'
    base = url.split('#')[0].split('?')[0]
    manifest = context.request.get(base + 'build-info.json?check=1').json()
    assert page.locator('meta[name="source-revision"]').get_attribute('content') == manifest['source_revision']
    pdf_response = context.request.get(base + manifest['pdf_file'])
    assert pdf_response.status == 200
    assert hashlib.sha256(pdf_response.body()).hexdigest() == manifest['pdf_sha256']
    data = page.locator('#bib-data').evaluate('(e) => JSON.parse(e.textContent)')
    n = page.locator('.paper').count()
    assert n == manifest['paper_count'] and n > 0

    # PDF-like detailed table of contents: section -> numbered paper title / arXiv.
    assert page.locator('.toc-section').count() == manifest['section_count']
    assert page.locator('.toc-paper-link').count() == manifest['paper_count']
    for paper in page.locator('.paper').all():
        pid = paper.get_attribute('id')
        toc_link = page.locator(f'.toc-paper-link[href="#{pid}"]')
        assert toc_link.count() == 1, pid
        arxiv_link = paper.locator('.actions a[href*="arxiv.org/abs/"]')
        if arxiv_link.count():
            eprint = arxiv_link.first.get_attribute('href').split('/abs/', 1)[1]
            assert eprint.lower() in toc_link.inner_text().lower(), (pid, eprint)
    ice_toc = page.locator('.toc-paper-link', has_text='2608.29746')
    assert ice_toc.count() == 1 and 'IceCube' in ice_toc.inner_text()
    first_toc_group = page.locator('.toc-section').first
    before = first_toc_group.evaluate('(e) => e.open')
    first_toc_group.locator('summary').click()
    assert first_toc_group.evaluate('(e) => e.open') != before
    first_toc_group.locator('summary').click()
    assert first_toc_group.evaluate('(e) => e.open') == before

    for button in page.locator('[data-copy="bib"]').all():
        key = button.get_attribute('data-key')
        button.click()
        page.wait_for_timeout(30)
        assert page.evaluate('navigator.clipboard.readText()') == data[key], key
    first = page.locator('.paper').first
    key = first.get_attribute('data-key')
    first.locator('[data-copy="key"]').click()
    page.wait_for_function("document.getElementById('toast').textContent === 'Citation keyをコピーしました'")
    assert page.evaluate('navigator.clipboard.readText()') == key
    first.locator('[data-copy="cite"]').click()
    page.wait_for_function("document.getElementById('toast').textContent.includes('cite')")
    assert page.evaluate('navigator.clipboard.readText()') == '\\cite{' + key + '}'
    first.locator('.citation').first.click()
    assert '#ref-' in page.url
    assert page.locator('.reference:target').count() == 1
    page.locator('#search').fill('2608.29746')
    assert page.locator('.paper:visible').count() == 1
    assert 'IceCube' in page.locator('.paper:visible h3').inner_text()
    page.locator('#search').fill('zzzznonexistentzzzz')
    assert page.locator('#empty').is_visible()
    page.locator('#reset').click()
    page.locator('#topic').select_option('section-extra-dimensional-neutrinos')
    assert page.locator('.topic:visible').count() == 1
    assert page.locator('.paper:visible').count() > 0
    page.locator('#reset').click()
    page.evaluate("history.replaceState(null, '', location.pathname); window.scrollTo(0, 0)")
    page.screenshot(path=str(args.screenshots / 'desktop.png'))
    page.locator('#search').fill('zzzznonexistentzzzz')
    page.evaluate("location.hash = '#paper-2608.29746'")
    page.wait_for_timeout(100)
    expect(page.locator('[id="paper-2608.29746"]')).to_be_visible()
    assert page.locator('.toc-section[data-section="section-extra-dimensional-neutrinos"]').evaluate('(e) => e.open')
    page.screenshot(path=str(args.screenshots / 'icecube.png'))
    # A block-bodied function avoids Playwright auto-invoking an assignment's returned function.
    page.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new DOMException('Denied', 'NotAllowedError')); }")
    paper = page.locator('[id="paper-2608.29746"]')
    paper.locator('[data-copy="bib"]').click()
    expect(page.locator('#copy-dialog')).to_be_visible()
    assert page.locator('#copy-text').input_value() == data[paper.get_attribute('data-key')]
    page.locator('#copy-dialog button').click()
    for width in [375, 390, 768]:
        page.set_viewport_size({'width': width, 'height': 844})
        page.locator('#reset').click()
        page.evaluate('window.scrollTo(0, 0)')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), width
        page.screenshot(path=str(args.screenshots / f'mobile-{width}.png'))
    assert not errors, errors
    (args.screenshots / 'report.json').write_text(json.dumps({'papers': n, 'references': len(data), 'bib_copy_checks': n + len(data), 'math_verified': args.require_math, 'pdf_sha256_verified': manifest['pdf_sha256'], 'url': url, 'javascript_errors': errors, 'source_revision': manifest['source_revision']}, indent=2))
    print('Browser checks passed:', n, 'cards and', len(data), 'references')
    browser.close()
if server:
    server.shutdown()
