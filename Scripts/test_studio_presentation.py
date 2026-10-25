"""Regression: Studio regeneration must retain presentation and acquisition links."""
import json
import unittest
from pathlib import Path
from lxml import html
from site_studio_presentation import normalize

ROOT = Path(__file__).resolve().parents[1]


class StudioPresentationRegression(unittest.TestCase):
    def test_generated_templates_keep_design_and_destinations(self):
        templates = json.loads((ROOT / 'data/creator-hub/templates.json').read_text())
        for name, source in templates.items():
            if not any(name.endswith('-' + kind) for kind in ('hub', 'dulpi', 'music', 's05e01', 's05e02')):
                continue
            with self.subTest(template=name):
                before, after = html.fromstring(source), html.fromstring(normalize(source))
                self.assertEqual(sorted(before.xpath('//a/@href')), sorted(after.xpath('//a/@href')))
                self.assertEqual(before.xpath('//link[@rel="canonical"]/@href'), after.xpath('//link[@rel="canonical"]/@href'))
                self.assertEqual(before.xpath('//script[@type="application/ld+json"]/text()'), after.xpath('//script[@type="application/ld+json"]/text()'))
                self.assertIn('suite-experience', after.xpath('//body/@class')[0].split())
                self.assertEqual(len(after.xpath('//script[contains(@src,"suite-experience.js")]')), 1)
                self.assertEqual(len(after.xpath('//link[contains(@href,"suite-experience.css")]')), 1)
                for card in after.xpath('//article[contains(@class,"project-card")]'):
                    for link in card.xpath('.//a[contains(@class,"store-button")]'):
                        self.assertIn('project-store-grid', link.getparent().get('class', ''))
                self.assertEqual(normalize(source), normalize(normalize(source)))


if __name__ == '__main__':
    unittest.main()
