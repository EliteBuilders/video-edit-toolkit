---
name: reference-video
description: Read a reference VIDEO (a file or a YouTube link) for its graphics, animations, transitions and pacing - find every moment, let the operator pick the ones they meant, then measure each pick to the frame and file it. Use when the operator hands over a video and says "I like the animations in this", "make it look like this video", "what animations are in this", "how did they do this transition", "steal this style", "here's a reference video", or pastes a YouTube link as a style reference. Works in Claude Code and Codex. Reading a still screenshot is the edit-style skill; filing a reusable treatment is the graphics-library skill.
triggers:
  - i like the animations in this video
  - reference video
  - make it look like this video
  - what animations are in this
  - how did they do this
  - steal this style
  - watch this video for the graphics
---

# Reference video

**A reference video is read, never guessed at.** Screenshots lose the motion, and the motion is
usually why the video was sent. This skill turns "I like the animations in this" into a numbered
list of real moments, the operator's picks, and each pick's timing measured in frames.

It is **perception, then a question, then measurement**, in that order. Do not decide on the
operator's behalf which part of the video they meant.

## What it needs

- **The `claude-video-vision` MCP**, registered for Claude Code and Codex by the toolkit's
  `bin/setup.sh`, **pinned to an audited version and on the local whisper backend** (nothing
  leaves the machine). Check with `claude mcp list` / `codex mcp list`. Never install it from its
  own plugin marketplace: that floats on `@latest` and runs whatever was published last.
- **In Codex, MCP tool calls ask for approval.** Approve them in an interactive session; in a
  non-interactive `codex exec` run, pass `--approve-for-me` or the call is refused with "approval
  policy is never" (verified 2026-09-25; the same call then returned the file's duration and fps).
- `ffmpeg`; `yt-dlp` for links; `whisper-cli` for audio.
- If the MCP is not connected, use `scripts/scan_fallback.py` for the scan (below). Say which path
  you took.

## The procedure

### 1. Scan

- `video_info` (duration, fps, resolution, audio). A YouTube URL goes straight in as `path`.
- `video_analyze` with `scene_changes: true`, and `transcription: true` when the audio matters
  (the words say where a graphic is about to land). **Graphics, cards, overlays and transitions
  show up as scene changes** with scores of roughly 2 to 5 on a talking-head video.
- No MCP: `python3 scripts/scan_fallback.py <file-or-URL> --out <dir>` finds the same moments
  with ffmpeg's `scdet` (not `select=gt(scene,...)`, which only fires on hard cuts and missed every
  overlay and dissolve in testing) and writes a numbered contact sheet.

### 2. Look

`video_detail` with `segments: [{start, end, fps, resolution}]` around each change (timestamps are
`HH:MM:SS`, whole seconds) and `view_sample: 3`. Describe what is actually on screen: the element,
where it sits, how much of the frame it takes, what it is doing. **Never describe a moment you have
not extracted frames from.**

### 3. Ask

Show the operator **a numbered list of every animation found**: timestamp, one line on what it
is, and the job it does (process, comparison, spectrum, structure, who is speaking, proof, range,
labels over the speaker, beat, screen/document). Put a small frame strip with each. Ask which ones
they meant, and what about them: the look, the motion, the timing, or the idea. One answer
changes the whole extraction.

### 4. Measure the picks

The MCP finds and shows, but works in whole seconds: a 10-frame pop and a 30-frame slide look the
same at one frame a second. For each pick:

```bash
python3 scripts/motion_timing.py <video> <start-seconds> <duration-seconds> \
        [--region x,y,w,h] [--strip strip.png]
```

It prints per-frame change and every motion burst: first and last frame, duration in frames and
seconds, and the ease shape (fast-in / slow settle, slow start / fast finish, even). `--region`
limits it to where the graphic is, so a speaker moving behind it does not count. The threshold is
relative to the window's median, because a talking head never stops moving.

Verified on a known render: an end-card dissolve measured 9 frames (0.30s, ease-out), a
pull-quote reveal 14 frames (0.47s). Both matched what had been built.

### 5. File

- **This client's look** -> the `edit-style` skill, into their `EDIT-STYLE.md` (adopt / try /
  reject, dated).
- **A treatment worth reusing on any client** -> the `graphics-library` skill: cut the moment to a
  5-10s clip (`ffmpeg -ss S -t D -i video -c copy clip.mp4`, re-encode if the cut is not on a
  keyframe), drop it in the library's `_inbox/`, and catalogue it with the measured timing.
- **A one-off** -> nowhere.

## Rules

- **The system, never the design.** Take the layout, hierarchy, proportion of frame, palette
  logic and timing; build this brand's own version. Say this the first time a reference arrives.
- **Measured beats inferred.** A timing from `motion_timing.py` is written as measured, with its
  frame count. A timing read off a still is written as inferred.
- **Reference videos are often a client's or a competitor's.** Keep them local; do not switch
  the MCP to a cloud backend to save time.
- **Report in the operator's terms**: "the stat pops in over about a third of a second and
  settles", not "burst 1596-1604, peak +0".
