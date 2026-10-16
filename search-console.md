# Google Search Console setup for Record Picker

This file documents the public indexing setup for the Record Picker GitHub Pages site.

## Property to add

Use a URL-prefix property:

https://recordpicker.app/

## Sitemap to submit

https://recordpicker.app/sitemap.xml

## Robots file

https://recordpicker.app/robots.txt

## Verification

Google Search Console verification must be completed from the owner's Google account.

Recommended options:

- URL-prefix verification from Google Search Console.
- HTML file verification with `googlec6e93ec4f524be4f.html`.
- HTML tag verification, if Google provides a `google-site-verification` token instead.

The HTML verification file is published at:

https://recordpicker.app/googlec6e93ec4f524be4f.html


## Canonical alignment — 7 October 2026

Search Console reported 17 URLs under “Duplicate, Google chose different canonical
than user”; validation started 21 September and failed 5 October. Inspection
confirmed these two examples:

- `/en-gb/choose-vinyl-record/`: Google selected `/choose-vinyl-record/`.
- `/fr-ca/mac-app/`: Google selected `/fr/mac-app/`.

Regional English guides, support, privacy, feature documentation and screenshots
now declare the unprefixed English counterpart as canonical. The equivalent
French Canadian informational pages, including the Mac page, declare their
French counterpart. Market homepages remain separate; distinct English Mac and
Watch content is not consolidated. `/en-us/` continues to prefer the unprefixed
English experience. No French page is consolidated into English.

The regional URLs remain available with their language, storefront links and
visible copy intact. Reciprocal `hreflang` links still target the appropriate
regional URLs, as recommended by Google's
[regional duplicate guidance](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites#handling-duplicate-pages-with-multilingualmulti-regional-sites).
`en-US` and `x-default` point to the matching unprefixed route. Canonical, Open
Graph page URL and structured page identity agree. Both sitemaps contain only
canonical URLs, with existing image metadata and unaffected dates retained.

Policy and repeatable verification:

```sh
python3 Scripts/site_canonical_policy.py
PYTHONPATH=Scripts python3 -m unittest Scripts/test_site_canonical_policy.py
```

The workflow checks this on every pull request and main-branch update. Use
`--write` to reconcile metadata and sitemaps after intentionally generating
pages; it does not rewrite public copy. Historical generators share the same
canonical policy. A new Google validation is requested only after deployment
and verification of the live pages; it does not mean Google has accepted the
change or completed its next crawl.

## US Mac alias consolidation — 16 October 2026

`/en-us/mac-app/` now immediately redirects to `/mac-app/`. GitHub Pages
does not provide a per-route HTTP redirect configuration, so the alias uses
an instant meta refresh, which Google treats as a permanent redirect.
`location.replace` preserves query parameters and fragment links for visitors.
The canonical, Open Graph URL, structured data and `en-US` alternate continue
to identify `/mac-app/`; both sitemaps already omit the alias.

Navigation links resolving to the US Mac alias, including relative links from
the US homepage and platform pages, now point directly to `/mac-app/`.
`site_canonical_policy.py --write` maintains the redirect and link alignment
after future page generation. In-page skip links and other regional Mac pages
remain unchanged. Sitemap modification dates are not advanced merely because
a noncanonical alias changed.

Google must crawl the updated alias before its reported canonical can change.
No Search Console indexing request or validation submission is part of this
correction. The existing deployment workflow retains its usual IndexNow notice.
