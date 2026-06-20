---
name: website
description: "Wrench inside the `build` mechanic. Full website builder using the DRIP framework (Design → Refine → Integrate → Publish). Routes through Stitch (vibe design + reference images), the `awesome-design` brand library (68 brand DNA references), 21st.dev / CodePen for component sourcing, ending in production HTML variants. Phase 0 intake auto-fires when target is ambiguous. Default routing: code authorship → Codex via router (Claude steps in on documented carve-outs). Fires on \"build a website\", \"make a landing page\", \"create a site for\", \"design a page\", \"do the front end\", \"redo the design\", \"polish the UI\" — anything that wants a new web surface stood up."
---

# website — full website builder (DRIP)

The website pathway for the build mechanic. Stands up a complete web surface from concept to production HTML, coordinating with `design-studio` for visual work and `router` for code writing. Phase 0 always asks the questions worth asking before any pixel renders.

**Default: Codex writes the HTML / CSS / JS code; Claude composes the spec.** Per the build mechanic's routing-defaults, code goes through `router` → Codex by default. Claude can step in for the code when Codex is down, the work is small + well-understood, or the user explicitly says "just do it" (per `[[Actions/routing-defaults]]`). This wrench composes the design + structure + content spec regardless of who writes.

---

## The DRIP framework

Four phases. Each ends with a clear handoff or user-gate.

### Phase 0 — Intake (auto-fires when target is unclear)

Before any design or code, get the brief right. Quick interview, not a wizard. Stop after answers are clear.

Ask in one pass (use one structured question, not five sequential):

- **Who's the user?** (the actual person who arrives at the URL)
- **What's the one job the page does?** (sign up, read, buy, contact, etc.)
- **What's the brand vibe?** (pick from `awesome-design` library: Apple-clean / Stripe-business / Anthropic-serious / Lamborghini-bold / Claude-warm / custom-from-URL / no-strong-preference)
- **Tech constraints?** (static HTML / Next.js / SvelteKit / WordPress / framework-locked-in / open)
- **Where does it deploy?** (Vercel / Netlify / Cloudflare Pages / self-hosted / TBD)

If the user already brain-dumped enough context, skip the Q's he answered. Default scope: a single landing page or small marketing site. If the answer to "what's the one job" is multiple jobs, escalate to `project-orchestrator`.

### Phase 1 — Design (the D)

Design comes first. Three paths in priority order:

**Path A: Brand reference from `awesome-design` library**
The library is seed-on-demand: brand identities are codified as markdown design systems at `_system/skills/design-studio/awesome-design-library/<slug>.md`, but only `phoenix-web-ai.md` is seeded today (Apple/Stripe/Claude/etc. are generated on first request, not pre-stocked). If the user's brand-vibe answer maps to an already-seeded brand, load that file as the design source of truth; otherwise generate it via Path B and save it to the library for next time. Always check the dir before assuming a brand file exists.

**Path B: Extract brand DNA from a reference URL via Firecrawl + `awesome-design` skill**
If the user pastes a URL ("I want it to feel like example.com"), use Firecrawl's branding format:
```
formats: ["branding", "screenshot", "rawHtml", "links"]
```
The `branding` format returns structured JSON with colors, fonts, typography, components, logo, personality. Save as `brand-style.md`.

**Path C: Vibe-design via Stitch (Google Stitch)**
For greenfield design exploration when no brand reference exists, fire the `stitch` wrench (lives under `design-studio`):
1. Collect 3-5 reference images from godly.website / dribbble
2. Stitch generates multiple UI variants
3. The user picks the direction
4. Download the ZIP (includes DESIGN.md + HTML)

This is the design-studio mechanic's specialty — hand off there if Phase 1 needs deep exploration.

**Output of Phase 1:** `DESIGN.md` at the project root capturing the chosen brand DNA, color tokens, typography, component conventions, layout grid. This is the design source of truth all later phases reference.

### Phase 2 — Refine (the R)

With the design system locked, refine the page structure:

- **Page sections** — hero, value props, social proof, CTA, footer (or whatever the page actually needs based on Phase 0's "one job")
- **Component picks** — for each section, source from 21st.dev + CodePen for tested patterns. Don't reinvent navbars / footers / CTAs.
- **Copy direction** — headline, sub-headline, CTAs. Pull `content-forge → marketing` if copy needs to be platform-grade ad copy.
- **Interaction sketch** — what hovers / clicks / scrolls. Keep simple unless the user asks for animation.

The user sees the refined plan as a tight one-pager and approves before code work starts. Iteration here is cheap; iteration in Phase 3 is expensive.

### Phase 3 — Integrate (the I)

Now the HTML gets written. Default routing: Claude composes the per-file spec, dispatches via `router → codex`. Claude can author directly when Codex is down OR the work is small + well-understood OR the user says "just do it" — same carve-outs as the routing-defaults. The spec includes:

- The relevant `DESIGN.md` section (colors, fonts, components for this surface)
- The Phase 2 plan (page sections, component picks, copy)
- File-level constraints (one HTML file? Next.js app? component-per-file?)
- Output contract (semantic HTML, no inline styles, Tailwind tokens from the design system, mobile-first responsive, accessibility baseline)

For a single landing page, this is one Codex dispatch returning the full HTML. For a multi-page site, this is N dispatches (one per page) all referencing the same `DESIGN.md`. For a Next.js app, multiple component files dispatched in dependency order.

**Multi-file builds:** if the page count is > 5 or component count > 15, route the SCOPING through Gemini first (Gemini reads + outputs the file structure as prose), then Codex writes per-file. Gemini does NOT write code per the router's no-Gemini-code rule.

### Phase 4 — Publish (the P)

The build is done. Hand off to `ship`:

```
website build complete (DRIP).
Project at: <path>
Self-sufficient runtime: confirmed (boots with `npm run dev` / opens in browser)
Files touched: <list>
DESIGN.md at: <path>

Ready for ship?
```

Ship runs the standard pipeline: commit → review → tests → PR → deploy → canary → pay-for-this verdict.

---

## When to escalate to `project-orchestrator`

This wrench handles single websites and small marketing sites well. Escalate when:
- The "one job" answer is actually 3+ jobs across multiple personas
- The scope includes a backend, an auth flow, AND a frontend (all three together)
- The user wants the full build from "brain dump" to "deployed and tested" in one prompt
- Multi-week or multi-developer work

The orchestrator pulls in plan-room → build → design-studio → ship → second-brain in sequence. The website wrench is then one tool the orchestrator calls.

---

## When to escalate to `design-studio`

This wrench has a design Phase 1, but design-studio is the design mechanic. Escalate when:
- The design exploration itself is the work (the user wants 5 different visual directions explored)
- The design system needs to be established for an entire brand, not just one page
- Polish on an existing live site is the goal (`design-studio → design-review` wrench)

The website wrench's Phase 1 is "pick a direction"; design-studio is "explore directions deeply".

---

## What this wrench does NOT do

- **Does not write HTML by default.** Codex via router does (per [[Actions/routing-defaults]]). Claude steps in only on the documented carve-outs.
- **Does not deploy.** Ship does. (Phase 4 hands off.)
- **Does not handle auth flows.** Fire `onboarding-guard` wrench before writing redirect logic.
- **Does not build mobile apps.** Mobile wrench exists for that, native-runtime targets (NOT webview-in-a-shell).
- **Does not handle backends.** Backend wrench for that, with cso inline.
- **Does not run QA loops automatically.** Hand off to `codex-goal-dispatcher` with the `comprehensive_user_testing` template for that.

---

## See also

- [../SKILL.md](../SKILL.md) — build mechanic (cardinal rules + cross-mechanic dependencies)
- [onboarding-guard.md](onboarding-guard.md) — fires before any redirect logic in the new site
- [../../design-studio/SKILL.md](../../design-studio/SKILL.md) — for deep design exploration in Phase 1
- [../../router/wrenches/codex.md](../../router/wrenches/codex.md) — Codex dispatch for Phase 3 code writing
- [../../router/wrenches/gemini.md](../../router/wrenches/gemini.md) — multi-file scoping for large builds
- [../../ship/SKILL.md](../../ship/SKILL.md) — Phase 4 handoff
