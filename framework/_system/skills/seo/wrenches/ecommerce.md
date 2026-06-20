---
name: seo-ecommerce
description: E-commerce SEO. Google Shopping visibility, Amazon marketplace intelligence, Product schema validation, competitor pricing analysis, marketplace keyword gaps. Combines on-page product SEO with marketplace data from DataForSEO Merchant API. Trigger phrases include "ecommerce SEO", "product SEO", "Google Shopping", "marketplace SEO", "product schema", "Amazon SEO", "product listings", "shopping ads", "merchant SEO", "product feed".
---

# seo-ecommerce — e-commerce SEO

E-commerce SEO is different — product schema matters more, marketplaces matter, pricing visibility matters, and inventory dynamics matter. This wrench covers what classic SEO misses.

---

## When to fire

- E-commerce site detected during audit
- "Product SEO" / "Google Shopping"
- "Amazon SEO" / "marketplace optimization"
- "Product schema audit"

Don't fire when:
- Non-ecommerce site (no products)
- Just classic SEO needed (use other wrenches)

---

## Dimensions

| Dimension | What |
|---|---|
| **Product schema** | Product, Offer, AggregateRating, Review JSON-LD per product page |
| **Product feed** | Google Merchant Center feed quality, attributes coverage |
| **Google Shopping** | Visibility per product, competitor pricing, image quality |
| **Amazon listings** | Title structure, bullets, A+ content, keywords (if the user sells on Amazon) |
| **Pricing visibility** | Are prices visible to bots? On-page + schema? |
| **Inventory signals** | Out-of-stock handling (canonical / noindex / redirect?) |
| **Faceted navigation** | Filter URLs handled correctly (crawl budget) |
| **Category vs product pages** | Both optimized for their tier of keyword |
| **Reviews + ratings** | UGC schema-marked + visible |

---

## Product schema completeness

For each product page, check:

```jsonc
{
  "@type": "Product",
  "name": "...",                          // required
  "image": ["..."],                       // required
  "description": "...",                   // recommended
  "sku": "...",                           // recommended
  "brand": { "@type": "Brand", "name": "..." },
  "offers": {
    "@type": "Offer",
    "price": "29.99",                     // required for shopping
    "priceCurrency": "USD",               // required
    "availability": "InStock",            // required
    "url": "..."                          // recommended
  },
  "aggregateRating": {                    // if ratings exist
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "127"
  }
}
```

Flag missing fields per Google's product rich result requirements.

---

## Marketplace intelligence (DataForSEO conditional)

If DataForSEO Merchant API wired:

- Top competitor products for each of your keywords
- Pricing distribution (are you 20% above / below median?)
- Amazon ranking position for parallel SKUs
- Shopping ad coverage

---

## See also

- [SKILL.md](../SKILL.md)
- [schema.md](schema.md) — Product schema deep dive
- [dataforseo.md](dataforseo.md) — Merchant API
- [competitor-pages.md](competitor-pages.md) — "X vs Y" pages targeting comparison keywords
