/* Scroll-triggered reveal for topic-page sections - one restrained pattern
 * applied consistently down the page (fade + rise as each section enters
 * view), not bespoke per-element animation. The .reveal class is what the
 * CSS transition is keyed on (style.css already no-ops it entirely under
 * prefers-reduced-motion); skipping it here too just avoids setting up an
 * observer that would have nothing to do.
 */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const sections = document.querySelectorAll('.topic-page > section');
  if (!sections.length) return;

  sections.forEach((s) => s.classList.add('reveal'));

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  sections.forEach((s) => io.observe(s));
})();
