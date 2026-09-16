'use strict';
(() => {
  const data = JSON.parse(document.getElementById('bib-data').textContent);
  const search = document.getElementById('search');
  const topic = document.getElementById('topic');
  const papers = [...document.querySelectorAll('.paper')];
  const references = [...document.querySelectorAll('.reference')];
  const sections = [...document.querySelectorAll('.topic')];
  if (window.matchMedia('(max-width: 760px)').matches) document.querySelector('.toc').open = false;
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
