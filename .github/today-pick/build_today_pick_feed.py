#!/usr/bin/env python3
"""Build a bounded, source-backed Today Pick feed.

The input is an editorial JSON object containing an ``events`` array. This
tool performs the same structural and source checks as the app before writing
the versioned public envelope atomically. It never reads a user collection.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = 1
MAX_PAYLOAD_BYTES = 2 * 1024 * 1024
MAX_EVENTS = 500
MAX_VALIDITY_HOURS = 7 * 24
MAX_HEADLINE_LENGTH = 280
MAX_NAME_LENGTH = 160
MAX_URL_LENGTH = 2048
MAX_IDENTITIES = 32
LOCALE_PATTERN = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z]{4})?(?:-[A-Za-z]{2}|-[0-9]{3})?$")
SOURCE_KINDS = {"official", "editorial", "structuredDatabase", "socialSignal"}
EVENT_KINDS = {
    "newRelease",
    "reissue",
    "anniversary",
    "award",
    "concert",
    "obituary",
    "birthday",
    "news",
}


class FeedValidationError(ValueError):
    """Raised when an editorial input cannot become a trustworthy feed."""


def parse_timestamp(raw: Any, field: str) -> datetime:
    if not isinstance(raw, str) or not raw.strip():
        raise FeedValidationError(f"{field} must be an ISO-8601 timestamp")
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise FeedValidationError(f"{field} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise FeedValidationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def isoformat(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def validate_https_url(raw: Any, field: str) -> str:
    if not isinstance(raw, str) or len(raw) > MAX_URL_LENGTH:
        raise FeedValidationError(f"{field} is missing or too long")
    parsed = urlparse(raw)
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise FeedValidationError(f"{field} must be a public HTTPS URL")
    return raw


def canonical_domain(raw_url: str) -> str:
    host = (urlparse(raw_url).hostname or "").lower().strip(".")
    labels = [label for label in host.split(".") if label]
    if labels[:1] == ["www"]:
        labels = labels[1:]
    if len(labels) <= 2:
        return ".".join(labels)
    country_second_levels = {"ac", "co", "com", "gov", "net", "org"}
    suffix_length = 3 if len(labels[-1]) == 2 and labels[-2] in country_second_levels else 2
    return ".".join(labels[-suffix_length:])


def bounded_string(raw: Any, field: str, maximum: int = MAX_NAME_LENGTH) -> str:
    if not isinstance(raw, str):
        raise FeedValidationError(f"{field} must be text")
    value = raw.strip()
    if not value or len(value) > maximum:
        raise FeedValidationError(f"{field} is empty or too long")
    return value


def bounded_strings(raw: Any, field: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list) or len(raw) > MAX_IDENTITIES:
        raise FeedValidationError(f"{field} must contain at most {MAX_IDENTITIES} values")
    return [bounded_string(value, f"{field}[]") for value in raw]


def normalized_localizations(raw: Any, field: str) -> dict[str, str]:
    if raw is None:
        return {}
    if not isinstance(raw, dict) or len(raw) > MAX_IDENTITIES:
        raise FeedValidationError(f"{field} must contain at most {MAX_IDENTITIES} values")
    normalized: dict[str, str] = {}
    for locale, value in raw.items():
        if not isinstance(locale, str):
            raise FeedValidationError(f"{field} contains an invalid locale")
        canonical_locale = locale.strip().replace("_", "-")
        if not LOCALE_PATTERN.fullmatch(canonical_locale):
            raise FeedValidationError(f"{field} contains an invalid locale")
        canonical_locale = "-".join(
            part.title() if index == 1 and len(part) == 4
            else part.upper() if index > 0 and len(part) in {2, 3}
            else part.lower()
            for index, part in enumerate(canonical_locale.split("-"))
        )
        if canonical_locale in normalized:
            raise FeedValidationError(f"{field} contains duplicate locales")
        normalized[canonical_locale] = bounded_string(
            value,
            f"{field}.{canonical_locale}",
            MAX_HEADLINE_LENGTH,
        )
    return {locale: normalized[locale] for locale in sorted(normalized)}


def normalized_source(raw: Any, field: str, now: datetime) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise FeedValidationError(f"{field} must be an object")
    name = bounded_string(raw.get("name"), f"{field}.name")
    url = validate_https_url(raw.get("url"), f"{field}.url")
    published = parse_timestamp(raw.get("publishedAt"), f"{field}.publishedAt")
    if published > now + timedelta(minutes=5):
        raise FeedValidationError(f"{field}.publishedAt is in the future")
    kind = raw.get("kind")
    if kind not in SOURCE_KINDS:
        raise FeedValidationError(f"{field}.kind is unsupported")
    return {
        "name": name,
        "url": url,
        "publishedAt": isoformat(published),
        "kind": kind,
    }


def validate_source_policy(event: dict[str, Any]) -> None:
    sources = [
        {
            "name": event["sourceName"],
            "url": event["sourceURL"],
            "publishedAt": event["publishedAt"],
            "kind": event["sourceKind"],
        }
    ] + event["corroboratingSources"]
    if any(source["kind"] == "official" for source in sources):
        return
    evidence = [source for source in sources if source["kind"] != "socialSignal"]
    if not evidence:
        raise FeedValidationError(f"{event['id']}: a social signal is not evidence")
    if event["kind"] == "obituary":
        domains = {canonical_domain(source["url"]) for source in evidence}
        if len(domains) < 2:
            raise FeedValidationError(f"{event['id']}: an obituary needs two independent domains")


def normalized_place(raw: Any, event_id: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise FeedValidationError(f"{event_id}: place must be an object")
    country = bounded_string(raw.get("countryCode"), f"{event_id}.place.countryCode").upper()
    if len(country) != 2 or not country.isalpha():
        raise FeedValidationError(f"{event_id}: countryCode must contain two letters")
    city = bounded_string(raw.get("city"), f"{event_id}.place.city")
    venue = raw.get("venueName")
    if venue is not None:
        venue = bounded_string(venue, f"{event_id}.place.venueName")
    geohash = raw.get("coarseGeohash")
    if geohash is not None:
        if not isinstance(geohash, str):
            raise FeedValidationError(f"{event_id}: coarseGeohash must be text")
        geohash = "".join(character for character in geohash.lower() if character.isalnum())
        if not 3 <= len(geohash) <= 12:
            raise FeedValidationError(f"{event_id}: coarseGeohash has an invalid precision")
    return {
        "venueName": venue,
        "city": city,
        "countryCode": country,
        "coarseGeohash": geohash,
    }


def normalize_event(raw: Any, now: datetime) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise FeedValidationError("every event must be an object")
    event_id = bounded_string(raw.get("id"), "event.id")
    kind = raw.get("kind")
    if kind not in EVENT_KINDS:
        raise FeedValidationError(f"{event_id}: unsupported event kind")
    headline = bounded_string(raw.get("headline"), f"{event_id}.headline", MAX_HEADLINE_LENGTH)
    source_name = bounded_string(raw.get("sourceName"), f"{event_id}.sourceName")
    source_url = validate_https_url(raw.get("sourceURL"), f"{event_id}.sourceURL")
    published = parse_timestamp(raw.get("publishedAt"), f"{event_id}.publishedAt")
    if published > now + timedelta(minutes=5):
        raise FeedValidationError(f"{event_id}: publishedAt is in the future")
    source_kind = raw.get("sourceKind", "editorial")
    if source_kind not in SOURCE_KINDS:
        raise FeedValidationError(f"{event_id}: unsupported source kind")
    importance = raw.get("importance", 0.5)
    if not isinstance(importance, (int, float)) or isinstance(importance, bool) or not 0 <= importance <= 1:
        raise FeedValidationError(f"{event_id}: importance must be between 0 and 1")
    release_id = raw.get("discogsReleaseID")
    if release_id is not None and (not isinstance(release_id, int) or isinstance(release_id, bool) or release_id <= 0):
        raise FeedValidationError(f"{event_id}: discogsReleaseID must be a positive integer")
    event_date = raw.get("eventDate")
    if event_date is not None:
        event_date = isoformat(parse_timestamp(event_date, f"{event_id}.eventDate"))
    corroborating_raw = raw.get("corroboratingSources", [])
    if not isinstance(corroborating_raw, list) or len(corroborating_raw) > MAX_IDENTITIES:
        raise FeedValidationError(f"{event_id}: too many corroborating sources")
    corroborating = [
        normalized_source(value, f"{event_id}.corroboratingSources[]", now)
        for value in corroborating_raw
    ]
    event = {
        "id": event_id,
        "kind": kind,
        "headline": headline,
        "headlineLocalizations": normalized_localizations(
            raw.get("headlineLocalizations"),
            f"{event_id}.headlineLocalizations",
        ),
        "sourceName": source_name,
        "sourceURL": source_url,
        "publishedAt": isoformat(published),
        "sourceKind": source_kind,
        "corroboratingSources": corroborating,
        "eventDate": event_date,
        "importance": float(importance),
        "artists": bounded_strings(raw.get("artists"), f"{event_id}.artists"),
        "albumTitles": bounded_strings(raw.get("albumTitles"), f"{event_id}.albumTitles"),
        "composers": bounded_strings(raw.get("composers"), f"{event_id}.composers"),
        "discogsReleaseID": release_id,
        "place": normalized_place(raw.get("place"), event_id),
    }
    validate_source_policy(event)
    return event


def build_feed(document: Any, generated_at: datetime, ttl_hours: int) -> dict[str, Any]:
    if not isinstance(document, dict) or not isinstance(document.get("events"), list):
        raise FeedValidationError("input must be an object containing an events array")
    if not 1 <= ttl_hours <= MAX_VALIDITY_HOURS:
        raise FeedValidationError(f"ttl-hours must be between 1 and {MAX_VALIDITY_HOURS}")
    raw_events = document["events"]
    if len(raw_events) > MAX_EVENTS:
        raise FeedValidationError(f"feed contains more than {MAX_EVENTS} events")

    by_id: dict[str, dict[str, Any]] = {}
    for raw_event in raw_events:
        event = normalize_event(raw_event, generated_at)
        existing = by_id.get(event["id"])
        if existing is not None and existing != event:
            raise FeedValidationError(f"{event['id']}: conflicting duplicate identifier")
        by_id[event["id"]] = event

    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": isoformat(generated_at),
        "expiresAt": isoformat(generated_at + timedelta(hours=ttl_hours)),
        "events": [by_id[event_id] for event_id in sorted(by_id)],
    }


def validate_published_feed(
    document: Any,
    relative_to: datetime | None = None,
) -> dict[str, Any]:
    """Validate that a deployed envelope is fresh and exactly canonical."""

    if not isinstance(document, dict):
        raise FeedValidationError("published feed must be a JSON object")
    expected_keys = {"schemaVersion", "generatedAt", "expiresAt", "events"}
    if set(document) != expected_keys:
        raise FeedValidationError("published feed contains missing or unexpected fields")
    if document.get("schemaVersion") != SCHEMA_VERSION:
        raise FeedValidationError("published feed uses an unsupported schema version")

    now = (relative_to or datetime.now(timezone.utc)).astimezone(timezone.utc)
    generated_at = parse_timestamp(document.get("generatedAt"), "generatedAt")
    expires_at = parse_timestamp(document.get("expiresAt"), "expiresAt")
    if generated_at > now + timedelta(minutes=5):
        raise FeedValidationError("published feed was generated in the future")
    if expires_at <= now:
        raise FeedValidationError("published feed has expired")
    if expires_at <= generated_at:
        raise FeedValidationError("published feed expires before it was generated")
    if expires_at - generated_at > timedelta(hours=MAX_VALIDITY_HOURS):
        raise FeedValidationError("published feed validity exceeds seven days")

    raw_events = document.get("events")
    if not isinstance(raw_events, list):
        raise FeedValidationError("published feed events must be an array")
    if len(raw_events) > MAX_EVENTS:
        raise FeedValidationError(f"published feed contains more than {MAX_EVENTS} events")

    normalized_events = [normalize_event(event, generated_at) for event in raw_events]
    identifiers = [event["id"] for event in normalized_events]
    if len(identifiers) != len(set(identifiers)):
        raise FeedValidationError("published feed contains duplicate event identifiers")
    if identifiers != sorted(identifiers):
        raise FeedValidationError("published feed events are not sorted by identifier")

    canonical = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": isoformat(generated_at),
        "expiresAt": isoformat(expires_at),
        "events": normalized_events,
    }
    if document != canonical:
        raise FeedValidationError("published feed is not in canonical form")
    encoded_feed(canonical)
    return canonical


def encoded_feed(feed: dict[str, Any]) -> bytes:
    data = (json.dumps(feed, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(data) > MAX_PAYLOAD_BYTES:
        raise FeedValidationError("generated feed exceeds the 2 MiB client limit")
    return data


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ttl-hours", type=int, default=24)
    parser.add_argument("--generated-at", help="fixed ISO-8601 timestamp for reproducible builds")
    arguments = parser.parse_args()

    if arguments.input.stat().st_size > MAX_PAYLOAD_BYTES:
        parser.error("input exceeds 2 MiB")
    try:
        document = json.loads(arguments.input.read_text(encoding="utf-8"))
        generated_at = (
            parse_timestamp(arguments.generated_at, "generated-at")
            if arguments.generated_at
            else datetime.now(timezone.utc)
        )
        feed = build_feed(document, generated_at, arguments.ttl_hours)
        atomic_write(arguments.output, encoded_feed(feed))
    except (FeedValidationError, json.JSONDecodeError, OSError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
