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
import unicodedata
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


USER_AGENT = "RecordPickerTodayPick/1.10 (https://recordpicker.app/support/)"
MAX_DOWNLOAD_BYTES = 4 * 1024 * 1024
MAX_ARTICLES_PER_SOURCE = 40
MAX_MUSICBRAINZ_RESULTS = 8
MUSICBRAINZ_MINIMUM_SCORE = 90
MUSICBRAINZ_DELAY_SECONDS = 1.05
MUSICBRAINZ_ADDRESS_COUNTRIES = {
    "australia": "AU",
    "austria": "AT",
    "belgium": "BE",
    "canada": "CA",
    "deutschland": "DE",
    "espana": "ES",
    "finland": "FI",
    "france": "FR",
    "germany": "DE",
    "italia": "IT",
    "italy": "IT",
    "japan": "JP",
    "mexico": "MX",
    "nederland": "NL",
    "netherlands": "NL",
    "norge": "NO",
    "norway": "NO",
    "osterreich": "AT",
    "poland": "PL",
    "polska": "PL",
    "schweiz": "CH",
    "spain": "ES",
    "suisse": "CH",
    "suomi": "FI",
    "svenska": "SE",
    "sweden": "SE",
    "sverige": "SE",
    "switzerland": "CH",
    "united kingdom": "GB",
    "united states": "US",
    "united states of america": "US",
    "usa": "US",
}
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
    r"bans?|banned|offers?|joins?|opens?|will\s+(?:open|tour|play|perform|release)|"
    r"brings?|honou?rs?|drives?|"
    r"publishes?|issues?|annonce|annoncent|partage|partagent|sort|sortent|"
    r"dévoile|dévoilent|revele|revelent|révèle|révèlent|publie|publient|"
    r"meurt|décède|disparaît|disparait|renaît|renait|remporte|lance|lancent|confirme|"
    r"confirment|célèbre|celebre|célèbrent|celebrent|anuncia|anuncian|"
    r"comparte|comparten|lanza|lanzan|estrena|estrenan|regresa|regresan|"
    r"publica|publican|muere|fallece|gana|ganan|celebra|celebran|confirma|"
    r"confirman|kündigt|veröffentlicht|kehrt|stirbt|gewinnt|teilt|"
    r"bestätigt|feiert|verstorben)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EditorialSource:
    name: str
    url: str
    importance: float
    lead_identity_role: str | None = None


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
    EditorialSource("NME", "https://www.nme.com/feed", 0.68),
    EditorialSource("Variety Music", "https://variety.com/v/music/feed/", 0.70),
    EditorialSource("Billboard", "https://www.billboard.com/feed/", 0.72),
    EditorialSource("Metal Injection", "https://metalinjection.net/feed", 0.64),
    EditorialSource("DJ Mag", "https://djmag.com/rss.xml", 0.66, "artist"),
    EditorialSource("Le Monde Musiques", "https://www.lemonde.fr/musiques/rss_full.xml", 0.72),
    EditorialSource("Rolling Stone en Español", "https://es.rollingstone.com/feed/", 0.68),
    EditorialSource("MondoSonoro", "https://www.mondosonoro.com/feed/", 0.64),
    EditorialSource("Jenesaispop", "https://jenesaispop.com/feed/", 0.64),
    EditorialSource("Musikexpress", "https://www.musikexpress.de/feed/", 0.66),
    EditorialSource("Rolling Stone Germany", "https://www.rollingstone.de/feed/", 0.68),
    EditorialSource("Soompi Music", "https://www.soompi.com/category/music/feed", 0.62),
    EditorialSource("Bandcamp Daily", "https://daily.bandcamp.com/feed", 0.66),
    EditorialSource("WBGO Music", "https://www.wbgo.org/music.rss", 0.70),
    EditorialSource("Attack Magazine", "https://www.attackmagazine.com/feed/", 0.65),
    EditorialSource("Télérama Musique", "https://www.telerama.fr/rss/musique.xml", 0.72),
    EditorialSource("France Musique", "https://www.radiofrance.fr/francemusique/rss", 0.74),
    EditorialSource("Tsugi", "https://www.tsugi.fr/feed/", 0.70),
    EditorialSource("Jazz Magazine", "https://www.jazzmagazine.com/feed/", 0.70),
    EditorialSource("VAN Magazine", "https://van-magazine.com/feed/", 0.72),
    EditorialSource("Rockdelux", "https://www.rockdelux.com/feed", 0.68, "artist"),
    EditorialSource("Groove", "https://groove.de/feed/", 0.68),
    EditorialSource("The Wire", "https://www.thewire.co.uk/rss", 0.72),
    EditorialSource("Sequenza21", "https://www.sequenza21.com/feed/", 0.66),
    EditorialSource("Stereogum", "https://stereogum.com/feed", 0.68, "artist"),
    EditorialSource("RFI Musique", "https://www.rfi.fr/fr/musique/rss", 0.70),
    EditorialSource("OndaRock", "https://www.ondarock.it/feed.php", 0.66, "artist"),
    EditorialSource("JAZZIZ", "https://jazziz.com/feed/", 0.68),
    EditorialSource("Jazz Views", "https://www.jazzviews.net/feed", 0.66, "artist"),
    EditorialSource("Jazz thing", "https://www.jazzthing.de/feed/", 0.70),
    EditorialSource(
        "The Classic Review",
        "https://theclassicreview.com/feed/",
        0.70,
        "classical",
    ),
    EditorialSource("MusicRadar", "https://www.musicradar.com/feeds/all", 0.67),
    EditorialSource("Louder", "https://www.loudersound.com/feeds/all", 0.67),
    EditorialSource("Clash", "https://www.clashmusic.com/feed/", 0.66),
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


def fetch_musicbrainz_json(url: str) -> dict[str, Any]:
    """Fetch MusicBrainz without allowing a degraded service to stall a run."""

    try:
        document = json.loads(
            fetch_bytes(url, "application/json", timeout=12, attempts=2).decode("utf-8")
        )
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
    folded = unicodedata.normalize("NFKD", value.casefold())
    ascii_like = "".join(character for character in folded if not unicodedata.combining(character))
    return " ".join(re.findall(r"[a-z0-9]+", ascii_like))


def country_code_from_musicbrainz_address(address: str | None) -> str | None:
    """Return a country only when the final address component is explicit.

    MusicBrainz places do not expose a country code directly.  Guessing from
    a city name would create misleading nearby-concert suggestions, so the
    collector accepts only a recognised country written as the final address
    component.  Unknown or incomplete addresses remain place-free news.
    """

    components = [clean_text(component) for component in (address or "").split(",")]
    terminal = normalized(components[-1]) if components and components[-1] else ""
    return MUSICBRAINZ_ADDRESS_COUNTRIES.get(terminal)


def headline_without_quoted_titles(headline: str) -> str:
    value = headline
    for pattern in (r'"[^"\n]*"', r"“[^”\n]*”", r"‘[^’\n]*’", r"'[^'\n]*'"):
        value = re.sub(pattern, " ", value)
    return re.sub(r"\s+", " ", value).strip()


def headline_subject_candidates(headline: str) -> list[str]:
    visible = headline_without_quoted_titles(clean_text(headline))
    visible = re.sub(
        r"^(?:à voir|a voir|à écouter|a ecouter|watch|listen|premiere)\s*:\s*",
        "",
        visible,
        flags=re.IGNORECASE,
    )
    memorial = re.match(
        r"^(?:rip|in memoriam|remembering)\s*:\s*(.{2,80}?)(?:\s+[–—-]\s+|$)",
        visible,
        flags=re.IGNORECASE,
    )
    if memorial:
        candidate = clean_text(memorial.group(1)).strip(" :-–—")
        return [candidate] if candidate else []
    # A large share of English-language music desks use a possessive artist
    # credit rather than an announcement verb ("The Cure's ...", "How to
    # watch PJ Harvey's ...").  Keep the extraction anchored at the start and
    # let the exact MusicBrainz check below reject names that are not artists.
    possessive = re.match(
        r"^(?:how to (?:watch|hear|see|stream)\s+)?(.{2,80}?)[’']s\s+",
        visible,
        flags=re.IGNORECASE,
    )
    if possessive:
        candidate = clean_text(possessive.group(1)).strip(" :-–—")
        generic = {
            "music", "rock", "pop", "jazz", "metal", "today", "this week",
            "the year", "the decade", "the world",
        }
        if (
            candidate
            and normalized(candidate) not in generic
            and len(candidate.split()) <= 8
            and len(candidate) <= builder.MAX_NAME_LENGTH
        ):
            return [candidate]
    match = HEADLINE_SUBJECT_PATTERN.search(visible)
    if not match:
        return []
    candidate = clean_text(match.group(1)).strip(" :-–—")
    if ":" in candidate:
        candidate = candidate.split(":", 1)[0].strip()
    candidate = re.sub(
        r"^(?:the|le|la|les|un|une)\s+(?:band|groupe|duo)\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"^(?:legendary\s+)?(?:jazz\s+)?(?:singer|songwriter|producer|drummer|composer|dj)\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    if (
        not candidate
        or "?" in candidate
        or normalized(candidate).startswith(("est ce ", "is it ", "how ", "why "))
        or len(candidate) > builder.MAX_NAME_LENGTH
    ):
        return []
    return [candidate]


def leading_identity_candidate(
    headline: str,
    allow_plain_identity: bool = False,
) -> str | None:
    """Extract an explicit review credit before a typographic dash.

    This path is enabled source by source.  It is intentionally not a generic
    headline heuristic: on specialist review feeds the stable convention is
    ``Artist – Album`` or ``Review: Composer – Work – Performer``.
    """

    visible = headline_without_quoted_titles(clean_text(headline))
    visible = re.sub(
        r"^(?:album\s+review|record\s+review|review|critique|recensione)\s*:\s*",
        "",
        visible,
        flags=re.IGNORECASE,
    )
    parts = re.split(r"\s+[-–—]\s+", visible)
    if len(parts) < 2:
        if not allow_plain_identity:
            return None
        plain = clean_text(visible).strip(" :-–—")
        if (
            not 2 <= len(plain) <= builder.MAX_NAME_LENGTH
            or len(plain.split()) > 6
            or re.search(r"[?!,:;]", plain)
            or normalized(plain) in {
                "news", "reviews", "features", "tracks", "albums",
                "new music", "best new music", "various artists",
            }
        ):
            return None
        return plain
    candidate_index = 0
    if re.fullmatch(
        r"top\s+(?:five|ten|\d+)",
        normalized(parts[0]),
        flags=re.IGNORECASE,
    ):
        candidate_index = 1
    candidate = clean_text(parts[candidate_index]).strip(" :-–—")
    if normalized(candidate) in {
        "top five",
        "top ten",
        "best recordings",
        "the best recordings",
    }:
        return None
    if (
        len(candidate) < 2
        or len(candidate) > builder.MAX_NAME_LENGTH
        or "?" in candidate
        or "," in candidate
        or not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", candidate)
    ):
        return None
    return candidate


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
    if re.search(r"\b(dies|died|dead|death|obituary|remembering|rip|mort|deces|decede|disparait)\b", key):
        return "obituary"
    if re.search(r"\b(birthday|born on this day|would have been|anniversaire de naissance)\b", key):
        return "birthday"
    if re.search(r"\b(reissue|reissued|re release|remaster|remastered|box set|deluxe edition|reedition|reedite|remasterise)\b", key):
        return "reissue"
    if re.search(r"\b(new album|debut album|announces album|album announced|releases album|nouvel album|premier album)\b", key):
        return "newRelease"
    if re.search(r"\b(tour|tournee|concert|festival|live dates|gig|show dates)\b", key):
        return "concert"
    if re.search(r"\b(award|awards|prize|grammy|mercury prize|prix de musique|recompense|remporte le prix)\b", key):
        return "award"
    if re.search(r"\b(anniversary|anniversaire)\b", key):
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
        json_fetcher: Callable[[str], dict[str, Any]] = fetch_musicbrainz_json,
        delay_seconds: float = MUSICBRAINZ_DELAY_SECONDS,
    ) -> None:
        self.json_fetcher = json_fetcher
        self.delay_seconds = max(0, delay_seconds)
        self.cache: dict[str, list[str]] = {}
        self.identity_roles: dict[str, set[str]] = {}
        self._last_request_at: float | None = None
        self._service_unavailable = False

    def resolve(
        self,
        headline: str,
        additional_candidates: Iterable[str] = (),
        include_headline_candidates: bool = True,
    ) -> list[str]:
        extras = tuple(clean_text(value) for value in additional_candidates if clean_text(value))
        key = "\x1f".join((
            "headline" if include_headline_candidates else "lead-only",
            normalized(headline),
            *(normalized(value) for value in extras),
        ))
        if key in self.cache:
            return self.cache[key]
        resolved: list[str] = []
        seen: set[str] = set()
        candidates = [
            *(headline_subject_candidates(headline) if include_headline_candidates else []),
            *extras,
        ]
        for subject in candidates:
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
        if self._service_unavailable:
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
        except Exception:
            # A single fetch already includes bounded retries.  Continuing to
            # issue hundreds of identical requests would turn a temporary
            # MusicBrainz incident into a stalled feed generation.
            self._service_unavailable = True
            raise
        finally:
            self._last_request_at = time.monotonic()
        expected = normalized(value)
        candidates: list[tuple[int, str, set[str]]] = []
        for item in document.get("artists", []):
            if not isinstance(item, dict):
                continue
            name = clean_text(item.get("name"))
            score = item.get("score", 0)
            aliases = item.get("aliases", [])
            if not isinstance(aliases, list):
                aliases = []
            tags = item.get("tags", [])
            if not isinstance(tags, list):
                tags = []
            roles = {
                normalized(clean_text(tag.get("name")))
                for tag in tags
                if isinstance(tag, dict) and clean_text(tag.get("name"))
            }
            exact_alias = any(
                isinstance(alias, dict)
                and normalized(clean_text(alias.get("name"))) == expected
                for alias in aliases
            )
            if (
                isinstance(score, int)
                and score >= MUSICBRAINZ_MINIMUM_SCORE
                and (normalized(name) == expected or exact_alias)
            ):
                candidates.append((score, name, roles))
        resolved = sorted(candidates, key=lambda result: (-result[0], result[1]))
        if resolved:
            self.identity_roles[normalized(resolved[0][1])] = resolved[0][2]
        self.cache[key] = [resolved[0][1]] if resolved else []
        return self.cache[key][0] if self.cache[key] else None

    def is_composer(self, identity: str) -> bool:
        roles = self.identity_roles.get(normalized(identity), set())
        return any(role == "composer" or role.endswith(" composer") for role in roles)


def stable_event_id(prefix: str, *values: str) -> str:
    digest = hashlib.sha256("\x1f".join(values).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def editorial_events(
    now: datetime,
    sources: Iterable[EditorialSource] = DEFAULT_EDITORIAL_SOURCES,
    resolver: MusicBrainzArtistResolver | None = None,
    byte_fetcher: Callable[[str, str], bytes] = fetch_bytes,
    health: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    resolver = resolver or MusicBrainzArtistResolver()
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    for source in sources:
        source_health = {
            "url": source.url,
            "downloadedArticles": 0,
            "resolvedEvents": 0,
            "status": "ok",
        }
        if health is not None:
            health[source.name] = source_health
        try:
            articles = parse_editorial_feed(
                byte_fetcher(source.url, "application/rss+xml, application/atom+xml, text/xml"),
                source,
                now,
            )
        except Exception as error:  # one publisher must never empty the whole feed
            warnings.append(f"{source.name}: {error}")
            source_health["status"] = "failed"
            source_health["error"] = str(error)[:240]
            continue
        source_health["downloadedArticles"] = len(articles)
        if not articles:
            source_health["status"] = "noRecentArticles"
        for article in articles:
            lead_candidate = (
                leading_identity_candidate(
                    article["title"],
                    allow_plain_identity=source.lead_identity_role == "artist",
                )
                if source.lead_identity_role is not None
                else None
            )
            try:
                identities = resolver.resolve(
                    article["title"],
                    [lead_candidate] if lead_candidate else [],
                    include_headline_candidates=source.lead_identity_role is None,
                )
            except Exception as error:
                warnings.append(f"MusicBrainz resolver: {error}")
                continue
            if not identities:
                continue
            if source.lead_identity_role == "classical":
                composers = [
                    identity
                    for identity in identities
                    if getattr(resolver, "is_composer", lambda _identity: False)(identity)
                ]
                composer_keys = {normalized(identity) for identity in composers}
                artists = [
                    identity
                    for identity in identities
                    if normalized(identity) not in composer_keys
                ]
            else:
                composers = []
                artists = identities
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
                    "composers": composers,
                }
            )
            source_health["resolvedEvents"] += 1
    return corroborate_and_deduplicate_editorial(events), warnings


def editorial_health_document(
    generated_at: datetime,
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ordered = {name: sources[name] for name in sorted(sources)}
    return {
        "generatedAt": builder.isoformat(generated_at),
        "configuredSources": len(ordered),
        "reachableSources": sum(
            value.get("status") != "failed" for value in ordered.values()
        ),
        "contributingSources": sum(
            int(value.get("resolvedEvents", 0)) > 0 for value in ordered.values()
        ),
        "sources": ordered,
    }


def source_domain(event: dict[str, Any]) -> str:
    return builder.canonical_domain(event["sourceURL"])


def corroborate_and_deduplicate_editorial(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = {}
    for event in events:
        identity_key = tuple(
            sorted(
                [f"artist:{normalized(value)}" for value in event.get("artists", [])]
                + [f"composer:{normalized(value)}" for value in event.get("composers", [])]
            )
        )
        groups.setdefault((event["kind"], identity_key), []).append(event)

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
        *primary.get("composers", []),
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
    json_fetcher: Callable[[str], dict[str, Any]] = fetch_musicbrainz_json,
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


def musicbrainz_live_events(
    now: datetime,
    days_ahead: int = 120,
    maximum_pages: int = 4,
    maximum_events: int = 180,
    maximum_place_lookups: int = 60,
    json_fetcher: Callable[[str], dict[str, Any]] = fetch_musicbrainz_json,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect future concerts and festivals with linked performer identities.

    Event search provides place identifiers but usually not their location.
    After ranking, the retained places are resolved at MusicBrainz's documented
    rate.  A nearby-concert row is emitted only when the detailed place has a
    city/area and an address ending in an explicit recognised country.  All
    other events remain useful place-free live-music news.
    """

    start = now.date()
    end = start + timedelta(days=max(1, days_ahead))
    query = (
        f"begin:[{start.isoformat()} TO {end.isoformat()}] "
        "AND (type:Concert OR type:Festival)"
    )
    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for page in range(max(1, maximum_pages)):
        url = "https://musicbrainz.org/ws/2/event/?" + urlencode(
            {
                "query": query,
                "limit": 100,
                "offset": page * 100,
                "fmt": "json",
            }
        )
        try:
            document = json_fetcher(url)
        except Exception as error:
            warnings.append(f"MusicBrainz live events: {error}")
            break
        raw_events = document.get("events", [])
        if not isinstance(raw_events, list) or not raw_events:
            break
        for item in raw_events:
            if not isinstance(item, dict) or item.get("cancelled") is True:
                continue
            event_id = clean_text(item.get("id"))
            event_name = clean_text(item.get("name"))
            event_type = clean_text(item.get("type"))
            life_span = item.get("life-span", {})
            begin = full_date(life_span.get("begin")) if isinstance(life_span, dict) else None
            if (
                not event_id
                or event_id in seen
                or not event_name
                or event_type not in {"Concert", "Festival"}
                or begin is None
                or not start <= begin <= end
            ):
                continue
            relations = item.get("relations", [])
            artists = []
            place_id = ""
            for relation in relations if isinstance(relations, list) else []:
                artist = relation.get("artist") if isinstance(relation, dict) else None
                name = clean_text(artist.get("name")) if isinstance(artist, dict) else ""
                if name and name not in artists:
                    artists.append(name)
                place = relation.get("place") if isinstance(relation, dict) else None
                candidate_place_id = clean_text(place.get("id")) if isinstance(place, dict) else ""
                if candidate_place_id and not place_id:
                    place_id = candidate_place_id
            if not artists:
                continue
            seen.add(event_id)
            event_date = datetime.combine(begin, datetime_time(12), tzinfo=timezone.utc)
            candidates.append(
                {
                    "id": f"musicbrainz-event-{event_id}",
                    "kind": "news",
                    "headline": f"{event_name} — upcoming {event_type.lower()}"[
                        : builder.MAX_HEADLINE_LENGTH
                    ],
                    "sourceName": "MusicBrainz Events",
                    "sourceURL": f"https://musicbrainz.org/event/{event_id}",
                    "publishedAt": builder.isoformat(now),
                    "sourceKind": "structuredDatabase",
                    "eventDate": builder.isoformat(event_date),
                    "importance": 0.64 if event_type == "Concert" else 0.66,
                    "artists": artists[: builder.MAX_IDENTITIES],
                    "albumTitles": [],
                    "composers": [],
                    "_musicbrainzPlaceID": place_id,
                }
            )
        if len(raw_events) < 100:
            break
        if page + 1 < maximum_pages:
            time.sleep(MUSICBRAINZ_DELAY_SECONDS)
    candidates.sort(
        key=lambda event: (
            event["eventDate"],
            -len(event["artists"]),
            event["id"],
        )
    )
    retained = candidates[:max(0, maximum_events)]
    place_cache: dict[str, dict[str, Any] | None] = {}
    request_count = 0
    # Festivals expose many performers at once and therefore have the best
    # chance of matching a real collection.  Resolve those places first and
    # bound the daily work; all unexamined events remain valid global news.
    location_candidates = sorted(
        (event for event in retained if clean_text(event.get("_musicbrainzPlaceID"))),
        key=lambda event: (-len(event["artists"]), event["eventDate"], event["id"]),
    )[:max(0, maximum_place_lookups)]
    location_candidate_ids = {event["id"] for event in location_candidates}
    for event in retained:
        place_id = clean_text(event.pop("_musicbrainzPlaceID", None))
        if not place_id or event["id"] not in location_candidate_ids:
            continue
        if place_id not in place_cache:
            if request_count:
                time.sleep(MUSICBRAINZ_DELAY_SECONDS)
            request_count += 1
            url = f"https://musicbrainz.org/ws/2/place/{place_id}?fmt=json"
            try:
                place_cache[place_id] = json_fetcher(url)
            except Exception as error:
                warnings.append(f"MusicBrainz place {place_id}: {error}")
                place_cache[place_id] = None
        place = place_cache[place_id]
        if not isinstance(place, dict):
            continue
        area = place.get("area") if isinstance(place.get("area"), dict) else {}
        city = clean_text(area.get("name"))
        venue = clean_text(place.get("name"))
        country_code = country_code_from_musicbrainz_address(place.get("address"))
        if not city or not country_code:
            continue
        event["kind"] = "concert"
        event["place"] = {
            "countryCode": country_code,
            "city": city,
            "venueName": venue or None,
        }
    return retained, warnings


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
    maximum_pages_per_country: int = 5,
    page_size: int = 200,
    maximum_placed_events: int = 140,
    maximum_tour_summaries: int = 160,
) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    touring_artists: dict[str, dict[str, Any]] = {}
    end = now + timedelta(days=120)
    for country in countries:
        country_code = country.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", country_code):
            continue
        seen_event_ids: set[str] = set()
        for page_index in range(max(1, maximum_pages_per_country)):
            url = "https://app.ticketmaster.com/discovery/v2/events.json?" + urlencode(
                {
                    "apikey": api_key,
                    "countryCode": country_code,
                    "classificationName": "music",
                    "startDateTime": builder.isoformat(now),
                    "endDateTime": builder.isoformat(end),
                    "sort": "date,asc",
                    "size": min(max(1, page_size), 200),
                    "page": page_index,
                    "locale": "*",
                }
            )
            try:
                document = json_fetcher(url)
            except Exception as error:
                warnings.append(f"Ticketmaster {country_code} page {page_index}: {error}")
                break
            embedded = document.get("_embedded", {})
            raw_events = embedded.get("events", []) if isinstance(embedded, dict) else []
            if not isinstance(raw_events, list) or not raw_events:
                break
            for item in raw_events:
                if not isinstance(item, dict) or item.get("test") is True:
                    continue
                event_id = clean_text(item.get("id"))
                if not event_id or event_id in seen_event_ids:
                    continue
                seen_event_ids.add(event_id)
                name = clean_text(item.get("name"))
                source_url = clean_text(item.get("url"))
                attractions = item.get("_embedded", {}).get("attractions", []) if isinstance(item.get("_embedded"), dict) else []
                artists = [clean_text(value.get("name")) for value in attractions if isinstance(value, dict)]
                artists = list(dict.fromkeys(value for value in artists if value))
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
                if not name or not artists or not source_url or not event_date or not city:
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
                for artist in artists:
                    artist_key = normalized(artist)
                    if not artist_key:
                        continue
                    summary = touring_artists.setdefault(
                        artist_key,
                        {
                            "artist": artist,
                            "eventIDs": set(),
                            "nextDate": event_date,
                            "sourceURL": source_url,
                        },
                    )
                    summary["eventIDs"].add(event_id)
                    if event_date < summary["nextDate"]:
                        summary["nextDate"] = event_date
                        summary["sourceURL"] = source_url
            page = document.get("page")
            if not isinstance(page, dict):
                break
            total_pages = page.get("totalPages")
            if not isinstance(total_pages, int) or page_index + 1 >= total_pages:
                break
    # Keep a fair cross-country sample in the global envelope. A country-only
    # build naturally spends the whole allowance on that country, while a
    # multi-country build cannot let the first market consume all 500 slots.
    by_country: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        country = event.get("place", {}).get("countryCode", "")
        by_country.setdefault(country, []).append(event)
    for country_events in by_country.values():
        country_events.sort(key=lambda event: (event["eventDate"], event["id"]))
    placed_events: list[dict[str, Any]] = []
    country_codes = sorted(by_country)
    row = 0
    while len(placed_events) < max(0, maximum_placed_events):
        added = False
        for country in country_codes:
            country_events = by_country[country]
            if row < len(country_events):
                placed_events.append(country_events[row])
                added = True
                if len(placed_events) >= maximum_placed_events:
                    break
        if not added:
            break
        row += 1
    events = placed_events

    # A tour is relevant musical news even when the nearest listed show is not
    # in the user's city.  Publish one place-free fact for artists with several
    # upcoming dates; the app still filters individual venue events locally.
    # This keeps the collection private while avoiding the previous blind spot
    # where an active international tour vanished outside an exact city match.
    summaries = [
        value for value in touring_artists.values()
        if len(value["eventIDs"]) >= 2
    ]
    summaries.sort(
        key=lambda value: (
            -len(value["eventIDs"]),
            value["nextDate"],
            normalized(value["artist"]),
        )
    )
    for summary in summaries[:max(0, maximum_tour_summaries)]:
        show_count = len(summary["eventIDs"])
        artist = summary["artist"]
        events.append(
            {
                "id": stable_event_id("ticketmaster-tour", artist),
                "kind": "news",
                "headline": f"{artist} has {show_count} upcoming concerts listed"[
                    : builder.MAX_HEADLINE_LENGTH
                ],
                "sourceName": "Ticketmaster",
                "sourceURL": summary["sourceURL"],
                "publishedAt": builder.isoformat(now),
                "sourceKind": "structuredDatabase",
                "eventDate": builder.isoformat(summary["nextDate"]),
                "importance": min(0.78, 0.66 + show_count * 0.005),
                "artists": [artist],
                "albumTitles": [],
                "composers": [],
            }
        )
    return events, warnings


def validate_ticketmaster_api_key(
    api_key: str,
    json_fetcher: Callable[[str], dict[str, Any]] = fetch_json,
) -> None:
    """Fail fast when the configured Ticketmaster consumer key is unusable.

    The full editorial collection can take several minutes.  Checking the
    provider first prevents an invalid or inactive key from wasting an entire
    workflow run before the missing-concert validation fails.
    """

    url = "https://app.ticketmaster.com/discovery/v2/events.json?" + urlencode(
        {
            "apikey": api_key,
            "countryCode": "FR",
            "classificationName": "music",
            "size": 1,
            "page": 0,
            "locale": "*",
        }
    )
    try:
        document = json_fetcher(url)
    except HTTPError as error:
        if error.code in {401, 403}:
            raise CollectionError(
                "Ticketmaster rejected TICKETMASTER_API_KEY; configure the active "
                "Consumer Key, not the Consumer Secret"
            ) from error
        raise CollectionError(f"Ticketmaster preflight failed with HTTP {error.code}") from error
    except Exception as error:
        raise CollectionError(f"Ticketmaster preflight failed: {error}") from error
    if not isinstance(document.get("page"), dict):
        raise CollectionError("Ticketmaster preflight returned an unexpected response")


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
    include_musicbrainz_events: bool = True,
    include_wikimedia: bool = True,
    ticketmaster_api_key: str | None = None,
    ticketmaster_countries: Iterable[str] = (),
    editorial_health: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    events: list[dict[str, Any]] = []
    warnings: list[str] = []
    if include_editorial:
        collected, messages = editorial_events(now, health=editorial_health)
        events.extend(collected)
        warnings.extend(messages)
    if include_musicbrainz:
        collected, messages = musicbrainz_release_events(now)
        events.extend(collected)
        warnings.extend(messages)
    if include_musicbrainz_events:
        collected, messages = musicbrainz_live_events(now)
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


def regional_document(document: dict[str, Any], country_code: str) -> dict[str, Any]:
    code = country_code.strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", code):
        raise CollectionError(f"invalid regional country code: {country_code}")
    events = []
    for event in document.get("events", []):
        if not isinstance(event, dict):
            continue
        place = event.get("place")
        if event.get("kind") != "concert" or not isinstance(place, dict):
            events.append(event)
        elif clean_text(place.get("countryCode")).upper() == code:
            events.append(event)
    return {"events": events}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--editorial-output", type=Path)
    parser.add_argument("--health-output", type=Path)
    parser.add_argument("--regional-output-dir", type=Path)
    parser.add_argument("--generated-at", help="fixed ISO-8601 timestamp")
    parser.add_argument("--ttl-hours", type=int, default=36)
    parser.add_argument("--without-editorial", action="store_true")
    parser.add_argument("--without-musicbrainz", action="store_true")
    parser.add_argument("--without-musicbrainz-events", action="store_true")
    parser.add_argument("--without-wikimedia", action="store_true")
    parser.add_argument("--require-ticketmaster", action="store_true")
    parser.add_argument("--minimum-editorial-sources", type=int, default=0)
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
    ticketmaster_api_key = (os.environ.get("TICKETMASTER_API_KEY") or "").strip()
    if arguments.require_ticketmaster and not ticketmaster_api_key:
        parser.error("TICKETMASTER_API_KEY is required for this production collection")
    if arguments.require_ticketmaster and ticketmaster_api_key:
        try:
            validate_ticketmaster_api_key(ticketmaster_api_key)
        except CollectionError as error:
            parser.error(str(error))
    editorial_health: dict[str, dict[str, Any]] = {}
    document, warnings = collect(
        now,
        include_editorial=not arguments.without_editorial,
        include_musicbrainz=not arguments.without_musicbrainz,
        include_musicbrainz_events=not arguments.without_musicbrainz_events,
        include_wikimedia=not arguments.without_wikimedia,
        ticketmaster_api_key=ticketmaster_api_key,
        ticketmaster_countries=arguments.ticketmaster_countries.split(","),
        editorial_health=editorial_health,
    )
    health_document = editorial_health_document(now, editorial_health)
    required_editorial_sources = max(0, arguments.minimum_editorial_sources)
    if health_document["contributingSources"] < required_editorial_sources:
        parser.error(
            f"only {health_document['contributingSources']} editorial sources contributed; "
            f"at least {required_editorial_sources} are required"
        )
    feed = builder.build_feed(document, now, arguments.ttl_hours)
    builder.atomic_write(arguments.output, builder.encoded_feed(feed))
    if arguments.editorial_output:
        builder.atomic_write(
            arguments.editorial_output,
            (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    if arguments.health_output:
        builder.atomic_write(
            arguments.health_output,
            (json.dumps(health_document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    if arguments.regional_output_dir:
        arguments.regional_output_dir.mkdir(parents=True, exist_ok=True)
        for raw_country in arguments.ticketmaster_countries.split(","):
            code = raw_country.strip().upper()
            if not re.fullmatch(r"[A-Z]{2}", code):
                continue
            regional_feed = builder.build_feed(
                regional_document(document, code),
                now,
                arguments.ttl_hours,
            )
            builder.atomic_write(
                arguments.regional_output_dir / f"today-pick-v1-{code}.json",
                builder.encoded_feed(regional_feed),
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
