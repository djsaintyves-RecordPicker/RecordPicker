/* Progressive enhancement, isolated to the French Studio home. */
(() => {
 const root = document.querySelector('.studio-shadow-study');
 if (!root || !('IntersectionObserver' in window)) return;
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 if (reduced.matches) return;
 const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
   if (!entry.isIntersecting) continue;
   entry.target.classList.add(entry.target.matches('.project-store-grid') ? 'stores-arriving' : 'art-arriving');
   observer.unobserve(entry.target);
  }
 }, {threshold: .25});
 root.querySelectorAll('.music .playlist-art').forEach((art, index) => {
  art.style.setProperty('--arrival-delay', `${(index % 2) * 140}ms`);
  observer.observe(art);
 });
 const storeObserver = new IntersectionObserver(entries => {
  for (const entry of entries) {
   if (!entry.isIntersecting) continue;
   entry.target.classList.add('stores-arriving');
   storeObserver.unobserve(entry.target);
  }
 }, {threshold:.85});
 root.querySelectorAll('#record-picker .project-store-grid,.music .playlist-actions').forEach(group => storeObserver.observe(group));
 reduced.addEventListener('change', event => {
  if (event.matches) {
   observer.disconnect();
   storeObserver.disconnect();
   root.querySelectorAll('.art-arriving,.stores-arriving').forEach(element => element.classList.remove('art-arriving','stores-arriving'));
  }
 });
})();
