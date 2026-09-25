# video-edit-toolkit

Three Claude skills for editing video in DaVinci Resolve Studio, building motion graphics as
code, and getting closer to what a client actually wants with every pass.

**This is the edit layer and nothing else.** No research, no packaging, no titles, no thumbnails,
no scripting. It cuts what is in front of it, whatever that is and wherever it runs.

| Skill | What it does | When |
|---|---|---|
| `video-creative-brief` | Ten-question interview producing `BRAND.md` and `CREATIVE-BRIEF.md` | Once per brand, before any footage |
| `edit-style` | Turns a dropped screenshot or reference into a dated, extracted decision in `EDIT-STYLE.md` | Every time an example is handed over |
| `reference-video` | Reads a reference video or YouTube link: finds every animation, the operator picks, each pick measured to the frame | "I like the animations in this video" |
| `graphics-library` | Keeps the operator's private swipe file of on-screen graphics, filed by the job each does, and uses it when planning | "Add the new references"; every graphics plan |
| `resolve-ai-edit` | Six gated stages: ingest, rough cut, polish, QA, review-then-render, debrief | Every video |

## Start here

New to this repo? Read in this order:

1. **`skills/resolve-ai-edit/PIPELINE.md`** — how the machine is wired. Three programs, not one:
   HyperFrames renders the graphics, Resolve renders an *intermediate*, ffmpeg makes the file a
   human watches. **Resolve's render queue never shows you a finished video** — that one fact
   confuses everybody once.
2. **`skills/resolve-ai-edit/SKILL.md`** — the six gated stages and the QA checklist per video type.
3. **`skills/resolve-ai-edit/VSL-PLAYBOOK.md`** — the ordered procedure for long-form sales
   video, the most expensive type to get wrong. Settle it on a still, in a text file, or in the
   timeline — before rendering a frame.
4. **`skills/resolve-ai-edit/AUDIO-PLAYBOOK.md`** — what to do when audio is the note, in order.
   Echo, level, speaker balance, loudness. Every number in it was measured and every mistake in
   it was actually made.
5. **`skills/resolve-ai-edit/LEARNINGS.md`** — craft rules earned from real corrections, grouped
   by theme. Binding.
6. **`skills/resolve-ai-edit/RESOLVE-API-TRAPS.md`** — verified Resolve 21.1 behaviour that
   contradicts the documented stubs. Silent write failures, mostly.
7. **`skills/resolve-ai-edit/templates/tools/`** — a caption generator and a delivery script with
   the traps already fixed. Copy them into a project rather than writing your own.

## It carries no client

Everything about a specific brand lives in that brand's **project folder**, never in a skill. The
same three skills cut a client testimonial, a paid ad and an in-house YouTube video, each in its
own brand, because each reads its own folder.

```
<client>/video/<project>/
  BRAND.md            colours, type, layout zones, loudness       (mechanical spec)
  CREATIVE-BRIEF.md   viewer, promise, feel, pacing, prohibitions (stable intent)
  EDIT-STYLE.md       every reference shown, extracted and dated  (visual evidence, grows)
  SPOT-BRIEF.md       ads and testimonials: offer, claim, CTA, sign-offs
  BROLL.md            which B-roll sources are enabled
  reference/          the actual screenshots and frames behind EDIT-STYLE.md
  raw/ output/ assets/ graphics/kit/ broll/candidates/
```

**A client's work belongs in that client's own folder.** If they do not have one, create it.
Never in this repo.

## The three files, and why they are separate

Keeping them apart is what stops the brief becoming an unreadable log:

- **`BRAND.md`** answers *what are the values* — a hex code, a typeface, a safe zone. Mechanical,
  rarely changes, no judgment required to apply.
- **`CREATIVE-BRIEF.md`** answers *what is this supposed to feel like* — the viewer, the promise,
  the pacing, the prohibitions. Stable intent. Changes when the brand moves.
- **`EDIT-STYLE.md`** answers *what have they actually shown us they like* — append-only, dated,
  each entry naming the reference file it came from and what it supersedes. This is the one that
  grows, and it is why the fifth edit for a client is closer than the first.

## What it asks before touching media

Type and platform, every time, never inferred from a folder name: is this a YouTube long-form, a
Short or Reel, a paid ad, a testimonial, a case study, a screen recording — and where does it
run? The type sets the structure, the platform sets the format, and one video for three platforms
is three deliverables rather than one file someone crops later.

## Requirements

- **DaVinci Resolve Studio 21.1+**, running, reachable over its native MCP server. Studio
  specifically — 21.1 removed Python scripting from the free edition, so free Resolve cannot
  drive this at all. Two settings inside Resolve are not optional and `setup.sh` cannot set them:
  **Preferences > General > "External scripting using" = Local**, and **File > Setup AI
  Assistants**. Without the first, the MCP connects and nothing can touch the timeline.
- **bun.** HyperFrames is a bun workspace whose packages depend on each other through
  `workspace:^`, which npm cannot resolve at all. `brew install oven-sh/bun/bun`.
- **HyperFrames** for motion graphics — `github.com/heygen-com/hyperframes`. Apache 2.0, fully
  local, no API key: HTML and CSS with timing attributes, rendered through headless Chrome and
  ffmpeg. Installed by `./bin/setup.sh`. Ignore the hosted MCP — it needs a HeyGen account and
  renders on their infrastructure for the same result.
- Animated captions need nothing extra — Resolve Studio ships Word Highlight, Slide In, Rotate,
  Lollipop and Statement on the subtitle track. **Do not rebuild in HyperFrames what Resolve
  already does.**
- **Video vision** (optional, recommended): `claude-video-vision`, an MIT MCP server that pulls
  frames and a transcript from a local video or a YouTube link, so a reference *video* ("I like
  the animations in this") can be read, not just a screenshot. `setup.sh` registers it **pinned to
  an audited version and on the local backend** (whisper.cpp; nothing leaves the machine). Its own
  plugin installer floats on `@latest`; do not use it. Needs `whisper-cpp`, and `yt-dlp` for links.
- Optional, and the only thing that costs money: AI B-roll generation, gated behind a cost
  estimate and an explicit yes.

## The process

Five phases, gated. Nothing starts before the previous one is approved.

| # | Phase | What happens |
|---|---|---|
| 1 | **Intake** | Type, platforms, whose it is, what it must achieve — then the look, asked for in *examples* rather than adjectives |
| 2 | **Cut** | Transcribe, cut list as text, then the timeline |
| 3 | **Polish** | Pacing, B-roll, grade, audio, captions |
| 4 | **Graphics** | Reference loop, then motion graphics as code, placed and checked |
| 5 | **Deliver** | QA, human review, one render per platform, debrief |

**To run the whole thing:**

> Use the resolve-ai-edit skill. Run the full process from intake. Start with preflight and
> report it before touching anything.

To resume: *"pick up at polish"*. To run one piece: *"just build the cut list"*.

## Installation

```
./install.sh        # symlink the skills
./bin/setup.sh      # once per machine: Resolve MCP + HyperFrames + ffmpeg check + video vision (Claude + Codex)
bash skills/graphics-library/scripts/init_library.sh <folder>   # once: create or adopt your graphics library
```

`setup.sh` clones HyperFrames from `github.com/heygen-com/hyperframes` to `~/Tools/hyperframes`,
installs its dependencies, records the path, and runs `npx davinci-resolve-mcp setup`. Idempotent;
it never touches an existing clone.

Symlinks the skills into `~/.claude/skills` (Claude Code) and `~/.codex/skills` plus
`~/.agents/skills` (Codex), so every skill works in both, and editing one here is live in the next session
with no re-install. Installs post-merge and post-checkout hooks so a pull that adds a skill makes
it invocable.

### Starting a project

```
./bin/new-project.sh <path-inside-the-client-folder>
```

Scaffolds the folder layout and copies in the templates. Idempotent, and it never overwrites a
`BRAND.md`, `BROLL.md` or `EDIT-STYLE.md` that has already been edited.

## Portability

The skills are plain Markdown with no Claude-specific syntax beyond the frontmatter, so another
assistant can read them as a procedure. Two things do not travel: `~/.claude/skills` is a Claude
Code convention, and driving Resolve needs that MCP server connected in whatever tool is running.
A tool without it can follow the method but cannot touch the timeline.

## Relationship to youtube-toolkit

`youtube-toolkit` runs a YouTube channel — research, architecture, planning, greenlighting,
packaging. Its workflow hands off to this repo after recording and picks the video back up for
packaging afterwards. **They install independently and neither needs the other**; a client with
ads and testimonials and no channel at all only needs this one.

Read `MAINTENANCE.md` before editing any skill. `DECISIONS.md` records why the edit layer is
shaped the way it is — read it before changing a rule, because several exist due to a specific
approach that was tried and failed.
