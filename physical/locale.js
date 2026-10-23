// MPR pages follow the browser's ordered language preferences, without controls.
(() => {
 const locales = ["ar-SA", "bn-BD", "ca", "cs", "da", "de-DE", "el", "en-AU", "en-CA", "en-GB", "en-US", "es-ES", "es-MX", "fi", "fr-CA", "fr-FR", "gu-IN", "he", "hi", "hr", "hu", "id", "it", "ja", "kn-IN", "ko", "ml-IN", "mr-IN", "ms", "nl-NL", "no", "or-IN", "pa-IN", "pl", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl-SI", "sv", "ta-IN", "te-IN", "th", "tr", "uk", "ur-PK", "vi", "zh-Hans", "zh-Hant"];
 const exact = new Map(locales.map(locale => [locale.toLowerCase(), locale]));
 const defaults = {en:'en-US',fr:'fr-FR',es:'es-ES',pt:'pt-PT',zh:'zh-Hans',nb:'no',nn:'no',iw:'he'};
 function choose(preferences) {
  for (const preference of preferences) {
   const tag = String(preference).toLowerCase().replace(/_/g,'-');
   if (exact.has(tag)) return exact.get(tag);
   const base = tag.split('-')[0];
   if (base === 'zh') return /(?:hant|tw|hk|mo)/.test(tag) ? 'zh-Hant' : 'zh-Hans';
   if (defaults[base]) return defaults[base];
   const match = locales.find(locale => locale.toLowerCase().split('-')[0] === base);
   if (match) return match;
  }
  return 'en-US';
 }
 function applyLanguage() {
  const match = location.pathname.match(/^\/physical\/(?:([a-z-]+)\/)?(about|support|privacy)\/(?:index\.html)?$/i);
  const guide = location.pathname.match(/^\/(?:([a-z-]+)\/)?physical-routine-guide\/(?:index\.html)?$/i);
  if (!match && !guide) return;
  const locale = choose(navigator.languages?.length ? navigator.languages : [navigator.language || 'en-US']);
  const prefix = locale === 'en-US' ? '' : locale === 'fr-FR' ? 'fr/' : locale.toLowerCase() + '/';
  const guidePrefix = locale === 'en-US' ? '' : locale === 'fr-FR' ? 'fr/' : locale.toLowerCase() + '/';
  const target = guide ? '/' + guidePrefix + 'physical-routine-guide/' : '/physical/' + prefix + match[2].toLowerCase() + '/';
  if (target !== location.pathname) location.replace(target + location.search + location.hash);
 }
 applyLanguage();
 addEventListener('languagechange', applyLanguage);
})();
