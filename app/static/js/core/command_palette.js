/* Ctrl/Cmd+K quick-jump across every topic - VS Code style. Reads its search
 * index straight from the sidebar nav DOM (already rendered server-side, one
 * source of truth) rather than duplicating the roadmap as a separate JSON
 * blob, so it can never drift out of sync with the actual nav.
 */
(function () {
  const overlay = document.getElementById('cmdk-overlay');
  const input = document.getElementById('cmdk-input');
  const resultsEl = document.getElementById('cmdk-results');
  const emptyEl = document.getElementById('cmdk-empty');
  const trigger = document.getElementById('cmdk-trigger');
  if (!overlay || !input || !resultsEl) return;

  const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  const triggerKey = document.querySelector('.cmdk-trigger-key');
  if (triggerKey) triggerKey.textContent = isMac ? '⌘K' : 'Ctrl K';

  function buildIndex() {
    return [...document.querySelectorAll('.nav-topic[data-progress-slug]')].map((el) => {
      const categoryEl = el.closest('.nav-category');
      const categoryNameEl = categoryEl && categoryEl.querySelector('.nav-category-name');
      return {
        slug: el.dataset.progressSlug,
        title: el.textContent.trim().replace(/\s+/g, ' '),
        category: categoryNameEl ? categoryNameEl.textContent.trim().replace(/\s+/g, ' ') : '',
        href: el.getAttribute('href'),
      };
    });
  }

  const index = buildIndex();
  let activeIndex = 0;
  let filtered = [];
  let lastFocused = null;

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function matchScore(item, q) {
    const title = item.title.toLowerCase();
    if (title.startsWith(q)) return 3;
    if (title.includes(q)) return 2;
    if (item.slug.includes(q)) return 1;
    if (item.category.toLowerCase().includes(q)) return 0;
    return -1;
  }

  function render(query) {
    const q = query.trim().toLowerCase();
    if (!q) {
      filtered = index.slice(0, 8);
    } else {
      filtered = index
        .map((item) => ({ item, score: matchScore(item, q) }))
        .filter((r) => r.score >= 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 8)
        .map((r) => r.item);
    }

    activeIndex = 0;
    resultsEl.innerHTML = '';
    emptyEl.hidden = filtered.length > 0;
    filtered.forEach((item, i) => {
      const li = document.createElement('li');
      li.id = `cmdk-option-${i}`;
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      li.className = 'cmdk-result' + (i === 0 ? ' active' : '');
      li.innerHTML = `<span class="cmdk-result-title">${escapeHtml(item.title)}</span><span class="cmdk-result-category">${escapeHtml(item.category)}</span>`;
      li.addEventListener('mousemove', () => setActive(i));
      li.addEventListener('click', () => go(item));
      resultsEl.appendChild(li);
    });
    // Keep the accessible name of the trigger's popup in sync so a screen
    // reader announces how many topics matched, not just the raw list.
    emptyEl.textContent = filtered.length ? '' : 'No topics match.';
    setActive(0);
  }

  function setActive(i) {
    activeIndex = i;
    [...resultsEl.children].forEach((el, idx) => {
      const isActive = idx === i;
      el.classList.toggle('active', isActive);
      el.setAttribute('aria-selected', String(isActive));
    });
    const activeOption = resultsEl.children[i];
    if (activeOption) {
      input.setAttribute('aria-activedescendant', activeOption.id);
      activeOption.scrollIntoView({ block: 'nearest' });
    } else {
      input.removeAttribute('aria-activedescendant');
    }
  }

  function go(item) {
    window.location.href = item.href;
  }

  function isOpen() {
    return !overlay.hidden;
  }

  function open() {
    lastFocused = document.activeElement;
    overlay.hidden = false;
    input.value = '';
    render('');
    requestAnimationFrame(() => input.focus());
  }

  function close() {
    overlay.hidden = true;
    input.blur();
    // Return focus to whatever opened the palette (the Ctrl+K trigger, or
    // wherever the keyboard was) instead of dropping it back to <body>.
    if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
    lastFocused = null;
  }

  input.addEventListener('input', () => render(input.value));
  input.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (filtered.length) setActive((activeIndex + 1) % filtered.length);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (filtered.length) setActive((activeIndex - 1 + filtered.length) % filtered.length);
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (filtered[activeIndex]) go(filtered[activeIndex]);
    } else if (event.key === 'Escape') {
      event.preventDefault();
      close();
    } else if (event.key === 'Tab') {
      // The input is the only focusable control in the dialog (result
      // selection moves via aria-activedescendant, not real DOM focus) -
      // trap Tab here instead of letting it escape to the page behind the
      // overlay.
      event.preventDefault();
    }
  });

  overlay.addEventListener('mousedown', (event) => {
    if (event.target === overlay) close();
  });
  if (trigger) trigger.addEventListener('click', open);

  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      isOpen() ? close() : open();
    }
  });
})();
