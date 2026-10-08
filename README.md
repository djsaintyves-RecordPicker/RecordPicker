# Record Picker

Record Picker helps you rediscover your physical music collection and choose the next album to play.

Windows 2.7 is available in the Microsoft Store: https://apps.microsoft.com/detail/9N2ZWRL4M3JC
Android is waiting for beta testers.

The Android closed beta is recruiting 12 testers worldwide. The beta is
available in English and French; participants need a compatible Android phone
or tablet, a Google Account, and 14 consecutive days to test and share feedback.

This repository hosts the public discovery, support, screenshots, privacy, and features pages for Record Picker on GitHub Pages.

## Public pages

- Official website: https://recordpicker.app/
- Discover page: https://recordpicker.app/
- Support: https://recordpicker.app/support/
- Screenshots: https://recordpicker.app/screenshots/
- Privacy policy: https://recordpicker.app/privacy/
- Press kit: https://recordpicker.app/press/
- Features page: https://recordpicker.app/readme/
- How to choose what vinyl record to play next: https://recordpicker.app/choose-vinyl-record/
- Random vinyl record picker app: https://recordpicker.app/random-vinyl-record-picker/
- Manage and rediscover a vinyl collection: https://recordpicker.app/manage-vinyl-collection/
- App Store: https://apps.apple.com/app/id6780422305
- YouTube: https://www.youtube.com/@recordpicker
- Facebook: https://www.facebook.com/profile.php?id=61591096987226
- Instagram: https://www.instagram.com/recordpicker/
- Reddit: https://www.reddit.com/user/RepulsiveInsect919/
- Contact: support@recordpicker.app

## Current release

Record Picker 2.7 is available on iPhone, iPad, Apple Watch, Mac and Windows.
On Apple it brings more varied Listening Journeys, saved Collection Stories,
a combined acquisition/listening timeline and collection-wide missing-information
lookup, plus camera import on iPhone and clearer navigation.

Apple 2.7.1 is available. Its Discogs release ID/link import previews genres,
styles, tracks and edition details before saving.

Record Picker 3.0 (formerly the 2.8 development cycle) is in preparation. Its
agreed Light offer is €2.99 as a one-time purchase: a simple album catalogue,
unlimited records and imports, Random Pick, Today's Pick and Mood Pick, plus
favourites, search, backup and restore. Pro adds Listening Journeys, collection
graphs, advanced statistics, Reviews/Keywords tools, batch enrichment and
private pressing details. Existing Pro purchases retain their rights and the
Pro price remains unchanged. The local storefront price is shown before
purchase. Private pressing photos currently remain on the device.

The offer is staged on all 33 localized site variants; it does not imply that
3.0 has been submitted or released. English and French copy was edited
manually; the other new offer translations remain machine drafts pending a
native-speaker linguistic review. Existing screenshots retain their actual
capture versions. The yellow Android beta recruitment banner is preserved.

## App Store version history

## Platform roadmap

- Windows: 2.7 available on the Microsoft Store; 3.0 is under validation with Windows 10 x64 and Windows 11 ARM64 compatibility targets.
- Android: waiting for beta testers; ChromeOS compatibility is being validated through the Android app.
- 3.1: audio recognition; 3.2: recognition from record spines.

Regenerate the agreed offer with `python3 Scripts/announce_release_3_0.py`.
Its publication state is separate from the current release in
`data/release-state.json`. Store availability must be verified before promoting
3.0 from a staged announcement to the current release.

Localized Windows product pages are available under `/windows-app/` for every
supported site language.

### v2.3.2 - Available now on Mac; coming soon on iPhone, iPad and Apple Watch

- A portable `.recordpicker` file will carry the collection, wishlist,
  favourites, custom artwork and pick history between devices.
- Export, import and verification will be available on iPhone, iPad and Mac;
  the existing JSON and CSV options remain available.
- The format is independent of iCloud and prepares future transfers with the
  Android and Windows versions.

### v2.3 - Available now on iPhone, iPad, Apple Watch and Mac

- A more complete Apple Watch experience for picking another record and
  following the result from the wrist.
- Clearer iPhone-Watch synchronization states for picks and artwork.
- Playback status appears consistently on iPhone, iPad and Mac.
- Today's Pick notifications can reflect several new suggestions with an
  incrementing badge.

### v2.2 - Available now on iPhone, iPad, Apple Watch and Mac

- CSV import clearly separates the Record Crate from the Wishlist, supports
  custom column mapping and provides a detailed result summary.
- Artist, genre and label suggestions, plus a preferred physical format, make
  manual entry faster without overwriting the collector's own metadata.
- Genre sorting and multi-genre filters make the library easier to explore and
  sharpen Random Pick and Mood Pick.
- Today's Pick shows stronger sources, freshness and evidence, with relevant or
  not relevant feedback to improve future suggestions.
- Reliability, accessibility and localization improvements keep large
  collections responsive and private across iPhone, iPad and Mac.

### v2.1.1

- Compact-iPhone layouts keep navigation visible, including in portrait on
  iPhone SE.
- Discogs CSV imports handle real-world exports more reliably.
- Contextual help, faster artwork, safer backup and restore, accessibility,
  localisation and interface refinements improve everyday use.

### v1.9 - Available now on iPhone, iPad, Apple Watch and Mac

- Today's Pick gives collectors a timely, private reason to rediscover a
  record they already own.
- Verified music news, anniversaries and optional nearby concerts are matched
  to the collection on device.
- Every suggestion explains its reason and cites a dated source; the
  collection is never sent to the news service.
- Record Picker is localized in 32 languages and regional variants.

### v1.8

- One shared version number across every Apple platform.
- More physical formats, including CD, SACD, MiniDisc, cassette, DVD-Audio,
  Blu-ray Audio and 78 rpm records.
- Dedicated classical-music fields for works, catalogue numbers, conductors,
  orchestras, ensembles, soloists, recording dates and recording places.
- Proactive Collection Health separates reliable automatic fixes from choices
  that need the collector's decision.
- MusicBrainz and Discogs conflicts are shown side by side with source and
  confidence; the resumable repair queue supports CSV reports and undo.
- A new four-step guide introduces imports, data quality, Random Pick,
  Mood Pick and Free/Pro.
- Record pages lead with the original release year while preserving the exact
  edition year.
- Clearer CSV portability and stronger safeguards for backups, favourites,
  artwork, imports and metadata repairs.

### v1.6 / macOS 1.0

- Record Picker is now free for collections of up to 100 records; a one-time Pro purchase unlocks an unlimited collection on iPhone, iPad and Mac, with no subscription.
- The new native Mac app turns the big screen into a command center for browsing, enriching, cleaning up and rediscovering the collection.
- iCloud synchronization is more responsive, with its status now visible in a dedicated Sync Center.
- CSV imports now protect existing favorites; you can also restore favorites only from an earlier backup without replacing the current collection.
- Duplicate detection is much faster, review selection is better, and review-keyword reindexing now shows clear progress.
- Clear storage diagnostics report problems instead of making an error look like data loss.

### v1.5

- More reliable iCloud synchronization across iPhone, iPad and Apple Watch.
- Artwork is now added automatically after manual or barcode entry, with more robust fallbacks.
- Improved data-quality tools, duplicate management and critical-review fetching.

### v1.4

- iPhone landscape selector: turn the phone sideways to see the cover on the left and full record details on the right, including title, artist, genre tags, format, label, and added-in year.
- The Pick button stays centered next to the metadata, while the bottom toolbar floats equidistantly between the cover and the screen edge.
- Swipe the album cover from right to left to draw a new record, or left to right to undo the last draw. Tap still opens details, long-press still excludes, and it works on iPad too.
- In the record crate, the Favorite chip is replaced by a small red star on every iPhone row and every iPad grid tile: one tap to mark, one tap to unmark.
- Statistics get denser in landscape: on iPhone, tiles reflow into three columns, matching the iPad density.
- Cleaner swipes everywhere: swipe-to-delete is back on the wishlist and added to AI Mood history; old cross-screen swipes that fought row-level deletions have been retired.

### v1.3

- Apple Watch reimagined: the cover sits as a blurred backdrop, with three thumb-friendly buttons for favorite, undo the last draw, and next draw, each with dedicated haptic feedback.
- Apple Watch layout adapted from 41 mm to Ultra.
- Barcode scan now falls back to Discogs when MusicBrainz does not know the reference; if Discogs finds the edition, the form is pre-filled automatically.
- Record Picker is available in 32 languages and regional variants, including Arabic, Catalan, Korean, Danish, English for Australia/Canada/United Kingdom, Finnish, Canadian French, Hebrew, Hindi, Indonesian, Norwegian, Polish, Portuguese for Brazil/Portugal, Russian, Spanish for Mexico, Swedish, Thai, Turkish and Vietnamese.
- Small polish: better balanced cover picker sheet on iPad, faster iPhone-Watch sync, and a discreet App Store review request after regular use.

### v1.2

- Full music collection catalog for imports, manual album entry, and barcode scanning.
- Animated random draw, year filters, favorites, temporary exclusions, listening history, and collection statistics.
- Mood-based picking with local Apple models when available, otherwise on-device matching from collection metadata.
- MusicBrainz metadata lookup, Cover Art Archive artwork or manual artwork import, backup/restore, Siri Shortcuts, and Apple Watch companion.
- The collection stays stored locally; metadata and artwork lookups happen only when the user starts them.

### v1.1.1

- Interface and internal foundations refined for a smoother experience.
- Improved iPad support.
- Mood-based picking with better use of critical reviews.
- Data quality: record detail sheets, manual row deletion, Discogs/MusicBrainz searches.
- Missing tracks: MusicBrainz search followed by Discogs search.

## Privacy

Your collection stays stored locally on your device and, when you enable
iCloud for Record Picker, may synchronize through your private iCloud
database. Record Picker does not operate a collection server. Metadata and
cover searches contact external services only when you start a lookup.

## Release checks

Run the media builder before the final site refinement so legacy screenshots
are served as high-quality WebP files while their source captures remain
available in the repository:

```sh
python3 Scripts/build_legacy_web_media.py
python3 Scripts/refine_site_finish.py
python3 Scripts/refine_homepage_descriptions.py
python3 Scripts/refine_remaining_localized_copy.py
python3 Scripts/add_official_identity_and_press.py
python3 Scripts/complete_growth_strategy.py
python3 Scripts/publish_release_2_3.py
python3 Scripts/announce_release_2_3_2.py
python3 Scripts/test_release_2_3_2_staging.py
python3 Scripts/publish_release_2_3_2_mac.py
python3 Scripts/test_release_2_3_2_mac_publication.py
python3 Scripts/announce_android_pc_development.py
python3 Scripts/audit_growth_strategy.py
python3 Scripts/audit_site_quality.py
python3 Scripts/site_localization_integrity.py
python3 Scripts/test_release_publication.py
```

When all 2.3.2 builds for iPhone, iPad, Apple Watch and Mac are approved and
ready, promote the staged announcement with the explicit safety gate:

```sh
python3 Scripts/publish_release_2_3_2.py \
  --confirm-apple-builds-ready \
  --publication-date YYYY-MM-DD
```

Public copy has a semantic integrity baseline. After reviewing an intentional
change across the generated localized pages, accept it explicitly:

```sh
python3 Scripts/site_localization_integrity.py --accept --reason "Reviewed 2.3 site copy"
```

The lock covers titles, descriptions, visible main content and accessible
image/control labels. It detects accidental localization drift while ignoring
unrelated HTML formatting.

## Search discovery and beta recruitment

The 6 October 2026 discovery update clarifies two existing uses: cataloguing
vinyl records and CDs, and choosing what to play from an owned collection.
English, French, Italian and Portuguese homepages link directly to the relevant
existing guides. The French CD guide explains imports, editions and the free
100-record limit. The Italian Mac page no longer labels the app itself as 2.6;
real screenshots retain their actual capture version. Above-the-fold home images
load eagerly, and the touch targets remain usable on phones.

All 32 storefront labels preserve translated free-tier wording at runtime.
Android navigation and status badges now say Waiting for beta testers, with
localized equivalents. Beta language and 14-day participation requirements stay
explicit. Public release status remains governed by `data/release-state.json`;
this update does not publish an app release.

Run `Scripts/adapt_search_discovery_2026_10_06.py` and
`Scripts/update_android_beta_status.py` to apply these scoped copy updates.
Review and explicitly accept the resulting localization-integrity manifest
before deployment.

## Physical support pages

The separate Physical app uses `/physical/privacy/`, `/physical/support/` and
`/physical/about/`, with French equivalents under `/physical/fr/`. These pages
describe the current development app, not future ads or Health imports.
Run `python3 Scripts/audit_physical.py`; the main quality audit also includes it.
Physical has its own content and is excluded from Record Picker release checks.

## Creator ecosystem — 8 October 2026

The bilingual creator hub lives at `/apps/` (English) and `/fr/apps/` (French). Principal Record Picker, Physical Routine and Snory Teller pages link to one another and to this hub. Keep product claims and availability separate. Hub pages have a dedicated link audit; canonical and localization checks still apply. Snory Teller has its own sitemap, also declared in robots.txt.

Instagram profile verified in Safari: `https://www.instagram.com/my_musical_update/`, bio “Monthly playlists”. Existing links: Spotify, Apple Music, Record Picker App Store, Record Picker website, Mac4Ever article. Proposed bio: “Monthly playlists & music discoveries 🎶\nCreator of @recordpicker\nMy apps: music, movement & nights ↓”. Proposed destination for the existing website slot: `https://recordpicker.app/apps/?utm_source=instagram&utm_medium=social&utm_campaign=creator_hub&utm_content=my_musical_update_bio`, label “My apps · Yves Durand”. Retain music-service links and the direct App Store link. No Instagram profile edits or posts were made by this release.

Next editorial work: a Snory Teller bedside setup and report-reading guide; a Physical Routine first-week guide; contextual links to existing Record Picker collection guides. Keep each article useful on its own. Do not promise sleep improvements, stronger watch motors or guaranteed search rankings. Measure search clicks and impressions in the existing webmaster consoles; campaign parameters alone do not provide analytics, and no tracking scripts were added.
