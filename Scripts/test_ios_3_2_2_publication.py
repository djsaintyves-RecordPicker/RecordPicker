import json
from pathlib import Path
import unittest
from lxml import html
from publish_ios_3_2_2 import normalize
ROOT=Path(__file__).resolve().parents[1]

class IOS322PublicationTests(unittest.TestCase):
    def test_only_apple_mobile_version_advances(self):
        state=json.loads((ROOT/'data/release-state.json').read_text())
        self.assertEqual(state['current_release']['platform_versions'],dict(iphone='3.2.2',ipad='3.2.2',watch='3.2.2',mac='3.2.1',windows='3.2.1'))
        self.assertEqual(state['publication_assets']['screenshot_version'],'3.0.1')
    def test_all_studio_cards_use_localized_duo_copy_and_keep_store_destinations(self):
        pages=[ROOT/'apps/index.html',*ROOT.glob('*/apps/index.html')]
        count=0
        for p in pages:
            root=html.fromstring(p.read_text()); cards=root.xpath('//article[@id="record-picker"]')
            if not cards: continue
            count+=1; card=cards[0]
            self.assertIn('3.2.2',card.xpath('.//details/summary')[0].text_content())
            self.assertIn('iPhone Duo',card.xpath('.//details')[0].text_content())
            self.assertIn('Mac · 3.2.1',card.text_content())
            self.assertIn('Windows · 3.2.1',card.text_content())
            urls=card.xpath('.//a/@href')
            self.assertTrue(any('id6780422305' in u for u in urls))
            self.assertTrue(any('9N2ZWRL4M3JC' in u for u in urls))
            self.assertEqual(normalize(p.read_text()),normalize(normalize(p.read_text())))
        self.assertEqual(count,50)
    def test_macos_and_windows_schema_versions_are_preserved(self):
        for route in ['mac-app','windows-app']:
            p=ROOT/'fr'/route/'index.html'; root=html.fromstring(p.read_text())
            schema=next(json.loads(n.text) for n in root.xpath('//script[@type="application/ld+json"]') if json.loads(n.text).get('@type')=='SoftwareApplication')
            self.assertEqual(schema['softwareVersion'],'3.2.1')
            self.assertEqual(root.xpath('//*[@id="site-footer-version"]')[0].text_content(),'Record Picker · 3.2.1')
if __name__=='__main__': unittest.main()
