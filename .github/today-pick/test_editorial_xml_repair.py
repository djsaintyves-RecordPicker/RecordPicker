import unittest
from datetime import datetime, timezone
from collect_today_pick_feed import parse_editorial_feed, EditorialSource, CollectionError


class EditorialXMLRepairTests(unittest.TestCase):
    def parse(self, title, suffix=''):
        payload = ('<rss><channel><item><title>' + title + '</title>'
            '<link>https://example.com/article?a=1&amp;b=2</link>'
            '<pubDate>Fri, 11 Sep 2026 08:00:00 GMT</pubDate></item>'
            + suffix + '</channel></rss>').encode()
        return parse_editorial_feed(payload, EditorialSource('Test', 'https://example.com', 0.6),
                                    datetime(2026, 9, 11, 9, tzinfo=timezone.utc))

    def test_bare_ampersand_is_recovered(self):
        result = self.parse('Overspace & Supertime')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Overspace & Supertime')

    def test_existing_entities_remain_correct(self):
        self.assertEqual(self.parse('Rock &amp; Roll')[0]['title'], 'Rock & Roll')

    def test_cdata_is_preserved_during_repair_elsewhere(self):
        self.assertEqual(self.parse('<![CDATA[Rock & Roll]]>', '<extra>R & B</extra>')[0]['title'], 'Rock & Roll')

    def test_structural_errors_still_fail(self):
        with self.assertRaises(CollectionError):
            self.parse('Rock & Roll', '<broken>')

    def test_unknown_entities_are_not_invented(self):
        with self.assertRaises(CollectionError):
            self.parse('Rock &unknown; Roll')


if __name__ == '__main__':
    unittest.main()
