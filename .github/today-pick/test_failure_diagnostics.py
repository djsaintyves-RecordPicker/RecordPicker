#!/usr/bin/env python3

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import collect_today_pick_feed as collector
from test_collect_today_pick_feed import NOW, editorial_event


class FailedCollectionDiagnosticsTests(unittest.TestCase):
    def invoke(self, folder, source_count, minimum=6, extra=None):
        argv = ["collector", "--output", str(folder / "feed.json"),
                "--editorial-output", str(folder / "editorial.json"),
                "--health-output", str(folder / "health.json"),
                "--minimum-editorial-sources", str(minimum),
                "--generated-at", NOW.isoformat()]
        if extra:
            argv.extend(extra)

        def collect(*args, **kwargs):
            cache = kwargs["resolver"].identity_cache
            if cache is not None:
                cache.remember("radiohead", "Radiohead", set(),
                               "a74b1b7f-71a5-4011-9441-d0b5e4122711")
            kwargs["editorial_health"].update({
                f"Source {index}": {"status": "ok", "resolvedEvents": 1}
                for index in range(source_count)
            })
            return {"events": [editorial_event(f"event-{index}", f"Source {index}", NOW)
                               for index in range(source_count)]}, ["A diagnostic warning"]

        with patch("sys.argv", argv), patch.dict(os.environ, {"TICKETMASTER_API_KEY": ""}), \
                patch.object(collector, "collect", side_effect=collect) as mocked:
            with contextlib.redirect_stdout(io.StringIO()) as output, \
                    contextlib.redirect_stderr(io.StringIO()):
                try:
                    code = collector.main()
                except SystemExit as error:
                    code = error.code
            return code, output.getvalue(), mocked.call_count

    def test_failed_source_gate_preserves_feed_and_writes_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            original = b"previous feed remains untouched"
            (folder / "feed.json").write_bytes(original)
            code, output, calls = self.invoke(folder, source_count=2)
            self.assertEqual(code, 2)
            self.assertEqual(calls, 1)
            self.assertEqual((folder / "feed.json").read_bytes(), original)
            self.assertFalse((folder / "editorial.json").exists())
            health = json.loads((folder / "health.json").read_text())
            self.assertEqual(health["effectiveContributingSources"], 2)
            self.assertEqual(health["requiredContributingSources"], 6)
            self.assertFalse(health["editorialSourceGatePassed"])
            self.assertIn("WARNING: A diagnostic warning", output)

    def test_success_still_writes_validated_feed_and_separate_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            code, _, _ = self.invoke(folder, source_count=6)
            self.assertEqual(code, 0)
            feed = json.loads((folder / "feed.json").read_text())
            self.assertEqual(len(feed["events"]), 6)
            self.assertTrue((folder / "editorial.json").exists())
            health = json.loads((folder / "health.json").read_text())
            self.assertTrue(health["editorialSourceGatePassed"])

    def test_output_aliases_are_rejected_before_collection(self):
        for option in ["--health-output", "--editorial-output", "--identity-cache"]:
            with self.subTest(option=option), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                original = b"do not overwrite"
                (folder / "feed.json").write_bytes(original)
                code, _, calls = self.invoke(folder, 2, extra=[option, str(folder / "feed.json")])
                self.assertEqual(code, 2)
                self.assertEqual(calls, 0)
                self.assertEqual((folder / "feed.json").read_bytes(), original)

    def test_failed_feed_preserves_only_successful_identity_checks(self):
        from verified_identity_cache import VerifiedIdentityCache
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            original = b"previous feed"
            (folder / "feed.json").write_bytes(original)
            cache_path = folder / "identities.json"
            code, _, calls = self.invoke(folder, 1, extra=["--identity-cache", str(cache_path)])
            self.assertEqual(code, 2)
            self.assertEqual(calls, 1)
            self.assertEqual((folder / "feed.json").read_bytes(), original)
            self.assertEqual(VerifiedIdentityCache(cache_path).get("radiohead")["name"], "Radiohead")


if __name__ == "__main__":
    unittest.main()
