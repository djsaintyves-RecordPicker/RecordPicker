# Record Picker

Record Picker helps you rediscover your physical music collection and choose the next album to play.

Android and Windows versions are in development. Release details will be announced
when both versions are ready.

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

## App Store version history

## Platform roadmap

- Windows: coming soon.
- Android: in development.

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
python3 Scripts/announce_android_pc_development.py
python3 Scripts/audit_growth_strategy.py
python3 Scripts/audit_site_quality.py
python3 Scripts/site_localization_integrity.py
python3 Scripts/test_release_publication.py
```

Public copy has a semantic integrity baseline. After reviewing an intentional
change across the generated localized pages, accept it explicitly:

```sh
python3 Scripts/site_localization_integrity.py --accept --reason "Reviewed 2.3 site copy"
```

The lock covers titles, descriptions, visible main content and accessible
image/control labels. It detects accidental localization drift while ignoring
unrelated HTML formatting.
