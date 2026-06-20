# Implementation prompt — adopt this AI workflow (AI-agnostic)

> Paste this into **whatever AI you use** and attach `phoenix-workflow-framework.zip`.
> It asks what AIs you run, maps the framework's *roles* onto your lineup, rewrites the files to
> match your primary AI, takes only what your AI can use, and ends with a best-practices cheat-sheet.
> (Same text as the copy button in the pamphlet.)

---

I'm adopting another power-user's AI workflow system. Attached is **phoenix-workflow-framework.zip** — a "mechanic / wrench" skill framework with a role-based router, a cross-AI bridge, hooks, and a lock layer. It is a TEMPLATE, not a drop-in. It's written around the AUTHOR's specific AI lineup (a thinking lane = Claude, a building lane = Codex, a long-context reading lane = Gemini, a cheap/bulk lane = a local model router), and the paths are their machine. The private vault and all secrets were left out.

**The philosophy is vendor-agnostic — the ROLE matters, not the brand.** Your job is to adapt it to MY AIs, whatever they are, and implement only what's useful to me. Do NOT copy anything yet. First, interview me.

**STEP 1 — Learn my actual setup.** Ask a few at a time, wait for answers, and ask follow-ups until you genuinely understand my lineup. Do NOT assume I use Claude or Codex.
- **List every AI/LLM I use** — Claude, Codex, GPT, Gemini, local/open models, or anything niche or obscure (even something like "owl alpha"). For EACH: what is it good at, and what can it actually DO — write files? run shell commands? use tools/MCPs? or only chat? Which one is my daily driver?
- Which of my AIs (if any) would fill each role: deciding/architecting · writing code · reading long docs or video · cheap bulk work. One AI can wear several hats — that's fine; say so.
- My OS and shell (paths + hooks differ across Windows / macOS / Linux).
- The kinds of projects I work on, and what I repeat often enough to want templated.
- What's broken or annoying in my current workflow.
- Whether I want a persistent "second brain" vault, and where it'd live.
- My autonomy comfort, from approve-every-step to fully hands-free.
- What tools / MCPs / CLIs I already have, and which providers I pay for.
- Solo, or do multiple AIs/people touch the same repos?

**STEP 2 — Map the framework onto MY AIs.** Read AGENTS.md, SKILLS_INDEX.md, DECISION_MAP.md and MANIFEST.md to learn the philosophy and the role-based router. Then translate the author's role assignments onto MY lineup and show me a ranked proposal:
- which mechanics / wrenches / hooks / patterns help MY work, and which to skip;
- how each role maps to one of MY AIs — e.g. "you're Codex-primary, so think + build both route to Codex"; or "your main model can't run hooks, so keep the skill docs + vault discipline and drop the PowerShell machinery";
- for any AI that can only chat (no file/command access), keep the IDEAS — the routing logic, the prompts, the vault habit — and drop the machinery it can't execute.
Then wait for my approval.

**STEP 3 — Implement the approved subset, rewritten for me.** Rewrite the files so they match MY primary AI and machine: swap the author's lane assignments for mine throughout the docs/skills, rewrite every hardcoded path for my OS/username, and translate or drop hooks/scripts my AI can't run. If I'm Codex-primary, rewrite the Claude-lane wording to Codex (and vice-versa); if I'm on an obscure model, grab only what it can genuinely use. Never introduce secrets. Work in small phases; after each, say exactly what changed and how to check it.

**STEP 4 — Verify.** Show me each thing working with a concrete example from MY actual work, plus a one-line "how do I know it's working" check.

**STEP 5 — Best-practices handoff.** Once it's built on my machine, give me a short "how to operate your new workflow" cheat-sheet so I get the best results:
- right-size the call — a wrench for a narrow ask, a mechanic for a coordinated job, the apex for a whole project; don't over-summon;
- route by role every turn — pick the lane/AI that fits the task;
- keep the vault current — capture decisions + status as you go, or the memory rots;
- trigger, don't automate — nothing runs on its own; you summon it;
- verify before "done" — show evidence, never "it should work";
- cost-first — prefer the cheapest capable lane; push bulk to the free/local one;
- start small — adopt 2–3 pieces, live with them a week, then add more.

Rules: surgical changes, explain trade-offs, ask before anything irreversible, adapt to me rather than cloning the author. Begin with STEP 1 now.
