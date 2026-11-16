# Evergreen homepage sharing image

The English and French homepages use the same year-round photo, cropped from the
approved classic homepage source. This does not change the visible homepage hero,
header, logo, seasonal calendar, canonical URLs or structured data.

Primary Facebook/Messenger/Twitter image:
`https://kitchengearlab.github.io/assets/images/og/home-og-v2-1200x630.jpg`

An equivalent optimized WebP is archived at
`assets/images/og/home-og-v2-1200x630.webp`. The old
`assets/images/og/home-og-1200x630.webp` remains available for existing shares.
Do not list the outdated asset as a second `og:image`, which could allow selection
of the old composition again. Both homepages declare exactly one primary image.

## Image preparation

Source: `_originals/seasonal-homepage/homepage-classic.png`, 1672 × 941 RGB/RGBA.
Source SHA-256: `b91007aec8380d7e65c251625ab8d5e45d23954b4e5d8155e03eb0826bd573c5`.
The original stays excluded from publication.

Use Pillow `ImageOps.fit(source.convert('RGB'), (1200, 630),
method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))`. This keeps the full width
and crops only the top/bottom (source crop box 0, 31.6, 1672, 909.4).
No generative image editing, compositing, text, seasonal elements or product changes
are applied. All three appliances remain visible and retain their proportions.

JPEG: quality 92, subsampling 0, optimize true, progressive false; baseline RGB,
177,593 bytes. WebP: quality 90, method 6; RGB, 84,702 bytes. Both are exactly
1200 × 630. Image preparation tools are offline dependencies only.

## Metadata and maintenance

`python scripts/homepage_og.py` updates only the known homepage image URL/type
fields and adds `og:image:secure_url`. `--check` verifies idempotence. Existing
localized titles, descriptions, image alt text, locales and canonical social URLs
are retained. `bilingual.py build --check` verifies that regeneration preserves
the French page. No client-side script supplies social metadata and no App ID
is invented.

The bilingual and header regression checks allow this exact intentional image
update against their historical baselines while continuing to protect all other
content, metadata and image assets. Build Jekyll into `_site/header2` before
running those rendered checks (see `HEADER.md`).

Use a new filename for any future approved revision rather than overwriting v2.
The JPEG is the primary format because Meta documents `image/jpeg`, `image/gif`
and `image/png` for `og:image:type`:
https://developers.facebook.com/documentation/sharing/webmasters

## Refresh Facebook's cached page preview

After the Pages deployment succeeds, open the official Sharing Debugger for each
exact homepage URL and use **Debug**, then **Scrape Again** if the old page preview
is still cached:

- https://developers.facebook.com/tools/debug/?q=https%3A%2F%2Fkitchengearlab.github.io%2F
- https://developers.facebook.com/tools/debug/?q=https%3A%2F%2Fkitchengearlab.github.io%2Ffr%2F

These inspect `https://kitchengearlab.github.io/` and
`https://kitchengearlab.github.io/fr/` respectively. A versioned asset URL avoids
reusing the old image cache; it does not itself prove Facebook has re-scraped the
page. Verify the actual Facebook card in the official tool. HTTP/crawler-user-agent
tests alone cannot certify Meta's cached preview or existing Messenger shares.
