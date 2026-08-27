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

  // Groups every `[data-progress-slug]` element on the page by its
  // `data-category` attribute (present on the hidden topic-data block in
  // base.html, which renders on every page) rather than DOM nesting - there
  // is no persistent per-category container in this layout anymore.
  function fullyCompletedCategories() {
    const byCategory = new Map();
    document.querySelectorAll('[data-progress-slug]').forEach((el) => {
      const cat = el.dataset.category;
      if (!cat) return;
      if (!byCategory.has(cat)) byCategory.set(cat, []);
      byCategory.get(cat).push(el.dataset.progressSlug);
    });
    const result = new Set();
    byCategory.forEach((slugs, cat) => {
      if (slugs.length && slugs.every((slug) => completed.has(slug))) result.add(cat);
    });
    return result;
  }

  function celebrateCompletion(slug, categoriesBefore) {
    if (!window.dsaCelebrate) return;
    // Prefer the status bar on the topic page the user is actually looking
    // at (they just watched the visualizer finish); fall back to the
    // sidebar nav link for a content-only topic with no visualizer/status
    // bar, or if markComplete somehow fired from elsewhere.
    const origin = document.getElementById('note') || document.querySelector(`.nav-topic[data-progress-slug="${slug}"]`);
    if (!origin) return;
    const categoriesAfter = fullyCompletedCategories();
    const justFinishedCategory = [...categoriesAfter].some((id) => !categoriesBefore.has(id));
    window.dsaCelebrate(origin, justFinishedCategory ? { count: 40 } : { count: 18 });
  }

  function markComplete(slug) {
    if (!slug || completed.has(slug)) return;
    // Snapshot which categories are already 100% before this completion, so
    // celebrateCompletion can tell afterward whether one just crossed the
    // line - a bigger burst for finishing a whole category, not just a topic.
    const categoriesBefore = fullyCompletedCategories();
    completed.add(slug);
    save(completed);
    renderMarks();
    celebrateCompletion(slug, categoriesBefore);
    if (window.dsaAchievements) window.dsaAchievements.check();
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
