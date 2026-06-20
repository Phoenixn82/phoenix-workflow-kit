---
name: backend
description: "Wrench inside the `build` mechanic. Backend / API / server scaffold with `cso` running INLINE during build, not after. Stack detection (Node/Express, Python/FastAPI, Go, Rust, Bun). Auth pattern selection. Secrets policy. DB choice. MCP integration via `printing-press-router` for external services. Default routing: code writing → Codex via router (Claude steps in on documented carve-outs). Cardinal: bolted-on security is broken security. Fires on \"build a backend\", \"build the API\", \"scaffold a server\", \"build a service\", \"design the endpoints\", \"add a backend to this\", \"make a serverless function\"."
---

# backend — backend builder with cso inline

The backend pathway for the build mechanic. Scaffolds a real backend / API / service with security review running ALONGSIDE the build, not as a post-hoc audit. Stack-agnostic (picks the right runtime per project), opinionated about security defaults.

**Cardinal: cso runs inline.** Every major scaffold step (auth, secrets, input handling, DB queries, external API calls) gets reviewed before the next step starts. Bolted-on security is broken security — by the time the build is "done", security holes are baked in and expensive to refactor out.

**Default: Codex writes the code; Claude composes the spec.** Per `[[Actions/routing-defaults]]` Codex is the default code lane; Claude steps in when Codex is down, the work is small + well-understood, or the user says "just do it". Multi-file backends route through Gemini for scoping + Codex for per-file writes (Gemini does NOT write to code files).

---

## Stack defaults

The decision tree, in order:

```
Existing codebase / team already on a stack?
  → Match the existing stack. Don't introduce new infra without reason.

Greenfield, the user has a preference?
  → Use the user's preference. Ask once.

Greenfield, no preference, project type signals?
  → Quick prototype / scripting / data work → Python + FastAPI
  → Web SaaS backend, JS-team-friendly → TypeScript + Fastify (or Hono for edge)
  → High-throughput service, performance critical → Go + Chi/Echo
  → Systems-level / strict types / cross-platform binary → Rust + Axum
  → Edge / serverless-first → Bun + Hono (or Vercel Functions if Vercel-deployed)

Always: TypeScript over JavaScript. Kotlin over Java. Rust > C++ for new systems work.
```

### Stack-specific defaults

| Stack | Framework | ORM/DB | Auth | Validation | Testing |
|---|---|---|---|---|---|
| **Python** | FastAPI | SQLAlchemy 2.0 / SQLModel (or Drizzle-style raw SQL) | python-jose for JWT, Clerk/Auth0 for OAuth | Pydantic | pytest + httpx |
| **TypeScript** | Fastify / Hono | Drizzle ORM (preferred) / Prisma | Better-Auth (preferred) / Clerk / Auth0 | Zod | Vitest + supertest |
| **Go** | Chi / Echo | sqlc + raw SQL | golang-jwt + Clerk JWKS | go-playground/validator | testing + httptest |
| **Rust** | Axum | sqlx (compile-checked) | jsonwebtoken + custom claims | validator | built-in + reqwest |
| **Bun (edge)** | Hono | Drizzle | Clerk / Better-Auth | Zod | bun:test |

Database default: **PostgreSQL** unless the user specifies otherwise (Supabase if Vercel-deployed, plain Postgres if self-hosted, Neon for serverless). SQLite for embedded / single-process services.

---

## Phase flow (each phase has a cso checkpoint)

### Phase 0 — Intake

- **What does this backend do?** (one sentence)
- **Who uses it?** (frontend app, mobile app, other services, external clients)
- **Auth model:** anonymous / users / users + admin / B2B with orgs
- **Data shape:** rough entity list + relationships
- **External integrations:** payments / email / SMS / 3rd-party APIs (each triggers `printing-press-router` for tier check)
- **Deployment target:** Vercel / Render / Fly.io / AWS / self-hosted
- **Scale signal:** prototype / < 1000 users / 1k-100k / 100k+

### Phase 1 — Architecture spec

Lay out the architecture as PROSE before code:
- Runtime + framework (per stack defaults)
- Entity model (tables + relationships, in dbdiagram syntax)
- API surface (route list + HTTP methods + auth requirements per route)
- Auth flow (token format, session storage, refresh strategy)
- Secrets policy (which secrets go where: env vars vs secrets manager vs config)
- External integration list (each one via `printing-press-router` CLI > API > MCP)
- Deployment topology (single service vs split, edge vs region vs serverless)

**Cso checkpoint #1:** review the architecture spec for security at the design level — input boundaries, authorization model, data exposure, secrets handling. Fix issues at the spec level before any code starts. (Cheap; later it's expensive.)

### Phase 2 — Scoping (multi-file via Gemini)

For non-trivial backends (> 10 routes or > 5 entities), route scoping through Gemini:
- File-by-file structure (paths + purpose)
- Migration files (one per entity, in dependency order)
- Shared types / interfaces / Pydantic models
- Per-file change spec as PROSE

Gemini does NOT write code. Codex writes per-file from the spec.

### Phase 3 — Implementation (Codex, with cso inline)

Dispatch Codex per file in dependency order:

1. **Database schema + migrations first** — entities + indexes + constraints
   - **Cso checkpoint #2:** review the schema for sensitive-field handling (PII flagged for column-level encryption, indexes don't leak data via timing, FKs prevent orphans)
2. **Auth middleware + session handling next** — before any route depends on it
   - **Cso checkpoint #3:** review auth for JWT secret rotation, session fixation, CSRF tokens (if cookie-based), brute-force rate limiting
3. **Each route handler** — dispatched one at a time, each with its validation schema + auth requirements
   - **Cso checkpoint per critical route:** review for SQL injection (parameterised? always), authorization checks (does this route's auth match the architecture spec?), input validation (does Zod/Pydantic actually cover the surface?), error handling (do errors leak internals?)
4. **External integration wrappers last** — `printing-press-router` confirms the tier ladder for each
   - **Cso checkpoint #4:** review external calls for secret leakage in URLs, request signing, rate-limit handling, retry-with-backoff
5. **Tests** — written alongside or via `codex-goal-dispatcher` with the `test_coverage_lift` template

Each Codex dispatch includes:
- File path
- Stack + framework
- Imports + types
- Function/endpoint contract (inputs, outputs, errors)
- Auth requirements
- Output contract (idiomatic, follows the stack defaults, no `any` types in TS, no `Optional[Any]` in Python without justification)

### Phase 4 — End-to-end test

After all files are written:
- Boot the service locally
- Hit the routes via `curl` or `httpie` (one happy path per route)
- Run the test suite
- Run a basic load test on critical endpoints (`oha` — Windows-friendly; install with `cargo install oha` or `winget install oha` if missing)

Failures → diagnose (often a missing migration, env var, or auth wiring) → dispatch Codex to fix.

### Phase 5 — Cso final review

Before ship handoff, `cso` runs the comprehensive backend review:
- All OWASP Top 10 + STRIDE threat model items
- Secrets archaeology (no secrets in code, in commits, in logs)
- Dependency supply chain (every dep version pinned, no known CVEs)
- CI/CD pipeline security (if the project has GitHub Actions / similar)
- LLM trust boundaries (if any user input flows into LLM calls)

If cso surfaces a HIGH severity issue here, fix before ship. MEDIUM/LOW → log and ship.

### Phase 6 — Hand off to ship

```
backend build complete.
Stack: <runtime + framework>
Project at: <path>
Cso reviews: 4 inline + 1 final → <PASS / N issues to fix before ship>
External integrations: <list> (each via printing-press-router)
Boots: confirmed (local)
End-to-end happy path: passed

Ready for ship?
```

Ship runs the standard pipeline: commit → review → tests → PR → deploy → canary → pay-for-this verdict.

---

## When to escalate

- **Frontend needed too** → run frontend build (website / mobile wrench) in parallel
- **Multi-service architecture** (microservices, queue workers, schedulers) → `project-orchestrator` for coordination
- **Compliance / regulated industry** (HIPAA, PCI, SOC2) → escalate scope to the user; this wrench does standard security inline but doesn't claim compliance certification

---

## What this wrench does NOT do

- **Does not write code by default.** Codex via router does (per [[Actions/routing-defaults]]). Claude steps in only on the documented carve-outs.
- **Does not deploy.** Ship does.
- **Does not configure cloud infrastructure.** That's IaC work (Terraform / Pulumi / SST) — fires a separate Codex dispatch with the architecture spec as input.
- **Does not run cso AFTER the build.** Cso runs INLINE at each major step. Final cso review is a confirmation, not the only review.
- **Does not skip MCP/CLI tier check** when integrating an external service. `printing-press-router` is mandatory before any new integration.

---

## See also

- [../SKILL.md](../SKILL.md) — build mechanic
- [../../cso/SKILL.md](../../cso/SKILL.md) — security standalone keeper, runs at checkpoints
- [../../printing-press-router/SKILL.md](../../printing-press-router/SKILL.md) — standalone keeper, tier check for external integrations
- [../../router/wrenches/codex.md](../../router/wrenches/codex.md) — Codex dispatch for code writing
- [../../router/wrenches/codex-goal.md](../../router/wrenches/codex-goal.md) — for test coverage lift via `/goal`
- [../../ship/SKILL.md](../../ship/SKILL.md) — terminus
