"""Regression checks for regional duplicates without changing public content."""
import json
from pathlib import Path
import tempfile
import unittest

import site_canonical_policy as policy


class CanonicalPolicyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def page(self, locale, route, canonical=None):
        path = self.root / locale / route / 'index.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        url = canonical or policy.public_url(locale, route)
        path.write_text('<html><head><title>Original content</title>'
                        f'<link rel="canonical" href="{url}">'
                        f'<meta property="og:url" content="{url}">'
                        '</head><body><main>Keep this regional content.</main></body></html>')
        return path

    def test_reported_regional_duplicates_keep_same_language(self):
        for route in ('choose-vinyl-record', 'manage-vinyl-collection', 'random-vinyl-record-picker', 'support', 'privacy'):
            self.page('', route)
            self.page('fr', route)
            for locale in ('en-au', 'en-ca', 'en-gb', 'en-us'):
                path = self.page(locale, route)
                self.assertEqual(policy.canonical_for(path, self.root), f'{policy.SITE}/{route}/')
            path = self.page('fr-ca', route)
            self.assertEqual(policy.canonical_for(path, self.root), f'{policy.SITE}/fr/{route}/')
            path = self.page('de', route)
            self.assertEqual(policy.canonical_for(path, self.root), f'{policy.SITE}/de/{route}/')
        self.page('fr', 'mac-app')
        path = self.page('fr-ca', 'mac-app')
        self.assertEqual(policy.canonical_for(path, self.root), f'{policy.SITE}/fr/mac-app/')

    def test_market_home_and_distinct_mac_pages_remain_separate(self):
        for route in ('', 'mac-app', 'watch-app'):
            self.page('', route)
            path = self.page('en-gb', route)
            self.assertEqual(policy.canonical_for(path, self.root), policy.public_url('en-gb', route))

    def test_missing_counterpart_is_not_linked(self):
        path = self.page('en-gb', 'support')
        self.assertEqual(policy.canonical_for(path, self.root), f'{policy.SITE}/en-gb/support/')

    def test_us_mac_alias_redirects_and_keeps_campaigns_and_deep_links(self):
        self.page('', 'mac-app')
        path = self.page('en-us', 'mac-app')
        after = policy.normalize_page(path, self.root)
        self.assertIn('<meta http-equiv="refresh" content="0;url=/mac-app/">', after)
        self.assertIn('window.location.search + window.location.hash', after)
        self.assertIn(f'<link rel="canonical" href="{policy.SITE}/mac-app/">', after)
        self.assertIn('<main>Keep this regional content.</main>', after)
        path.write_text(after)
        self.assertEqual(policy.normalize_page(path, self.root), after)
        self.assertNotIn('http-equiv="refresh"', policy.normalize_page(self.root / 'mac-app/index.html', self.root))

    def test_mac_navigation_resolves_aliases_but_keeps_other_languages_and_skip_links(self):
        text = ('<a href="../mac-app/?utm_source=instagram&amp;x=1#screens">Mac</a>'
                '<a href="https://recordpicker.app/en-us/mac-app/index.html">Mac</a>'
                "<a href='/en-us/mac-app'>Mac</a>"
                '<a href="../mac-app-extra/">Other page</a>'
                '<a href="/fr/mac-app/">Français</a>'
                '<a href="https://example.com/en-us/mac-app/">External</a>'
                '<a href="#main-content">Skip</a>')
        after = policy.normalize_mac_links(text, f'{policy.SITE}/en-us/support/')
        self.assertIn('href="/mac-app/?utm_source=instagram&amp;x=1#screens"', after)
        self.assertIn('href="/mac-app/"', after)
        self.assertIn("href='/mac-app/'", after)
        for unchanged in ('../mac-app-extra/', '/fr/mac-app/', 'https://example.com/en-us/mac-app/', '#main-content'):
            self.assertIn(unchanged, after)
        self.assertEqual(policy.normalize_mac_links(after, f'{policy.SITE}/en-us/support/'), after)

    def test_hreflang_is_reciprocal_and_stays_on_requested_route(self):
        paths = [self.page(locale, 'mac-app') for locale in ('', 'en-gb', 'en-us', 'fr', 'fr-ca')]
        for path in paths:
            after = policy.normalize_page(path, self.root)
            links = dict(policy.ALTERNATE.findall(after))
            self.assertEqual(links['x-default'], f'{policy.SITE}/mac-app/')
            self.assertEqual(links['en-US'], f'{policy.SITE}/mac-app/')
            self.assertEqual(links['en-GB'], f'{policy.SITE}/en-gb/mac-app/')
            self.assertEqual(links['fr-CA'], f'{policy.SITE}/fr-ca/mac-app/')
            self.assertEqual(links, policy.alternate_urls('mac-app', self.root))
            self.assertIn('<title>Original content</title>', after)
            self.assertIn('<main>Keep this regional content.</main>', after)
            path.write_text(after)
            self.assertEqual(policy.normalize_page(path, self.root), after)

    def test_structured_page_identity_changes_but_store_offer_does_not(self):
        self.page('', 'privacy')
        path = self.page('en-gb', 'privacy')
        url = f'{policy.SITE}/en-gb/privacy/'
        payload = {'url': url, '@id': url + '#page', 'offers': {'url': 'https://apps.apple.com/gb/app/recordpicker/id6780422305'}}
        path.write_text(path.read_text().replace('</head>', '<script type="application/ld+json">' + json.dumps(payload) + '</script></head>'))
        after = policy.normalize_page(path, self.root)
        self.assertNotIn(url, after.split('<script')[1].split('</script>')[0])
        self.assertIn('https://apps.apple.com/gb/app/recordpicker/id6780422305', after)
        self.assertIn(f'{policy.SITE}/privacy/#page', after)

    def test_sitemap_retains_images_and_unchanged_dates_and_removes_aliases(self):
        path = self.root / 'sitemap-media.xml'
        root_url = f'{policy.SITE}/privacy/'
        path.write_text('<urlset>\n<url><loc>' + root_url + '</loc><lastmod>2026-10-06</lastmod><image:loc>cover.webp</image:loc></url>\n'
                        '<url><loc>' + f'{policy.SITE}/en-gb/privacy/' + '</loc></url>\n</urlset>\n')
        after = policy.normalize_sitemap(path, {root_url}, set(), '2026-10-07')
        self.assertIn('cover.webp', after)
        self.assertIn('2026-10-06', after)
        self.assertNotIn('/en-gb/', after)
        path.write_text(after)
        self.assertEqual(policy.normalize_sitemap(path, {root_url}, set(), '2026-10-07'), after)
        self.assertIn('2026-10-07', policy.normalize_sitemap(path, {root_url}, {root_url}, '2026-10-07'))

    def test_missing_sitemap_entry_fails_before_writing_pages(self):
        path = self.page('en-gb', 'privacy')
        self.page('', 'privacy')
        before = path.read_bytes()
        (self.root / 'sitemap.xml').write_text('<urlset><url><loc>https://recordpicker.app/irrelevant/</loc></url></urlset>')
        with self.assertRaises(ValueError):
            policy.write(self.root)
        self.assertEqual(path.read_bytes(), before)

    def test_published_site_policy(self):
        self.assertEqual(policy.audit(), [])


if __name__ == '__main__':
    unittest.main()
