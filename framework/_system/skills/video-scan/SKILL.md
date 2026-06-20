---
name: video-scan
description: Transcribe + screenshot a video on demand. yt-dlp for download, ffmpeg for frames, native YouTube captions as primary transcript source, Whisper (Groq/OpenAI) as fallback only when no captions exist. Frame analysis routed to Codex (ChatGPT subscription, not Claude tokens). Renamed from video-watch per the consolidation. Trigger phrases include "scrape this video", "get the transcript", "screenshot this video", "video-scan", "the scraper skill", "extract from youtube", "transcript and frames", "watch this video for me".
---

# video-scan — video transcription + frame extraction

The user pastes a YouTube URL (or local video file). This mechanic returns:

- Full transcript (native captions when available, Whisper fallback)
- Key frame screenshots
- Optional frame analysis (description of what's on screen at timestamps)

Per AGENTS.md hard rule #5, frame analysis routes to Codex (his ChatGPT subscription) — not Claude tokens. The yt-dlp + ffmpeg work is local; the heavy multimodal lifting is on Codex's tier.

---

## Cardinals

1. **Native captions first.** YouTube's auto-captions are free, fast, accurate enough for ~95% of use. Don't Whisper-transcribe a video that has good native captions — wasteful.

2. **Whisper fallback only when needed.** When no captions exist OR captions are clearly bad (heavy accent, technical jargon, etc.), fall through to Whisper via Groq (free tier) or OpenAI (paid).

3. **Frame analysis to Codex.** Multimodal vision is Codex's job here per the hard rule — frees Claude tokens for everything else.

4. **Don't analyse every frame.** For a 30-minute video, sample every 60-120 seconds, OR at chapter boundaries (yt-dlp can extract chapter metadata), OR at user-specified timestamps.

---

## When this fires

- YouTube URL pasted with extract / transcript / screenshot / "watch this" request
- "scrape this video" / "get the captions" / "what's this video about"
- Local video file + transcript/screenshot ask

Don't fire when:
- The user wants a polished video summary as a deliverable → that's a different lane (was `video-lens`, now CUT per DECISIONS_LOCKED; not replaced)
- The user wants to curate videos for the morning briefing → that's `morning-briefing/video-curator`

---

## Sequence

```
1. yt-dlp metadata: title, duration, chapters, available captions
2. Decide caption source:
   - Native YouTube captions exist + look clean → use them
   - No captions OR low quality → Whisper via Groq/OpenAI
3. Download + transcribe
4. Sample frames: every N seconds OR at chapter boundaries OR user-specified timestamps
5. ffmpeg extracts frames to /tmp/<slug>/frame-<ts>.jpg
6. If frame analysis requested:
   - Dispatch to Codex (multimodal vision) with the frame batch
   - Codex returns timestamped descriptions
7. Assemble output:
   - Transcript with timestamps
   - Frame URLs / paths with timestamps + descriptions
   - Metadata (title, duration, channel, chapters)
```

---

## Output shape

```markdown
# <Video title>

**Channel:** <name>
**Duration:** <hh:mm:ss>
**URL:** <youtube url>

## Chapters
- 00:00 — Intro
- 02:14 — Main topic
- 12:30 — Demo
- 18:45 — Q&A

## Transcript
[timestamped lines]

## Key frames
- [00:30](/tmp/<slug>/frame-30.jpg) — <description from Codex>
- [02:14](/tmp/<slug>/frame-134.jpg) — <description>
- ...
```

---

## Cost shape

- yt-dlp + ffmpeg: trivial (local)
- Native captions: free
- Whisper fallback: Groq free / OpenAI paid (depends on the user's tier)
- Frame analysis: Codex multimodal (his subscription, NOT Claude tokens)
- Claude's role: orchestration + assembly only — very low

Per hard rule #5, this routing keeps the Claude bill near zero while the user gets the deliverable.

---

## See also

- [`AGENTS.md`](../../../AGENTS.md) — hard rule #5 (Codex tier for multimodal frame analysis)
- [`router/wrenches/codex.md`](../router/wrenches/codex.md) — dispatch mechanics
- [`morning-briefing/wrenches/video-curator.md`](../morning-briefing/wrenches/video-curator.md) — different lane: curation, not scraping
