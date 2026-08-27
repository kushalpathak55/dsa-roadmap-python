/* Reusable celebration burst - the particle-burst technique validated in
 * the concept-mockup artifact, extracted into a shared module other scripts
 * (progress.js, predict.js) call on a real accomplishment. Skips the
 * animation entirely under prefers-reduced-motion, falling back to a brief
 * static highlight on the origin element so the moment still registers
 * without motion.
 */
(function () {
  const DEFAULT_COLORS = ['#2f5fa8', '#9e5a1d', '#177767', '#8253ba'];

  function reduceMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function staticHighlight(originEl) {
    if (!originEl) return;
    originEl.classList.add('celebrate-flash');
    setTimeout(() => originEl.classList.remove('celebrate-flash'), 600);
  }

  function celebrate(originEl, options) {
    const opts = options || {};
    const colors = opts.colors || DEFAULT_COLORS;
    const count = opts.count || 20;

    if (reduceMotion() || !originEl || typeof originEl.getBoundingClientRect !== 'function') {
      staticHighlight(originEl);
      return;
    }

    const rect = originEl.getBoundingClientRect();
    const originX = rect.left + rect.width / 2;
    const originY = rect.top + rect.height / 2;

    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'celebrate-particle';
      p.style.background = colors[i % colors.length];
      p.style.left = `${originX}px`;
      p.style.top = `${originY}px`;
      document.body.appendChild(p);

      const angle = Math.random() * Math.PI * 2;
      const dist = 50 + Math.random() * 80;
      const dx = Math.cos(angle) * dist;
      const dy = Math.sin(angle) * dist - 24;
      const rot = Math.random() * 360;

      const anim = p.animate(
        [
          { transform: 'translate(0, 0) rotate(0deg)', opacity: 1 },
          { transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg)`, opacity: 0 },
        ],
        { duration: 650 + Math.random() * 350, easing: 'cubic-bezier(.2,.7,.3,1)' }
      );
      anim.onfinish = () => p.remove();
      // Belt-and-suspenders cleanup in case onfinish never fires (e.g. the
      // tab was backgrounded mid-animation) - a stray particle div left in
      // the DOM is harmless but pointless.
      setTimeout(() => p.remove(), 1200);
    }
  }

  window.dsaCelebrate = celebrate;
})();
