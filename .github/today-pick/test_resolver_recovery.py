"""Offline checks: recovery never bypasses exact artist verification."""
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from urllib.error import HTTPError

from collect_today_pick_feed import MusicBrainzArtistResolver
import collect_today_pick_feed as collector


class ResolverRecoveryTests(unittest.TestCase):
    def test_collection_shares_verified_identities_between_sources(self):
        resolver = self.make_resolver([self.artist('Radiohead')])
        def editorial(_now, **kwargs):
            self.assertIs(kwargs['resolver'], resolver)
            self.assertEqual(resolver.resolve_exact('Radiohead'), 'Radiohead')
            return [], []
        def wikimedia(_now, **kwargs):
            self.assertIs(kwargs['resolver'], resolver)
            self.assertEqual(resolver.resolve_exact('Radiohead'), 'Radiohead')
            return [], []
        with patch.object(collector, 'MusicBrainzArtistResolver', return_value=resolver), \
             patch.object(collector, 'editorial_events', side_effect=editorial), \
             patch.object(collector, 'wikimedia_on_this_day_events', side_effect=wikimedia):
            collector.collect(datetime.now(timezone.utc), include_musicbrainz=False,
                              include_musicbrainz_events=False)
        self.assertEqual(self.calls, 1)

    def make_resolver(self, responses):
        self.now = 0
        self.calls = 0
        def fetch(_url):
            self.calls += 1
            value = responses.pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        return MusicBrainzArtistResolver(fetch, delay_seconds=0,
            recovery_cooldown_seconds=60, maximum_recovery_probes=2,
            monotonic_clock=lambda: self.now)

    @staticmethod
    def unavailable():
        return HTTPError('https://musicbrainz.org/ws/2/artist/', 503, 'Unavailable', {}, None)

    @staticmethod
    def artist(name):
        return {'artists': [{'name': name, 'score': 100}]}

    def test_recovers_only_after_cooldown_and_exact_match(self):
        resolver = self.make_resolver([self.unavailable(), self.artist('Radiohead')])
        with self.assertRaises(HTTPError):
            resolver.resolve_exact('Radiohead')
        self.assertIsNone(resolver.resolve_exact('Radiohead'))
        self.assertEqual(self.calls, 1)
        self.now = 60
        self.assertEqual(resolver.resolve_exact('Radiohead'), 'Radiohead')
        self.assertEqual(self.calls, 2)

    def test_continuing_outage_has_a_hard_request_limit(self):
        resolver = self.make_resolver([self.unavailable() for _ in range(3)])
        for instant in (0, 60, 120):
            self.now = instant
            with self.assertRaises(HTTPError):
                resolver.resolve_exact('Radiohead')
        self.now = 10000
        for _ in range(100):
            self.assertIsNone(resolver.resolve_exact('Radiohead'))
        self.assertEqual(self.calls, 3)

    def test_previously_verified_identity_survives_outage(self):
        resolver = self.make_resolver([self.artist('Radiohead'), self.unavailable()])
        self.assertEqual(resolver.resolve_exact('Radiohead'), 'Radiohead')
        with self.assertRaises(HTTPError):
            resolver.resolve_exact('Björk')
        self.assertEqual(resolver.resolve_exact('Radiohead'), 'Radiohead')
        self.assertEqual(self.calls, 2)

    def test_recovery_does_not_accept_a_different_artist(self):
        resolver = self.make_resolver([self.unavailable(), self.artist('Another Artist')])
        with self.assertRaises(HTTPError):
            resolver.resolve_exact('Radiohead')
        self.now = 60
        self.assertIsNone(resolver.resolve_exact('Radiohead'))

    def test_outage_does_not_cache_an_unresolved_headline_permanently(self):
        resolver = self.make_resolver([self.unavailable(), self.artist('Radiohead')])
        def resolve():
            return resolver.resolve('New album', ['Radiohead'], include_headline_candidates=False)
        with self.assertRaises(HTTPError):
            resolve()
        self.assertEqual(resolve(), [])
        self.now = 60
        self.assertEqual(resolve(), ['Radiohead'])
        self.assertEqual(self.calls, 2)


if __name__ == '__main__':
    unittest.main()
