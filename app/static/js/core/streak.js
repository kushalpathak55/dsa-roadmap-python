/* Daily streak tracking - a visible reason to come back tomorrow. Runs on
 * every page (loaded in base.html, like progress.js) since the streak badge
 * lives in the sidebar, present everywhere. The badge markup already shows
 * "0 day streak" by default in the template, so a script failure just
 * leaves that static placeholder instead of anything broken-looking.
 */
(function () {
  const COUNT_KEY = 'dsa-streak-count';
  const DATE_KEY = 'dsa-streak-last-date';

  function todayLocal() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }

  // a/b are YYYY-MM-DD local-date strings - parsed at noon UTC so a plain
  // subtraction isn't thrown off by a DST transition landing between them.
  function daysBetween(a, b) {
    const da = new Date(a + 'T12:00:00Z');
    const db = new Date(b + 'T12:00:00Z');
    return Math.round((db - da) / 86400000);
  }

  function computeCount() {
    const today = todayLocal();
    let lastDate = null;
    let count = 0;
    try {
      lastDate = localStorage.getItem(DATE_KEY);
      const raw = localStorage.getItem(COUNT_KEY);
      const n = Number(raw);
      count = Number.isInteger(n) && n > 0 ? n : 0;
    } catch (e) {
      return 1; // storage unavailable - just show 1 for this visit, don't crash
    }

    if (lastDate === today) {
      if (count === 0) count = 1; // first-ever visit landed exactly today
    } else if (lastDate && daysBetween(lastDate, today) === 1) {
      count += 1;
    } else {
      count = 1; // gap of more than a day, or no prior visit at all
    }

    try {
      localStorage.setItem(COUNT_KEY, String(count));
      localStorage.setItem(DATE_KEY, today);
    } catch (e) {
      /* private browsing / quota exceeded - streak just won't persist */
    }
    return count;
  }

  const count = computeCount();

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.streak-badge-n').forEach((el) => {
      el.textContent = String(count);
    });
  });

  // Exposed so Part 5 (achievements) can read the current streak without a
  // second source of truth.
  window.dsaStreak = { getCount: () => count };
})();
