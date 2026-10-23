# My Physical Routine localized public pages

`templates.json` contains authored French/English sources for product, support
and privacy pages. `manifest.json` inventories 150 pages across the same 50 ASC
locale variants as the Studio. Other public copy uses cached machine translations;
native-language editorial review remains pending.

Generate offline with `python3 Scripts/localize_physical.py`. Use `--refresh`
only when deliberately translating new public text. Do not run it in CI.

MPR pages and its 50 getting-started guides follow `navigator.languages` in order,
including when entered through an old French/English URL. There is no visible
language control. Unsupported preferences fall through to the next supported
language; English is the final fallback. Region variants, traditional/simplified
Chinese, Norwegian and legacy Hebrew tags are supported. Redirects use replace
and retain query parameters and fragments; landing on the right locale is stable.
If JavaScript is unavailable, the requested static page stays readable.

URLs used by existing App Store metadata and app binaries remain valid.
All translations are static, crawlable pages with reciprocal hreflang metadata.
`physical/sitemap.xml` is advertised in robots.txt. Studio cards and app ecosystem
links point to the appropriate localized product page rather than a guide fallback.

Verify with `node Scripts/test_physical_language_navigation.cjs` and
`python3 Scripts/audit_physical.py`, alongside the Studio/link/SEO audits.
