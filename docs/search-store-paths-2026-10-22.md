# Search-to-store paths — 22 October 2026

The existing English guide now explicitly targets choosing a record to play from an owned collection. Its five English regional variants share the existing canonical policy; no new redirect or indexing request was introduced. The guide adds a practical Discogs → collection → random-pick path. FR/EN home, Mac and random-pick pages link to the corresponding Mac and Discogs guide pages.

The 12 main-site landing pages now use the existing Umami EU configuration and privacy controls. Four existing Studio guides additionally label store events by app. Store links preserve the existing Apple `ct` and Microsoft `cid` attribution. On the Mac landing pages, Apple links explicitly select `platform=mac`.

Event: `store_click`. Properties: `app` (`record_picker`, `snory_teller`, `my_physical_routine`) and `destination` (`apple_app_store` for a universal Apple link, `apple_mac` for Mac-specific links, `apple_ios` on existing explicitly iOS guide buttons, or `microsoft`). These are outbound clicks, not installations or purchases. No duplicate manual event handler was added.

The loader honors the existing opt-out, GPC and DNT, removes query strings/fragments, and retains only the referrer origin. New landing pages display the same analytics notice and opt-out as the Studio. CSP permits only the existing analytics script host and collection gateway in addition to same-origin resources. Local preview does not send analytics because the loader requires recordpicker.app.

References:
- https://docs.umami.is/docs/track-events
- https://docs.umami.is/docs/tracker-configuration

Validation: internal destinations and fragments, canonical/hreflang/sitemaps, campaign attribution, full site quality audit, localization baseline and 390-pixel mobile rendering. Production test clicks must be recorded as internal checks, not acquisition results. The daily monitoring must start this expanded measurement from publication, without treating prior absent events as zero real store visits.
