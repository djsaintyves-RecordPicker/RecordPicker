import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from verified_identity_cache import VerifiedIdentityCache
from collect_today_pick_feed import MusicBrainzArtistResolver


class VerifiedIdentityCacheTests(unittest.TestCase):
    MBID = 'a74b1b7f-71a5-4011-9441-d0b5e4122711'

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'identities.json'
        self.now = 10000000.0

    def cache(self):
        return VerifiedIdentityCache(self.path, clock=lambda: self.now)

    def test_verified_identity_survives_restart_without_network(self):
        cache = self.cache()
        resolver = MusicBrainzArtistResolver(delay_seconds=0, identity_cache=cache,
            json_fetcher=lambda _: {'artists': [{'id': self.MBID,
                'name': 'Radiohead', 'score': 100, 'tags': [{'name': 'composer'}]}]})
        self.assertEqual(resolver.resolve_exact('Radiohead'), 'Radiohead')
        cache.save()
        def offline(_):
            self.fail('A fresh verified identity must not require network access')
        restored = MusicBrainzArtistResolver(identity_cache=self.cache(), json_fetcher=offline)
        self.assertEqual(restored.resolve_exact('Radiohead'), 'Radiohead')
        self.assertTrue(restored.is_composer('Radiohead'))

    def test_expiration_is_not_extended_by_reading_or_saving(self):
        cache = self.cache()
        cache.remember('radiohead', 'Radiohead', set(), self.MBID)
        cache.save()
        self.now += cache.MAX_AGE - 1
        restored = self.cache()
        self.assertIsNotNone(restored.get('radiohead'))
        restored.save()
        self.now += 1
        self.assertIsNone(self.cache().get('radiohead'))

    def test_negative_or_inexact_results_are_not_persisted(self):
        for artists in ([], [{'id': self.MBID, 'name': 'Different artist', 'score': 100}],
                        [{'id': self.MBID, 'name': 'Radiohead', 'score': 20}]):
            cache = self.cache()
            resolver = MusicBrainzArtistResolver(delay_seconds=0, identity_cache=cache,
                json_fetcher=lambda _: {'artists': artists})
            self.assertIsNone(resolver.resolve_exact('Radiohead'))
            self.assertEqual(cache.entries, {})

    def test_missing_provider_identity_is_not_persisted(self):
        cache = self.cache()
        cache.remember('radiohead', 'Radiohead', set(), '')
        self.assertEqual(cache.entries, {})

    def test_outage_is_not_persisted(self):
        cache = self.cache()
        def offline(_):
            raise TimeoutError('offline')
        resolver = MusicBrainzArtistResolver(identity_cache=cache, json_fetcher=offline)
        with self.assertRaises(TimeoutError):
            resolver.resolve_exact('Radiohead')
        self.assertEqual(cache.entries, {})

    def test_malformed_cache_is_rejected(self):
        self.path.write_text(json.dumps({'schema': 1, 'entries': {'bad': {}}}))
        with self.assertRaises(ValueError):
            self.cache()

    def test_future_verification_is_not_accepted(self):
        cache = self.cache()
        cache.remember('radiohead', 'Radiohead', set(), self.MBID)
        cache.save()
        self.now -= 1
        self.assertEqual(self.cache().entries, {})

    def test_entry_count_is_bounded(self):
        cache = self.cache()
        cache.MAX_ENTRIES = 2
        for name in ('a', 'b', 'c'):
            cache.remember(name, name, set(), self.MBID)
            self.now += 1
        self.assertEqual(set(cache.entries), {'b', 'c'})


if __name__ == '__main__':
    unittest.main()
