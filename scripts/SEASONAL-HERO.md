# Seasonal Ninja collection hero

Only the primary `<figure class="hero-media">` on `/ninja/` and `/fr/ninja/` is managed. Headings, navigation, product listings, buttons, spacing, CSS, canonical URLs, hreflang, affiliate links, scripts, social-image metadata and JSON-LD remain unchanged.

## Calendar and reconciliation

`.github/workflows/seasonal-ninja-hero.yml` runs every day at **00:17 America/Toronto**, away from the busiest start of the hour, and supports manual execution. Python `zoneinfo` independently determines the date **when the job executes**:

| Toronto calendar date, every year | Hero |
| --- | --- |
| January 1–October 31 | Classic |
| November 1–December 26, inclusive | Christmas |
| December 27–December 31 | Classic |

The script reconciles the desired state instead of toggling the previous state. A delayed or missed run catches up using the current date. Both documents are computed and validated before either is written. Repeated runs do not rewrite matching files or change their modification times. No visitor JavaScript, CSS hiding, duplicate images or browser-language redirect is involved.

## Workflow and deployment safety

- One concurrency group, without cancelling a running job; latest `main` fetched before editing.
- Only the two allowed HTML files are staged, and only when their content changes. Push is never forced; a conflicting concurrent editorial push fails safely and the next run reconciles a fresh checkout.
- Workflow-wide permissions are empty. The reconciliation job has only `contents: write` and `pages: write`; checkout is pinned to the verified v6 commit. No personal token, new secret, Actions-write permission or OIDC permission is needed.
- The repository retains **legacy Pages from `main:/`**. A `GITHUB_TOKEN` push does not initiate the normal Pages build, so the job explicitly uses the Pages build API and waits for confirmation of the exact commit.
- A matching build already deployed or in progress is not queued again. If a previous push succeeded but its build request failed, a subsequent no-change run repairs deployment without creating another commit. Unknown Pages settings fail closed; the job never rewrites deployment configuration.

References: [GitHub token event behaviour](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow), [Pages build API](https://docs.github.com/en/rest/pages/pages#request-a-github-pages-build).

## Assets and presentation

The two user-supplied PNGs are preserved byte-for-byte under `_originals/seasonal-ninja/` as `ninja-collection-classic.png` and `ninja-collection-christmas.png`. They are excluded from the Pages artifact. Their hashes and encoding provenance are in `_data/seasonal-ninja-hero.json`.

30 published derivatives live in `assets/images/hero/ninja-collection/`: widths 480, 640, 960, 1280 and 1672, each in AVIF, WebP and JPEG, for both seasons. The image is resized proportionally without cropping, rearranging, upscaling, translating or regenerating any content. All five appliances remain inside the full frame. Native source geometry is 1672 × 941.

`<picture>` prefers AVIF, then WebP, with responsive JPEG fallback. The single `<img>` has intrinsic dimensions, a fixed source aspect ratio with `object-fit:contain`, responsive sizes, eager loading, async decoding and the only high fetch priority. The explicit ratio prevents subpixel layout shifts caused by rounding the height of resized derivatives. No additional preload competes with the selected format. Existing fluid image CSS is unchanged.

Offline encoding uses Pillow with AVIF and WebP support; it is not installed or executed by the daily workflow. The switching and deployment scripts use Python's standard library and the Ubuntu runner's IANA timezone database. Windows maintainers may need the first-party `tzdata` package or a `PYTHONTZPATH` pointing to IANA data.

## Checks and maintenance

```text
python -m unittest discover -s scripts -p test_seasonal_hero.py -v
python scripts/seasonal_hero.py --check
python scripts/bilingual.py build --check
python scripts/check-bilingual.py
```

The tests cover seasonal boundaries for 2026–2036, UTC/Toronto boundaries and DST, both languages and seasons, all asset hashes, ambiguous markup, no-op writes, missed-run recovery, deployment deduplication and a real two-run Git integration test against an isolated local bare remote. The existing bilingual generator knows the two seasonal alt-text translations and preserves the managed markup.

Do not manually toggle a season to test production. Unit tests inject dates into isolated fixtures. If re-encoding an original is necessary, run `prepare-seasonal-hero.py` with its explicit source paths, review derivatives and the manifest, and rerun validation. No image-generation model is used.

## GitHub platform limits

GitHub schedules may be delayed or dropped, so the hero is updated after the scheduled reconciliation and Pages deployment rather than guaranteed at exactly midnight. The next scheduled/manual run repairs a missed update. GitHub also **automatically disables scheduled workflows in public repositories after 60 days without repository activity**. Keep normal editorial activity or re-enable the workflow if GitHub disables it. No dummy keepalive commits or unnecessary daily Pages builds are created. A guarantee for a permanently dormant repository would require an external scheduler; none is added here.

[Official schedule limitations](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
