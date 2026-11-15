# Seasonal homepage and Ninja collection heroes

The primary hero on `/`, `/fr/`, `/ninja/` and `/fr/ninja/` is managed by the same workflow. Headings, navigation, product listings, buttons, spacing outside the hero, CSS, canonical URLs, hreflang, affiliate links, scripts, social-image metadata and JSON-LD remain unchanged. The homepage integration leaves the Ninja collection HTML and assets byte-for-byte unchanged at release.

## Calendar and reconciliation

`.github/workflows/seasonal-ninja-hero.yml` runs every day at **00:17 America/Toronto**, away from the busiest start of the hour, and supports manual execution. Python `zoneinfo` independently determines the date **when the job executes**:

| Toronto calendar date, every year | Hero |
| --- | --- |
| January 1–October 31 | Classic |
| November 1–December 26, inclusive | Christmas |
| December 27–December 31 | Classic |

The script reconciles the desired state instead of toggling the previous state. A delayed or missed run catches up using the current date. All four documents and all assets are validated before any document is written. Repeated runs do not rewrite matching files or change their modification times. No visitor JavaScript, CSS hiding, duplicate images or browser-language redirect is involved.

## Workflow and deployment safety

- One concurrency group, without cancelling a running job; latest `main` fetched before editing.
- Only the four allowed HTML files are staged, and only when their content changes. Push is never forced; a conflicting concurrent editorial push fails safely and the next run reconciles a fresh checkout.
- Workflow-wide permissions are empty. The reconciliation job has only `contents: write` and `pages: write`; checkout is pinned to the verified v6 commit. No personal token, new secret, Actions-write permission or OIDC permission is needed.
- The repository retains **legacy Pages from `main:/`**. A `GITHUB_TOKEN` push does not initiate the normal Pages build, so the job explicitly uses the Pages build API and waits for confirmation of the exact commit.
- A matching build already deployed or in progress is not queued again. If a previous push succeeded but its build request failed, a subsequent no-change run repairs deployment without creating another commit. Unknown Pages settings fail closed; the job never rewrites deployment configuration.

References: [GitHub token event behaviour](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow), [Pages build API](https://docs.github.com/en/rest/pages/pages#request-a-github-pages-build).

## Assets and presentation

The two user-supplied PNGs are preserved byte-for-byte under `_originals/seasonal-ninja/` as `ninja-collection-classic.png` and `ninja-collection-christmas.png`. They are excluded from the Pages artifact. Their hashes and encoding provenance are in `_data/seasonal-ninja-hero.json`.

30 published derivatives live in `assets/images/hero/ninja-collection/`: widths 480, 640, 960, 1280 and 1672, each in AVIF, WebP and JPEG, for both seasons. The image is resized proportionally without cropping, rearranging, upscaling, translating or regenerating any content. All five appliances remain inside the full frame. Native source geometry is 1672 × 941.

`<picture>` prefers AVIF, then WebP, with responsive JPEG fallback. The single `<img>` has intrinsic dimensions, a fixed source aspect ratio with `object-fit:contain`, responsive sizes, eager loading, async decoding and the only high fetch priority. The explicit ratio prevents subpixel layout shifts caused by rounding the height of resized derivatives. No additional preload competes with the selected format. Existing fluid image CSS is unchanged.

Offline encoding uses Pillow with AVIF and WebP support; it is not installed or executed by the daily workflow. The switching and deployment scripts use Python's standard library and the Ubuntu runner's IANA timezone database. Windows maintainers may need the first-party `tzdata` package or a `PYTHONTZPATH` pointing to IANA data.

### Homepage images

The supplied `Cuisine moderne avec appareils Ninja et fruits frais.png` is CLASSIC; `Cuisine de Noël avec appareils Ninja.png` is CHRISTMAS. This follows their actual visible content, resolving the reversed numbering in the request. Exact originals are preserved under `_originals/seasonal-homepage/`; provenance is `_data/seasonal-homepage-hero.json`. The original attachment bytes are never published as a hero or regenerated.

30 additional derivatives are published under `assets/images/hero/homepage/`, with the same five widths and AVIF/WebP/JPEG settings. Prepare only this set with `python scripts/prepare-seasonal-hero.py --kind homepage --classic PATH --christmas PATH`; the default `--kind ninja` retains its existing behaviour. Preparing homepage images does not re-encode the collection assets.

Both homepages use one static `<picture>` with localized alt text, explicit 1672 × 941 source dimensions, responsive sources, eager loading and one high-priority image. The existing 1600:840 display ratio is retained with `object-fit:cover;object-position:center`. The small vertical crop affects background/countertop; all three appliances remain within the visible source rectangle. The previous WebP-only homepage preload is removed to avoid a competing download when AVIF is selected. No replacement preload is needed: the picture is discoverable in the HTML and measured performance remains above the requested threshold. No global CSS or container spacing is changed.

## Checks and maintenance

```text
python -m unittest discover -s scripts -p test_seasonal_hero.py -v
python scripts/seasonal_hero.py --check
python scripts/bilingual.py build --check
python scripts/check-bilingual.py
```

The tests cover seasonal boundaries for 2026–2036, UTC/Toronto boundaries and DST, both languages and seasons, all 60 asset hashes, ambiguous markup, no-op writes, missed-run recovery, deployment deduplication and a real two-run Git integration test against an isolated local bare remote. The existing bilingual generator knows both sets of seasonal alt-text translations and preserves the managed markup.

Do not manually toggle a season to test production. Unit tests inject dates into isolated fixtures. If re-encoding an original is necessary, run `prepare-seasonal-hero.py` with its explicit source paths, review derivatives and the manifest, and rerun validation. No image-generation model is used.

## GitHub platform limits

GitHub schedules may be delayed or dropped, so the hero is updated after the scheduled reconciliation and Pages deployment rather than guaranteed at exactly midnight. The next scheduled/manual run repairs a missed update. GitHub also **automatically disables scheduled workflows in public repositories after 60 days without repository activity**. Keep normal editorial activity or re-enable the workflow if GitHub disables it. No dummy keepalive commits or unnecessary daily Pages builds are created. Daily no-op workflow runs are not treated as proof of repository activity.

### Reliable option for prolonged inactivity

An external daily watchdog can reuse **this exact workflow**, without another deployment pipeline or visitor JavaScript. A suitable independent cron host should run after the normal daily schedule (for example 07:47 UTC), authenticate using a short-lived GitHub App installation token restricted to this repository with `Actions: write`, and:

1. GET `/repos/KitchenGearLab/kitchengearlab.github.io/actions/workflows/seasonal-ninja-hero.yml` and its recent runs on `main`.
2. If the workflow state is `disabled_inactivity`, PUT the same workflow's `/enable` endpoint. Do not override a deliberate administrative disable.
3. If no successful reconciliation for today's Toronto date exists and no reconciliation is queued/in progress, POST its `/dispatches` endpoint with `{"ref":"main"}`.
4. Monitor the resulting run and retry failures on a later check. The existing reconcile/build safeguards prevent duplicate commits and builds on repeated dispatches.

External credentials belong in the scheduler's secret store, never the repository or the public website. The existing job token permissions remain unchanged. An external host and installation credential were not supplied, so this option is evaluated and documented, **not provisioned or claimed active**. Fully autonomous switching after indefinite repository inactivity cannot be guaranteed by GitHub's own public-repository cron alone.

References: [Enable a workflow](https://docs.github.com/en/rest/actions/workflows#enable-a-workflow), [Create a workflow dispatch](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event).

[Official schedule limitations](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
