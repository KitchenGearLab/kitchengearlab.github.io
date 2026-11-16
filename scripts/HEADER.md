# Shared bilingual header

`_includes/header.html` is the single source for all navigation labels, destinations,
EN/FR equivalents, brand text, logo assets and critical header setup. All 64 public
HTML sources have `layout: null` YAML front matter and exactly these two includes:

```liquid
{% include header.html part="head" %}
{% include header.html %}
```

Keep the first immediately before `</head>` and the second at the header position.
GitHub Pages' existing managed Jekyll build expands both into static, crawlable HTML.
No Python, new deployment workflow, external framework or browser translation is
needed in production. Edit the include once; do not copy rendered headers into pages.
For a new route, also update the bilingual inventory and translations as documented
in `BILINGUAL.md`. The language switch derives the exact counterpart from `page.url`.

## Presentation and interaction

Header rules are at the end of `assets/css/styles.css`; progressive interaction is
in `assets/js/navigation.js`. Desktop navigation starts at 1024 px. The fixed logo
frame is 40 px on mobile/tablet and 44 px on desktop, with the complete artwork
contained inside it. Logo source files, favicons and seasonal heroes are unchanged.

Native `details`/`summary` disclosures provide the mobile menu, Ninja dropdown and
five expandable categories. With JavaScript unavailable, mobile navigation starts
expanded and every link remains available. With JavaScript, the mobile menu closes
before paint, Escape closes the inner then outer disclosure and returns focus,
ArrowDown opens Ninja and focuses its first link, and leaving the header closes it.
These are navigation disclosures, not ARIA application menus; ordinary Tab/Shift+Tab
navigation and native Enter/Space activation are retained. There is no focus trap.

The seasonal logo script and picture are owned by this same include. Its Toronto
calendar and original-logo fallback are described in `SEASONAL-LOGO.md`. The existing
scheduled homepage/Ninja hero workflow is unchanged, including its inactivity limit.

## Checks before publishing

Build with native Jekyll 3.10.0 into `_site/header2` when available. Alternatively,
`ruby scripts/render-header.rb` uses Liquid 4.0.4 for local QA only; it is not part
of deployment. On this rollout its 271 public output files were byte-identical to
the native Jekyll build. Compile again after any source, stylesheet or script edit.

```text
python scripts/header.py --check
python scripts/bilingual.py build --check
python scripts/check-bilingual.py
python -m unittest discover -s scripts -p "test_header.py" -v
python -m unittest discover -s scripts -p "test_seasonal_*.py" -v
```

Compiled checks read `_site/header2`. They verify all 64 pages, existing header links,
exact language pairs, content outside the header, SEO, affiliate attributes, assets
and seasonal compatibility. Python calendar tests need IANA tzdata on Windows.
The local `check-header-browser.py` helper additionally exercises all 64 routes on
mobile/desktop, six viewport widths, keyboard focus, axe, no-JavaScript access and
both logo seasons/fallbacks; it uses existing local QA tools and a loopback server.
Do not publish QA reports or install browser/test dependencies into the public site.

Automated accessibility checks and Chromium accessibility trees do not replace a
physical screen-reader session. Lighthouse is a lab measurement, not field CWV or
INP. Recheck public EN/FR pages and the exact Pages artifact after deployment.
