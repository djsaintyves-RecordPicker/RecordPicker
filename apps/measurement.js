/* No requests or browser storage while configuration is absent. */
(async () => {
  let optedOut = false;
  try { optedOut = localStorage.getItem('yd-measurement-optout') === '1'; } catch (_) {}
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-measurement-optout]').forEach(input => {
      input.checked = optedOut;
      input.addEventListener('change', () => {
        try { localStorage.setItem('yd-measurement-optout', input.checked ? '1' : '0'); } catch (_) {}
        location.reload();
      });
    });
  });
  if (optedOut || location.hostname !== 'recordpicker.app' || navigator.globalPrivacyControl || navigator.doNotTrack === '1') return;
  try {
    const response = await fetch('/apps/measurement-config.json', {credentials:'omit', cache:'no-cache'});
    if (!response.ok) return;
    const {websiteId, scriptUrl} = await response.json();
    if (!/^[a-f0-9-]{36}$/i.test(websiteId || '') || scriptUrl !== 'https://cloud.umami.is/script.js') return;
    const script = document.createElement('script');
    script.defer = true;
    script.src = scriptUrl;
    script.dataset.websiteId = websiteId;
    script.dataset.doNotTrack = 'true';
    script.dataset.excludeSearch = 'true';
    script.dataset.excludeHash = 'true';
    window.ydBeforeSend = (type, payload) => {
      if (payload.url) payload.url = payload.url.split(/[?#]/)[0];
      if (payload.referrer) {
        try { const ref = new URL(payload.referrer); payload.referrer = ref.origin; } catch (_) { payload.referrer = ''; }
      }
      return payload;
    };
    script.dataset.beforeSend = 'ydBeforeSend';
    document.head.appendChild(script);
  } catch (_) { /* Navigation remains available if measurement fails. */ }
})();
