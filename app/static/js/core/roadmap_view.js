/* Cards/Timeline/Guided toggle for the homepage, plus the "next in your
 * guided path" continuation strip on topic pages. Two independent pieces in
 * one file since they share the same DOM-read-in-order technique
 * (command_palette.js's pattern: read the sidebar's .nav-topic elements as
 * the single source of truth, rather than a second data structure) - each
 * guards on its own page's elements so loading this on any page is safe.
 */

/* --- Homepage: Cards/Timeline/Guided view toggle + Guided Mode --- */
(function () {
  const grid = document.getElementById('roadmap-grid');
  const timeline = document.getElementById('roadmap-timeline');
  const guidedContainer = document.getElementById('roadmap-guided');
  const cardsBtn = document.getElementById('view-cards-btn');
  const timelineBtn = document.getElementById('view-timeline-btn');
  const guidedBtn = document.getElementById('view-guided-btn');
  if (!grid || !timeline || !guidedContainer || !cardsBtn || !timelineBtn || !guidedBtn) return;

  const VIEW_KEY = 'dsa-roadmap-view';
  const VIEWS = ['cards', 'timeline', 'guided'];

  function setView(view) {
    document.documentElement.dataset.view = view;
    cardsBtn.setAttribute('aria-pressed', String(view === 'cards'));
    timelineBtn.setAttribute('aria-pressed', String(view === 'timeline'));
    guidedBtn.setAttribute('aria-pressed', String(view === 'guided'));
    try {
      localStorage.setItem(VIEW_KEY, view);
    } catch (e) {
      /* private browsing / quota exceeded - choice just won't persist */
    }
  }

  const current = VIEWS.includes(document.documentElement.dataset.view) ? document.documentElement.dataset.view : 'cards';
  cardsBtn.setAttribute('aria-pressed', String(current === 'cards'));
  timelineBtn.setAttribute('aria-pressed', String(current === 'timeline'));
  guidedBtn.setAttribute('aria-pressed', String(current === 'guided'));

  cardsBtn.addEventListener('click', () => setView('cards'));
  timelineBtn.addEventListener('click', () => setView('timeline'));
  guidedBtn.addEventListener('click', () => {
    setView('guided');
    if (guided) guided.showCurrentStep();
  });

  function stripTitle(el) {
    const clone = el.cloneNode(true);
    clone.querySelectorAll('.sr-only, .badge').forEach((n) => n.remove());
    return clone.textContent.trim().replace(/\s+/g, ' ');
  }

  function buildSequence() {
    return [...document.querySelectorAll('.nav-topic[data-progress-slug]')].map((el) => {
      const categoryEl = el.closest('.nav-category');
      const categoryNameEl = categoryEl && categoryEl.querySelector('.nav-category-name');
      return {
        slug: el.dataset.progressSlug,
        title: stripTitle(el),
        why: el.dataset.guidedReason || '',
        href: el.getAttribute('href'),
        categoryLabel: categoryNameEl ? categoryNameEl.textContent.trim().replace(/\s+/g, ' ') : '',
        catVar: categoryEl ? categoryEl.style.getPropertyValue('--cat') : '',
      };
    });
  }

  function initGuided() {
    const sequence = buildSequence();
    if (!sequence.length) return null;

    const INDEX_KEY = 'dsa-guided-index';
    const stepEl = document.getElementById('guided-step');
    const catBadgeEl = document.getElementById('guided-category-badge');
    const titleEl = document.getElementById('guided-title');
    const whyEl = document.getElementById('guided-why');
    const completeEl = document.getElementById('guided-complete-badge');
    const backBtn = document.getElementById('guided-back');
    const nextBtn = document.getElementById('guided-next');
    const startLink = document.getElementById('guided-start');

    let index = null;

    function firstIncompleteIndex() {
      if (!window.dsaProgress) return 0;
      const i = sequence.findIndex((item) => !window.dsaProgress.isComplete(item.slug));
      return i === -1 ? sequence.length - 1 : i;
    }

    function loadIndex() {
      try {
        const raw = localStorage.getItem(INDEX_KEY);
        if (raw !== null) {
          const n = Number(raw);
          if (Number.isInteger(n) && n >= 0 && n < sequence.length) return n;
        }
      } catch (e) {
        /* ignore */
      }
      return firstIncompleteIndex();
    }

    // Persisting the step index means "a guided session is active" (the
    // topic-page continuation strip keys off this key's mere presence) - so
    // this must only happen once Guided is actually shown, never just
    // because this script ran on the homepage in Cards/Timeline view.
    function renderStep() {
      const item = sequence[index];
      guidedContainer.querySelector('.guided-card').style.setProperty('--cat', item.catVar || 'var(--cat-1)');
      stepEl.textContent = `Step ${index + 1} of ${sequence.length}`;
      catBadgeEl.textContent = item.categoryLabel;
      titleEl.textContent = item.title;
      whyEl.textContent = item.why;
      const done = window.dsaProgress && window.dsaProgress.isComplete(item.slug);
      completeEl.hidden = !done;
      startLink.href = item.href;
      startLink.textContent = done ? 'Review this topic →' : 'Start this topic →';
      backBtn.disabled = index === 0;
      nextBtn.disabled = index === sequence.length - 1;
      try {
        localStorage.setItem(INDEX_KEY, String(index));
      } catch (e) {
        /* ignore */
      }
    }

    function showCurrentStep() {
      if (index === null) index = loadIndex();
      renderStep();
    }

    backBtn.addEventListener('click', () => {
      if (index > 0) {
        index -= 1;
        renderStep();
      }
    });
    nextBtn.addEventListener('click', () => {
      if (index < sequence.length - 1) {
        index += 1;
        renderStep();
      }
    });

    // A reload landing directly on a persisted "guided" view (from an
    // earlier visit) should render immediately, not wait for a click.
    if (document.documentElement.dataset.view === 'guided') showCurrentStep();

    return { showCurrentStep };
  }

  const guided = initGuided();
})();

/* --- Topic pages: "next in your guided path" continuation strip --- */
(function () {
  const strip = document.getElementById('guided-continue');
  if (!strip) return;

  let hasGuidedSession = false;
  try {
    hasGuidedSession = localStorage.getItem('dsa-guided-index') !== null;
  } catch (e) {
    return;
  }
  if (!hasGuidedSession) return;

  const navTopics = [...document.querySelectorAll('.nav-topic[data-progress-slug]')];
  const currentIndex = navTopics.findIndex((el) => el.getAttribute('aria-current') === 'page');
  if (currentIndex === -1 || currentIndex >= navTopics.length - 1) return;

  const nextEl = navTopics[currentIndex + 1];
  const clone = nextEl.cloneNode(true);
  clone.querySelectorAll('.sr-only, .badge').forEach((n) => n.remove());
  const nextTitle = clone.textContent.trim().replace(/\s+/g, ' ');

  const label = document.createElement('span');
  label.className = 'guided-continue-label';
  label.textContent = 'Next in your guided path';

  const link = document.createElement('a');
  link.href = nextEl.getAttribute('href');
  link.textContent = `${nextTitle} →`;
  link.addEventListener('click', () => {
    try {
      localStorage.setItem('dsa-guided-index', String(currentIndex + 1));
    } catch (e) {
      /* ignore */
    }
  });

  strip.appendChild(label);
  strip.appendChild(link);
  strip.hidden = false;
})();
