/* Client-only "have I done this yet" tracker - no accounts, no backend, just
 * localStorage. A topic counts as complete when its visualizer has actually
 * played through to the end (see app.js's onEnd hook) or, for a content-only
 * topic with no visualizer, as soon as its page loads (there's nothing else
 * to "finish"). Every page includes this script and re-renders the
 * checkmarks/summary from whatever is in storage, so progress made on one
 * topic page shows up immediately in the sidebar and on the home page.
 */
(function () {
  const STORAGE_KEY = 'dsa-roadmap-progress';

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return new Set(raw ? JSON.parse(raw) : []);
    } catch {
      return new Set();
    }
  }

  function save(set) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
    } catch {
      /* private browsing / quota exceeded - progress just won't persist */
    }
  }

  const completed = load();

  function isComplete(slug) {
    return completed.has(slug);
  }

  function markComplete(slug) {
    if (!slug || completed.has(slug)) return;
    completed.add(slug);
    save(completed);
    renderMarks();
  }

  function resetProgress() {
    completed.clear();
    save(completed);
    renderMarks();
  }

  function renderMarks() {
    const slugEls = document.querySelectorAll('[data-progress-slug]');
    const allSlugs = new Set([...slugEls].map((el) => el.dataset.progressSlug));
    slugEls.forEach((el) => {
      const done = completed.has(el.dataset.progressSlug);
      el.classList.toggle('completed', done);
      // The visual checkmark is CSS ::before/::after generated content, which
      // screen readers don't reliably announce - this sr-only span is the
      // real accessible signal that a topic is done.
      const label = el.querySelector('.progress-complete-label');
      if (label) label.hidden = !done;
    });

    document.querySelectorAll('[data-progress-category]').forEach((el) => {
      const items = document.querySelectorAll(`[data-progress-slug][data-progress-category-of="${el.dataset.progressCategory}"]`);
      const done = [...items].filter((el2) => completed.has(el2.dataset.progressSlug)).length;
      el.textContent = items.length ? `${done}/${items.length}` : '';
    });

    const total = allSlugs.size;
    const done = [...allSlugs].filter((slug) => completed.has(slug)).length;
    document.querySelectorAll('.progress-summary').forEach((el) => {
      el.textContent = total ? `${done} / ${total} topics complete` : '';
    });
    document.querySelectorAll('.progress-bar-fill').forEach((el) => {
      el.style.width = total ? `${(100 * done) / total}%` : '0%';
    });
    document.querySelectorAll('.progress-bar-label').forEach((el) => {
      el.textContent = total ? `${done} / ${total} complete` : '';
    });
    document.querySelectorAll('#progress-reset').forEach((el) => {
      el.hidden = done === 0;
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    renderMarks();
    document.querySelectorAll('#progress-reset').forEach((el) => {
      el.addEventListener('click', resetProgress);
    });
    const contentOnlySlug = document.body.dataset.contentOnlySlug;
    if (contentOnlySlug) markComplete(contentOnlySlug);
  });

  window.dsaProgress = { isComplete, markComplete, resetProgress };
})();
