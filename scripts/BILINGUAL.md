# KitchenGearLab bilingual publication

The 32 original English routes remain authoritative. Each has an explicit French equivalent under `/fr/`; the complete map is `_data/bilingual-pages.json`. All pages, navigation, metadata and structured data are rendered to static HTML. The language switch is an ordinary pair of links, with no automatic redirect or client-side translation.

## Editorial workflow

1. Edit the English static source as needed. Run `python -X utf8 scripts/bilingual.py inventory` when adding routes or new text; existing segment identifiers and translations are retained.
2. Add or revise the French translation by identifier in `_content/fr-translations.tsv`. `_content/fr-preserved.json` explicitly lists unchanged brand names, model codes, official colour names, numbers and appropriate technical terms. There is no fallback to English for an unknown segment.
3. Run `python -X utf8 scripts/bilingual.py build`. It produces all French pages, preserves the shared Jekyll header includes, inserts reciprocal alternates into English pages, and writes the bilingual sitemap. The shared header generates each exact language-switch pair at build time. The translation build fails on missing translations. `_content/bilingual-fr.json` retains the source text, translation and first route for review.
4. Run `python -X utf8 scripts/bilingual.py build --check`, compile the site into `_site/header2` (see `HEADER.md`), then run `python -X utf8 scripts/check-bilingual.py` before publication. The latter checks rendered HTML and protects English editorial content against the pre-bilingual commit `f31080bf76fc6b664375f4378c9c02ffadd9714e`; a later intentional English editorial revision requires updating that regression baseline deliberately.

Use this bilingual workflow after the rollout. The earlier local `render-ninja.mjs` is a historical English-only generator and must not overwrite bilingual pages or the sitemap. HTML sources contain front matter and the two shared header includes described in `HEADER.md`; GitHub Pages expands these with its existing native Jekyll build. It does not need Python or a translation build step.

All translation inputs, scripts and reports are excluded from the Jekyll artifact by `_config.yml`. Only explicitly reviewed maintenance files are tracked, despite the repository's existing ignore patterns. Do not broadly force-add other local editorial inputs, credentials, original images or reports.

## Release checks

- All 64 canonical pages, reciprocal `en-CA` / `fr-CA`, same-language local links, fragments, image URLs, JSON-LD and sitemap annotations.
- Exact Amazon destinations, ASINs, `kitchengearla-20`, sponsored link attributes and tracking data retained. 72 active links and seven paused Philips modules per language.
- 64 routes at 320 and 1440 px; shared navigation also at 375, 430, 768, 1024 px and landscape; exact language switching, 200% text, keyboard Escape, no-JavaScript access and representative synthetic affiliate events.
- All 64 pages scanned with axe after correcting accessible labels. Lighthouse mobile compared on matching English/French Crispi pages; analytics blocked in local lab tests.

One pre-existing English inconsistency was corrected: the visible DualZone FAQ answer in the Ninja air fryer hub now matches its existing conservative JSON-LD answer. Its French counterpart uses the same answer. Other English editorial content, titles, descriptions and canonicals are preserved, apart from Canadian language metadata and the bilingual navigation/alternate annotations.

The local browser and Lighthouse evidence is in `_reports/bilingual-*`. Browser scripts use the existing local QA dependencies; they make no Amazon purchase or analytics requests. Automated accessibility and lab performance checks do not certify accessibility, field Core Web Vitals or future search rankings.
