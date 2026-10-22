/* Progressive enhancement, isolated to the French Studio home. */
(() => {
 const root = document.querySelector('.studio-shadow-study');
 if (!root || !('IntersectionObserver' in window)) return;
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 if (reduced.matches) return;
 const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
   if (!entry.isIntersecting) continue;
   entry.target.classList.add('art-arriving');
   observer.unobserve(entry.target);
  }
 }, {threshold: .25});
 root.querySelectorAll('.music .playlist-art').forEach((art, index) => {
  art.style.setProperty('--arrival-delay', `${(index % 2) * 140}ms`);
  observer.observe(art);
 });
 reduced.addEventListener('change', event => {
  if (event.matches) {
   observer.disconnect();
   root.querySelectorAll('.art-arriving').forEach(art => art.classList.remove('art-arriving'));
  }
 });
})();
