/* Homepage-only scroll-reveal for the roadmap cards. `.roadmap-card` stays
 * visible by default in the stylesheet - this script is what opts elements
 * into a hidden starting state (the `.reveal-init` class), and only once
 * it's confirmed running. A script load failure, ad blocker, or unrelated
 * earlier JS error must never be able to leave the homepage's primary nav
 * permanently invisible.
 */
(function () {
  const cards = [...document.querySelectorAll('.roadmap-card')];
  if (!cards.length) return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!('IntersectionObserver' in window)) return;

  cards.forEach((card) => card.classList.add('reveal-init'));

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('reveal-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  cards.forEach((card) => observer.observe(card));
})();
