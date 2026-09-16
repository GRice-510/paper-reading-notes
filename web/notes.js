'use strict';
(() => {
  const data = JSON.parse(document.getElementById('bib-data').textContent);
  const search = document.getElementById('search');
  const topic = document.getElementById('topic');
  const papers = [...document.querySelectorAll('.paper')];
  const references = [...document.querySelectorAll('.reference')];
  const sections = [...document.querySelectorAll('.topic')];
  const narrow = window.matchMedia('(max-width: 760px)');
  if (narrow.matches) document.querySelector('.toc').open = false;

  const tocGroups = new Map();
  function arxivFor(paper) {
    const link = paper.querySelector('.actions a[href*="arxiv.org/abs/"]');
    if (!link) return '';
    try {
      return decodeURIComponent(new URL(link.href).pathname.split('/abs/')[1] || '');
    } catch (_) { return ''; }
  }
  function paperTocTitle(paper) {
    let title = paper.querySelector('h3')?.textContent.trim() || paper.id.replace(/^paper-/, '');
    const eprint = arxivFor(paper);
    if (eprint && !title.toLocaleLowerCase().includes(eprint.toLocaleLowerCase())) {
      title += ` — arXiv:${eprint}`;
    }
    return title;
  }
  function installDetailedToc() {
    const nav = document.querySelector('.toc nav');
    if (!nav) return;
    const style = document.createElement('style');
    style.id = 'interactive-notes-style';
    style.textContent = `
      .toc nav{display:block}
      .toc-section{border-bottom:1px solid var(--border);padding:2px 0}
      .toc-section>summary{margin:0;padding:9px 5px;align-items:baseline;letter-spacing:0;font-size:.78rem;color:#344760}
      .toc-section>summary .toc-section-title{font-size:.78rem;letter-spacing:0;font-weight:700;color:#344760}
      .toc-section>summary .toc-section-count{font-size:.68rem;letter-spacing:0;font-weight:500;color:var(--muted);white-space:nowrap}
      .toc-paper-list{display:grid;gap:1px;margin:0 0 9px 8px;padding:2px 0 2px 9px;border-left:1px solid var(--border)}
      .toc nav a.toc-paper-link{display:grid;grid-template-columns:2.7rem minmax(0,1fr);justify-content:initial;gap:4px;padding:6px 7px;font-size:.75rem;line-height:1.45;border-radius:5px}
      .toc-paper-number{color:var(--blue);font-variant-numeric:tabular-nums;white-space:nowrap}
      .toc-paper-title{min-width:0;overflow-wrap:anywhere}
      .toc nav a.toc-reference-link{margin-top:10px;border-top:1px solid var(--border);border-radius:0;padding-top:12px}
      .topic>h2{display:flex;align-items:baseline;gap:7px}
      .collapse-toggle{margin-left:auto;flex:0 0 auto;width:32px;height:32px;padding:0;border:1px solid var(--border);border-radius:6px;background:white;color:#52627a;font-size:1rem;line-height:1;display:inline-grid;place-items:center}
      .collapse-toggle:hover{background:var(--soft);border-color:#a9bfdc;color:var(--blue)}
      .paper-heading>.collapse-toggle{align-self:flex-start;margin-top:1px}
      .topic[data-collapsed="true"]>:not(h2){display:none!important}
      .paper[data-collapsed="true"]>:not(.paper-heading){display:none!important}
      .paper[data-collapsed="true"]{padding-top:18px;padding-bottom:18px}
      .paper[data-collapsed="true"] .paper-heading{align-items:center}
      @media(max-width:760px){
        .toc nav{display:block}
        .toc-section>summary{padding:10px 5px;font-size:.8rem}
        .toc-section>summary .toc-section-title{font-size:.8rem}
        .toc nav a.toc-paper-link{grid-template-columns:2.65rem minmax(0,1fr);font-size:.77rem;padding:7px 5px}
        .collapse-toggle{width:34px;height:34px}
      }
      @media print{
        .collapse-toggle{display:none!important}
        .topic[data-collapsed="true"]>:not(h2),.paper[data-collapsed="true"]>:not(.paper-heading){display:revert!important}
      }
    `;
    document.head.append(style);
    nav.replaceChildren();
    sections.forEach((section, sectionIndex) => {
      const number = String(sectionIndex + 1);
      const numberNode = section.querySelector('.section-number');
      if (numberNode) numberNode.textContent = number;
      const heading = section.querySelector('h2');
      const headingCopy = heading?.cloneNode(true);
      headingCopy?.querySelector('.section-number')?.remove();
      const sectionTitle = headingCopy?.textContent.trim() || `Section ${number}`;
      const sectionPapers = [...section.querySelectorAll('.paper')];
      const details = document.createElement('details');
      details.className = 'toc-section';
      details.dataset.section = section.id;
      details.open = !narrow.matches;
      const summary = document.createElement('summary');
      const label = document.createElement('span');
      label.className = 'toc-section-title';
      label.textContent = `${number} ${sectionTitle}`;
      const count = document.createElement('span');
      count.className = 'toc-section-count';
      count.textContent = `${sectionPapers.length} papers`;
      summary.append(label, count);
      details.append(summary);
      const list = document.createElement('div');
      list.className = 'toc-paper-list';
      sectionPapers.forEach((paper, paperIndex) => {
        const link = document.createElement('a');
        link.className = 'toc-paper-link';
        link.href = `#${paper.id}`;
        const paperNumber = document.createElement('span');
        paperNumber.className = 'toc-paper-number';
        paperNumber.textContent = paper.querySelector('.paper-number')?.textContent.trim() || `${number}.${paperIndex + 1}`;
        const title = document.createElement('span');
        title.className = 'toc-paper-title';
        title.textContent = paperTocTitle(paper);
        link.append(paperNumber, title);
        list.append(link);
      });
      details.append(list);
      nav.append(details);
      tocGroups.set(section.id, details);
    });
    const referenceLink = document.createElement('a');
    referenceLink.className = 'toc-reference-link';
    referenceLink.href = '#references';
    const refLabel = document.createElement('span');
    refLabel.textContent = '参考文献';
    const refCount = document.createElement('span');
    refCount.className = 'count';
    refCount.textContent = String(references.length);
    referenceLink.append(refLabel, refCount);
    nav.append(referenceLink);
  }
  installDetailedToc();

  function targetLabel(target) {
    if (target.classList.contains('paper')) {
      return target.querySelector('h3')?.textContent.trim() || 'この論文';
    }
    const heading = target.querySelector(':scope > h2')?.cloneNode(true);
    heading?.querySelector('.section-number')?.remove();
    heading?.querySelector('.collapse-toggle')?.remove();
    return heading?.textContent.trim() || 'このセクション';
  }
  function collapseButton(target, kind) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `collapse-toggle ${kind}-toggle`;
    button.dataset.collapseTarget = target.id;
    button.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      setCollapsed(target, target.dataset.collapsed !== 'true');
    });
    return button;
  }
  function setCollapsed(target, collapsed) {
    target.dataset.collapsed = collapsed ? 'true' : 'false';
    const button = target.classList.contains('paper')
      ? target.querySelector(':scope > .paper-heading > .paper-toggle')
      : target.querySelector(':scope > h2 > .section-toggle');
    if (!button) return;
    const label = targetLabel(target);
    button.textContent = collapsed ? '▸' : '▾';
    button.setAttribute('aria-expanded', String(!collapsed));
    button.setAttribute('aria-label', `${label}を${collapsed ? '展開' : '閉じる'}`);
    button.title = collapsed ? '展開する' : '閉じる';
  }
  function installCollapsibles() {
    sections.forEach(section => {
      const heading = section.querySelector(':scope > h2');
      if (!heading || heading.querySelector('.section-toggle')) return;
      heading.append(collapseButton(section, 'section'));
      setCollapsed(section, false);
    });
    papers.forEach(paper => {
      const heading = paper.querySelector(':scope > .paper-heading');
      if (!heading || heading.querySelector('.paper-toggle')) return;
      heading.append(collapseButton(paper, 'paper'));
      setCollapsed(paper, false);
    });
  }
  installCollapsibles();

  function expandTarget(target) {
    const parentTopic = target.classList.contains('topic') ? target : target.closest('.topic');
    if (parentTopic) setCollapsed(parentTopic, false);
    if (target.classList.contains('paper')) setCollapsed(target, false);
  }

  const normalize = s => s.normalize('NFKC').toLocaleLowerCase();
  const index = new Map([...papers, ...references].map(el => [el, normalize(el.textContent + ' ' + el.dataset.key)]));
  let toastTimer;
  function announce(text) {
    const el = document.getElementById('toast');
    el.textContent = text; el.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 2400);
  }
  function manualCopy(text) {
    const dialog = document.getElementById('copy-dialog');
    const area = document.getElementById('copy-text');
    area.value = text;
    if (!dialog.open) dialog.showModal();
    area.focus(); area.select(); area.setSelectionRange(0, text.length);
  }
  document.querySelectorAll('[data-copy]').forEach(button => {
    const key = button.dataset.key;
    if (!Object.hasOwn(data, key)) return;
    button.disabled = false;
    button.addEventListener('click', async () => {
      const mode = button.dataset.copy;
      const text = mode === 'bib' ? data[key] : mode === 'cite' ? `\\cite{${key}}` : key;
      try {
        if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard API unavailable');
        await navigator.clipboard.writeText(text);
        announce(mode === 'bib' ? 'BibTeXをコピーしました' : mode === 'cite' ? '\\cite{…}をコピーしました' : 'Citation keyをコピーしました');
      } catch (_) { manualCopy(text); }
    });
  });
  function filter() {
    const terms = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    const match = el => terms.every(term => index.get(el).includes(term));
    const visibleRefs = new Set();
    const filtering = terms.length > 0 || Boolean(topic.value);
    let count = 0;
    papers.forEach(el => {
      el.hidden = (topic.value && topic.value !== el.dataset.section) || !match(el);
      if (!el.hidden) {
        count++;
        JSON.parse(el.dataset.refs).forEach(key => visibleRefs.add(key));
        if (filtering) {
          setCollapsed(el, false);
          const parent = el.closest('.topic');
          if (parent) setCollapsed(parent, false);
        }
      }
    });
    sections.forEach(el => {el.hidden = ![...el.querySelectorAll('.paper')].some(p => !p.hidden);});
    let refCount = 0;
    references.forEach(el => {
      const referenced = visibleRefs.has(el.dataset.key);
      el.hidden = topic.value ? !referenced : terms.length ? !(referenced || match(el)) : false;
      if (!el.hidden) refCount++;
    });
    document.getElementById('references').hidden = refCount === 0;
    document.getElementById('empty').hidden = count > 0 || refCount > 0;
    document.getElementById('result-count').textContent = `${count} / ${papers.length} 論文 · ${refCount} 参考文献`;
  }
  search.addEventListener('input', filter);
  topic.addEventListener('change', filter);
  document.getElementById('reset').addEventListener('click', () => {search.value = ''; topic.value = ''; filter(); search.focus();});
  function revealHash() {
    let id;
    try {id = decodeURIComponent(location.hash.slice(1));} catch (_) {return;}
    const el = document.getElementById(id) || document.getElementById('paper-' + id);
    if (!el) return;
    if (el.hidden || el.closest('[hidden]')) {search.value = ''; topic.value = ''; filter();}
    expandTarget(el);
    const parentTopic = el.classList.contains('topic') ? el : el.closest('.topic');
    if (parentTopic && tocGroups.has(parentTopic.id)) tocGroups.get(parentTopic.id).open = true;
    requestAnimationFrame(() => el.scrollIntoView({block: 'start', behavior: 'instant'}));
  }
  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', () => {
    const hash = link.getAttribute('href');
    if (hash === '#references' || hash.startsWith('#section-') || hash.startsWith('#ref-')) {
      search.value = ''; topic.value = ''; filter();
    }
    if (location.hash === hash) setTimeout(revealHash, 0);
  }));
  window.addEventListener('hashchange', revealHash);
  const stamp = document.querySelector('.edition time');
  if (stamp.dateTime && !Number.isNaN(Date.parse(stamp.dateTime))) {
    stamp.textContent = new Intl.DateTimeFormat('ja-JP', {dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Tokyo'}).format(new Date(stamp.dateTime)) + ' JST';
  }
  document.getElementById('mathjax-script')?.addEventListener('error', () => {document.getElementById('math-warning').hidden = false;});
  document.addEventListener('notes-math-ready', () => {if (location.hash) revealHash();});
  filter();
  if (location.hash) setTimeout(revealHash, 0);
})();

// Desktop contents sidebar resizing. Width is stored only in this browser.
(() => {
  const sidebar = document.querySelector('.sidebar');
  if (!sidebar) return;
  const root = document.documentElement;
  const storageKey = 'paper-notes-sidebar-width';
  const desktop = window.matchMedia('(min-width: 761px)');
  const minWidth = 180;
  const defaultWidth = () => window.innerWidth <= 1020 ? 205 : 245;
  const maxWidth = () => Math.max(minWidth, Math.min(440, window.innerWidth * 0.42));
  const clamp = value => Math.min(maxWidth(), Math.max(minWidth, value));

  const resizer = document.createElement('div');
  resizer.id = 'sidebar-resizer';
  resizer.className = 'sidebar-resizer';
  resizer.setAttribute('role', 'separator');
  resizer.setAttribute('aria-orientation', 'vertical');
  resizer.setAttribute('aria-label', '目次の幅を変更');
  resizer.setAttribute('tabindex', '0');
  resizer.title = 'ドラッグで目次幅を変更。ダブルクリックまたはHomeキーで初期幅に戻します。';
  sidebar.insertAdjacentElement('afterend', resizer);

  let remembered = null;
  try {
    const stored = Number(localStorage.getItem(storageKey));
    if (Number.isFinite(stored) && stored > 0) remembered = stored;
  } catch (_) {}

  function writeStored(value) {
    try { localStorage.setItem(storageKey, String(Math.round(value))); } catch (_) {}
  }
  function applyWidth(value, persist = false) {
    if (!desktop.matches) return;
    const width = clamp(value);
    root.style.setProperty('--sidebar-width', `${Math.round(width)}px`);
    resizer.setAttribute('aria-valuemin', String(minWidth));
    resizer.setAttribute('aria-valuemax', String(Math.round(maxWidth())));
    resizer.setAttribute('aria-valuenow', String(Math.round(width)));
    resizer.setAttribute('aria-valuetext', `${Math.round(width)}ピクセル`);
    if (persist) {
      remembered = width;
      writeStored(width);
    }
  }
  function restoreWidth() {
    if (!desktop.matches) {
      root.style.removeProperty('--sidebar-width');
      return;
    }
    applyWidth(remembered ?? defaultWidth());
  }

  let dragging = false;
  let startX = 0;
  let startWidth = 0;
  resizer.addEventListener('pointerdown', event => {
    if (!desktop.matches || event.button !== 0) return;
    dragging = true;
    startX = event.clientX;
    startWidth = sidebar.getBoundingClientRect().width;
    resizer.setPointerCapture(event.pointerId);
    document.body.classList.add('sidebar-resizing');
    event.preventDefault();
  });
  resizer.addEventListener('pointermove', event => {
    if (dragging) applyWidth(startWidth + event.clientX - startX);
  });
  function finishDrag(event) {
    if (!dragging) return;
    dragging = false;
    document.body.classList.remove('sidebar-resizing');
    if (event?.pointerId != null && resizer.hasPointerCapture(event.pointerId)) resizer.releasePointerCapture(event.pointerId);
    applyWidth(sidebar.getBoundingClientRect().width, true);
  }
  resizer.addEventListener('pointerup', finishDrag);
  resizer.addEventListener('pointercancel', finishDrag);

  resizer.addEventListener('keydown', event => {
    if (!desktop.matches) return;
    const current = sidebar.getBoundingClientRect().width;
    const step = event.shiftKey ? 32 : 12;
    if (event.key === 'ArrowLeft') {
      applyWidth(current - step, true);
      event.preventDefault();
    } else if (event.key === 'ArrowRight') {
      applyWidth(current + step, true);
      event.preventDefault();
    } else if (event.key === 'Home') {
      remembered = defaultWidth();
      applyWidth(remembered, true);
      event.preventDefault();
    }
  });
  resizer.addEventListener('dblclick', () => {
    remembered = defaultWidth();
    applyWidth(remembered, true);
  });
  desktop.addEventListener?.('change', restoreWidth);
  window.addEventListener('resize', restoreWidth, {passive: true});
  restoreWidth();
})();
