/* Light/dark toggle. The persisted choice is already stamped onto <html>
 * before first paint by the inline script at the top of base.html's <head>
 * (every page needs it, since the toggle button lives in the sidebar, which
 * is present everywhere) - this file only has to handle the click, keep the
 * meta theme-color in sync, and tell any live visualizer to repaint.
 */
(function () {
  const THEME_KEY = 'dsa-theme';
  const btn = document.getElementById('theme-toggle');
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (!btn) return;

  const PAGE_COLOR = { dark: '#10141c', light: '#f3f5f9' };

  function systemPrefersLight() {
    return window.matchMedia('(prefers-color-scheme: light)').matches;
  }

  function currentTheme() {
    const explicit = document.documentElement.dataset.theme;
    if (explicit === 'light' || explicit === 'dark') return explicit;
    return systemPrefersLight() ? 'light' : 'dark';
  }

  function applyMetaColor(theme) {
    if (metaThemeColor) metaThemeColor.setAttribute('content', PAGE_COLOR[theme]);
  }

  function syncButton() {
    const isLight = currentTheme() === 'light';
    btn.setAttribute('aria-pressed', String(isLight));
    btn.setAttribute('aria-label', isLight ? 'Switch to dark theme' : 'Switch to light theme');
  }

  applyMetaColor(currentTheme());
  syncButton();

  btn.addEventListener('click', () => {
    const next = currentTheme() === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch (e) {
      /* private browsing / quota exceeded - choice just won't persist */
    }
    applyMetaColor(next);
    syncButton();
    // Canvas/SVG visualizer colors are read live via getComputedStyle on
    // every render, but a Canvas's painted pixels don't update on their own
    // when the CSS variables change - the active renderer needs to be asked
    // to repaint. app.js listens for this alongside its existing
    // resize/orientationchange listeners.
    window.dispatchEvent(new Event('dsa-theme-change'));
  });
})();
