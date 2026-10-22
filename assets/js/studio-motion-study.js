/* Progressive enhancement, isolated to the French Studio home. */
(() => {
 const root = document.querySelector('.studio-shadow-study');
 if (!root || !('IntersectionObserver' in window)) return;
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 const artwork = [...root.querySelectorAll('.music .playlist-art')];
 const introduction = [...root.querySelectorAll('.studio-introduction')];
 const community = [...root.querySelectorAll('.community-grid article')];
 community.forEach((card, index) => card.style.setProperty('--community-delay', `${index * 140}ms`));
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
 const introductionObserver = revealObserver('intro-arriving', .35);
 const artObserver = revealObserver('art-arriving', .25);
 const storeObserver = revealObserver('stores-arriving', .85);
 const communityObserver = revealObserver('community-arriving', .65);
 function syncMotion() {
  artObserver.disconnect(); storeObserver.disconnect(); communityObserver.disconnect(); introductionObserver.disconnect();
  [...artwork,...groups,...community,...introduction].forEach(element => element.classList.remove('art-arriving','stores-arriving','community-arriving','intro-arriving'));
  if (reduced.matches) return;
  introduction.forEach(element => introductionObserver.observe(element));
  artwork.forEach(element => artObserver.observe(element));
  groups.forEach(element => storeObserver.observe(element));
  community.forEach(element => communityObserver.observe(element));
 }
 reduced.addEventListener('change', syncMotion);
 syncMotion();
})();
