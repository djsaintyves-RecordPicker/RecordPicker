(() => {
  const locales = ["ar-SA", "bn-BD", "ca", "cs", "da", "de-DE", "el", "en-AU", "en-CA", "en-GB", "en-US", "es-ES", "es-MX", "fi", "fr-CA", "fr-FR", "gu-IN", "he", "hi", "hr", "hu", "id", "it", "ja", "kn-IN", "ko", "ml-IN", "mr-IN", "ms", "nl-NL", "no", "or-IN", "pa-IN", "pl", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl-SI", "sv", "ta-IN", "te-IN", "th", "tr", "uk", "ur-PK", "vi", "zh-Hans", "zh-Hant"];
  const exact = new Map(locales.map(locale => [locale.toLowerCase(), locale]));
  const defaults = {en:'en-US',fr:'fr-FR',es:'es-ES',pt:'pt-PT',zh:'zh-Hans',nb:'no',nn:'no'};
  function choose(preferences) {
    for (const preference of preferences) {
      const tag = preference.toLowerCase().replace(/_/g, '-');
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
    const locale = choose(navigator.languages?.length ? navigator.languages : [navigator.language || 'en-US']);
    const match = location.pathname.match(/^\/(?:([a-zA-Z-]+)\/)?apps\/(dulpi\/)?(?:index\.html)?$/);
    if (!match || (match[1] && match[1] !== 'fr' && !exact.has(match[1].toLowerCase()))) return;
    const prefix = locale === 'en-US' ? '' : locale === 'fr-FR' ? 'fr/' : locale.toLowerCase() + '/';
    const target = '/' + prefix + 'apps/' + (match[2] || '');
    if (target !== location.pathname) location.replace(target + location.search + location.hash);
  }
  applyLanguage();
  addEventListener('languagechange', applyLanguage);
})();
