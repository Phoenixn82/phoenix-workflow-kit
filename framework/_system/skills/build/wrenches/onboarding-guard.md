---
name: onboarding-guard
description: Wrench inside the `build` mechanic. The 5-condition checklist the user built after Example App's 3-fix-in-17-min onboarding-redirect incident (Apr 26 2026). Run this before writing ANY conditional-redirect logic, onboarding wizard, "first-time user" state gate, or auth-driven route guard. All five conditions must be handled or explicitly decided against. Fires on "onboarding", "redirect if", "first login", "new user flow", "skip if completed", "show wizard", "setup wizard", "onboarding redirect", "auth guard". Also fires proactively whenever Claude is about to write a +layout.svelte, _middleware, or equivalent that contains redirect logic tied to user state.
---

# onboarding-guard — the 5-condition redirect checklist

Before writing any redirect-to-onboarding logic (or any conditional-redirect logic tied to user state), work through this checklist. **All five conditions must be handled or explicitly decided against.** Skipping this step is what caused Example App's 3 fix commits in 17 minutes on 2026-04-26.

This isn't bureaucracy. Every condition catches a specific failure mode the original Example App commit hit one by one.

---

## The 5 guard conditions

```
☐ 1. Backend / API reachable?
     If the backend is down, do NOT redirect to onboarding. Fail silently or show
     a "connecting..." state. Redirecting on backend failure creates an infinite loop:
     guard tries to check completion → API call fails → falls back to "must onboard"
     → redirects to /onboarding → which also calls the API → loop.

☐ 2. User already completed this flow?
     Check persistent state (DB column, user profile flag, server-side session).
     Never rely on session-only client state — users clear sessions, hit incognito,
     switch devices.

☐ 3. User already on this route?
     If the user is already on /onboarding, do NOT redirect again. Always check
     the current pathname before issuing a redirect. Otherwise: /onboarding redirects
     to /onboarding → loop.

☐ 4. Is there a feature flag or "disabled" override?
     During development, the flow may not be finalised. A single boolean
     (ONBOARDING_ENABLED = false) lets you disable the redirect without deleting
     the logic. Without this flag, the only way to disable mid-development is
     ripping out the code — which is the antipattern Example App's third commit was.

☐ 5. Does the redirect target actually exist AND is the user authorised to reach it?
     If /onboarding requires auth and the user isn't authenticated, the redirect
     fails with 403 or — worse — another redirect to /login that bounces back to
     onboarding. Verify auth state BEFORE redirecting to any gated route.
```

If a condition genuinely doesn't apply to the project (very rare — usually only condition 4 for a fully-locked production flow), document the decision in the project's CLAUDE.md or a comment. Don't silently skip.

---

## Implementation templates

Codex writes the actual code by default per `[[Actions/routing-defaults]]`. Claude can step in on the documented carve-outs (Codex down, small + well-understood, "just do it"). These templates are the SPEC the implementer follows.

### SvelteKit (+layout.svelte or hooks.server.ts)

```typescript
import { page } from '$app/stores';
import { get } from 'svelte/store';

// Condition 4: Feature flag — set false during dev, true when flow is finalized
const ONBOARDING_ENABLED = true;

async function shouldRedirectToOnboarding(
  user: User | null,
  apiHealthy: boolean
): Promise<boolean> {
  // Condition 4 first — fast exit during development
  if (!ONBOARDING_ENABLED) return false;

  // Condition 1: Backend must be reachable
  if (!apiHealthy) return false;

  // Condition 5: Must be authenticated to reach onboarding
  if (!user) return false;

  // Condition 3: Already on onboarding route
  const currentPath = get(page).url.pathname;
  if (currentPath.startsWith('/onboarding')) return false;

  // Condition 2: Check if already completed
  const hasCompleted = user.onboarding_completed ?? false;
  if (hasCompleted) return false;

  // All guards passed — redirect
  return true;
}
```

### Python / FastAPI middleware

```python
ONBOARDING_ENABLED = True  # Feature flag (condition 4)

def should_redirect_to_onboarding(
    user: Optional[User],
    current_path: str,
    api_healthy: bool,
) -> bool:
    if not ONBOARDING_ENABLED:        # 4: feature flag
        return False
    if not api_healthy:                # 1: backend health
        return False
    if not user:                       # 5: must be auth'd
        return False
    if current_path.startswith("/onboarding"):  # 3: already on route
        return False
    if getattr(user, "onboarding_completed", False):  # 2: already done
        return False
    return True
```

### Next.js (middleware.ts)

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getUserFromRequest } from './lib/auth';
import { checkApiHealth } from './lib/health';

const ONBOARDING_ENABLED = true;

export async function middleware(request: NextRequest) {
  if (!ONBOARDING_ENABLED) return NextResponse.next();             // 4
  if (!(await checkApiHealth())) return NextResponse.next();       // 1
  const user = await getUserFromRequest(request);
  if (!user) return NextResponse.next();                            // 5
  const path = request.nextUrl.pathname;
  if (path.startsWith('/onboarding')) return NextResponse.next();   // 3
  if (user.onboarding_completed) return NextResponse.next();        // 2
  return NextResponse.redirect(new URL('/onboarding', request.url));
}
```

For other runtimes (React Router, Express, Rails, Django, etc.) the same five conditions apply — adapt the call shape.

---

## Pre-commit checklist (before merging redirect logic)

Run through this before `git commit` of any code that calls `goto('/onboarding')`, `redirect(307, '/onboarding')`, `res.redirect('/onboarding')`, or equivalent:

```
☐ Backend unreachable case is handled (returns false / no redirect, not loop)
☐ user.onboarding_completed (or equivalent persistent flag) is checked
☐ Current route is checked before redirecting to prevent self-loops
☐ A feature flag exists to disable during development
☐ Auth state is verified before redirecting to any gated route
☐ This logic lives in ONE place (not duplicated across layouts + middleware + page guards)
```

If any box is unchecked, fix before committing. Don't ship the redirect "and add the guard later" — later is when the bug hits production.

---

## Anti-patterns this prevents

| Anti-pattern | What happens | Correct approach |
|---|---|---|
| Redirect on backend failure | Infinite loop when API is down | Condition 1 |
| No completion check | Every login hits the onboarding wizard | Condition 2 |
| No current-route check | /onboarding redirects to itself | Condition 3 |
| No feature flag | Must delete code to disable during dev | Condition 4 |
| Redirect without auth check | Fails with 403 or bounces between /login ⇄ /onboarding | Condition 5 |
| Logic duplicated in 3 places (layout + middleware + page) | Each fix needs 3 edits; one place gets missed | Single source of truth |

---

## When this wrench fires

- **Build mechanic detects** a build target involves auth / onboarding / first-time user flow → fires automatically before any redirect code is dispatched to Codex
- **the user says** "add the onboarding redirect" / "build the auth guard" / "redirect new users to setup" → fires directly
- **Claude is about to write** `+layout.svelte` / `middleware.ts` / `hooks.server.ts` / `_middleware.ts` that contains conditional redirect logic → fires proactively

The wrench's output is a SPEC (the 5 conditions worked through for this project) that Codex implements. Don't skip the wrench because the code "is just a few lines". The Example App incident was just a few lines.

---

## What this wrench does NOT do

- **Does not write the auth logic itself by default.** Codex does (per `[[Actions/routing-defaults]]`); Claude can step in on the documented carve-outs. This wrench is the checklist + spec regardless of who implements.
- **Does not catch all redirect bugs.** Just the 5 common failure modes around state-gated redirects. Other redirect bugs (race conditions, stale cookies, etc.) need `investigate`.
- **Does not handle multi-step onboarding flows.** This is the GUARD on whether to redirect. The flow itself (step 1 → step 2 → step 3 with progress) is its own design question for the `build` mechanic + the user.

---

## Origin (why this exists)

Example App's onboarding-redirect bug, 2026-04-26: 3 fix commits in 17 minutes:
- First fix: backend unreachable case (loop)
- Second fix: completion check (every login hit the wizard)
- Third fix: disable the whole redirect (the antipattern that means "no feature flag")

All three were predictable. They should have been handled together, upfront. This wrench enforces that.

---

## See also

- [../SKILL.md](../SKILL.md) — build mechanic (this wrench fires before any redirect-writing dispatch)
- [website.md](website.md) — auth flows on websites trigger this
- [mobile.md](mobile.md) — auth flows in mobile apps trigger this
- [backend.md](backend.md) — server-side auth middleware triggers this
- [../../investigate/SKILL.md](../../investigate/SKILL.md) — for OTHER redirect bugs (race conditions, stale state, etc.)
