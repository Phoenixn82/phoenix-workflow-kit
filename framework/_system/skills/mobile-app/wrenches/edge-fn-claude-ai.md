---
name: edge-fn-claude-ai
description: Wrench inside the `mobile-app` mechanic. The Supabase Edge Function -> Claude API pattern for in-app AI features (smart coaching / nudges, AI reflection reports / insights) on a React Native + Expo app — the serverless function reads the DB, calls the Anthropic API server-side, writes results back, and the app reads them and fires a push notification. Keeps the Anthropic key off the client (Edge Function is the secret boundary). Codex is the default code lane for the function + client wiring (AGENTS.md hard rule #5); Claude designs the architecture, the cadence, and the Claude-API prompt. Fires on "add an AI feature to the app", "AI coaching", "AI nudges", "AI insights / reports", "call Claude from the app", "Edge Function for AI", "smart coaching", "reflection summaries".
---

# edge-fn-claude-ai — Supabase Edge Function -> Claude API for in-app AI

The serverless AI loop for an Expo/RN app. A Supabase **Edge Function** turns on for ~1 second on a daily/weekly/monthly cadence, reads the user's data out of Postgres, ships that package plus a designed prompt to the **Claude API**, writes the returned coaching message / report back to a DB table, and the app reads it and fires a push + persistent notification. This is Nick's universal external-integration loop — **app -> server (Edge Function) -> database -> external API (Claude) -> back to app -> notification** — and he reuses it verbatim across the habit tracker, CalTracker, and the next calorie app. Two canonical features ride this wrench: **smart coaching / nudges** and **reflection summaries**.

**Cardinal: the Anthropic key NEVER touches the client.** The Edge Function is the secret boundary. The `ANTHROPIC_API_KEY` lives only as an Edge Function secret server-side. The RN app calls the function (authed as the user); the function calls Claude. If the key would be readable in the bundled app, you have shipped it to every user — see `mobile-security-audit.md`.

**Cardinal: serverless, not always-on.** Use an Edge Function precisely because it fires for ~1 second and turns off. Nick: *"you wouldn't be able to run this anywhere near as cheaply if you had a server that was always on."* An always-on server waiting 24h/day to occasionally call Claude costs far more for the same compute.

**Cardinal: Claude designs, Codex writes.** Claude owns the architecture, the cadence decision (daily/weekly/monthly), the DB-table shape for results, and the **prompt sent to the Claude API** — that prompt is the load-bearing part. Codex (via router) writes the actual `index.ts` of the function and the client call. Per AGENTS.md hard rule #5.

---

## The loop (universal external-integration shape)

Plan every AI integration on this exact loop — Nick draws it as a diagram and feeds the diagram screenshot to Claude Code when implementing:

```
[ RN/Expo app on phone ]
        │  on a daily / weekly / monthly cadence, fires a request
        ▼
[ Supabase Edge Function ]  ← serverless, ~1s on then off
        │  reads the DB
        ▼
[ Postgres ]  habits, completions, challenges, streaks, profiles
        │  function compiles a "package" of that data
        ▼
[ Claude API (Anthropic) ]  package + designed prompt → coaching msg / report
        │  Claude returns text
        ▼
[ Postgres ]  write result back to a results table (e.g. coach_messages)
        │
        ▼
[ RN/Expo app ]  reads the new row
        │
        ▼
[ push notification + persistent notification ]
```

Nick's framing: *"you're always going to have these core features. You're going to have the app, you're going to have the server, you're going to have the database, and then you're going to have whatever API it is that you're reaching out to. In our case, we're just reaching out to Claude API."* The next calorie-tracker app reuses this loop unchanged — so build it clean once.

---

## The two canonical features

Paste BOTH specs into Claude Code in one shot, plus the architecture-diagram screenshot, then voice-transcribe the implementation instruction (see below). Let Claude decide the cadence and the DB architecture.

**1. Smart coaching / nudges** — periodically analyze the streak + consistency data in the DB to push personalized motivational messages or suggest when to adjust goals. Example notification text Nick wants Claude to produce:

> "Hey, you've nailed sleep for 14 days. Congrats, but we're noticing that water intake is low. Here's a quick hack that you could use to improve your water intake."

**2. Reflection summaries** — on a weekly (maybe monthly) basis, AI-generate a report giving deeper context on progress: consistency %, where goals dropped off. Example:

> "You're the most consistent with meditation at 92%, but exercise dropped off midweek. You scored 19% out of your goal of 33% on X Y and Z."

These are inspired by his Whoop band app. The `completions` table (storing `date` + `count` + `habit_id`) is what lets the function reconstruct, months later, which specific habits (by id, e.g. `1177817`) were completed on a given day — that history is the raw material the coaching/report prompt chews on.

---

## Phase flow

### Phase 0 — Prereqs (owned by `supabase-mobile.md`)

The DB, RLS, auth, and tables must already exist. The function reads `habits`, `completions`, `challenges`, `profiles` scoped by `user_id`. If those aren't wired yet, go to `supabase-mobile.md` first. Edge Functions assume that schema.

### Phase 1 — Claude designs (this is the Claude lane)

Decide and write down, as prose the user reviews:

- **Cadence** — daily / weekly / monthly per feature (coaching can be daily, reflection weekly/monthly). Let Claude propose; Nick lets Claude pick.
- **Results table shape** — where the function writes Claude's output so the app can read it. e.g. a `coach_messages` table: `id, user_id, type (coaching|reflection), body, created_at, delivered (bool)`.
- **The Claude-API prompt** — the load-bearing artifact. Nick's prompt-design intent, verbatim:

  > "Hey, here is an example of a coaching message. Your job is to come up with a bunch of coaching messages, go through the user's data and stuff like that, and then do so. Understand that this is going to occur on a daily, weekly, or monthly basis."

  So: give Claude (a) a worked example of the desired output (the sleep/water nudge above), (b) the user's compiled data package, (c) the cadence context. One-shot the example into the prompt so the model matches tone + structure.
- **Model:** Nick's instruction — *"Use pretty smart models. Let's use the Sonnet."* Default to a current Sonnet model id for the coaching/report generation (smart enough for the reasoning, cheap enough for cadence). Fetch the exact current model id via the `claude-api` skill.

### Phase 2 — Codex writes the function + client call (the Codex lane)

The implementation instruction Nick voice-transcribes to Claude Code (adapt for Codex dispatch):

> "I'd like to implement both of these features into our application. I want you to use Claude as the backend and then send the request via Supabase. Use pretty smart models. Let's use the Sonnet."

The Edge Function (Deno, `index.ts`) does four things in order: **read DB -> compile package -> call Claude -> write result back.**

```ts
// supabase/functions/coach/index.ts  — shape, not boilerplate to paste blindly
import { createClient } from "jsr:@supabase/supabase-js@2";
import Anthropic from "npm:@anthropic-ai/sdk";

Deno.serve(async (req) => {
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, // service role: function reads/writes server-side
  );
  const anthropic = new Anthropic({ apiKey: Deno.env.get("ANTHROPIC_API_KEY")! });

  const { user_id } = await req.json();

  // 1. READ — pull this user's streak + consistency data
  // Service-role client BYPASSES RLS — you MUST scope every query to user_id
  // yourself, or you leak other users' data into one user's prompt.
  const { data: habits }      = await supabase.from("habits").select("*").eq("user_id", user_id);
  const habitIds = (habits ?? []).map((h) => h.id);
  const { data: completions } = await supabase.from("completions").select("*").in("habit_id", habitIds);

  // 2. COMPILE — package the data for the model
  const dataPackage = JSON.stringify({ habits, completions });

  // 3. CALL CLAUDE — key stays server-side, never in the app bundle
  const msg = await anthropic.messages.create({
    model: "<current-sonnet-model-id>",      // "use pretty smart models, let's use the Sonnet"
    max_tokens: 1024,
    messages: [{ role: "user", content: `${COACHING_PROMPT}\n\nUser data:\n${dataPackage}` }],
  });
  const body = msg.content[0].type === "text" ? msg.content[0].text : "";

  // 4. WRITE BACK — app reads this row, then fires the notification
  await supabase.from("coach_messages").insert({ user_id, type: "coaching", body });

  return new Response(JSON.stringify({ ok: true }), { headers: { "Content-Type": "application/json" } });
});
```

Set the secret server-side (NEVER in `.env` that ships, NEVER in the RN bundle):

```bash
supabase secrets set ANTHROPIC_API_KEY=sk-ant-...
supabase functions deploy coach
```

(Or use the Supabase MCP `deploy_edge_function` for live deploy.) The RN app's call is a plain authed POST to the function URL — it sends `user_id` (or relies on the auth JWT) and never sees the Anthropic key. The cadence trigger (daily/weekly/monthly) can be a Supabase scheduled `pg_cron` invoke, or the app firing on open; Claude picks per feature.

### Phase 3 — Deliver to the app + notify

App reads new `coach_messages` rows (subscribe via Realtime, or poll on open), then fires a **push notification + persistent notification**. Notification wiring is RN/Expo-side — see `rn-expo-ui.md` / `expo-go-test.md` for the notification + haptics layer.

### Phase 4 — Verify the full chain

Don't trust a UI screenshot. Walk the transformation top-to-bottom (the project's full-stack verification habit):

1. **DB has X** — `coach_messages` row exists for the `user_id` (Supabase MCP `execute_sql` or Table editor).
2. **API computes Y** — Edge Function logs show the Claude call succeeded (Supabase MCP `get_logs`, function logs).
3. **UI renders Z** — the notification text appears on the device.

Then run the mandatory three-device QA loop (below) before calling it done.

---

## Costs

- **Edge Function (serverless) chosen specifically to save money** vs. an always-on server. The function *"turns on very briefly for like 1 second, fires our function and then turns off ... it's more compute efficient and then it saves us a lot of money."* You could not run this anywhere near as cheaply on an always-on box.
- **Model spend** scales with cadence × user count × tokens-per-call. Daily coaching for many users is the cost driver — keep the data package tight and `max_tokens` modest. Sonnet is the deliberate pick: smart enough, not the most expensive.
- For prompt-caching the repeated example/instructions across calls, route the function's Claude integration through the `claude-api` skill (it bakes in caching).

---

## Gotchas

- **The key boundary is the whole point.** `ANTHROPIC_API_KEY` is an Edge Function secret only. If it's importable in the RN app, it's shipped to every user. This is the #1 thing `mobile-security-audit.md` checks.
- **Use the service role key inside the function** (server-side, full DB access), NOT the publishable/anon key — the function acts on the user's behalf after auth, reading rows RLS would otherwise scope.
- **Wire delete-from-DB explicitly.** Nick had Claude set up a line so deleting a habit in the app also deletes the DB row — otherwise the app and DB drift and the coaching package goes stale: *"when you delete it, I want you to delete it from the database as well."*
- **`supabase login` fails non-TTY inside Claude Code's terminal** (you'll see a non-TTY error). Open a fresh terminal, run `supabase login`, copy the printed login link, authenticate in the browser, paste the token back. Auth then shares across all terminal instances on the machine. Tell Claude Code "logged in" so it can deploy/apply.
- **Compile the data package server-side, not on the client** — the function does the DB read so the phone never ships raw data to Claude and the key stays put.
- **Let the cadence be a real trigger.** "Daily/weekly/monthly" must be an actual scheduled invoke (pg_cron) or an on-open check — not a vibe. Claude picks the mechanism per feature.
- **Long token sessions degrade the build.** During a long implementation session, `/compact` at ~250k–300k tokens to recover ~40% context (it takes a while but preserves model quality); `/clear` to reset to 0% for a genuinely discrete task like a separate security pass.

---

## Three-device QA loop (mandatory, every time)

The same non-negotiable loop the rest of the mechanic enforces — the AI feature isn't done until the notification has been seen on a real phone:

1. **Computer / Chrome** — run the app locally (shrink browser to ~150% zoom to simulate a phone). Expect a couple of crashes on first launch — normal; the app self-heals on a few re-runs.
2. **iPhone mirroring** — catch device-rendering issues invisible in Chrome (e.g. white status-bar icons on a white background).
3. **Expo on the physical phone** — confirm the push + persistent notification actually fires, haptics fire, nothing's cut off.

*"whatever it feels like on your computer, it's going to feel twice as worse on your phone."* Any change made while testing on the phone forces a full re-test from scratch (Chrome -> iPhone mirroring -> Expo phone). Budget an extra 10–15 min per error; voice-transcribe errors to Claude Code in plain natural language. Full loop lives in `expo-go-test.md`.

---

## What this wrench does NOT do

- **Does not set up the DB / schema / RLS / auth.** That's `supabase-mobile.md` (it must exist before the function can read it).
- **Does not write the app code or the function code by default.** Codex via router does (AGENTS.md hard rule #5). Claude owns the architecture, cadence, results-table shape, and the Claude-API prompt.
- **Does not do the deep Anthropic-SDK tuning** (prompt caching, model migration, thinking, batch). Route that to the `claude-api` skill — it's the canonical Anthropic-SDK surface and bakes in caching.
- **Does not wire the RN notification / haptics layer.** `rn-expo-ui.md` + `expo-go-test.md` own push + persistent notifications + on-device delivery.
- **Does not run live DB/auth/function ops by hand.** Use the **Supabase MCP** — `apply_migration`, `execute_sql`, `deploy_edge_function`, `get_logs`, `get_advisors`.
- **Does not do the deep infra security audit.** The pre-launch prompt-audit + key/RLS boundary check is `mobile-security-audit.md`; deep infra security routes to `cso`.
- **Does not handle git / CI / deploy plumbing.** Routes to `ship`.

---

## See also

- [../SKILL.md](../SKILL.md) — mobile-app mechanic
- [supabase-mobile.md](supabase-mobile.md) — DB schema, tables, RLS, auth (prereq — must exist first)
- [mobile-security-audit.md](mobile-security-audit.md) — the key-boundary / RLS-gap / Edge-Function-as-secret-boundary audit
- [rn-expo-ui.md](rn-expo-ui.md) — push + persistent notifications, haptics, the app-side delivery
- [expo-go-test.md](expo-go-test.md) — on-device hot-reload + the three-device QA loop
- [expo-scaffold.md](expo-scaffold.md) — Expo/RN project init (precedes everything)
- [ship-to-stores.md](ship-to-stores.md) — release pipeline once the feature ships
- [../../router/SKILL.md](../../router/SKILL.md) — route the function + client code to Codex (Claude thinks, Codex does)
- [../../cso/SKILL.md](../../cso/SKILL.md) — deep infrastructure security audit
- `claude-api` skill — Anthropic SDK tuning, prompt caching, model ids/migration for the function's Claude call
- Supabase MCP — `deploy_edge_function`, `execute_sql`, `apply_migration`, `get_logs`, `get_advisors`
