/* Copy-to-clipboard for every syntax-highlighted code block (loader.py wraps
 * each one in a .code-card with a .copy-btn header). One delegated listener
 * handles every block on the page, built or content-only alike, instead of
 * wiring a per-block handler - a topic's markdown can contain more than one
 * fenced code snippet.
 */
(function () {
  document.addEventListener('click', (event) => {
    const btn = event.target.closest('.copy-btn');
    if (!btn) return;
    const card = btn.closest('.code-card');
    const code = card && card.querySelector('code');
    if (!code) return;
    navigator.clipboard.writeText(code.innerText).then(() => {
      const original = btn.textContent;
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      clearTimeout(btn._copyResetTimer);
      btn._copyResetTimer = setTimeout(() => {
        btn.textContent = original;
        btn.classList.remove('copied');
      }, 1400);
    }).catch(() => {
      /* clipboard permission denied or unavailable - fail silently, the
       * button just won't confirm a copy that didn't happen */
    });
  });
})();
