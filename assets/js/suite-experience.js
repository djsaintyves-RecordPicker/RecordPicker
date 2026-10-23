/* Shared progressive enhancement for Record Picker Studio web pages. */
(() => {
 const root = document.querySelector('.suite-experience');
 if (!root || !('IntersectionObserver' in window)) return;
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 // Include editorial illustrations across products, guides and support pages.
 // Device wrappers animate as one object; their nested screenshots stay settled.
 const artwork = [...root.querySelectorAll('main img,.phone-shell,.watch-shell')].filter(element => {
  if (element.matches('.phone-shell,.watch-shell')) return true;
  if (element.closest('.phone-shell,.watch-shell,.studio-brand-composition,button,.store-cta,.store-link,.button,.playlist-actions,.platforms')) return false;
  if (element.matches('.platform-logo,.store-logo')) return false;
  const width = Number(element.getAttribute('width'));
  return !width || width > 48;
 });
 const introduction = [...root.querySelectorAll('.studio-introduction')];
 const community = [...root.querySelectorAll('.community-grid article')];
 community.forEach((card, index) => card.style.setProperty('--community-delay', `${index * 220}ms`));
 const singleControls = [...root.querySelectorAll('main .store-cta,main .suite-product-cta,main .store-link,main .button')].filter(element => !element.closest('.project-store-grid,.playlist-actions,.cta-row,.app-actions,.platforms'));
 const groups = [...root.querySelectorAll('.project-store-grid,.playlist-actions,.cta-row,.app-actions,.platforms')];
 artwork.forEach((art, index) => art.style.setProperty('--arrival-delay', `${(index % 2) * 120}ms`));
 const rearmTimers = new Map();
 function revealObserver(className, visibleFraction) {
  return new IntersectionObserver(entries => {
   for (const entry of entries) {
    // Brief scroll reversals keep the element settled instead of flashing again.
    if (!entry.isIntersecting) {
     if (!rearmTimers.has(entry.target)) rearmTimers.set(entry.target, setTimeout(() => {
      entry.target.classList.remove(className); rearmTimers.delete(entry.target);
     }, 500));
    } else {
     clearTimeout(rearmTimers.get(entry.target)); rearmTimers.delete(entry.target);
     if (entry.intersectionRatio >= visibleFraction) entry.target.classList.add(className);
    }
   }
  }, {threshold:[0, visibleFraction]});
 }
 const introductionObserver = revealObserver('intro-arriving', .35);
 const artObserver = revealObserver('art-arriving', .25);
 const storeObserver = revealObserver('stores-arriving', .85);
 const singleObserver = revealObserver('single-arriving', .65);
 const communityObserver = revealObserver('community-arriving', .65);
 function syncMotion() {
  rearmTimers.forEach(timer => clearTimeout(timer)); rearmTimers.clear();
  artObserver.disconnect(); storeObserver.disconnect(); communityObserver.disconnect(); introductionObserver.disconnect(); singleObserver.disconnect();
  [...artwork,...groups,...community,...introduction,...singleControls].forEach(element => element.classList.remove('art-arriving','stores-arriving','community-arriving','intro-arriving','single-arriving'));
  if (reduced.matches) return;
  introduction.forEach(element => introductionObserver.observe(element));
  artwork.forEach(element => artObserver.observe(element));
  groups.forEach(element => storeObserver.observe(element));
  singleControls.forEach(element => singleObserver.observe(element));
  community.forEach(element => communityObserver.observe(element));
 }
 reduced.addEventListener('change', syncMotion);
 syncMotion();
})();

/* A single short pulse on real touch activation, where the browser supports it. */
(() => {
 const root = document.querySelector('.suite-experience');
 if (!root || typeof navigator.vibrate !== 'function') return;
 const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
 let lastTouch = -Infinity;
 let lastPulse = -Infinity;
 root.addEventListener('pointerup', event => {
  if (event.isTrusted && event.pointerType === 'touch') lastTouch = performance.now();
 }, {passive:true});
 root.addEventListener('click', event => {
  const now = performance.now();
  if (!event.isTrusted || reduced.matches || now-lastTouch > 500 || now-lastPulse < 100) return;
  const control = event.target instanceof Element ? event.target.closest('a,button,summary') : null;
  if (!control || control.matches(':disabled,[aria-disabled="true"]')) return;
  try { navigator.vibrate(8); lastPulse = now; } catch { /* Unsupported or restricted: keep the normal action. */ }
 }, {passive:true});
})();
