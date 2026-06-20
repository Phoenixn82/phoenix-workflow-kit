---
name: web-scrape-agent
description: Schema-driven structured JSON extraction wrench. AI-navigates complex sites and returns typed data matching a schema. Use when the ask is "extract all products as JSON", "get pricing tiers from this page", "pull every entry from this directory", "extract structured data with this schema", or anything where the deliverable is structured records not markdown. Handles multi-page navigation, pagination, and complex DOM structures automatically.
---

# web-scrape-agent — schema-driven structured extraction

When markdown isn't the right output shape — when the user wants typed records, not prose — this wrench is the tool. Define a schema, point at a URL, get JSON back. The agent navigates pagination, follows detail links, and resolves the schema across multiple pages without scripting each step.

This is the most powerful wrench in web-scrape, and the right one for catalog / directory / pricing / matrix / table-shaped data.

---

## When to fire

- "Extract all products from \<catalog URL\> as JSON with fields name, price, sku, image, description"
- "Pull every entry from this directory"
- "Get pricing tiers from \<site\>"
- "Build a feature matrix comparing X across these competitors"
- "Extract the full schedule from \<event site\>"
- "Get every job listing from this board with company / role / location / link"
- "Crawl this docs site and return each page as { title, slug, content, frontmatter }"

Don't fire when:
- The output is prose, not structured records → use `scrape` or `crawl`
- It's a single page with a single table — a `scrape --format markdown` plus a Codex parse may be cheaper
- You don't have a schema yet and the data shape is unclear → start with `scrape` to see one page, design the schema, then come back

---

## CLI patterns

```bash
# With inline schema (simple case)
firecrawl agent --url "<url>" --schema '{"products":[{"name":"string","price":"number"}]}'

# With schema file (reusable, version-controlled)
firecrawl agent --url "<url>" --schema schema.json

# With navigation prompt (multi-page extraction)
firecrawl agent --url "<catalog-url>" \
  --schema schema.json \
  --prompt "Click each product card to load its detail page, extract product fields"

# With pagination handling
firecrawl agent --url "<list-url>" \
  --schema schema.json \
  --prompt "Paginate through all pages of results until no Next button is visible"

# Output
firecrawl agent --url "<url>" --schema schema.json --output products.json

# Limit extraction (cost cap)
firecrawl agent --url "<url>" --schema schema.json --max-pages 10
```

The `--prompt` flag is how you tell the agent what to do beyond the schema. Without it, the agent extracts from the seed page only. With it, the agent navigates as instructed.

---

## Schema shape

JSON Schema-flavored, lightweight. Examples:

```jsonc
// One record per call (single page, single record)
{
  "title": "string",
  "publishedAt": "string",
  "author": "string",
  "content": "string"
}

// Array of records (catalog page)
{
  "products": [{
    "name": "string",
    "price": "number",
    "currency": "string",
    "sku": "string",
    "imageUrl": "string",
    "description": "string",
    "inStock": "boolean"
  }]
}

// Nested (entries with sub-entries)
{
  "categories": [{
    "name": "string",
    "products": [{
      "name": "string",
      "price": "number"
    }]
  }]
}
```

For complex schemas with enums, required fields, or constraints, use proper JSON Schema. The agent honors those.

---

## Cost shape

- Substantially more expensive than `scrape` — the agent makes navigation decisions, retries, and reasons over the DOM
- Roughly 3-10× a single `scrape` per page, depending on schema complexity and navigation depth
- `--max-pages` caps the bill; always set it on first-run jobs to avoid surprise
- Compared to "scrape every page + Codex parses with regex": agent wins on JS-rendered / inconsistent / paginated sites; loses on simple uniform HTML where regex is fine

---

## When agent beats scrape + parse

| Site shape | Better tool |
|---|---|
| Catalog with paginated grid, each item has a detail page | **agent** (handles pagination + detail-page navigation) |
| One static table on one page | **scrape + Codex** (cheaper, more deterministic) |
| Directory with consistent card layout, no pagination | **scrape + Codex** (regex is reliable here) |
| Catalog with inconsistent product card layouts | **agent** (handles the inconsistency) |
| Site behind login with structured data | **interact --do "log in" → agent** chained |
| Many sites, same schema (cross-site comparison) | **search + agent per result** with shared schema |

---

## Common failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Returns empty array | Schema doesn't match DOM | Test with `scrape` first to see the markdown; adjust schema field names to match content |
| Returns malformed records | Some fields ambiguous in DOM | Add `--prompt` clarifying how to disambiguate ("price excludes shipping" / "use the on-sale price if shown") |
| Pagination stops early | Pagination signal missed | Make `--prompt` explicit: "Continue paginating until the Next button is disabled or absent" |
| Cost balloons | No `--max-pages` cap and site is huge | Add cap; sample first; reconsider if data is worth it |
| Returns partial schema | Some fields missing on some pages | Mark fields optional in schema; agent will null them gracefully |

---

## Pairing patterns

- **`search` → `agent` per result** with same schema, for cross-site structured extraction (price comparison, feature matrix)
- **`map --search "products"` → `agent` on each URL** for catalog extraction across many product pages
- **`interact --do "log in"` → `agent`** for auth-walled structured data
- **`agent` → save to second-brain as a reference dataset** for recurring competitor / market intel

---

## Schema design tip

Start small. Run agent with 3-5 fields on one page. Verify shape matches expectation. Then expand. Designing a 30-field schema upfront wastes runs because every adjustment is a new agent invocation.

```bash
# Sample run with minimal schema
firecrawl agent --url "<url>" --schema '{"items":[{"name":"string","price":"number"}]}' --max-pages 1

# Inspect output, expand schema, re-run
firecrawl agent --url "<url>" --schema schema-v2.json --max-pages 3

# Production run
firecrawl agent --url "<url>" --schema schema-v2.json
```

---

## See also

- [SKILL.md](../SKILL.md) — mechanic entry (cost ladder, when to escalate)
- [scrape.md](scrape.md) — markdown alternative for single pages
- [crawl.md](crawl.md) — markdown alternative for bulk extraction
- [interact.md](interact.md) — chain when extraction needs login/clicks first
- [search.md](search.md) — chain when sourcing URLs across the web for the same schema
