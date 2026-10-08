# Creator hub localization

The creator hub and the public Dulpi presentation support the exact 50 locale
identifiers used by Snory Teller's ASC metadata (44 distinct languages plus
regional variants). `manifest.json` is the authoritative URL inventory.

French and English retain the existing authored copy. Additional languages use
machine translations of public English copy, cached in the language JSON files.
Regional English, French, Spanish and Portuguese variants share their language
copy; the locale identifiers and navigation remain distinct. Additional-language
copy still needs native-speaker editorial review; automated checks cannot prove
translation quality. Brand names, playlist titles and destination URLs are kept.

Regenerate offline with `python3 Scripts/localize_creator_hub.py` (requires lxml).
Refresh missing translations explicitly with `--refresh`; it sends only public
copy to Google Translate. Do not run translation refresh in deployment CI.
Edit the authored source snapshots in `templates.json`, then regenerate.

Validation: `python3 Scripts/audit_creator_locales.py` plus the site's existing
canonical, localization-integrity and quality checks. Both sitemaps include all
100 pages. Language links are static and crawlable; no language detection or
redirect prevents visitors from choosing their preferred version. Dulpi remains
a public presentation only, with no interactive demo or restricted-app link.
