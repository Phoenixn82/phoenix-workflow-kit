# Brand DNA — Acme Web & AI

> Seeded 2026-06-05 as the first entry in the awesome-design library. Project: Acme Web & AI
> (Springfield web design + AI automation + SEO studio). Use this as the DESIGN.md source for
> `design-html`, the prompt source for `stitch`, and the rubric for `design-review`.

## The one-line aesthetic
**A warm regional foundry where bleeding-edge AI is forged.** Friendly enough to call on a Tuesday,
sharp enough to trust with your whole business. Every screen must hold *both* at once — drop the
warmth and it's cold enterprise; drop the polish and it's forgettable. The brand
*is* the AND.

## What it is / what it is NOT
- IS: warm, hand-made-feeling, confident, local-proud, alive with controlled fire, premium.
- IS NOT: corporate-blue SaaS, purple-gradient-on-white AI slop, stock-photo agency, cold minimal
  tech, clip-art mascots, generic Tailwind cards on white. **If it looks like every other AI
  landing page, it's wrong.**

## Color — the fire system
Refined from the "fire" exploration. Warm-dominant, with deep espresso for gravity and a single
disciplined hot accent.

| Token | Hex | Role |
|---|---|---|
| `--cream` | `#FBF1E2` | primary light background (warmth, the "front porch") |
| `--espresso` | `#1A1110` | primary text on light / dark sections (gravity, polish) |
| `--ember` | `#D7341E` | primary brand red — CTAs, key marks |
| `--sunset` | `#FF6A1A` | secondary orange — energy, highlights, gradients |
| `--amber` | `#FFB02E` | tertiary gold — accents, glow, small details |
| `--mesquite` | `#6B3A1E` | deep warm brown — grounding, borders, eyebrows |
| `--bone` | `#EDE3D4` | warm off-white for cards on dark |

- **Fire gradient** (`--ember → --sunset → --amber`, ~115°) reserved for hero moments, the logo,
  and a *single* primary CTA per view. Never wallpaper it.
- Warmth dominates (cream + espresso carry 80% of surface); fire is the sharp 20% accent.
- Dark sections use `--espresso` base with ember glow, not pure black.

## Typography
- **Display / headlines:** `Fraunces` (variable, opsz high, wght 500–600) — warm editorial serif
  with real character. Carries the "craftsman" + premium read.
- **Body / UI:** `Bricolage Grotesque` (wght 300–700) — warm humanist sans, distinctive, friendly.
- **Technical / eyebrows / data:** `JetBrains Mono` — the "engineering / AI under the hood" signal.
  Used small, uppercase, letter-spaced, often in `--ember`/`--amber` (e.g. `// Springfield · WEB · AI · SEO`).
- Never Inter/Roboto/Arial/system as a primary. Big, confident headline scale; generous leading on body.

## Layout & space
- Generous negative space on light; controlled density on dark proof sections.
- Max content width ~1180px. Asymmetry welcome — offset eyebrows, section numbers (`01`, `02`)
  in mono, headings that break the grid slightly.
- Rounded-but-not-pill cards (16–20px radius). Warm hairline borders (`#ffffff14` on dark,
  `--mesquite` at low alpha on light). Soft, warm-toned shadows — never cold gray drop-shadows.

## Motion
- Purposeful, warm, never twitchy. One orchestrated hero load (staggered fade-up).
- Scroll-reveal on sections (but content must be visible without JS — progressive enhancement).
- Hover: gentle lift + warm ember glow on interactive cards. Motion should "animate proof," not decorate.
- Respect `prefers-reduced-motion`.

## Signature elements (the memorable bits)
- The **rising phoenix** mark + **fire gradient** used sparingly and with intent.
- **Mono eyebrows** in fire color as section/label system.
- A **"watch the AI work"** live surface — the brand shows working AI, doesn't claim it.
- **Blaze** the mascot (friendly firebird / baseball-mascot energy) as the chatbot face — warmth made literal.

## Voice (for any copy in the UI)
Warm, plain, specific, confident-by-proof, owner-respecting. A sharp Springfield craftsman wrote it.
No "delve / unlock / elevate / in today's fast-paced world," no tricolon-on-every-line, varied
sentence length. Always pair a substance line with a warmth line.

## Pattern library (landing)
Hero (fire + live-AI spark) → problem/agitate (in the owner's words) → 3 headline services
(web / SEO+GEO / automation) → live AI demo (the proof) → portfolio proof → local Springfield trust →
process → FAQ → strong single CTA (`Get My Free Springfield Visibility Snapshot`).

## Reference moodboard (for Stitch / image gen)
Warm foundry / blacksmith glow · the region golden-hour · Anthropic-grade warmth + restraint ·
Stripe-grade polish & live proof · Linear-grade modern edge · a friendly modern firebird mascot
(NOT clip-art) · molten metal & ember textures over deep espresso.

---
*This is the project's design source of truth. Update via design-consultation as the brand locks.*
