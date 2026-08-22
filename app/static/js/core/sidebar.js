/* Mobile-only off-canvas sidebar drawer. Desktop never sees this - the
 * sidebar is always visible there and this script's toggle/backdrop simply
 * has nothing to do (buttons that open it are display:none above the
 * mobile breakpoint, see style.css). */
(function () {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  const openBtn = document.getElementById('sidebar-toggle');
  const closeBtn = document.getElementById('sidebar-close');
  const searchBtn = document.getElementById('mobile-search-trigger');
  if (!sidebar || !backdrop || !openBtn) return;

  function open() {
    sidebar.classList.add('open');
    backdrop.classList.add('open');
    openBtn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('sidebar-locked');
  }

  function close() {
    sidebar.classList.remove('open');
    backdrop.classList.remove('open');
    openBtn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('sidebar-locked');
  }

  openBtn.addEventListener('click', open);
  if (closeBtn) closeBtn.addEventListener('click', close);
  backdrop.addEventListener('click', close);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && sidebar.classList.contains('open')) close();
  });

  // The search icon in the mobile top bar just opens the same command
  // palette the desktop "jump to..." button and Ctrl+K do - one search
  // implementation, two entry points.
  if (searchBtn) {
    searchBtn.addEventListener('click', () => {
      const cmdkTrigger = document.getElementById('cmdk-trigger');
      if (cmdkTrigger) cmdkTrigger.click();
    });
  }
})();
