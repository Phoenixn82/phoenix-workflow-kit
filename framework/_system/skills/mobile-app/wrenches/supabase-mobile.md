---
name: supabase-mobile
description: Wire Supabase into an Expo/RN app — client setup, Postgres schema/tables, Row Level Security, and email/password + OAuth auth flows on mobile, with a local-first AsyncStorage cache layer for instant UX. Uses the Supabase MCP for live ops (apply_migration, execute_sql, get_advisors). Claude (you) does the architecture/schema/RLS design and drives the MCP; Codex is the default lane for the actual app integration code (AGENTS.md rule #5) — Claude steps in on the carve-out where it owns the live MCP ops and the security-sensitive RLS/auth wiring. Fires on "add a database to the app", "Supabase auth on mobile", "RLS", "store user data", "login/signup in the app", "sync local cache to cloud", "tie data to a user".
---

# supabase-mobile — cloud DB + auth for an Expo/RN app, local-first

This wrench takes an Expo/React Native app that currently stores everything on-device (AsyncStorage) and gives it a Supabase backend: a Postgres database, Row Level Security so each user only sees their own rows, and email/password (+ OAuth) authentication — while **keeping AsyncStorage as the instant read layer** so the app never feels slower. It is the exact path Nick used to migrate the habit tracker and CalTracker from local-only to cloud, including the live Supabase MCP ops. The DB/SQL schema work that "back in the day took ~2.5 of 3 weeks" now takes ~30 seconds because you describe the schema and the MCP applies the migration.

**Cardinal: a database alone is not enough — you MUST add auth.** Cloud storage forces every row to be tied to a user (Nick's data vs. another user's), and without auth anyone could log in as anyone. DB + RLS + auth ship together or not at all.

**Cardinal: enable automatic RLS at project creation, every time.** It is the single lowest-hanging-fruit security upgrade. Vibe-coded apps have leaked precisely because RLS was off. Supabase now offers it at creation (it used to require backend coding). Treat RLS as opt-out, not opt-in.

**Cardinal: local-first, sync periodically — never round-trip the DB on every change.** Keep AsyncStorage as the immediate read layer so the app feels instant (zero added initial load time), add the database underneath, and sync periodically. Reading/writing the DB on every interaction adds milliseconds-to-seconds of lag and a value pulled straight from the DB on reload introduces visible ~1s flicker.

**Cardinal: never put service-role keys or secrets in the client.** The mobile app only ever holds the publishable/anon key + project URL. RLS is what makes the anon key safe. Anything secret (e.g. an Anthropic key for in-app AI) goes behind an Edge Function — see `edge-fn-claude-ai.md` and `mobile-security-audit.md`.

---

## When to fire vs. defer

Fire this wrench when the user says any of: *add a database to the app*, *Supabase auth on mobile*, *RLS*, *store user data*, *login/signup in the app*, *sync local cache to cloud*. The mental model Nick draws: the app talks to the device (local storage = a partitioned hard disk / USB key on the phone); going cloud adds a layer where the device also sends/receives to a remote DB (Supabase), and that remote layer forces you to tie each user to their own records via auth.

The stack is deliberately opinionated — Supabase, not because it's objectively best, but because it's a well-carved river. The same DB-setup ideas transfer to any provider; this wrench is the Supabase-specific recipe.

---

## Phase 0 — Decide the architecture before touching the MCP (Claude owns this)

Prompt Claude Code with the full intent and let it propose, then confirm against your intent:

```text
I'd like to add a database to this project. In addition to a database, I also want
local caching so the user has a very immediate and snappy experience when they use
the app. We're going to be using Supabase as our app. And in addition, we're going
to need to set up user authentication so that you know which user is accessing which
data. Help me through this process.
```

The architecture Claude should return (and the one to confirm):

1. **Supabase Auth** — email+password AND OAuth (OAuth = social login, e.g. one-click Google sign-in). Email+password is the simplest to start. Google, Apple, GitHub OAuth are available out of the box.
2. **Postgres database** for the app's domain tables (habits, completions, challenges; or meals, profiles; etc.) — Postgres is built into Supabase.
3. **Local-first caching** — keep AsyncStorage as the immediate read layer, add the DB, sync periodically.
4. **Replace the onboarding-only gate screen with a Supabase auth screen** (sign up + sign in), then onboard *new* users.

**Parallelize the setup.** You haven't created the Supabase project yet — tell Claude to build everything it can up to that point while you go make the account:

```text
I don't yet have Supabase set up, but I'll do that now. Let's go with email and
password. Work on everything that you can up until that point.
```

---

## Phase 1 — Create the Supabase project

You can do this in the dashboard (free to create an account and start a project) **or** via the Supabase MCP — prefer the MCP so the whole flow stays in-session.

Dashboard flow (CalTracker example): create a new project named e.g. `Cal Tracker`, use the **default generated DB password** (copy it via the "use password copy" button), and **enable automatic RLS at project creation**. Cost: free.

MCP flow — these are deferred tools; load their schemas first. The Supabase MCP server prefix is install-specific (a UUID like `mcp__2490c682-…__`, NOT `mcp__claude_ai_Supabase__`), so use a **keyword** ToolSearch (matches any prefix) rather than an exact `select:`:

```text
ToolSearch query: supabase list_organizations get_cost confirm_cost create_project get_project get_project_url get_publishable_keys
```

Then:
1. `list_organizations` → pick the org.
2. `get_cost` → `confirm_cost` (free tier returns $0; the create call requires the confirmation id).
3. `create_project` with a clear name (e.g. `Cal Tracker`, `habit tracker`).
4. After provisioning, `get_project_url` + `get_publishable_keys` → hand the **project URL** and **publishable/anon key** to the app config. Never hand over the service-role key.

Give Claude the keys and have it implement the full DB integration (auth + database, wire local app to remote DB). On CalTracker this was done largely autonomously once the keys were in hand.

---

## Phase 2 — Client setup (config the app holds)

The mobile app needs the project URL + publishable/anon key, an `AsyncStorage`-backed auth session, and the AsyncStorage version pin.

**AsyncStorage version pin (Expo Go compatibility) — non-negotiable:** `@react-native-async-storage/async-storage` **v3 is NOT compatible with Expo Go. Downgrade to ~v2.2.0.** Symptom on-device: an "uncaught in promise" line at the bottom of the log and a get-item failure. This only surfaces on a real phone, never in local preview. The fix: paste the full error log into Claude Code and it identifies + applies the downgrade.

```jsonc
// package.json — pin AsyncStorage for Expo Go
{
  "dependencies": {
    "@react-native-async-storage/async-storage": "2.2.0",
    "@supabase/supabase-js": "latest"
  }
}
```

The Supabase client uses AsyncStorage as the session store and disables URL-session detection (no browser on mobile):

```ts
// supabaseClient.ts
import 'react-native-url-polyfill/auto'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
})
```

> Generic RN stack defaults (TypeScript, Zustand, React Query, React Navigation, Expo SecureStore) are owned by the `build/mobile` wrench — do not restate them. This wrench only covers the Supabase-specific client + the AsyncStorage pin.

---

## Phase 3 — Schema + RLS via the Supabase MCP (the ~30-second step)

Describe the tables to Claude; it writes the SQL and applies it through the MCP. Load the MCP ops:

```text
ToolSearch query: supabase apply_migration execute_sql list_tables list_migrations generate_typescript_types get_advisors
```

Procedure:
1. **Design tables** keyed to the user. Every user-owned table carries a `user_id` column defaulting to `auth.uid()`. Habit-tracker example tables: `habits`, `completions`, `challenges`. CalTracker: `profiles`, plus meal/macro entries.
2. **`apply_migration`** — one named migration per logical change (tables + RLS policies together). Use `apply_migration` for DDL/schema; use `execute_sql` for ad-hoc queries and seeding.
3. **Enable RLS on every user table and add policies** — if you created the project with automatic RLS, tables come RLS-enabled; you still must add the per-user policies. Example migration body:

```sql
-- habits table, RLS-locked to the owning user
create table public.habits (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users (id) on delete cascade default auth.uid(),
  name        text not null,
  created_at  timestamptz not null default now()
);

alter table public.habits enable row level security;

create policy "owner can read"   on public.habits for select using  (auth.uid() = user_id);
create policy "owner can insert" on public.habits for insert with check (auth.uid() = user_id);
create policy "owner can update" on public.habits for update using  (auth.uid() = user_id);
create policy "owner can delete" on public.habits for delete using  (auth.uid() = user_id);
```

4. **`generate_typescript_types`** → drop the generated types into the app so DB reads/writes are typed.
5. **`get_advisors`** (security + performance) after migrating — this is your fast RLS-gap and missing-index check. Run it any time you add or change tables. (Deep infra security goes to `cso` and `mobile-security-audit.md`.)
6. **`list_tables` / `list_migrations`** to verify state any time.

---

## Phase 4 — Auth flows on mobile (replace the onboarding gate)

Swap the current onboarding-only gate for an auth screen (sign up + sign in), then onboard *new* users behind it. Start with **email+password** (simplest); add Google/Apple/GitHub OAuth later out of the box.

Core auth calls (email/password):

```ts
// sign up
await supabase.auth.signUp({ email, password })
// sign in
await supabase.auth.signInWithPassword({ email, password })
// sign out (CalTracker wired this into the profile screen)
await supabase.auth.signOut()
// observe session to gate the app
supabase.auth.onAuthStateChange((_event, session) => { /* route to auth vs. app */ })
```

The session persists via AsyncStorage (Phase 2 client config), so the user stays logged in across launches. With RLS in place, the anon key + the user's JWT is all the client needs — the DB returns only that user's rows.

**Sign-in UI shortcut Nick used:** pull a sign-in page reference from Dribbble, feed the image straight into Claude Code, and ask:

```text
Can you build me something kind of like this for my sign-in page?
```

(Routes the brand/visual layer to `ui-ux-pro-max` / `design-studio`; this wrench just notes the image-reference trick.)

---

## Phase 5 — Local-first caching + sync (keep it snappy)

The whole reason to keep AsyncStorage: instant on-device cached loads with no added initial load time, plus periodic DB updates. Pattern:

- **Read from AsyncStorage first** (instant), then reconcile with the DB in the background.
- **Sync periodically**, not on every change. Writing/reading the DB on every interaction adds ms-to-seconds of lag.
- **Cache any value you'd otherwise pull straight from the DB on reload** — a toggle pulled directly from the DB took ~1s to reflect on reload; caching it client-side removes the flicker. Same for onboarding flicker.

**Performance tuning that actually moved numbers (CalTracker):**
- Consolidate multiple DB calls into a **single DB call** — saved ~600ms on cellular.
- Overall app got ~14% faster (home screen avg ~254ms → ~219ms); network latency dropped from ~560ms on LTE to ~80ms (~half a second saved).
- Token-for-speed tradeoff: these optimizations cost more tokens — you trade money/tokens for time saved.

**Autonomous polish loop for post-DB usability** (after the DB lands, the app gains new latency/flicker surfaces):

```text
I want you to open up every individual page of the app and then ideate small
improvements that it could make to the usability and then the speed by which the
app loads and then works. [loop repeatedly, both ideating AND implementing]
```

On CalTracker this ran ~24,000 tokens over ~6 minutes; take a quick verify pass after. Also useful: *"What sorts of changes are currently contributing to the very long load times?"* then have it optimize.

---

## Phase 6 — Verify the migration on real hardware

A DB change is invisible until you test on-device. **Whatever it feels like on your computer, it feels about twice as bad on the phone** — and any change made while testing on the phone forces a full re-test from scratch. Run the three-device QA sequence (full procedure lives in `expo-go-test.md`):

1. Chrome on the computer.
2. iPhone mirroring.
3. Expo (Expo Go) on the actual phone.

Device-only bugs you cannot catch in Chrome/simulator: iPhone native top-bar status icons (time/battery/Wi-Fi) rendering white against a white background, the AsyncStorage v3 failure, push-notification permission prompts. When one appears, tell Claude the exact symptom — e.g. *"My iPhone's native top bar icons are white and blend into the white background — is there any way to fix it? How do I force the colors?"* — and paste full error logs verbatim, no interpretation needed.

Seed realistic data to test the populated UX:

```text
Add a bunch of entries to the database so I could see what this app would look like
if it was fully populated.
```

(Use `execute_sql` via the MCP to insert seed rows.) Watch for **DB-state mismatches surfacing in the UI** — e.g. it said "two trees" but three were showing, a likely database bug.

---

## Phase 7 — Token + session hygiene during the build

- Model performance degrades significantly after **~200,000 tokens**; at **~250k–300k**, run `/compact` before continuing. It compresses the full conversation history (~40–50% shorter) while keeping the information, bankrolling the saved tokens for better next-iteration quality. Downside: it takes a fair amount of time.
- Use `/clear` (not `/compact`) to start a genuinely fresh conversation for a discrete new task (e.g. the security audit) — tokens drop to 0%.
- Update `CLAUDE.md` after the DB/auth land so it describes all the new functionality. `CLAUDE.md` is auto-loaded into every conversation; a stale one misinforms every future edit.

---

## Phase 8 — Security pass before publish

After DB + auth + RLS, run the security audit in a fresh `/clear`ed conversation, then re-run the three-device sequence. The full prompt asset and the mobile-specific risk model (exposed keys, client trust boundaries, RLS gaps, Edge Function as the secret boundary) live in `mobile-security-audit.md`. The fast in-session check is the MCP `get_advisors` call (Phase 3, step 5). Deep infrastructure security routes to `cso`.

---

## Gotchas (Supabase/DB-specific)

- **DB without auth is broken by design** — the DB must pull records for a specific user, and others must not be able to log in as you.
- **Local-only storage is the whole problem you're solving** — data lives on one device; send the app to someone else and they can't use your data; nothing syncs between your phone and computer.
- **RLS opt-in is a trap** — enable automatic RLS at creation and still add per-user policies. `get_advisors` catches gaps.
- **AsyncStorage v3 ≠ Expo Go** — pin ~2.2.0; symptom is an "uncaught in promise" + get-item failure that only appears on-device.
- **DB-pulled-on-reload values flicker** — cache client-side; never round-trip on reload.
- **Never ship the service-role key** — client holds only URL + publishable/anon key; RLS makes the anon key safe.
- **Renaming/reopening the project folder reverts your Claude Code session** — you will NOT be in the same session; checkpoint (commit) first. (Renaming the auto-named GitHub repo "example project" to a real name, and the README still referencing the old name, is git plumbing — routes to `ship`.)

---

## What this wrench does NOT do

- **Expo/RN project init, file-based routing, dev-environment setup** → `expo-scaffold.md`.
- **UI/UX patterns, navigation, screen design, the iterate-on-design loop** → `rn-expo-ui.md`; visual brand + design system → `../../<design>/...` via `ui-ux-pro-max` / `design-studio`.
- **In-app AI features (Claude API behind an Edge Function), keeping the Anthropic key off the client** → `edge-fn-claude-ai.md`.
- **Device pairing, on-device hot-reload, the three-device QA loop mechanics** → `expo-go-test.md`.
- **EAS Build, TestFlight/App Store, Google Play submission** → `ship-to-stores.md`.
- **The security-audit prompt + full mobile risk model** → `mobile-security-audit.md`; deep infra security → `cso`.
- **Git/commit/repo-rename/README/CI/deploy plumbing** → `ship` mechanic.
- **The actual app integration code** → Codex via `router` (Claude designs schema/RLS/auth + drives the live MCP; Codex writes the app wiring — AGENTS.md rule #5).
- **"Which runtime if not Expo/RN"** → `build/mobile` wrench (this mechanic supersedes it for the opinionated Expo/RN path).

---

## See also

- [expo-scaffold.md](expo-scaffold.md) — project init + scaffolding scope
- [rn-expo-ui.md](rn-expo-ui.md) — UI/UX patterns, design iterate loop
- [edge-fn-claude-ai.md](edge-fn-claude-ai.md) — Edge Function → Claude API, secret boundary
- [expo-go-test.md](expo-go-test.md) — device pairing + three-device QA sequence
- [ship-to-stores.md](ship-to-stores.md) — EAS Build + store submission
- [mobile-security-audit.md](mobile-security-audit.md) — pre-launch security prompt + RLS-gap risks
- [../SKILL.md](../SKILL.md) — mobile-app mechanic (dispatch + routing)
- Supabase MCP — live DB/auth ops: `apply_migration`, `execute_sql`, `generate_typescript_types`, `get_advisors`, `create_project`, `get_publishable_keys`
- `cso` (standalone keeper) — deep infrastructure security audit
- `ship` (mechanic) — git/commit/tests/PR/CI/deploy
- `router` → Codex — the actual integration code lane
- `second-brain` — capture project decisions; `dev-registry/ports.md` for local ports
