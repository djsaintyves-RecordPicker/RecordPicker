import unittest
from site_campaign_links import decorate, normalize


class CampaignLinksTests(unittest.TestCase):
    def test_website_fallback_preserves_mac_and_language(self):
        from urllib.parse import urlsplit, parse_qs
        url = decorate('https://apps.apple.com/fr/app/id6780422305?platform=mac&ct=old')
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query, {'platform': ['mac'], 'ct': ['RP_Website'], 'pt': ['129016722'], 'mt': ['8']})

    def test_only_known_store_products(self):
        for href in ('https://example.com/id6780422305', 'https://apps.apple.com/app/id1111111111', 'mailto:a@example.com'):
            self.assertEqual(decorate(href), href)

    def test_html_is_idempotent_and_does_not_rewrite_embedded_json(self):
        sample = '<html><head><script type="application/ld+json">{"url":"https://apps.apple.com/app/id6780422305"}</script></head><body><a href="https://apps.apple.com/app/id6820177689">Snory</a></body></html>'
        result = normalize(sample)
        self.assertEqual(normalize(result), result)
        self.assertIn('ct=ST_Website', result)
        self.assertIn('"url":"https://apps.apple.com/app/id6780422305"', result)
        self.assertEqual(result.count('/apps/campaign-links.js'), 0)

    def test_executable_pages_keep_campaign_runtime(self):
        page = '<html><head><script src="/site.js"></script></head><body></body></html>'
        result = normalize(page)
        self.assertEqual(result.count('/apps/campaign-links.js'), 1)
        self.assertEqual(normalize(result), result)

    def test_routine_and_windows(self):
        self.assertIn('ct=MPR_Website', decorate('https://apps.apple.com/app/id6820104318'))
        self.assertIn('cid=RP_Website', decorate('https://apps.microsoft.com/detail/9N2ZWRL4M3JC'))

    def test_static_privacy_subsites_remain_script_free(self):
        page = '<html><head></head><body><a href="https://apps.apple.com/app/id6820177689">Store</a></body></html>'
        normalized = normalize(page)
        self.assertNotIn('<script', normalized)
        self.assertIn('ct=ST_Website', normalized)

    def test_japanese_and_korean_static_links_have_their_own_rp_tokens(self):
        japanese = normalize('<html lang="ja"><head></head><body><a href="https://apps.apple.com/jp/app/recordpicker/id6780422305">Store</a></body></html>')
        korean = normalize('<html lang="ko"><head></head><body><a href="https://apps.microsoft.com/detail/9N2ZWRL4M3JC">Store</a></body></html>')
        self.assertIn('ct=RP_Website_JP', japanese)
        self.assertIn('cid=RP_Website_KR', korean)


if __name__ == '__main__':
    unittest.main()
