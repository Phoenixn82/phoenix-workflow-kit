---
name: blog-write
description: Write or update the personal-site blog from radar candidates. Triggers on "write the blog", "blog update", "weekly digest", "blog-radar", "what should I blog", or after blog_radar.py flags a candidate. Four modes: NEW_ANCHOR, UPDATE_ARTICLE, ANCHOR_UPDATE/STALE, WEEKLY_DIGEST.
---

# blog-write - personal-site blog writer

The detector (`Blog/tools/blog_radar.py`) decides when a project is blog-worthy and writes `Blog/_RADAR.md`.
This skill decides what to write after the user explicitly triggers it. It never writes autonomously.

## 0. Always Start Here

1. Run the radar fresh: `python Blog/tools/blog_radar.py report`, then read `Blog/_RADAR.md`.
2. Pick the target: the user names a project, or use the top candidate. The radar lane selects the mode.
3. Read the voice rules every time: `Blog/_VOICE.md`, `Reference/phoenix-writing-style-guide.md`, `Blog/video-curator/post.md`, and `Blog/example_app/post.md`.
4. Pull the project's fresh beats from `Blog/_QUEUE.md`. Use the unconsumed beat IDs listed by the radar/report.

## Modes

### NEW_ANCHOR

Use when a project has no blog anchor yet.

- Scaffold `Blog/<slug>/` from `Blog/_TEMPLATE.md`.
- Draft in the house voice: reason, journey, result.
- Theme it to the project's own design tokens. Follow `PORTFOLIO_GUIDELINE.md`.
- Capture screenshots through the existing workflow recipe in `Blog/_screenshot-task.md`. Never fabricate screenshots, metrics, dates, or repo links.
- Add the homepage card only if the user approved publishing the new anchor.
- Finish with the mandatory state update:
  `python Blog/tools/blog_radar.py mark --slug <slug> --date <today> --sha <repoHEAD-or-omit> --consume <beatIds...>`

### UPDATE_ARTICLE

Use when one project has a large batch that deserves its own dated article.

- Create `Blog/<slug>/updates/<YYYY-MM-DD>-<short>/index.html`.
- Keep it self-contained and sized to the actual batch.
- Append or extend the anchor's `Updates` section with a link to the new article.
- Make sure the weekly digest carries only a teaser plus the user's callout line:
  "I did way too much work on this project to fit it in the weekly update - check out the full write-up here".
- Link the repo only when `tools/projects.json` has `public: true` for that slug.
- Finish with the mandatory state update:
  `python Blog/tools/blog_radar.py mark --slug <slug> --date <today> --consume <beatIds...> --article <YYYY-MM-DD>-<short>`

### ANCHOR_UPDATE / STALE

Use when the existing anchor has drifted or needs a small factual reconcile.

- Surgically update the anchor. Do not regenerate the page.
- Preserve every frozen zone: figures, SVGs, scripts, lightbox code, and the built-with ticker.
- Keep the anchor lean. Add current facts, then trim or compress older low-value detail so the post stays in its length band.
- Always preserve the opening problem, the current result, and one honest-mistake beat.
- Finish with the mandatory state update:
  `python Blog/tools/blog_radar.py mark --slug <slug> --date <today> --consume <beatIds...>`

### WEEKLY_DIGEST

Use when the radar weekly banner is READY or the user asks for a weekly roundup.

- Build `Blog/weekly/<YYYY-Www>/index.html` from `Blog/_weekly-digest.template.html`.
- Use one tight paragraph for each `WEEKLY_ITEM` project.
- Use a two-sentence teaser for each `UPDATE_ARTICLE` project and link to the full update article.
- Refresh the landing `What I've been up to this week` block in `Blog/index.html`.
- Add or prepend the digest to `Blog/weekly/index.html`, using `Blog/_weekly-archive.template.html` if the archive does not exist.
- Finish with the mandatory state update:
  `python Blog/tools/blog_radar.py mark --week <YYYY-Www> --date <today> --consume <all digest beatIds...>`

## Guardrails

- The user must trigger the write. The detector may surface candidates, but it does not spend AI tokens or write prose.
- Keep anchors lean; move heavy new detail into update articles.
- Keep weekly digest blocks short.
- Private or unknown repos are never linked.
- Local changes only until the user explicitly approves deploy/push.
- The `blog_radar.py mark` call is mandatory and last, or the same beats will keep reappearing.
