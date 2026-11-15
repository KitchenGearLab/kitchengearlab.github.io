# Seasonal header logo

All 64 English/French static pages share the managed logo picture and one small inline script in the document head. No scheduled task, external library, API, cookie, local storage, network time service or new workflow is required. The existing homepage/Ninja hero files and automation remain separate and unchanged.

## Calendar and first render

The script uses the browser's current clock with `Intl.DateTimeFormat`, explicit `America/Toronto`, Gregorian calendar and Latin digits. November 1 through December 26 inclusive selects Christmas; December 27 through October 31 selects the original, every year. Native-JavaScript tests compare this result against `seasonal_hero.season_for` across 2026–2036, Toronto/UTC midnight and DST boundaries.

The original logo remains the actual static `img` source and srcset. Christmas WebP and PNG sources have `media="not all"` by default. During Christmas, a short-lived MutationObserver registered in the head activates those sources in a DOM microtask before rendering and disconnects as soon as the picture and img exist. There is no inline script interrupting parsing in the middle of the header. Tests record source changes before first paint and exactly one displayed-image load, already Christmas. The HTML picture content follows the standard source/img model.

The wrapper reserves exactly 32 × 32 CSS px and does not shrink. The img retains explicit 32 × 32 dimensions, empty alt (the adjacent brand name labels the link), original decoding behaviour and `object-fit:contain`. All pixels of the square artwork remain in frame, including the Santa hat. Brand name, tagline, navigation, CSS, SEO metadata, structured data and favicons stay unchanged. The brand stays a normal accessible link.

## Fallbacks and limits

- With JavaScript disabled/blocked, unsupported Intl/timezone data, unavailable MutationObserver, or any initialization exception, both festive sources remain inactive and the original static logo displays.
- If an activated festive image fails, the img error handler clears itself and removes the festive sources. Native picture selection then uses the unchanged original src/srcset; no recursive image retry is introduced.
- PNG is available when WebP is unsupported. Browsers may speculatively fetch the original 1.9 KB asset while parsing, even when Christmas is ultimately selected. Only one img is present and displayed; no high-priority logo request competes with the hero.
- Calendar selection occurs on each document load and depends on the visitor's device clock. A page kept open, or restored from the browser's page cache without reloading across a boundary, retains its initial logo until the next document load. No background timer or server-clock request is added.
- GitHub's inactivity rule cannot disable this logo selection because the deployed HTML contains it. This does not remove the existing scheduled-hero workflow's documented 60-day inactivity limitation.

## Approved assets

The exact supplied PNG is retained at `_originals/seasonal-logo/kitchengearlab-logo-christmas.png`, excluded from the Pages artifact. `_data/seasonal-logo.json` records source SHA-256, sizes and all derivative hashes. Source geometry is 1254 × 1254 RGBA, with the original transparent padding preserved. No crop, recolouring, rearrangement, regeneration or favicon replacement is performed.

`assets/images/brand/kitchengearlab-logo-christmas-{64,128,192}.{webp,png}` provides 1x, 2x and 3x sources. Offline preparation uses Lanczos resizing of the complete source, lossless optimized PNG and lossless exact WebP. Each encoded derivative is decoded and compared pixel-for-pixel to its resized RGBA input. The existing official logo files remain byte-for-byte unchanged.

## Maintenance and checks

The static HTML is the deployed source. `seasonal_logo.py` installs the same bounded head/header blocks on the inventory's 64 pages, computes all results before writing, refuses duplicate/ambiguous markup, and makes no writes when already current. `strip_logo` restores the original head/header bytes for the bilingual content-preservation checks. The bilingual generator preserves the inline script, image URLs and empty decorative alt unchanged.

```text
python scripts/seasonal_logo.py --check
python -m unittest discover -s scripts -p "test_seasonal_*.py" -v
python scripts/bilingual.py build --check
python scripts/check-bilingual.py
```

To prepare an approved replacement source offline, use `python scripts/prepare-christmas-logo.py SOURCE.png`, then review its images and manifest. Pillow is an offline preparation dependency only. Switching has no dependency installation or runtime build step. Windows tests for the existing Python hero calendar may require IANA tzdata as documented in SEASONAL-HERO.md.

Local QA additionally verifies all 64 routes at mobile/desktop widths, the full header geometry against the previous release at six widths, current Christmas selection before first paint, no-JavaScript/Intl-error/asset-error/PNG fallback, 2x/3x assets, visitor timezones far from Toronto, accessibility, and Lighthouse. QA reports are excluded from publication.

References: [HTML picture content model](https://html.spec.whatwg.org/multipage/embedded-content.html#the-picture-element), [DOM mutation observers](https://dom.spec.whatwg.org/#mutation-observers), [Intl DateTimeFormat](https://tc39.es/ecma402/#sec-intl.datetimeformat).
