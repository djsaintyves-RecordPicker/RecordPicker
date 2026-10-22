/* Progressive enhancement, isolated to the French Studio home. */
(() => {
 const root = document.querySelector('.studio-shadow-study');
 if (!root || !('IntersectionObserver' in window)) return;
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 const artwork = [...root.querySelectorAll('.music .playlist-art')];
 const groups = [...root.querySelectorAll('#record-picker .project-store-grid,.music .playlist-actions')];
 artwork.forEach((art, index) => art.style.setProperty('--arrival-delay', `${(index % 2) * 140}ms`));
 function revealObserver(className, visibleFraction) {
  return new IntersectionObserver(entries => {
   for (const entry of entries) {
    // Rearm only after leaving the viewport completely, avoiding scroll flicker.
    if (!entry.isIntersecting) entry.target.classList.remove(className);
    else if (entry.intersectionRatio >= visibleFraction) entry.target.classList.add(className);
   }
  }, {threshold:[0, visibleFraction]});
 }
 const artObserver = revealObserver('art-arriving', .25);
 const storeObserver = revealObserver('stores-arriving', .85);
 function syncMotion() {
  artObserver.disconnect(); storeObserver.disconnect();
  [...artwork,...groups].forEach(element => element.classList.remove('art-arriving','stores-arriving'));
  if (reduced.matches) return;
  artwork.forEach(element => artObserver.observe(element));
  groups.forEach(element => storeObserver.observe(element));
 }
 reduced.addEventListener('change', syncMotion);
 syncMotion();
})();
