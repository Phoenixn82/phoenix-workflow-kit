# Data-Dense UI Craft Library — dashboards, tables, app surfaces

> Seeded 2026-06-23. Source: dashboard-UI-craft video — https://youtu.be/Ksx9C2-3yMo ("the three tells you've never built a dashboard before"). Distilled to declaratives.
>
> **What this is:** the fourth reference axis. ARCHETYPES (STRUCTURE), brand DNA (STYLE), and FRAMEWORKS (STACK) are about *variety* — making surfaces look distinct. This library is about *function* — making data-dense surfaces (dashboards, admin, tables, app UI) actually work once you start using them. Variety stops slop; craft stops "looks good in a screenshot, breaks the moment you use it."
>
> **When to consult:** any dashboard, admin panel, data table, activity feed, settings surface, or app UI — anything built to display or operate on data. Skip it for marketing/landing pages (those live by ARCHETYPES + brand DNA; you can get away with decorative color and sparse UI there — a dashboard cannot).
>
> **The three tells of a beginner data UI** (the spine of this library): (1) the data isn't driving the form, (2) the wrong things are shown vs. hidden, (3) the invisible UI that makes it function is missing. Each section below fixes one.
>
> Read the rules relevant to what you're building; don't pre-load all of them.

---

## A. Let the data drive the form

The shape of the data dictates the shape of the UI. Pick the form factor from what the data *is*, not from habit.

**A1 · Enumerable fields become chips** — When a column holds a finite set of values (department, status, role, tier), render them as chips, not raw text. *Why:* a closed set reads as labeled tokens; chips signal "this is one of N options" at a glance. *Tell:* status/category columns left as plain left-aligned strings.

**A2 · Right-align numbers** — Numeric columns are right-aligned so digits line up by place value. *Why:* magnitude comparison becomes visual scanning instead of reading. *Tell:* left-aligned numbers that force the eye to re-measure each row.

**A3 · Truncate to protect breathing room** — Truncate long free-text cells so they don't starve the columns that matter. *Why:* one runaway column collapses the whole table's rhythm; the full value belongs in a tooltip/expand, not the row. *Tell:* one wrapping description column squeezing everything else.

**A4 · Encode row state visually** — Shade/mute inactive, deactivated, or archived rows. *Why:* state is data; make it legible without a click. *Tell:* dead rows that look identical to live ones.

**A5 · Time-dimensioned data is a timeline, not a time-sorted table** — If the records have a time axis, a timeline reads far easier than rows sorted by timestamp. *Why:* the table format hides the thing that matters (sequence/gaps). *Do:* tuck the timeline into a sidebar pop-out, or widen it into a second column beside the table — same data, the form that fits it.

**A6 · Roll up with a summary chart** — Add a chart that summarizes the rows, especially when there's a time dimension. *Why:* a chart shows the shape instantly instead of making the user hunt through a timestamp column. *Tell:* a dense table with no overview; the user has to compute the trend in their head.

**A7 · Color comes from the data, never decoration** — In a dashboard, every color should encode meaning, not "look nice." *Examples:* a red icon/chip pulls the eye to an urgent action; an avatar lets the eye associate who-did-what faster than reading a name in a column. *Tell:* brand colors sprinkled across a data UI for vibe — landing-page logic misapplied. (This is the one rule that flips between page types: marketing pages may decorate with color; dashboards may not.)

---

## B. Hide the right things until they're needed (progressive disclosure)

There are two hierarchies. One is visual (size/weight/contrast within an element). The other is **progressive disclosure** — what you show vs. hide across time and interaction. Beginners only do the first.

**B1 · Demote infrequent actions into a popover** — A low-frequency, low-stakes action (Share, export, settings) goes in a popover, not permanently riveted to the UI, and not a full page navigation. *Why:* don't rip the user out of context for a secondary task; don't spend prime real estate on something rarely used.

**B2 · Primary visible, secondary on hover** — Inside any disclosed surface, the primary action is immediately visible (e.g. the search box at the top of a share popover); a secondary action (remove a user) appears on hover, with a tooltip. *Why:* visibility should track importance.

**B3 · The spectrum of explicitness** — Every action sits on a line from high explicitness (global, always-visible button) to low (an icon that only appears on hover; a label that's icon-only until hovered). Place each action on that line by its importance × your space budget. *Rule:* more important or more space → more explicit; less important or tighter space → less explicit. *Reference:* Apple Reminders reveals secondary actions on swipe while keeping the primary (check-off) direct.

**B4 · Onboarding is progressive disclosure over time** — Don't greet a new user with a fully loaded dashboard or a six-bullet modal (instantly forgotten on dismiss). Start with one tooltip on the single most important action; once done, surface the next, or a small corner checklist. *Principle:* "You're not hiding functionality, you're sequencing it so the user is never overwhelmed."

---

## C. The invisible UI is most of the UI

"UI is as much about what you can see as what you can't." In a dense surface, the visible layout is a fraction of the real interface — and the hidden part is what makes it function. AI and beginners both under-build this.

**C1 · Build the hidden affordances** — Dense surfaces need functionality that lives in parts you don't see until you reach for them: copy-on-hover chips over cells, a comment affordance marked by a small triangle indicator, the populated/empty/loading/error states of drawers and modals. *Tell:* a table that looks finished but does nothing once you try to operate on a cell.

**C2 · Orchestration is the work, not placement** — Spacing and sizing the visible pieces is easy; orchestrating the hidden components and states takes the thought. Budget design time for states and interactions, not just the static frame.

**C3 · A feature rarely needs its own page** — Most new features are better expressed as hidden components/states on an existing surface (popover, drawer, inline reveal) than as a dedicated page. *Why:* keeps the user in context; forces you to think through the states.

**C4 · Always add tooltips** — Tooltips are the single most common omission in beginner dashboards. Assume users won't recognize every icon and will want detail on ambiguous labels. Add them. *Tell:* a wall of unlabeled icons with no hover explanation.

---

## See also
- [SKILL.md](../SKILL.md) — design-studio mechanic; Cardinal on data-dense UI points here
- [layout-library/ARCHETYPES.md](../layout-library/ARCHETYPES.md) — STRUCTURE axis (page-level variety)
- [framework-library/FRAMEWORKS.md](../framework-library/FRAMEWORKS.md) — STACK axis
- [wrenches/ui-ux-pro-max.md](../wrenches/ui-ux-pro-max.md) — knowledge wrench; consult this stored craft library for dashboard/table/admin patterns
