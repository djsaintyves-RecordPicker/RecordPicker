"""Bounded cache of successful MusicBrainz identity checks, not news events."""
import json
import math
import time
from pathlib import Path
from uuid import UUID

from build_today_pick_feed import atomic_write


class VerifiedIdentityCache:
    MAX_AGE = 30 * 24 * 60 * 60
    MAX_ENTRIES = 2000
    MAX_BYTES = 2 * 1024 * 1024

    def __init__(self, path: Path, clock=time.time):
        self.path = path
        self.clock = clock
        self.entries = {}
        if not path.exists():
            return
        if path.stat().st_size > self.MAX_BYTES:
            raise ValueError("identity cache exceeds size limit")
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("schema") != 1:
            raise ValueError("unsupported identity cache schema")
        entries = document.get("entries")
        if not isinstance(entries, dict) or len(entries) > self.MAX_ENTRIES:
            raise ValueError("invalid identity cache entries")
        for key, value in entries.items():
            if not self.valid(key, value):
                raise ValueError("invalid verified identity cache entry")
            if self.fresh(value):
                self.entries[key] = value

    @staticmethod
    def valid(key, value):
        if not isinstance(key, str) or not 1 <= len(key) <= 300:
            return False
        if not isinstance(value, dict):
            return False
        name, roles = value.get("name"), value.get("roles")
        stamp = value.get("verifiedAt")
        if not isinstance(name, str) or not 1 <= len(name) <= 300:
            return False
        if not isinstance(roles, list) or len(roles) > 100:
            return False
        if not all(isinstance(role, str) and len(role) <= 300 for role in roles):
            return False
        if isinstance(stamp, bool) or not isinstance(stamp, (float, int)) or not math.isfinite(stamp):
            return False
        try:
            UUID(value.get("mbid", ""))
        except (ValueError, TypeError, AttributeError):
            return False
        return True

    def fresh(self, value):
        age = self.clock() - value["verifiedAt"]
        return 0 <= age < self.MAX_AGE

    def get(self, key):
        value = self.entries.get(key)
        return value if value is not None and self.fresh(value) else None

    def remember(self, key, name, roles, mbid):
        value = dict(name=name, roles=sorted(roles), mbid=mbid, verifiedAt=self.clock())
        # Older provider responses without an MBID may work in memory, but
        # cannot become durable verification records.
        if self.valid(key, value):
            self.entries[key] = value
            self.entries = dict(sorted(self.entries.items(),
                key=lambda item: (-item[1]["verifiedAt"], item[0]))[:self.MAX_ENTRIES])

    def save(self):
        entries = {k: v for k, v in self.entries.items() if self.fresh(v)}
        payload = json.dumps(dict(schema=1, entries=entries), ensure_ascii=False,
                             sort_keys=True, allow_nan=False).encode("utf-8")
        if len(payload) > self.MAX_BYTES:
            raise ValueError("identity cache exceeds size limit")
        atomic_write(self.path, payload)
