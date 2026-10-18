const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../apps/campaign-links.js'), 'utf8');
const rp = 'https://apps.apple.com/fr/app/recordpicker/id6780422305?platform=mac';
const st = 'https://apps.apple.com/app/id6820177689';
const mpr = 'https://apps.apple.com/fr/app/id6820104318';
const ms = 'https://apps.microsoft.com/detail/9N2ZWRL4M3JC?hl=fr-fr';
function run(search = '', {storage = new Map(), referrer = '', blocked = false} = {}) {
  const links = [rp, st, mpr, ms, 'https://example.com/id6780422305', 'mailto:support@recordpicker.app'].map(href => ({
    href, getAttribute() { return this.href; }, setAttribute(_, value) { this.href = value; }
  }));
  const document = { readyState: 'complete', referrer, querySelectorAll: () => links };
  const sessionStorage = {
    getItem(key) { if (blocked) throw Error('blocked'); return storage.get(key); },
    setItem(key, value) { if (blocked) throw Error('blocked'); storage.set(key, value); },
    removeItem(key) { if (blocked) throw Error('blocked'); storage.delete(key); }
  };
  const window = {location: {search, href: 'https://recordpicker.app/mac-app/' + search}};
  vm.runInNewContext(source, {window, document, sessionStorage, URL, URLSearchParams});
  return {links, api: window.recordPickerCampaigns};
}
function token(result, index = 0) { return new URL(result.links[index].href).searchParams.get(index === 3 ? 'cid' : 'ct'); }
const website = run();
assert.equal(token(website), 'RP_Website');
assert.equal(token(website, 1), 'ST_Website');
assert.equal(token(website, 2), 'MPR_Website');
assert.equal(token(website, 3), 'RP_Website');
assert.equal(new URL(website.links[0].href).searchParams.get('platform'), 'mac');
assert.equal(new URL(website.links[3].href).searchParams.get('hl'), 'fr-fr');
assert.equal(website.links[4].href, 'https://example.com/id6780422305');
assert.equal(website.links[5].href, 'mailto:support@recordpicker.app');
for (const alias of ['ig', 'instagram', 'IG']) {
  const result = run('?utm_source=' + alias);
  assert.equal(token(result), 'RP19_InstagramBio');
  assert.equal(token(result, 1), 'ST_Instagram');
  assert.equal(token(result, 2), 'MPR_Instagram');
  assert.equal(token(result, 3), 'RP19_InstagramBio');
}
for (const alias of ['tiktok', 'tt']) assert.equal(token(run('?utm_source=' + alias)), 'RP_TikTok');
assert.equal(token(run('?utm_source=tiktok', {blocked: true})), 'RP_TikTok');
assert.equal(token(run('', {referrer: 'https://l.instagram.com/'})), 'RP19_InstagramBio');
assert.equal(token(run('', {referrer: 'https://www.tiktok.com/@record.picker'})), 'RP_TikTok');
assert.equal(token(run('?utm_source=not-a-campaign')), 'RP_Website');
const storage = new Map();
run('?utm_source=ig', {storage});
assert.equal(token(run('', {storage})), 'RP19_InstagramBio');
assert.equal(token(run('?utm_source=website', {storage})), 'RP_Website');
assert.equal(token(run('', {storage})), 'RP_Website');
assert.equal(run('?utm_source=tiktok').api.decorate('https://apps.apple.com/app/id1111111111'), 'https://apps.apple.com/app/id1111111111');
assert.equal(run('?utm_source=tiktok').api.decorate('https://apps.apple.com.evil.test/app/id6780422305'), 'https://apps.apple.com.evil.test/app/id6780422305');
// Execute the real homepage redirect: a language hop must retain attribution.
const site = fs.readFileSync(require('node:path').join(__dirname, '../site.js'), 'utf8');
const redirect = site.match(/function redirectToStaticLocale\(lang\) \{[\s\S]*?return true;\n  \}/)[0];
for (const query of ['?utm_source=ig', '?utm_source=tiktok&lang=fr']) {
  let destination;
  const window = {location: {pathname: '/', protocol: 'https:', search: query, hash: '#record-picker', replace(value) { destination = value; }}};
  vm.runInNewContext(redirect + '; redirectToStaticLocale("fr");', {
    window, body: {hasAttribute() { return false; }}, currentPublicPagePath() { return ''; }, siteBasePath: '/'
  });
  assert.equal(destination, '/fr/' + query + '#record-picker');
}
console.log('OK: website/Instagram/TikTok, three apps, Windows, navigation, blocked storage and destination parameters.');
