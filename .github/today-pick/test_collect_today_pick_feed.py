#!/usr/bin/env python3

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import build_today_pick_feed as builder
import collect_today_pick_feed as collector


NOW = datetime(2026, 8, 20, 16, 0, tzinfo=timezone.utc)


def editorial_event(event_id: str, source: str, published_at: datetime) -> dict:
    return {
        "id": event_id,
        "kind": "news",
        "headline": f"{source} music update",
        "sourceName": source,
        "sourceURL": f"https://example.com/{event_id}",
        "publishedAt": builder.isoformat(published_at),
        "sourceKind": "editorial",
        "importance": 0.6,
        "artists": ["Example Artist"],
        "albumTitles": [],
        "composers": [],
    }


class EditorialFallbackTests(unittest.TestCase):
    def write_feed(self, events: list[dict], generated_at: datetime) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "today-pick-v1.json"
        feed = builder.build_feed({"events": events}, generated_at, 36)
        path.write_bytes(builder.encoded_feed(feed))
        return path

    def test_reuses_only_recent_events_from_sources_missing_in_fresh_run(self):
        path = self.write_feed(
            [
                editorial_event("recent-missing", "Missing Source", NOW - timedelta(hours=42)),
                editorial_event("recent-live", "Live Source", NOW - timedelta(hours=41)),
                editorial_event("old-missing", "Old Source", NOW - timedelta(hours=80)),
            ],
            NOW - timedelta(hours=40),
        )

        events, counts, generated_at = collector.fallback_editorial_events(
            path,
            NOW,
            {"Live Source"},
            72,
        )

        self.assertEqual([event["id"] for event in events], ["recent-missing"])
        self.assertEqual(counts, {"Missing Source": 1})
        self.assertEqual(generated_at, builder.isoformat(NOW - timedelta(hours=40)))

    def test_rejects_a_noncanonical_fallback_feed(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "today-pick-v1.json"
        path.write_text(json.dumps({"events": []}), encoding="utf-8")

        with self.assertRaisesRegex(collector.CollectionError, "invalid fallback feed"):
            collector.fallback_editorial_events(path, NOW, set(), 72)


if __name__ == "__main__":
    unittest.main()
