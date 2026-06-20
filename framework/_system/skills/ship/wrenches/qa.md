---
name: ship-qa
description: Systematic QA testing + fix loop. Walks the live app via chrome-devtools-mcp like a real user, surfaces bugs, dispatches fixes to Codex /goal for sustained iteration. --report-only flag emits a bug report without firing the fix loop (qa-only collapsed into this wrench). Trigger phrases include "qa", "QA this", "test this app", "find bugs", "test and fix", "fix what's broken", "bug bash", "qa-only", "report bugs", "test but don't fix".
---

# ship-qa — test, find bugs, fix them (or just report)

When the user wants to know what's broken in the live app, this wrench runs the QA loop. Walks critical user paths, takes screenshots, checks for errors, surfaces failures with evidence. Then dispatches the fix work to Codex `/goal` for sustained bug-bashing.

`--report-only` flag flips off the fix loop. Just emits the bug report. (This is the old `qa-only` skill, collapsed into qa per DECISIONS_LOCKED.)

---

## When to fire

- After a deploy when the user says "QA this"
- Direct: "find bugs" / "test this site" / "bug bash this app" / "qa-only" (for report-only)
- Pipeline auto-fires qa if `pay-for-this` surfaces issues that need deeper investigation
- After a feature build, before ship, when the user wants the full test pass

Don't fire when:
- The change is doc-only or config-only (no runtime to test)
- The user wants unit tests (those run in `python-ci-preflight` or the project's test runner)
- A bug is already root-caused (escalate to `investigate` for the root-cause path)

---

## Two modes

### Default mode: test + fix loop

```
1. Run QA pass via chrome-devtools-mcp (see "QA pass" below)
2. Surface findings to the user
3. If bugs found:
   a. Dispatch Codex /goal with the bug list as the goal:
      "Fix all bugs in the bug-list.json file. Verify each fix in the live app via chrome-devtools-mcp.
       Open a PR for the fixes when done."
   b. Codex iterates: write fix, verify in browser, commit, move to next bug
   c. Claude polls for progress, surfaces to the user
4. Re-run QA pass to verify fixes took
5. Report final state: bugs found, bugs fixed, bugs deferred
```

This mode is the bulk-fix path. Per DECISION_MAP "UI/bug testing on an app → chrome-devtools-mcp + codex-goal-dispatcher."

### `--report-only` mode

```
1. Run QA pass
2. Surface findings
3. STOP
```

No fix dispatch. The user decides what to do with the report. This was the old `qa-only` skill.

---

## QA pass (what gets tested)

| Tier | What | When |
|---|---|---|
| **Quick** | Critical + high-severity paths only | After a small change; ~10 min |
| **Standard** | + medium-severity paths | Default; ~30 min |
| **Exhaustive** | + cosmetic + edge cases | Before a major release; ~2 hr |

The user picks: `qa --tier=quick|standard|exhaustive`. Defaults to standard.

### Critical paths (always tested in every tier)

- Home page renders
- Primary CTA works (signup / buy / contact / etc.)
- Navigation menu functions
- Auth flow (login / logout / signup if applicable)
- Core feature happy path (the user configures per project)

### High-severity paths

- Form submissions on every form on the site
- Payment flow (if applicable) — test with sandbox/test mode
- Search functionality
- Cart / checkout (if applicable)
- Account / profile editing

### Medium-severity paths

- Filter / sort / pagination
- Modal open/close
- File uploads
- Error states (404, validation errors, network failures)
- Responsive layouts (resize to mobile, tablet, desktop)

### Cosmetic / edge cases

- Visual consistency across pages
- Touch targets on mobile (44px minimum)
- Loading states
- Accessibility (keyboard nav, alt text, focus rings)
- Browser console clean of warnings

---

## How each path is tested

Drive chrome-devtools-mcp like a paying user:

```
1. navigate_page to URL
2. take_snapshot (the DOM-aware snapshot)
3. take_screenshot (visual evidence)
4. list_console_messages (capture any errors)
5. Walk the path:
   - click → wait_for → take_snapshot
   - fill / type → wait_for → take_snapshot
   - Check the expected DOM state after each step
6. If a step fails:
   - Capture screenshot at failure
   - Note expected vs actual
   - Add to bug list
7. Move to next path
```

For each failure, the bug list entry includes:
- Severity (CRITICAL / HIGH / MEDIUM / LOW / COSMETIC)
- Description (what didn't work)
- Repro steps (the click path)
- Expected behavior
- Actual behavior
- Screenshot URL or path
- Console messages captured

---

## Bug report shape

```markdown
## QA report — example.app

**Tier:** standard | **Run at:** 2026-05-28 14:30 | **Coverage:** 12 paths tested

### Health score
- Before fixes: 6.2/10 (bugs found in 4 critical paths)
- After fixes (if fix loop ran): 9.1/10

### Bugs found

#### CRITICAL — Signup form silently fails on Safari
- **Repro:** Open / on Safari → click Sign up → fill email → click Submit
- **Expected:** Redirect to /onboarding
- **Actual:** No redirect, no error message; form just stays open
- **Console:** TypeError: undefined is not an object (evaluating 'window.crypto.randomUUID')
- **Screenshot:** [link]

[... more bugs ...]

### Fixes applied (default mode)
- CRITICAL bug 1 → fixed in commit abc1234, verified
- HIGH bug 2 → fixed in commit def5678, verified
- MEDIUM bug 3 → deferred, opened issue #42

### Fixes deferred
- COSMETIC bug 4 → not in scope; logged for next sprint
```

---

## Fix dispatch (default mode)

When bugs surface, dispatch to Codex `/goal`:

```bash
codex goal --plain "$(cat <<'EOF'
[FILESYSTEM BOUNDARY: do NOT read ~/.claude/, ~/.agents/, .claude/skills/, agents/]

Goal: Fix all CRITICAL and HIGH severity bugs in the attached bug list.

Bug list: ./bug-list.json

For each bug:
1. Read the repro steps and expected behavior
2. Investigate root cause in source (do not patch surface symptoms)
3. Write the fix
4. Verify the fix in the live app via chrome-devtools-mcp (replay the repro)
5. Run the project's test suite
6. Commit on a topic branch with clear message

When all CRITICAL + HIGH are fixed, open a PR titled "fix: QA bugs from <date>".

Stop conditions:
- All CRITICAL + HIGH fixed → success
- A bug requires architectural change → defer with note; flag for the user
- A bug can't be reproduced → mark "flaky" with evidence

Do not fix MEDIUM or COSMETIC bugs unless you find them while fixing CRITICAL/HIGH and the fix is trivial.
EOF
)"
```

Codex iterates autonomously. Claude polls periodically (every few minutes) for progress and surfaces to the user.

---

## Cost shape

- QA pass = chrome-devtools-mcp model calls × paths × steps per path
- Quick tier = ~50-100 model calls
- Standard tier = ~200-400 model calls
- Exhaustive = ~1000+ model calls
- Fix loop = Codex `/goal` runtime (the user's $200/mo Pro subscription absorbs this — Codex iterates on Codex tokens, not Claude tokens)
- Total: standard tier with moderate bugs = a few dollars of chrome-devtools-mcp usage + Codex /goal runtime

The fix-loop dispatch to Codex is the cost-discipline reason qa is structured this way. Claude orchestrates; Codex grinds.

---

## Off browse-daemon (per DECISIONS_LOCKED)

Old qa used a gstack browse daemon. Cut. This wrench drives chrome-devtools-mcp directly (via MCP tools) for live testing and dispatches Codex /goal for repeatable testing scripts when the user wants them.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Every test path "fails" | Auth/cookie issue, site not loading | Verify production URL first; check if login is needed |
| Codex /goal stalls | Spec ambiguity, can't find root cause | Surface stalled goal; the user decides escalate to investigate or override |
| Fix loop introduces new bugs | Codex over-corrects | Re-run qa --report-only after fix loop; surface new bugs in next iteration |
| QA pass times out | Too many paths × tight timeouts | Lower tier; or increase per-path timeout |

---

## Pairing patterns

- After `land-and-deploy` → qa runs as part of post-deploy when the user asks
- `pay-for-this` surfaces a UX issue → escalate to qa for systematic testing
- qa finds a deep bug → escalate to `investigate` for root cause; investigate's fix routes back through ship pipeline

---

## See also

- [SKILL.md](../SKILL.md) — pipeline mechanic
- [land-and-deploy.md](land-and-deploy.md) — what fed the live app under test
- [pay-for-this.md](pay-for-this.md) — paired post-deploy, escalates to qa
- [`investigate`](../../investigate/) — root-cause path when qa finds something deep
- [`router/wrenches/codex-goal.md`](../../router/wrenches/codex-goal.md) — fix-loop dispatch mechanics
