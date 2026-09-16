#!/usr/bin/env python3
"""Browser checks for the desktop table-of-contents resizer."""
import argparse
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
args = parser.parse_args()
server = None
if args.url:
    url = args.url
else:
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(args.site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1000})
    page = context.new_page()
    response = page.goto(url, wait_until='domcontentloaded')
    assert response.status == 200, response.status
    page.wait_for_selector('#sidebar-resizer')
    resizer = page.locator('#sidebar-resizer')
    sidebar = page.locator('.sidebar')
    expect(resizer).to_be_visible()

    initial = sidebar.bounding_box()['width']
    handle = resizer.bounding_box()
    page.mouse.move(handle['x'] + handle['width'] / 2, handle['y'] + 100)
    page.mouse.down()
    page.mouse.move(handle['x'] + handle['width'] / 2 + 72, handle['y'] + 100, steps=5)
    page.mouse.up()
    resized = sidebar.bounding_box()['width']
    assert resized > initial + 50, (initial, resized)
    stored = page.evaluate("Number(localStorage.getItem('paper-notes-sidebar-width'))")
    assert abs(stored - resized) <= 2, (stored, resized)

    page.reload(wait_until='domcontentloaded')
    page.wait_for_selector('#sidebar-resizer')
    persisted = page.locator('.sidebar').bounding_box()['width']
    assert abs(persisted - stored) <= 2, (persisted, stored)

    resizer = page.locator('#sidebar-resizer')
    resizer.press('Home')
    reset = page.locator('.sidebar').bounding_box()['width']
    assert abs(reset - 245) <= 2, reset
    resizer.press('ArrowRight')
    keyboard = page.locator('.sidebar').bounding_box()['width']
    assert keyboard >= reset + 10, (reset, keyboard)
    assert resizer.get_attribute('aria-valuenow') is not None

    page.set_viewport_size({'width': 375, 'height': 844})
    expect(page.locator('#sidebar-resizer')).to_be_hidden()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')

    browser.close()
if server:
    server.shutdown()
print('Sidebar resize checks passed')
