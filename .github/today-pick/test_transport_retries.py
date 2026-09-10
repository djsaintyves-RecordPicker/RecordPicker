"""Read-time failures must use the same bounded retries as connection errors."""
import unittest
from unittest.mock import MagicMock, patch

import collect_today_pick_feed as collector


class TransportRetryTests(unittest.TestCase):
    def test_read_timeout_retries_and_returns_only_complete_second_response(self):
        first = MagicMock()
        first.__enter__.return_value = first
        first.status = 200
        first.read.side_effect = TimeoutError("read timed out")
        second = MagicMock()
        second.__enter__.return_value = second
        second.status = 200
        second.read.return_value = b'{"artists": []}'
        with patch.object(collector, "urlopen", side_effect=[first, second]) as opened, \
                patch.object(collector.time, "sleep") as sleep:
            self.assertEqual(collector.fetch_musicbrainz_json("https://example.test/artist"), {"artists": []})
        self.assertEqual(opened.call_count, 2)
        sleep.assert_called_once_with(1)
        first.__exit__.assert_called_once()

    def test_persistent_read_timeout_stops_at_two_attempts(self):
        with patch.object(collector, "urlopen", side_effect=TimeoutError("timeout")) as opened, \
                patch.object(collector.time, "sleep") as sleep:
            with self.assertRaises(TimeoutError):
                collector.fetch_musicbrainz_json("https://example.test/artist")
        self.assertEqual(opened.call_count, 2)
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
