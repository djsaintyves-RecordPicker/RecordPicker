#!/usr/bin/env python3
"""Collect a broad, privacy-preserving public feed for Today Pick.

The collector never receives a Record Picker library.  It gathers public
events, resolves conservative musical identities, and hands the resulting
editorial document to :mod:`build_today_pick_feed` for the same validation the
app applies.  Optional providers are enabled only when their server-side key
is present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, time as datetime_time, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

import build_today_pick_feed as builder


USER_AGENT = "RecordPickerTodayPick/1.9 (https://recordpicker.app/support/)"
MAX_DOWNLOAD_BYTES = 4 * 1024 * 1024
MAX_ARTICLES_PER_SOURCE = 12
MAX_MUSICBRAINZ_RESULTS = 8
MUSICBRAINZ_MINIMUM_SCORE = 90
MUSICBRAINZ_DELAY_SECONDS = 1.05
WIKIMEDIA_API_ROOT = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"
WIKIMEDIA_MUSICAL_OCCUPATION = re.compile(
    r"\b(?:singer|vocalist|musician|composer|songwriter|rapper|record producer|"
    r"conductor|pianist|keyboardist|organist|guitarist|bassist|drummer|"
    r"percussionist|violinist|violist|cellist|harpist|flautist|flutist|"
    r"saxophonist|clarinetist|trumpeter|trombonist|oboist|bandleader|dj)\b",
    re.IGNORECASE,
)
WIKIMEDIA_COMPOSER_OCCUPATION = re.compile(r"\bcomposer\b", re.IGNORECASE)
ENGLISH_MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
HEADLINE_SUBJECT_PATTERN = re.compile(
    r"^(.{2,80}?)\s+(?:announces?|shares?|releases?|reveals?|returns?|dies?|died|"
    r"wins?|launches?|unveils?|confirms?|adds?|speaks?|says?|signs?|sets?|"
    r"teams?|performs?|celebrates?|marks?|details?|previews?|drops?|debuts?|"
    r"publishes?|issues?)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EditorialSource:
    name: str
    url: str
    importance: float


DEFAULT_EDITORIAL_SOURCES = (
    EditorialSource("BBC Music", "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", 0.72),
    EditorialSource("The Guardian Music", "https://www.theguardian.com/music/rss", 0.74),
    EditorialSource("NPR Music", "https://feeds.npr.org/1039/rss.xml", 0.75),
    EditorialSource("Pitchfork News", "https://pitchfork.com/rss/news/", 0.68),
    EditorialSource("Rolling Stone Music", "https://www.rollingstone.com/music/music-news/feed/", 0.72),
    EditorialSource("Consequence", "https://consequence.net/category/music/feed/", 0.66),
    EditorialSource("BrooklynVegan", "https://www.brooklynvegan.com/feed/", 0.64),
    EditorialSource("The Quietus", "https://thequietus.com/feed/", 0.72),
    EditorialSource("OperaWire", "https://operawire.com/feed/", 0.68),
    EditorialSource("Slipped Disc", "https://slippedisc.com/feed/", 0.62),
    EditorialSource("The Line of Best Fit", "https://www.thelineofbestfit.com/feed", 0.65),
    EditorialSource("Electronic Groove", "https://electronicgroove.com/feed/", 0.62),
)


class CollectionError(RuntimeError):
    """Raised when a provider returns an unusable response."""


def fetch_bytes(url: str, accept: str, timeout: int = 30, attempts: int = 4) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    last_error: Exception | None = None
    for attempt in range(max(1, attempts)):
        try:
            with urlopen(request, timeout=timeout) as response:
                if getattr(response, "status", response.getcode()) != 200:
                    raise CollectionError(f"{url}: unexpected HTTP status")
                payload = response.read(MAX_DOWNLOAD_BYTES + 1)
            if len(payload) > MAX_DOWNLOAD_BYTES:
                raise CollectionError(f"{url}: response exceeds {MAX_DOWNLOAD_BYTES} bytes")
            return payload
        except HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503, 504} or attempt + 1 >= attempts:
                raise
            retry_after = error.headers.get("Retry-After")
            try:
                delay = min(max(float(retry_after), 1), 30) if retry_after else 2 ** attempt
            except ValueError:
                delay = 2 ** attempt
            time.sleep(delay)
        except URLError as error:
            last_error = error
            if attempt + 1 >= attempts:
                raise
            time.sleep(2 ** attempt)
    raise CollectionError(f"{url}: unavailable after retries") from last_error


def fetch_json(url: str) -> dict[str, Any]:
    try:
        document = json.loads(fetch_bytes(url, "application/json").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CollectionError(f"{url}: invalid JSON") from error
    if not isinstance(document, dict):
        raise CollectionError(f"{url}: JSON root is not an object")
    return document


def clean_text(raw: str | None) -> str:
    value = unescape(raw or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def headline_without_quoted_titles(headline: str) -> str:
    value = headline
    for pattern in (r'"[^"\n]*"', r"“[^”\n]*”", r"‘[^’\n]*’", r"'[^'\n]*'"):
        value = re.sub(pattern, " ", value)
    return re.sub(r"\s+", " ", value).strip()


def headline_subject_candidates(headline: str) -> list[str]:
    visible = headline_without_quoted_titles(clean_text(headline))
    match = HEADLINE_SUBJECT_PATTERN.search(visible)
    if not match:
        return []
    candidate = clean_text(match.group(1)).strip(" :-–—")
    if not candidate or len(candidate) > builder.MAX_NAME_LENGTH:
        return []
    return [candidate]


def parse_publication_date(raw: str | None) -> datetime | None:
    value = clean_text(raw)
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def child_text(element: ElementTree.Element, names: Iterable[str]) -> str:
    wanted = set(names)
    for child in element:
        local_name = child.tag.rsplit("}", 1)[-1]
        if local_name in wanted and child.text:
            return child.text
    return ""


def parse_editorial_feed(
    payload: bytes,
    source: EditorialSource,
    now: datetime,
    maximum_age_days: int = 14,
) -> list[dict[str, Any]]:
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as error:
        raise CollectionError(f"{source.name}: invalid XML feed") from error

    items = root.findall(".//item")
    if not items:
        items = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "entry"]

    cutoff = now - timedelta(days=maximum_age_days)
    articles: list[dict[str, Any]] = []
    for item in items:
        title = clean_text(child_text(item, ("title",)))
        link = clean_text(child_text(item, ("link",)))
        if not link:
            for child in item:
                if child.tag.rsplit("}", 1)[-1] == "link" and child.attrib.get("href"):
                    link = child.attrib["href"]
                    break
        published = parse_publication_date(
            child_text(item, ("pubDate", "published", "updated", "date"))
        )
        parsed_link = urlparse(link)
        if not title or not published or published < cutoff or published > now + timedelta(minutes=5):
            continue
        if parsed_link.scheme.lower() != "https" or not parsed_link.hostname:
            continue
        articles.append(
            {
                "title": title[: builder.MAX_HEADLINE_LENGTH],
                "url": link,
                "publishedAt": published,
                "source": source,
            }
        )
        if len(articles) >= MAX_ARTICLES_PER_SOURCE:
            break
    return articles


def event_kind_for_headline(headline: str) -> str:
    key = normalized(headline)
    if re.search(r"\b(dies|died|dead|death|obituary|remembering|rip)\b", key):
        return "obituary"
    if re.search(r"\b(birthday|born on this day|would have been)\b", key):
        return "birthday"
    if re.search(r"\b(reissue|reissued|re release|remaster|remastered|box set|deluxe edition)\b", key):
        return "reissue"
    if re.search(r"\b(new album|debut album|announces album|album announced|releases album)\b", key):
        return "newRelease"
    if re.search(r"\b(tour|concert|festival|live dates|gig|show dates)\b", key):
        return "concert"
    if re.search(r"\b(award|awards|prize|grammy|mercury prize|prix de musique)\b", key):
        return "award"
    if re.search(r"\banniversary\b", key):
        return "anniversary"
    return "news"


def contains_identity(headline: str, identity: str) -> bool:
    headline_key = f" {normalized(headline_without_quoted_titles(headline))} "
    identity_key = normalized(identity)
    return len(identity_key) >= 3 and f" {identity_key} " in headline_key


class MusicBrainzArtistResolver:
    """Resolve only explicit headline subjects confirmed by MusicBrainz."""

    def __init__(
        self,
        json_fetcher: Callable[[str], dict[str, Any]] = fetch_json,
        delay_seconds: float = MUSICBRAINZ_DELAY_SECONDS,
    ) -> None:
        self.json_fetcher = json_fetcher
        self.delay_seconds = max(0, delay_seconds)
        self.cache: dict[str, list[str]] = {}
        self._last_request_at: float | None = None

    def resolve(self, headline: str) -> list[str]:
        key = normalized(headline)
        if key in self.cache:
            return self.cache[key]
        resolved: list[str] = []
        seen: set[str] = set()
        for subject in headline_subject_candidates(headline):
            exact = self.resolve_exact(subject)
            if not exact:
                continue
            name_key = normalized(exact)
            if name_key not in seen:
                seen.add(name_key)
                resolved.append(exact)
        self.cache[key] = resolved[:4]
        return self.cache[key]

    def resolve_exact(self, identity: str) -> str | None:
        """Return an artist only when MusicBrainz confirms the exact name."""

        value = clean_text(identity)
        key = f"exact:{normalized(value)}"
        if not value or len(value) > builder.MAX_NAME_LENGTH:
            return None
        if key in self.cache:
            return self.cache[key][0] if self.cache[key] else None
        if self._last_request_at is not None and self.delay_seconds:
            remaining = self.delay_seconds - (time.monotonic() - self._last_request_at)
            if remaining > 0:
                time.sleep(remaining)
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        url = "https://musicbrainz.org/ws/2/artist/?" + urlencode(
            {"query": f'artist:"{escaped}"', "limit": MAX_MUSICBRAINZ_RESULTS, "fmt": "json"}
        )
        try:
            document = self.json_fetcher(url)
        finally:
            self._last_request_at = time.monotonic()
        expected = normalized(value)
        candidates: list[tuple[int, str]] = []
        for item in document.get("artists", []):
            if not isinstance(item, dict):
                continue
            name = clean_text(item.get("name"))
            score = item.get("score", 0)
            if (
                isinstance(score, int)
                and score >= MUSICBRAINZ_MINIMUM_SCORE
                and normalized(name) == expected
            ):
                candidates.append((score, name))
        resolved = sorted(candidates, key=lambda result: (-result[0], result[1]))
        self.cache[key] = [resolved[0][1]] if resolved else []
        return self.cache[key][0] if self.cache[key] else None


def stable_event_id(prefix: str, *values: str) -> str:
    digest = hashlib.sha256("\x1f".join(values).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def editorial_events(
    now: datetime,
    sources: Iterable[EditorialSource] = DEFAULT_EDITORIAL_SOURCES,
    resolver: MusicBrainzArtistResolver | None = None,
    byte_fetcher: Callable[[str, str], bytes] = fetch_bytes,
) -> tuple[list[dict[str, Any]], list[str]]:
    resolver = resolver or MusicBrainzArtistResolver()
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    for source in sources:
        try:
            articles = parse_editorial_feed(
                byte_fetcher(source.url, "application/rss+xml, application/atom+xml, text/xml"),
                source,
                now,
            )
        except Exception as error:  # one publisher must never empty the whole feed
            warnings.append(f"{source.name}: {error}")
            continue
        for article in articles:
            try:
                artists = resolver.resolve(article["title"])
            except Exception as error:
                warnings.append(f"MusicBrainz resolver: {error}")
                continue
            if not artists:
                continue
            kind = event_kind_for_headline(article["title"])
            events.append(
                {
                    "id": stable_event_id("press", kind, article["url"]),
                    "kind": kind,
                    "headline": article["title"],
                    "sourceName": source.name,
                    "sourceURL": article["url"],
                    "publishedAt": builder.isoformat(article["publishedAt"]),
                    "sourceKind": "editorial",
                    "importance": source.importance,
                    "artists": artists,
                    "albumTitles": [],
                    "composers": [],
                }
            )
    return corroborate_and_deduplicate_editorial(events), warnings


def source_domain(event: dict[str, Any]) -> str:
    return builder.canonical_domain(event["sourceURL"])


def corroborate_and_deduplicate_editorial(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = {}
    for event in events:
        artist_key = tuple(sorted(normalized(value) for value in event.get("artists", [])))
        groups.setdefault((event["kind"], artist_key), []).append(event)

    output: list[dict[str, Any]] = []
    for (kind, _), group in groups.items():
        chronological = sorted(group, key=lambda item: item["publishedAt"])
        clusters: list[list[dict[str, Any]]] = []
        maximum_gap = timedelta(days=7) if kind == "obituary" else timedelta(hours=36)
        for event in chronological:
            published = builder.parse_timestamp(event["publishedAt"], "publishedAt")
            if not clusters:
                clusters.append([event])
                continue
            previous = builder.parse_timestamp(clusters[-1][-1]["publishedAt"], "publishedAt")
            if published - previous <= maximum_gap:
                clusters[-1].append(event)
            else:
                clusters.append([event])

        for cluster in clusters:
            cluster.sort(
                key=lambda item: (float(item.get("importance", 0)), item["publishedAt"], item["sourceURL"]),
                reverse=True,
            )
            output.extend(merged_editorial_cluster(kind, cluster))
    return output


def merged_editorial_cluster(kind: str, group: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_domain: dict[str, dict[str, Any]] = {}
    for event in group:
        by_domain.setdefault(source_domain(event), event)
    if kind == "obituary" and len(by_domain) < 2:
        return []
    primary = next(iter(by_domain.values())).copy()
    corroborating = []
    for event in list(by_domain.values())[1:]:
        corroborating.append(
            {
                "name": event["sourceName"],
                "url": event["sourceURL"],
                "publishedAt": event["publishedAt"],
                "kind": "editorial",
            }
        )
    primary["corroboratingSources"] = corroborating
    primary["id"] = stable_event_id(
        kind,
        *primary["artists"],
        min(event["publishedAt"][:10] for event in group),
    )
    return [primary]


def full_date(raw: Any) -> date | None:
    if not isinstance(raw, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def musicbrainz_release_events(
    now: datetime,
    days_ahead: int = 21,
    maximum_pages: int = 6,
    json_fetcher: Callable[[str], dict[str, Any]] = fetch_json,
) -> tuple[list[dict[str, Any]], list[str]]:
    start = now.date() - timedelta(days=2)
    end = now.date() + timedelta(days=max(1, days_ahead))
    query = f"date:[{start.isoformat()} TO {end.isoformat()}] AND status:official"
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen_releases: set[str] = set()
    for page in range(maximum_pages):
        url = "https://musicbrainz.org/ws/2/release/?" + urlencode(
            {"query": query, "limit": 100, "offset": page * 100, "fmt": "json"}
        )
        try:
            document = json_fetcher(url)
        except Exception as error:
            warnings.append(f"MusicBrainz releases: {error}")
            break
        releases = document.get("releases", [])
        if not isinstance(releases, list) or not releases:
            break
        for release in releases:
            if not isinstance(release, dict):
                continue
            release_id = clean_text(release.get("id"))
            release_date = full_date(release.get("date"))
            title = clean_text(release.get("title"))
            credits = release.get("artist-credit", [])
            artists = [clean_text(item.get("name")) for item in credits if isinstance(item, dict)]
            artists = [name for name in artists if name]
            if not release_id or release_id in seen_releases or not release_date or not title or not artists:
                continue
            if not start <= release_date <= end:
                continue
            seen_releases.add(release_id)
            group = release.get("release-group") if isinstance(release.get("release-group"), dict) else {}
            group_title = clean_text(group.get("title")) or title
            event_date = datetime.combine(release_date, datetime_time(12), tzinfo=timezone.utc)
            events.append(
                {
                    "id": f"musicbrainz-release-{release_id}",
                    "kind": "newRelease",
                    "headline": f"{title} — new official release by {', '.join(artists)}"[: builder.MAX_HEADLINE_LENGTH],
                    "sourceName": "MusicBrainz",
                    "sourceURL": f"https://musicbrainz.org/release/{release_id}",
                    "publishedAt": builder.isoformat(now),
                    "sourceKind": "structuredDatabase",
                    "eventDate": builder.isoformat(event_date),
                    "importance": 0.58,
                    "artists": artists[: builder.MAX_IDENTITIES],
                    "albumTitles": [group_title],
                    "composers": [],
                }
            )
        if len(releases) < 100:
            break
        if page + 1 < maximum_pages:
            time.sleep(MUSICBRAINZ_DELAY_SECONDS)
    return events, warnings


def wikimedia_identity(event_text: Any) -> str | None:
    """Extract the named person, never the potentially misleading page title."""

    text = clean_text(event_text if isinstance(event_text, str) else None)
    if not text or "," not in text or not WIKIMEDIA_MUSICAL_OCCUPATION.search(text):
        return None
    identity = clean_text(text.split(",", 1)[0])
    if not identity or len(identity) > builder.MAX_NAME_LENGTH:
        return None
    if not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", identity):
        return None
    return identity


def wikimedia_on_this_day_events(
    now: datetime,
    resolver: MusicBrainzArtistResolver | None = None,
    json_fetcher: Callable[[str], dict[str, Any]] = fetch_json,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect today's musician birthdays from Wikimedia's structured feed."""

    resolver = resolver or MusicBrainzArtistResolver()
    month_day = f"{now.month:02d}/{now.day:02d}"
    url = f"{WIKIMEDIA_API_ROOT}/births/{month_day}"
    try:
        document = json_fetcher(url)
    except Exception as error:
        return [], [f"Wikimedia On this day: {error}"]

    births = document.get("births", [])
    if not isinstance(births, list):
        return [], ["Wikimedia On this day: births is not an array"]

    source_url = (
        f"https://en.wikipedia.org/wiki/{ENGLISH_MONTH_NAMES[now.month - 1]}_{now.day}"
    )
    event_date = datetime.combine(now.date(), datetime_time(12), tzinfo=timezone.utc)
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for entry in births:
        if not isinstance(entry, dict):
            continue
        text = clean_text(entry.get("text"))
        identity = wikimedia_identity(text)
        birth_year = entry.get("year")
        if identity is None or not isinstance(birth_year, int) or birth_year > now.year:
            continue
        try:
            resolved = resolver.resolve_exact(identity)
        except Exception as error:
            warnings.append(f"MusicBrainz exact resolver ({identity}): {error}")
            continue
        if not resolved or normalized(resolved) in seen:
            continue
        seen.add(normalized(resolved))
        composers = [resolved] if WIKIMEDIA_COMPOSER_OCCUPATION.search(text) else []
        events.append(
            {
                "id": stable_event_id("birthday", resolved, now.date().isoformat()),
                "kind": "birthday",
                "headline": f"{resolved} was born on this day in {birth_year}",
                "sourceName": "Wikipedia On this day",
                "sourceURL": source_url,
                "publishedAt": builder.isoformat(now),
                "sourceKind": "structuredDatabase",
                "eventDate": builder.isoformat(event_date),
                "importance": 0.56,
                "artists": [resolved],
                "albumTitles": [],
                "composers": composers,
            }
        )
    return events, warnings


def ticketmaster_events(
    now: datetime,
    api_key: str,
    countries: Iterable[str],
    json_fetcher: Callable[[str], dict[str, Any]] = fetch_json,
) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    end = now + timedelta(days=120)
    for country in countries:
        country_code = country.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", country_code):
            continue
        url = "https://app.ticketmaster.com/discovery/v2/events.json?" + urlencode(
            {
                "apikey": api_key,
                "countryCode": country_code,
                "classificationName": "music",
                "startDateTime": builder.isoformat(now),
                "endDateTime": builder.isoformat(end),
                "sort": "date,asc",
                "size": 25,
                "locale": "*",
            }
        )
        try:
            document = json_fetcher(url)
        except Exception as error:
            warnings.append(f"Ticketmaster {country_code}: {error}")
            continue
        embedded = document.get("_embedded", {})
        raw_events = embedded.get("events", []) if isinstance(embedded, dict) else []
        for item in raw_events if isinstance(raw_events, list) else []:
            if not isinstance(item, dict) or item.get("test") is True:
                continue
            event_id = clean_text(item.get("id"))
            name = clean_text(item.get("name"))
            source_url = clean_text(item.get("url"))
            attractions = item.get("_embedded", {}).get("attractions", []) if isinstance(item.get("_embedded"), dict) else []
            artists = [clean_text(value.get("name")) for value in attractions if isinstance(value, dict)]
            artists = [value for value in artists if value]
            venues = item.get("_embedded", {}).get("venues", []) if isinstance(item.get("_embedded"), dict) else []
            venue = venues[0] if isinstance(venues, list) and venues and isinstance(venues[0], dict) else {}
            city = clean_text(venue.get("city", {}).get("name")) if isinstance(venue.get("city"), dict) else ""
            venue_country = clean_text(venue.get("country", {}).get("countryCode")) if isinstance(venue.get("country"), dict) else country_code
            venue_name = clean_text(venue.get("name")) or None
            date_value = item.get("dates", {}).get("start", {}).get("dateTime") if isinstance(item.get("dates"), dict) else None
            event_date = parse_publication_date(date_value)
            if not event_date:
                local_date = item.get("dates", {}).get("start", {}).get("localDate") if isinstance(item.get("dates"), dict) else None
                parsed_local = full_date(local_date)
                if parsed_local:
                    event_date = datetime.combine(parsed_local, datetime_time(12), tzinfo=timezone.utc)
            if not event_id or not name or not artists or not source_url or not event_date or not city:
                continue
            events.append(
                {
                    "id": f"ticketmaster-{event_id}",
                    "kind": "concert",
                    "headline": f"{name} — {city}"[: builder.MAX_HEADLINE_LENGTH],
                    "sourceName": "Ticketmaster",
                    "sourceURL": source_url,
                    "publishedAt": builder.isoformat(now),
                    "sourceKind": "structuredDatabase",
                    "eventDate": builder.isoformat(event_date),
                    "importance": 0.64,
                    "artists": artists[: builder.MAX_IDENTITIES],
                    "albumTitles": [],
                    "composers": [],
                    "place": {
                        "venueName": venue_name,
                        "city": city,
                        "countryCode": venue_country.upper(),
                        "coarseGeohash": None,
                    },
                }
            )
    return events, warnings


def unique_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    release_signatures: set[tuple[tuple[str, ...], tuple[str, ...], str]] = set()
    dated_identity_owners: dict[tuple[str, tuple[str, ...], str], str] = {}
    for event in events:
        if event.get("sourceName") == "MusicBrainz":
            signature = (
                tuple(sorted(normalized(value) for value in event.get("artists", []))),
                tuple(sorted(normalized(value) for value in event.get("albumTitles", []))),
                (event.get("eventDate") or "")[:10],
            )
            if signature in release_signatures:
                continue
            release_signatures.add(signature)
        if event.get("kind") in {"birthday", "anniversary"}:
            identities = tuple(
                sorted(normalized(value) for value in event.get("artists", []) if normalized(value))
            )
            if not identities:
                by_id.setdefault(event["id"], event)
                continue
            signature = (
                event["kind"],
                identities,
                "" if event["kind"] == "birthday"
                else (event.get("eventDate") or event.get("publishedAt") or "")[:10],
            )
            owner_id = dated_identity_owners.get(signature)
            if owner_id is not None:
                existing = by_id[owner_id]
                source_priority = {"official": 3, "editorial": 2, "structuredDatabase": 1}
                existing_rank = (
                    float(existing.get("importance", 0)),
                    source_priority.get(existing.get("sourceKind"), 0),
                    existing["id"],
                )
                new_rank = (
                    float(event.get("importance", 0)),
                    source_priority.get(event.get("sourceKind"), 0),
                    event["id"],
                )
                if new_rank <= existing_rank:
                    continue
                del by_id[owner_id]
            dated_identity_owners[signature] = event["id"]
        by_id.setdefault(event["id"], event)
    priority = {
        "obituary": 0,
        "reissue": 1,
        "award": 2,
        "concert": 3,
        "newRelease": 4,
        "birthday": 5,
        "anniversary": 6,
        "news": 7,
    }
    return sorted(
        by_id.values(),
        key=lambda event: (
            priority.get(event["kind"], 6),
            -float(event.get("importance", 0)),
            event["id"],
        ),
    )[: builder.MAX_EVENTS]


def collect(
    now: datetime,
    include_editorial: bool = True,
    include_musicbrainz: bool = True,
    include_wikimedia: bool = True,
    ticketmaster_api_key: str | None = None,
    ticketmaster_countries: Iterable[str] = (),
) -> tuple[dict[str, Any], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    if include_editorial:
        collected, messages = editorial_events(now)
        events.extend(collected)
        warnings.extend(messages)
    if include_musicbrainz:
        collected, messages = musicbrainz_release_events(now)
        events.extend(collected)
        warnings.extend(messages)
    if include_wikimedia:
        collected, messages = wikimedia_on_this_day_events(now)
        events.extend(collected)
        warnings.extend(messages)
    if ticketmaster_api_key:
        collected, messages = ticketmaster_events(
            now,
            ticketmaster_api_key,
            ticketmaster_countries,
        )
        events.extend(collected)
        warnings.extend(messages)
    return {"events": unique_events(events)}, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--editorial-output", type=Path)
    parser.add_argument("--generated-at", help="fixed ISO-8601 timestamp")
    parser.add_argument("--ttl-hours", type=int, default=36)
    parser.add_argument("--without-editorial", action="store_true")
    parser.add_argument("--without-musicbrainz", action="store_true")
    parser.add_argument("--without-wikimedia", action="store_true")
    parser.add_argument(
        "--ticketmaster-countries",
        default="FR,GB,US,CA,DE,ES,IT,NL,BE,CH,AT,AU,MX,JP,PL,NO,SE,FI",
    )
    arguments = parser.parse_args()
    now = (
        builder.parse_timestamp(arguments.generated_at, "generated-at")
        if arguments.generated_at
        else datetime.now(timezone.utc)
    )
    document, warnings = collect(
        now,
        include_editorial=not arguments.without_editorial,
        include_musicbrainz=not arguments.without_musicbrainz,
        include_wikimedia=not arguments.without_wikimedia,
        ticketmaster_api_key=os.environ.get("TICKETMASTER_API_KEY"),
        ticketmaster_countries=arguments.ticketmaster_countries.split(","),
    )
    feed = builder.build_feed(document, now, arguments.ttl_hours)
    builder.atomic_write(arguments.output, builder.encoded_feed(feed))
    if arguments.editorial_output:
        builder.atomic_write(
            arguments.editorial_output,
            (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    for warning in warnings:
        print(f"WARNING: {warning}")
    print(
        f"Collected {len(feed['events'])} events; "
        f"feed expires {feed['expiresAt']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
