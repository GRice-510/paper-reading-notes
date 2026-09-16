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
    style.id = 'detailed-toc-style';
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
      @media(max-width:760px){
        .toc nav{display:block}
        .toc-section>summary{padding:10px 5px;font-size:.8rem}
        .toc-section>summary .toc-section-title{font-size:.8rem}
        .toc nav a.toc-paper-link{grid-template-columns:2.65rem minmax(0,1fr);font-size:.77rem;padding:7px 5px}
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
        // Only write on a user click. Never read or request access to clipboard contents.
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
    let count = 0;
    papers.forEach(el => {
      el.hidden = (topic.value && topic.value !== el.dataset.section) || !match(el);
      if (!el.hidden) {count++; JSON.parse(el.dataset.refs).forEach(key => visibleRefs.add(key));}
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
