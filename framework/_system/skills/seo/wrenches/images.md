---
name: seo-images
description: Image optimization audit. Alt text, file sizes, formats (WebP / AVIF conversion), responsive images, lazy loading, CLS prevention, image SERP rankings (via DataForSEO if wired), IPTC/XMP metadata. Trigger phrases include "image SEO", "alt text", "image optimization", "image size", "image audit", "optimize images", "WebP", "AVIF", "image metadata", "image SERP rankings".
---

# seo-images — image optimization audit

Images are often the biggest performance + SEO opportunity. This wrench audits accessibility (alt text), performance (size, format), and discoverability (image SERP).

---

## When to fire

- "Image SEO audit"
- "Alt text audit"
- "Optimize images" / "WebP conversion"
- "Why is my LCP slow" (often image-related)
- Fired as part of `audit` always-set

---

## Dimensions

| Dimension | Checks |
|---|---|
| **Alt text** | Present, descriptive, not keyword-stuffed, blank for decorative |
| **File size** | < 200 KB for content images, < 100 KB for thumbnails |
| **Format** | Modern (WebP / AVIF) over JPG/PNG where supported |
| **Dimensions** | Served at displayed size, not 4000px wide when shown at 600px |
| **Responsive** | `srcset` + `sizes` for content images |
| **Lazy loading** | `loading="lazy"` for below-fold images |
| **CLS** | Width / height attributes present to prevent layout shift |
| **Image SERP** | Title / alt / filename SEO-friendly (DataForSEO if wired) |
| **Metadata** | IPTC / XMP fields for important images |

---

## Sequence

1. Crawl image URLs from pages
2. Per image: HEAD request for size + format
3. Per image: extract alt text + dimensions attributes from HTML
4. Compute composite score per page (% optimized)
5. List bottom-20 pages (most image issues)
6. Recommend fixes (Codex can batch-convert via Phase 5 helper script)

---

## Output shape

```markdown
## Image audit — example.com

### Coverage
- 1,247 images on site
- 689 (55%) optimized (alt + modern format + sized correctly)
- 558 (45%) need attention

### Top issues
- 234 missing alt text
- 187 oversized (>500 KB)
- 156 not modern format (JPG/PNG only)
- 89 missing width/height (CLS risk)
- 67 not lazy-loaded (below fold)

### Top 10 worst-offender pages
1. /home — 12 image issues
2. /products — 9 issues
...

### Recommended actions
1. Generate alt text for 234 images (Codex batch task)
2. Convert 187 oversized to WebP (batch ffmpeg or sharp)
3. Add width/height to 89 (lint check)
4. Add loading="lazy" to 67 below-fold images
```

---

## See also

- [SKILL.md](../SKILL.md)
- [image-gen.md](image-gen.md) — generate NEW images (banana MCP)
- [technical.md](technical.md) — CWV / LCP context
