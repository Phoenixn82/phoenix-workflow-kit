---
name: rag-architect
description: Wrench inside the `build` mechanic. Designs the optimal RAG (Retrieval-Augmented Generation) system for a project's data. Analyses data structure, format, relationships, and scale to pick the right RAG type (Naive / Advanced / Modular-Agentic / Graph), then delivers an implementation plan + starter scaffold. Stack-aware — recommends what fits the user's existing infra (Supabase pgvector, Pinecone, etc.) rather than introducing new tools. Fires on "RAG", "vector search", "semantic search", "chat with my docs / data", "knowledge base for an LLM", "embedding pipeline", "chunking strategy", "retrieval quality". **For project data, NOT the user's personal vault** — vault RAG is `second-brain`'s job.
---

# rag-architect — RAG architecture design

Architectures matter. The same data with the same LLM gets dramatically different retrieval quality depending on chunk strategy, retrieval method, and whether the data is naturally relational. This wrench picks the right RAG type for the actual data and writes the scaffold.

**Scope:** project-level RAG (the user building a "chat with their docs" feature for a client / their own product / a SaaS). NOT the user's personal knowledge vault — that's `second-brain`'s domain.

**Code writing:** Default routing is Codex via router for the scaffold (per `[[Actions/routing-defaults]]`). Claude can step in when Codex is down, the work is small + well-understood, or the user says "just do it". This wrench composes the spec + the SQL + the API call structures regardless of who implements.

---

## The 4 RAG types

Each type fits a specific data shape. Picking the wrong type wastes weeks rebuilding later.

### 1. Naive RAG

**When:** Simple, well-structured, single-source data. Uniform document types. Straightforward lookup queries.
**What it is:** Chunk documents → embed → store in vector DB → retrieve top-k → generate answer.
**Example fit:** Company FAQ. Product documentation. A single textbook. Support article archive.
**Why simpler:** No query analysis, no hybrid search, no reranking. Just embed-and-fetch.

### 2. Advanced RAG

**When:** Data mixes semantic content with exact-match identifiers (SKU codes, product IDs, ticket numbers). Queries blend natural language with specific codes or structured filters (price ranges, categories). Or messy/diverse data where naive retrieval consistently misses things.
**What it is:** Naive RAG **plus** hybrid search (vector + BM25 keyword), query analysis (detecting exact-match patterns, extracting structured filters), and reranking. For exact-match fields, route directly to lookup instead of embedding.
**Example fit:** Product catalogue where queries mix "waterproof hiking boots under £80" with "SKU-4421". Support ticket archive with inconsistent formatting.
**Performance tip:** Cache deterministic lookups (SKU/ID queries always return the same result) — high-impact, low-effort optimisation.

### 3. Modular / Agentic RAG

**When:** Complex multi-source setups where each source has different structure, update frequency, and retrieval characteristics. The query itself might need decomposing. Multiple indexes or data types that require routing.
**What it is:** Orchestration layer with a query router that directs queries to the right index, decomposes multi-part questions, retrieves from multiple sources in parallel, fuses results with source-diversity enforcement, reranks before generation.
**Key distinction from Advanced:** Modular uses **separate indexes per source with independent retrieval pipelines** — not a single unified index with metadata filtering. Enables per-source chunking, retrieval tuning, and update schedules.
**Example fit:** Enterprise knowledge base spanning Notion, Confluence, Slack, and a SQL database.

**Data sync strategy (first-class design decision):**
- **Notion:** Poll `last_edited_time` nightly; re-ingest changed pages only
- **Databases:** Trigger re-embedding on row update via DB webhooks or CDC
- **Static files (PDFs):** Re-ingest on upload; version-track by file hash

Stale data in one source can silently degrade the whole system — sync isn't optional.

### 4. Graph RAG

**When:** Highly relational data where entity relationships matter as much as the content. Questions involve traversing connections ("who worked with whom on what project?", "find all cases citing case X").
**What it is:** Knowledge graph layer (entities + relationships) on top of vector search. Three components:
1. **Entity extraction** — identify entities and relationships during ingestion
2. **Graph construction** — store in a graph DB (Neo4j; or Apache AGE on PostgreSQL if staying on Supabase)
3. **Query classifier** — route queries into 3 modes: graph-only (relationship traversal), vector-only (semantic), or hybrid (both)

The query classifier is a NAMED architectural component, not an afterthought — it determines whether to generate Cypher, run vector search, or merge both.

**Example fit:** Legal case databases with citations. Organisational data. Biomedical literature.

**Bootstrap strategy:** Seed the graph with the most-connected entities first (most-cited cases, most-referenced people). Establishes the relationship backbone early; makes subsequent entity resolution more accurate.

**Production risks to address:**
- LLM-generated Cypher can be syntactically invalid → wrap in try/catch with vector-search fallback
- Entity extraction is imperfect → plan for manual review of high-value entities
- For sensitive domains (legal, medical), document confidence level of extracted relationships

---

## Workflow

### Phase 1 — Understand the data

Quick signals capture, not a wall-of-questions interview:

- What data? (docs / databases / code / transcripts / mixed)
- How much? (rough doc / row / file count)
- What kinds of questions will users ask?
- Current stack? (default: Next.js + Supabase + Claude API)

If the user shares actual files or schemas, analyse for:
- **Text length distributions** — short uniform vs long-form (determines chunk strategy)
- **Relationships** — cross-references, FKs, entity mentions (high interconnectedness → Graph RAG)
- **Cardinality** — ID/categorical vs free-text (only free-text benefits from embedding; categorical → metadata filter)
- **Scale** — small (<1K docs), medium (1K-100K), large (100K+) (affects vector DB choice)
- **Query patterns** — semantic intent vs exact lookups (SKU codes, IDs) (signals hybrid search)

Keep concise. Capture the signals that matter for type selection; the value is in the recommendation, not the analysis writeup.

### Phase 2 — Pick the type, justify it

Recommend ONE of the 4 types. The justification must include:
1. **Which type** and why it fits the user's specific data
2. **What would go wrong** with the simpler tier
3. **Trade-offs** — what the recommended approach costs in complexity

Don't recommend Graph RAG for a simple FAQ. Don't recommend Naive RAG when queries mix SKUs and natural language. Scale complexity to the problem.

### Phase 3 — Implementation plan

Concrete, not generic:

**Chunking strategy:**
- Method + chunk size with reasoning (not arbitrary — explain why 800 vs 1500 tokens based on the data's length distribution)
- Overlap strategy
- Justify top-k values: "top-20 candidates before reranking gives enough diversity for reranking to meaningfully reorder, while keeping latency under 200ms at this scale. Tune down for latency, up for recall."

**Embedding model:**
- Default: OpenAI `text-embedding-3-small` unless reason to go elsewhere
- Mention dimension trade-offs if relevant

**Vector database:**
- Default: Supabase pgvector if already on Supabase (zero new infra), Pinecone otherwise
- Adapt to the user's stated stack immediately
- Justify based on scale, filtering needs, operational complexity

**Retrieval method:**
- Naive: top-k similarity
- Advanced: hybrid search + reranking + query preprocessing + exact-match routing
- Modular: per-source retrieval + routing + parallel execution + result fusion with source diversity
- Graph: query classification → graph traversal / vector search / both → result merging

**Generation:**
- Prompt structure for the final LLM call
- How to format retrieved context with source attribution
- Citation approach

### Phase 4 — Starter scaffold

Generate a real mini-project structure:

```
/rag-setup
  ingest.ts       # Chunking, embedding, upserting to vector DB
  query.ts        # Retrieval + generation pipeline
  config.ts       # Model, DB connection, chunk size, all settings
  README.md       # Run order and setup
```

**Code guidelines for Codex dispatch:**
- Default stack: TypeScript, plain API calls (no LangChain unless asked), Supabase pgvector or Pinecone
- Use official SDKs (`openai`, `@anthropic-ai/sdk`, `@supabase/supabase-js`) — not raw `fetch()`
- Real error handling for API + DB ops
- Env vars for keys + connection strings
- Inline comments only where logic isn't obvious

If the user's stack differs (Python, LlamaIndex, n8n), adapt the scaffold.

**Scaffold completeness — non-negotiable:**

1. **Complete SQL migrations in `config.ts`** — every table, index, RPC function, extension required. The user copy-pastes into Supabase SQL Editor and has a working DB. For multi-source architectures, separate tables + match functions per source.
2. **No stub implementations** — every source mentioned in the recommendation has functional ingestion + query code. External APIs (Notion, Confluence) have real endpoint URLs, headers, response parsing. Mark TODO values inline but surrounding code is runnable.
3. **README is a complete setup guide** — exact `npm install`, every env var, step-by-step DB setup, ingestion command, test query command. Top-to-bottom following the README produces a working system.

### Phase 5 — Build companion (optional)

After the recommendation + scaffold, ask:

> "Want me to help build and test this pipeline against your real data?"

If yes, shift into build mode:
- Wire ingest against real data
- Run test queries + evaluate retrieval quality
- Debug common issues (poor chunk boundaries, missing context, irrelevant results)
- Tune chunk size, overlap, top-k, reranking thresholds based on actual results
- Iterate until retrieval is solid

---

## Stack awareness (critical)

Default recommendation stack:
- **Vector DB:** Supabase pgvector (if on Supabase) OR Pinecone
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Generation:** Claude API
- **Language:** TypeScript
- **No frameworks** by default — plain API calls over LangChain / LlamaIndex

**Critical:** if the user mentions a stack (Supabase, Vercel, Python, n8n), the recommendation MUST use it. Don't introduce new infrastructure when the right tools already exist. A user on Supabase should get pgvector, NOT a recommendation to spin up Qdrant. A user on Python should get a Python scaffold, NOT TypeScript.

Generic recommendations that ignore existing infrastructure are actively unhelpful.

---

## What makes a good recommendation

- References specific characteristics of the user's actual data
- Explains why alternatives were ruled out, not just why the winner was chosen
- Acknowledges trade-offs honestly rather than overselling
- Scales complexity to the problem — don't recommend Graph RAG for a simple FAQ
- Justifies magic numbers (chunk sizes, top-k, candidate counts) with reasoning the user can use to tune later

---

## What this wrench does NOT do

- **Does not RAG the user's personal vault.** That's `second-brain`'s job.
- **Does not write the scaffold code by default.** Codex via router does (per [[Actions/routing-defaults]]). Claude steps in only on the documented carve-outs.
- **Does not handle data ingestion at runtime.** The scaffold sets up the pipeline; running it is the project's own concern after handoff to `ship`.
- **Does not pick LangChain / LlamaIndex by default.** Plain SDKs unless the user specifically asks for a framework.

---

## See also

- [../SKILL.md](../SKILL.md) — build mechanic
- [../../second-brain/SKILL.md](../../second-brain/SKILL.md) — for the user's personal vault (different scope)
- [../../router/wrenches/codex.md](../../router/wrenches/codex.md) — Codex dispatch for scaffold code
- [../../printing-press-router/SKILL.md](../../printing-press-router/SKILL.md) — fires when the RAG pipeline integrates a 3rd-party service (Notion, Confluence, Slack APIs)
- [../../ship/SKILL.md](../../ship/SKILL.md) — terminus after build companion
