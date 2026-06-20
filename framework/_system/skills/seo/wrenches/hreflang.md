---
name: seo-hreflang
description: Hreflang and international SEO. Audit, validate, generate hreflang implementations. Detects common mistakes (mismatched, self-referencing missing, missing return tags). Validates language / region codes (ISO 639-1 + ISO 3166-1). Trigger phrases include "hreflang", "i18n SEO", "international SEO", "multi-language", "multi-region", "language tags", "language codes", "regional content".
---

# seo-hreflang — international SEO

Hreflang is famously error-prone. This wrench audits + validates + generates correct implementations.

---

## When to fire

- Multi-language / multi-region site detected
- "Hreflang audit" / "international SEO"
- "Why isn't my Spanish page ranking in Spain"

Don't fire when:
- Single-language site
- Pure language variant without separate URLs

---

## Implementation options

| Method | Use when |
|---|---|
| HTML `<link rel="alternate" hreflang="...">` tags | Default; works for most |
| HTTP headers | Non-HTML files (PDFs); or when controlling HTML harder than headers |
| Sitemap | Cleanest for large sites; centralized control |

The wrench detects what's used and audits accordingly.

---

## Common errors caught

| Error | Why bad |
|---|---|
| Self-referencing missing | Each page must include hreflang to itself |
| Return tags missing | Page A says "alt = B" but B doesn't say "alt = A" |
| Invalid language code | Not in ISO 639-1 |
| Invalid region code | Not in ISO 3166-1 alpha-2 |
| Underscore instead of hyphen | "en_US" wrong; "en-US" correct |
| Wrong region attached | "en-DE" rarely intended (English in Germany?) |
| `x-default` missing or wrong | Should point at the language-selector or default |
| URLs not canonical | Hreflang URLs should match canonical |
| Page doesn't actually return that language | Tag claims es-ES but page is English |

---

## Generation

For sites without hreflang, the wrench generates correct tags:

1. Detect language per URL (Content-Language header or HTML lang attribute or content sniff)
2. Group equivalent pages across languages
3. Generate full hreflang tag set per page (every page lists every other)
4. Add x-default
5. Codex writes to source (hard rule #5)

---

## See also

- [SKILL.md](../SKILL.md)
- [technical.md](technical.md) — broader technical audit
- [`AGENTS.md`](../../../../AGENTS.md) — hard rule #5
