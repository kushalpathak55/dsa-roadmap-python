/* Achievements - milestones derived from state that already exists
 * elsewhere (progress.js, streak.js, predict.js), not tracked separately.
 * Definitions are rebuilt from the live DOM/state on every check() call
 * rather than cached, so they can never drift out of sync with the actual
 * roadmap. check() is called on every page load and directly by
 * progress.js (topic/category completion) and predict.js (a correct
 * answer) - the same "call it if window.X exists" pattern already used for
 * window.dsaCelebrate.
 */
(function () {
  const STORAGE_KEY = 'dsa-achievements-unlocked';

  function loadUnlocked() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return new Set(raw ? JSON.parse(raw) : []);
    } catch (e) {
      return new Set();
    }
  }

  function saveUnlocked(set) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
    } catch (e) {
      /* private browsing / quota exceeded - unlocks just won't persist */
    }
  }

  const unlocked = loadUnlocked();

  // Same attribute-grouping technique progress.js uses internally: every
  // [data-progress-slug] element (the hidden topic-data block in base.html,
  // present on every page) carries its own data-category, no DOM nesting
  // to walk.
  function categoryGroups() {
    const byCategory = new Map();
    document.querySelectorAll('[data-progress-slug]').forEach((el) => {
      const name = el.dataset.category;
      if (!name) return;
      if (!byCategory.has(name)) byCategory.set(name, []);
      byCategory.get(name).push(el.dataset.progressSlug);
    });
    return [...byCategory.entries()].map(([name, slugs]) => ({ name, slugs }));
  }

  function allSlugs() {
    return [...document.querySelectorAll('[data-progress-slug]')].map((el) => el.dataset.progressSlug);
  }

  function buildDefinitions() {
    const progress = window.dsaProgress;
    if (!progress) return [];
    const defs = [];

    defs.push({
      id: 'first-topic',
      label: 'First Step',
      description: 'Complete your first topic.',
      check: () => allSlugs().some((slug) => progress.isComplete(slug)),
    });

    categoryGroups().forEach((cat, index) => {
      if (!cat.slugs.length) return;
      defs.push({
        id: `category-${index}`,
        label: `Finished ${cat.name}`,
        description: `Complete every topic in ${cat.name}.`,
        check: () => cat.slugs.every((slug) => progress.isComplete(slug)),
      });
    });

    defs.push({
      id: 'streak-7',
      label: '7-Day Streak',
      description: 'Visit 7 days in a row.',
      check: () => !!window.dsaStreak && window.dsaStreak.getCount() >= 7,
    });
    defs.push({
      id: 'streak-30',
      label: '30-Day Streak',
      description: 'Visit 30 days in a row.',
      check: () => !!window.dsaStreak && window.dsaStreak.getCount() >= 30,
    });
    defs.push({
      id: 'predict-streak-10',
      label: 'Sharp Shooter',
      description: '10 correct predictions in a row.',
      check: () => !!window.dsaPredictStreak && window.dsaPredictStreak.getCount() >= 10,
    });
    defs.push({
      id: 'roadmap-complete',
      label: 'Roadmap Complete',
      description: 'Finish every topic on the roadmap.',
      check: () => {
        const slugs = allSlugs();
        return slugs.length > 0 && slugs.every((slug) => progress.isComplete(slug));
      },
    });

    return defs;
  }

  function renderList(definitions) {
    const list = document.getElementById('achievements-list');
    if (!list) return;
    list.innerHTML = '';
    definitions.forEach((def) => {
      const done = unlocked.has(def.id);
      const item = document.createElement('div');
      item.className = 'achievement-item' + (done ? ' unlocked' : '');
      const stamp = document.createElement('span');
      stamp.className = 'achievement-stamp';
      stamp.setAttribute('aria-hidden', 'true');
      stamp.textContent = done ? '★' : '☆';
      const text = document.createElement('span');
      text.className = 'achievement-text';
      const label = document.createElement('span');
      label.className = 'achievement-label';
      label.textContent = def.label;
      const desc = document.createElement('span');
      desc.className = 'achievement-desc';
      desc.textContent = def.description;
      text.appendChild(label);
      text.appendChild(desc);
      item.appendChild(stamp);
      item.appendChild(text);
      list.appendChild(item);
    });
  }

  const trigger = document.getElementById('achievements-trigger');
  const overlay = document.getElementById('achievements-overlay');
  const dialog = overlay && overlay.querySelector('.achievements-dialog');
  const closeBtn = document.getElementById('achievements-close');
  let lastFocused = null;

  function getFocusable() {
    return dialog ? [...dialog.querySelectorAll('button:not([hidden])')].filter((el) => !el.disabled) : [];
  }

  function openModal() {
    if (!overlay) return;
    lastFocused = document.activeElement;
    overlay.hidden = false;
    requestAnimationFrame(() => {
      if (closeBtn) closeBtn.focus();
    });
  }

  function closeModal() {
    if (!overlay) return;
    overlay.hidden = true;
    if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
    lastFocused = null;
  }

  if (trigger) trigger.addEventListener('click', openModal);
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (overlay && dialog) {
    overlay.addEventListener('mousedown', (event) => {
      if (event.target === overlay) closeModal();
    });
    dialog.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeModal();
        return;
      }
      if (event.key !== 'Tab') return;
      const focusable = getFocusable();
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }

  function check() {
    const definitions = buildDefinitions();
    if (!definitions.length) return;
    let newlyUnlocked = null;
    definitions.forEach((def) => {
      if (!unlocked.has(def.id) && def.check()) {
        unlocked.add(def.id);
        newlyUnlocked = def;
      }
    });
    if (newlyUnlocked) {
      saveUnlocked(unlocked);
      if (window.dsaCelebrate && trigger) {
        window.dsaCelebrate(trigger, { count: 30, colors: ['#846514', '#2f5fa8', '#177767'] });
      }
    }
    renderList(definitions);
  }

  document.addEventListener('DOMContentLoaded', check);

  window.dsaAchievements = { check };
})();
