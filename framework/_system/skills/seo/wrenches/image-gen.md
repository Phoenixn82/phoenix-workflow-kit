---
name: seo-image-gen
description: AI image generation for SEO assets — OG / social preview images, blog hero images, schema images, product photography, infographics. Powered by Gemini (Nano Banana) via the banana MCP. Conditional wrench — requires banana extension installed. Trigger phrases include "generate image", "OG image", "social preview", "hero image", "blog image", "product photo", "infographic", "SEO image", "create visual", "image-gen", "favicon", "schema image", "pinterest pin", "generate visual", "banner", "thumbnail".
---

# seo-image-gen — AI image generation for SEO

When a project needs OG images, hero images, schema images at scale, or product mockups, this wrench generates them via the banana MCP (Gemini-powered).

CONDITIONAL: requires banana MCP installed. If not available, surface "install banana MCP to enable image-gen" and exit.

---

## When to fire

- "Generate OG image for X" / "social preview for Y"
- "Hero image for blog post Z"
- "Infographic from this data"
- "Generate schema images for products"
- "Make a thumbnail"

Don't fire when:
- Banana MCP not installed → surface install instructions, exit
- Photography (not generated) is needed → push back; AI gen isn't always right

---

## Image types

| Type | Specs | Use |
|---|---|---|
| OG image | 1200×630px | Social shares (Facebook / LinkedIn) |
| Twitter Card | 1200×600px or 1200×675px | Twitter / X shares |
| Blog hero | 1920×1080px or 2400×1260px | Header of blog post |
| Schema image | square 1:1 + 4:3 + 16:9 | For ImageObject in Article / Product schema (Google recommends all 3) |
| Pinterest pin | 1000×1500px | Pinterest |
| Product mockup | 1500×1500px | Product listings |
| Infographic | tall, scannable | Long-form content |
| Favicon | 32×32, 192×192, 512×512 | Browser tab + PWA |
| Banner / thumbnail | varies | YouTube thumbnails, page banners |

---

## Sequence

1. The user specifies: what image, what type, what style
2. Wrench composes the banana prompt (style guide + content + constraints)
3. Dispatch via banana MCP
4. Returns image to `$env:TEMP\<slug>\` (Windows scratch; or a project-local scratch dir)
5. The user approves / iterates
6. On approve, move to project's image directory
7. Update schema markup if relevant (schema images need to be referenced)

---

## Style consistency

Reads project's DESIGN.md (from design-studio) if exists, matches style to brand. Otherwise asks the user for style guide.

---

## See also

- [SKILL.md](../SKILL.md)
- [images.md](images.md) — audit existing images
- [schema.md](schema.md) — schema images go here
- [`design-studio/SKILL.md`](../../design-studio/SKILL.md) — DESIGN.md source
