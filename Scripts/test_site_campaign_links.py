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
        self.assertEqual(result.count('/apps/campaign-links.js'), 1)

    def test_routine_and_windows(self):
        self.assertIn('ct=MPR_Website', decorate('https://apps.apple.com/app/id6820104318'))
        self.assertIn('cid=RP_Website', decorate('https://apps.microsoft.com/detail/9N2ZWRL4M3JC'))

    def test_static_privacy_subsites_remain_script_free(self):
        page = '<html><head></head><body><a href="https://apps.apple.com/app/id6820177689">Store</a></body></html>'
        normalized = normalize(page)
        self.assertNotIn('<script', normalized)
        self.assertIn('ct=ST_Website', normalized)


if __name__ == '__main__':
    unittest.main()
