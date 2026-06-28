# Phoenix's AI Workflow Kit

A portable, privacy-scrubbed copy of my AI workflow system — the "mechanic / wrench"
skill framework, the cross-AI bridge, the hooks, and the lock layer. It's a **template
you adapt to your own AIs**, not a drop-in. Pull it down, let your AI read it, and take
only the parts that fit how *you* work.

> **This is shared with friends & family who want to level up their own AI setup.**
> Nothing here is mine-only — the philosophy is vendor-agnostic. The *role* matters
> (a thinking lane, a building lane, a reading lane, a cheap/bulk lane), not the brand
> of AI you point at each role.

**Built from:** plain-markdown skill files (portable to any AI), with Python and Node for the optional scrub, sync, and test tooling.

---

## How to use this (the 4-step flow)

1. **Pull the repo** (or download the zip — see [`dist/`](dist/)).
2. **Read the pamphlet** — open [`phoenix-workflow-pamphlet.html`](phoenix-workflow-pamphlet.html)
   in a browser (~5 min). It explains the philosophy.
3. **Hand it to your AI.** Copy [`implementation-prompt.md`](implementation-prompt.md)
   into whatever AI you use (Claude, ChatGPT, Gemini, Codex, a local model — anything),
   and attach [`dist/phoenix-workflow-framework.zip`](dist/).
4. **Answer its questions.** It interviews you about *your* AI lineup, maps the framework's
   roles onto *your* tools, rewrites the paths/wording for *your* machine, and takes only
   what your AI can actually run. You decide what to keep.

That's the whole point: **your AI evaluates it and you choose what to adopt.** Take 2–3
pieces, live with them a week, then come back for more.

---

## Getting the newest version

I keep adding to my workflow. When I do, I re-sync this repo and push. To get the latest:

```bash
git pull
```

Then check [`CHANGELOG.md`](CHANGELOG.md) — it lists exactly what changed since last time,
so you (or your AI) can decide whether the new pieces are worth adopting. Because the
framework lives as **plain unpacked files** (not just a zip), `git diff` shows you the
changes line-by-line.

## Validate locally

The repo has no install step for basic use. To verify the scrubbed framework and the
analytics-sites skill tests:

```bash
python tools/scrub.py framework
cd framework/_system/skills/analytics-sites
node --test tests/*.test.mjs
```

Environment-based pieces are opt-in. Use [`.env.example`](.env.example) as a checklist
when trying the analytics-sites connector or local harness scripts.

---

## What's in here

```
phoenix-workflow-kit/
├── README.md                       ← you are here
├── CHANGELOG.md                    ← what changed each update (read this after a pull)
├── phoenix-workflow-pamphlet.html  ← the philosophy (open in a browser first)
├── implementation-prompt.md        ← paste into your AI to adopt the framework
├── framework/                      ← the framework as a real file tree (diffable source of truth)
│   ├── AGENTS.md                   · operating manual: hard rules + mechanic/wrench philosophy
│   ├── SKILLS_INDEX.md             · one line per callable skill (the menu)
│   ├── DECISION_MAP.md             · task → which tool to grab
│   ├── RELIABILITY_STANDARD.md     · the "works every time" build standard
│   ├── _system/skills/             · every mechanic (SKILL.md) + its wrenches + scripts  ← the core
│   ├── _system/tool-parity/        · the cross-AI tool 1:1 parity checker
│   ├── harness/                    · cross-project rules, hook wiring, the bridge hooks
│   └── agentic-os/                 · the cross-session file-lock + headless spawn args
├── dist/                           ← convenience downloads (rebuilt from framework/)
│   ├── phoenix-workflow-framework.zip   · attach THIS to your AI in step 3
│   └── phoenix-workflow-kit.zip         · the full share kit (pamphlet + prompt + framework)
└── tools/                          ← how I keep this repo in sync (you can ignore these)
```

Paths inside the framework are placeholders (`C:\Users\<you>\...`) and the operator is
generalized as "the user" — your AI rewrites both for your environment during adoption.

---

## A note on honesty about your tools

The framework assumes some AIs can run shell commands, write files, and fire hooks. If
yours can only chat, **keep the ideas** (the routing logic, the prompts, the second-brain
habit) and **drop the machinery** it can't execute. The implementation prompt handles this
for you — it asks what each of your AIs can actually *do* before recommending anything.

## License

Released under the MIT license — see [`LICENSE`](LICENSE).
