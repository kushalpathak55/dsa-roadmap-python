/* A short, text-only first-run tour. Auto-shows once on the homepage (never
 * on a deep-linked topic page, so a first-time visitor isn't interrupted
 * before they can read anything) and can be reopened anytime via the "?"
 * buttons in the sidebar and mobile topbar.
 */
(function () {
  const overlay = document.getElementById('onboarding-overlay');
  const dialog = overlay && overlay.querySelector('.onboarding-dialog');
  const steps = overlay ? [...overlay.querySelectorAll('.onboarding-step')] : [];
  const dots = overlay ? [...overlay.querySelectorAll('.onboarding-dot')] : [];
  const nextBtn = document.getElementById('onboarding-next');
  const skipBtn = document.getElementById('onboarding-skip');
  if (!overlay || !dialog || !steps.length || !nextBtn || !skipBtn) return;

  const SEEN_KEY = 'dsa-onboarding-seen';
  let current = 0;
  let lastFocused = null;

  function hasSeenTour() {
    try {
      return localStorage.getItem(SEEN_KEY) === '1';
    } catch (e) {
      return false;
    }
  }

  function markSeen() {
    try {
      localStorage.setItem(SEEN_KEY, '1');
    } catch (e) {
      /* localStorage unavailable (private mode, disabled) - tour just
         re-shows next visit, not worth failing louder over. */
    }
  }

  function showStep(i) {
    steps.forEach((el, idx) => {
      el.hidden = idx !== i;
    });
    dots.forEach((el, idx) => el.classList.toggle('active', idx === i));
    nextBtn.textContent = i === steps.length - 1 ? 'Done' : 'Next';
    const heading = steps[i].querySelector('h2');
    if (heading) heading.focus();
  }

  function open() {
    lastFocused = document.activeElement;
    current = 0;
    overlay.hidden = false;
    document.body.classList.add('onboarding-locked');
    // Wait a frame so the overlay has actually painted (display:flex) before
    // focusing into it - focus() on a still-display:none element is a no-op.
    requestAnimationFrame(() => showStep(0));
  }

  function close() {
    overlay.hidden = true;
    document.body.classList.remove('onboarding-locked');
    if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
    lastFocused = null;
  }

  function closeAndMarkSeen() {
    markSeen();
    close();
  }

  function getFocusable() {
    return [skipBtn, nextBtn].filter((el) => el && !el.disabled);
  }

  nextBtn.addEventListener('click', () => {
    if (current === steps.length - 1) {
      closeAndMarkSeen();
    } else {
      current += 1;
      showStep(current);
    }
  });

  skipBtn.addEventListener('click', closeAndMarkSeen);

  overlay.addEventListener('mousedown', (event) => {
    if (event.target === overlay) closeAndMarkSeen();
  });

  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeAndMarkSeen();
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

  [document.getElementById('onboarding-trigger'), document.getElementById('mobile-onboarding-trigger')]
    .filter(Boolean)
    .forEach((btn) => btn.addEventListener('click', open));

  const isHomepage = !!document.querySelector('.roadmap-grid');
  if (isHomepage && !hasSeenTour()) open();
})();
