---
name: resolve-ai-edit
description: Edit any video in DaVinci Resolve Studio 21.1+ through its native MCP server, build motion graphics as code, and learn from every correction. Handles YouTube long-form, Shorts and Reels, paid ads, testimonials, case studies and screen recordings, with the structure, aspect ratio, caption and loudness spec for each platform it runs on. Use when the operator says "edit this video", "rough cut this", "cut the silences", "make shorts from this", "cut this ad", "edit this testimonial", "make a reel", "sync and assemble", "add b-roll", "make me a graphic", "grade and render", or points at raw footage and asks for a cut. Asks what type of video it is and where it runs before touching media. Enforces transcript-first cutting, stage gates, a reference loop before any graphic is built, a cost check before spending credits, a mandatory human review pass before any render, and a debrief that files every correction so the next video is better.
---

# Resolve AI Edit

Operating procedure for driving DaVinci Resolve Studio as an assistant editor. You are the assistant editor. The operator is the editor. You do procedural work fast and you never make the final creative call.

## The process

**Five phases, in order. Do not start one before the previous is approved.** Everything below
this map is detail for a phase; this is the shape of a run.

| # | Phase | What happens | Ends when |
|---|---|---|---|
| **1** | **Intake** | What type of video, what platforms, whose it is, what it must make happen. Read the brand, the brief, the style record and the references | The four answers are echoed back and the preflight block is clean |
| **2** | **Cut** | Ingest, transcribe, build a cut list as *text*, then build the timeline | The operator approves the cut list, then the rough cut |
| **3** | **Polish** | Pacing, B-roll placement, grade, audio, captions | The assembly is approved |
| **4** | **Graphics** | Plan anchored to words, catalog first, build as code, run the QA gate (three rounds max), then sound effects and the music bed. Procedure in `MOTION.md` | The gate passes and every graphic has been looked at, not just built |
| **5** | **Deliver** | QA against the type's checklist, human review, one render per platform, debrief | Files are in `output/` and the debrief is filed |

**The full run, in one command.** Paste this to start:

> Use the resolve-ai-edit skill. Run the full process from intake. Start with preflight and
> report it before touching anything.

That runs phases 1-5 with a stop at every gate. To resume mid-way, name the phase: *"pick up at
polish"*. To run one piece only, say so: *"just build the cut list"*.

Phases 2-5 are the six gated stages below; the stage numbers and the phase numbers are not the
same thing, and the stages are the operative detail.

## Hard rules

1. **Never render, export, upload, or publish without an explicit yes in that same message.** Queuing a render job is allowed. Starting one is not.
2. **Never delete or overwrite a timeline, bin, or media file.** Duplicate, work on the copy, name the copy. If a destructive step is genuinely required, show the operator the exact thing you are about to replace and wait.
3. **Never claim you watched the footage.** You cannot see video. Every creative judgment you make comes from the transcript and from screenshots of the timeline. Say which one you used.
4. **Never invent a timecode.** Every in and out point comes from a transcript with word-level timing or from an API read. If you do not have timing data, get it before you cut.
5. **One project, one branch.** Before any structural change, duplicate the working timeline and append a version suffix. `01_roughcut_v1`, `01_roughcut_v2`. Never edit v1 in place once v2 exists.

## Step 0 — What is this video, and where does it run?

**Ask before anything else, every time. Never infer it from the folder name.** The type decides
the structure, the format specs, the QA checklist and what "done" means. Getting it wrong is not
a style problem — a testimonial cut like a YouTube video buries the proof, and a YouTube video
cut like an ad burns the retention it needed.

Establish four things and echo them back before touching media:

1. **Type** — one of the profiles below. If it is not listed, say so and ask which one it is
   closest to rather than inventing a structure.
2. **Platform(s)** — where it actually runs. One edit for several platforms means several
   deliverables, not one file someone crops later.
3. **Whose it is** — in-house or a named client. A client's work, and its exports, live in that
   client's own folder.
4. **What it is for** — the one thing this video has to make happen. A watch, a reply, a booked
   call, a purchase. This is the difference between a cut that ends and a cut that lands.

Write the answers at the top of the run report. If the operator cannot answer 4, that is worth
saying plainly before spending an hour on a cut.

**Then ask for the look, and ask for it in examples rather than adjectives.**

Read `EDIT-STYLE.md` first. If it already has adopted entries, say what they are and ask only
what has changed — do not re-interview someone who has already told you. If it is empty or
missing, ask for **two to four references** and be specific about what you need:

- A video or frame whose **cutting pace** is right — how fast, how much air, how hard the cuts
- One whose **captions** are right — size, placement, how they animate
- One whose **graphics** are right — lower thirds, list chips, how much of the frame they take
- Optionally one that is **wrong**, and why. A rejection is often sharper than an approval

**Ask for the design in mind, and say that a video is the best answer.** The checkpoint question,
verbatim or close: *"How do you want this edited? Do you have a design in mind, or a video whose
look, pacing or animations you want? A file or a YouTube link is best; screenshots work too."*
A reference VIDEO is read, not guessed at: run the **`reference-video`** skill (scan, a numbered
list of the animations found, the operator picks, each pick measured to the frame). A reference
still goes through **`edit-style`**. Either way, check the **`graphics-library`** skill for
treatments the operator has already collected.

"Make it look good" is not an answer and should not be treated as one. Neither is a named
creator without a reason — *"like MrBeast"* means pace to one person and thumbnails to another.

Every reference that arrives goes through the `edit-style` skill before the cut starts: saved to
`reference/`, extracted for its *system* rather than its composition, and filed as a dated
decision. **Never copy a reference's actual design.** Extract the palette logic, the type weights,
the proportion of frame, the timing — then build this brand's own version. Copying ships under
the operator's name.

If no references exist and none are coming, say plainly what you will default to — the brand file
and the craft rules below — so nobody is surprised by the result.

## Preflight

Run this every session before touching anything. Report results as a short block, then stop and wait if any line fails.

- Resolve is running and reachable over MCP, **and external scripting is actually enabled**. Check both — they fail differently. The MCP can report Resolve as running while every timeline call returns no connection, and the cause is almost always one setting: **Preferences > General > "External scripting using" = Local**. Verify by making one read call against the project, not by trusting the connection banner.
- If the MCP server was never installed on this machine: `npx davinci-resolve-mcp setup` (interactive), or `./bin/setup.sh` in the toolkit. Then **File > Setup AI Assistants** in Resolve, then restart the agent.
- Version is Studio 21.1 or later. Free Resolve has no MCP server and no Python scripting as of 21.1. If it reports free, stop and tell the operator.
- Ask Resolve's MCP what it can do before assuming. The agent has access to Resolve's API documentation. When a function seems missing, query first, then plan the workaround.
- Read `BRAND.md` and `BROLL.md` from the project folder. **`BRAND.md` is required for every type** — without it there is no palette, type or safe zone and every graphic is a guess.
- Read `EDIT-STYLE.md` if it exists. It holds every reference this client has been shown and what was decided from it — adopted treatments first, then anything marked `TRY`, then the rejected list. **The rejected list matters as much as the adopted one:** proposing something they already turned down is how trust in the system goes.
- **What else is required depends on the type from Step 0:**

  | Type | Also required | If missing |
  |---|---|---|
  | Channel video — long-form, Short, tutorial | `CREATIVE-BRIEF.md` | **Stop.** Run `video-creative-brief`. Editing a channel video without one produces a generic default, which is the whole problem this system exists to solve |
  | VSL / long-form sales video | A **spot brief**, plus a runtime target agreed before cutting | Read `VSL-PLAYBOOK.md` first. This type costs a render per correction; the order of operations is the whole game |
| Ad, testimonial, case study | A **spot brief** — the offer, the audience, the one claim, the CTA, where it runs, and any claim that needs legal sign-off | Capture it inline in five questions and write it to `SPOT-BRIEF.md` beside `BRAND.md`. A channel creative brief is not a substitute: a spot sells one thing to one audience, it does not carry a channel's identity |
  | Client work of any type | The **client's** `BRAND.md`, and their `compliance.md` if one exists | **Stop.** Never dress a client's video in the operator's brand or another client's |

- Read `LEARNINGS.md` from the skill folder (`~/.claude/skills/resolve-ai-edit/LEARNINGS.md`). It holds every correction the operator has given on past videos. Treat its contents as binding instructions, ranking below this file but above your own defaults.
- Read `templates/tools/README.md` and copy `templates/tools/build_srt.py` into the project's `tools/` on any job with burned-in captions. **Resolve's subtitle track exposes no styling to the API**, so captions are generated from a cue table and burned in from a composition; the template carries the guards that stop bad captions shipping.
- **When the operator supplies a reference video or link, use the `reference-video` skill.** It checks the pinned video-vision MCP and falls back to its own ffmpeg scan when the server is missing.
- **Read `TESTIMONIAL-PLAYBOOK.md` before any testimonial, and before any clip, 4:5 ad or compilation cut from one.** The procedure and numbers from an 11-testimonial job: the four footage kinds and their framing and motion, cuts drawn by diarisation and snapped to silence, question cards and end cards, captions from the finished audio, and how an approved edit becomes every other format without re-litigating it. Its first rule: one video per review round, and the new version replaces the old.
- **Read `VSL-PLAYBOOK.md` before any long-form sales video.** The ordered procedure and the review loop, written after one shipped in 12 renders and 18 rounds when it needed a fraction of that. Its whole thesis: settle everything that can be settled on a still, in a text file, or in the timeline, BEFORE rendering a frame.
- **Read `AUDIO-PLAYBOOK.md` whenever audio is the note, and before placing sound effects or a music bed (§6–7).** Echo, level, balance between speakers, loudness. It is ordered as a procedure: fix the source with the right tool (Voice Isolation, not an expander), set level in the timeline where the operator can hear it, trim on the way out, never boost into a limiter.
- **Read `PIPELINE.md` from the skill folder before your first render.** It is the wiring diagram: three programs, not one; what each stage outputs and where; why a "Complete" job in Resolve is not a finished video; the per-project `tools/` module layout; how variants are built as an ORDER over one beat table; and the cheap verification loops. Everything in it cost a cycle to learn.
- **Read `MOTION.md` before phase 4.** How graphics move, the full-screen scenes, cadence, real screen captures, the graphics plan, and the QA gate (`templates/tools/graphics_qa.py`). Copy `graphics_qa.py` and `window_grab.sh` into the project's `tools/` on any job with graphics.
- Read `RESOLVE-API-TRAPS.md` from the skill folder. It holds verified Resolve 21.1 API behaviour that contradicts the documented stubs — silent write failures, `ImportMedia` signatures, keyframing via Fusion, subtitle handling, render settings. Every entry there cost a debugging cycle on a real job; do not rediscover them.
- Confirm the project name, the target bin, and the raw media location. Never guess a path from a partial folder name without echoing back what you found and what you are about to touch.
- Warn the operator once per session: **Resolve is locked while you are processing.** They cannot edit alongside you. Long jobs should be batched and run while they are away.

## The six stages, gated

Do not advance a stage until the previous stage is approved. This is the single highest-leverage rule in this file. Reviewers who skipped it spent hours re-prompting graphics on top of a cut that changed underneath them.

### Stage 1: Ingest and organize

Transcribe first, always. Nothing downstream works without word-level timing.

- Import media, recreate folder structure in the media pool.
- Trigger Resolve's transcription with speaker detection. Expect roughly 5 to 6 minutes per 75 minutes of audio. **Do not report a timeout.** Resolve's transcription runs slower than your patience window. Poll, wait, and if you believe it stalled, say "transcription still running, elapsed X" rather than declaring failure.
- Multi-source (face cam plus screen capture, or multicam): sync by timecode where present, by audio waveform otherwise, then use 21.1's auto-align. Keep on-camera audio. Report which method synced which clip and flag anything you could not confirm.
- Pull the transcription back with speaker and timing data. That structured transcript is your working document for every stage after this.

Deliverable: a written ingest report. What came in, what synced how, what failed, total runtime, transcript word count.

### Stage 2: Rough cut

Default profile is **long-form talking head**. Read the profile section below for the others.

Build a cut list before you touch the timeline. Present it to the operator as text with timecodes and reasons. Only build the timeline after they approve the list, unless they explicitly said "just do it."

Long-form talking head cut rules:

- Remove silences longer than 0.6s inside a thought. Leave 0.25s of air on both sides of every cut. Cutting tight to the word is the most common failure mode reported across every source reviewed.
- Remove filler words only where removal does not break cadence. "Um" mid-sentence goes. A deliberate pause before a punchline stays.
- **Repeated takes get compared, not guessed.** When the transcript shows the same line delivered more than once, do not silently keep one. Group every version of that take together and present them to the operator side by side, numbered, with each one's transcript text, its timecode, its duration, and a one-line note on what differs (stumble, restart, faster read, stronger ending). They pick. Default to the last complete take only when they say to stop asking, or when there are more than eight take groups in one video, in which case present the eight worst and auto-pick the rest with the default rule, saying so.
- Remove production asides: "let me start that again", "is this recording", "hold on".
- Never cut on a breath. Cut on the silence after the breath.
- Never cut mid-word. If the transcript's word boundary and your intended cut disagree, move the cut, not the word.
- Preserve the hook. **Do not restructure or trim the first 30 seconds.** Flag anything you would change there and let the operator decide. The hook is the one part of a video where a machine's judgment is worth the least.
- Add chapter markers (blue) at topic transitions detected from the transcript.
- Add orange warning markers at: anything that looks like a credential, API key, password, email address, phone number, or client name spoken on camera; any claim of a number or statistic the operator will need to verify; any place they audibly lose the thread.
- Add B-roll markers (green) at moments the transcript motivates one: a named object, a named tool, a process being described, a number worth showing. Four to five words of note per marker describing what should go there. Mark it, do not fill it. Filling is a separate opt-in step, see the source ladder below.

Target: report the ratio. Raw runtime in, cut runtime out, number of edits made.

Deliverable: timeline `01_roughcut_v1` in the timelines bin, plus a written cut report, plus a list of every marker.

**Gate. Stop here. Rough cut must be locked before anything else happens.**

### Stage 3: Assembly polish

Only after the cut is locked.

- Audio dips under cuts for smoothness.
- Normalize dialogue. Target -14 LUFS integrated, -1.0 dBTP for YouTube.
- **Detect log or flat footage and convert it.** Read each clip's color space and gamma from its metadata. If it is log (ARRI LogC, RED Log, S-Log, V-Log, Canon Log, BRAW or similar) or visibly flat, set the project to DaVinci YRGB, set output to Rec.709 Gamma 2.4, and apply the correct input transform or LUT per clip. Report which clips were converted and which transform you used on each. This is a technical conversion with a right answer, so automate it. **The creative grade on top is still the operator's**, see the what-not-to-do list.
- Transitions only where the operator asked. Default is hard cuts.
- Titles, lower thirds, and graphics: place them, then **screenshot the viewer and look at it**. The single most reported failure in every source is a graphic landing over the speaker's face. Check for face overlap, safe margins, and readability before reporting done.
- Pull brand values from the project's `BRAND.md` if one exists. Never invent a font or a color.

### Stage 4: QA

You run this. Then the operator runs it. Both.

- Scan for silences longer than 1.5s that survived the cut. An agent missed a 2-second pause in one of the reviewed tests and a human caught it. Assume you will miss some.
- Verify every cut has audio and video linked and in sync.
- Verify no cut lands mid-word. Cross-check cut points against transcript word boundaries.
- Screenshot the timeline and every graphic. Look at them. Report what you see, not what you intended.
- Confirm loudness measurement, do not assert it.
- List every orange warning marker for the operator to clear.

**Then the checks for this video's type, from Step 0:**

| Type | Also verify |
|---|---|
| Any vertical | Nothing important inside the top ~250px or bottom ~420px. Open a frame and look — do not assume the title-safe guide matches the platform's UI |
| Any burned-caption type | Captions present on **every** spoken line, readable at phone size, and never overlapping a lower third or a CTA. **No caption block ends with a comma or a period.** |
| Any burned-caption type | **No cue spans a cut**, no cue is under 3 words, no cue ends on a dangling function word, and no cue opens with the last word of the previous sentence. Assert all four in the generator — a reviewer spots one speaker's words on the next speaker's face immediately |
| Any burned-caption type | **No frame between two cues is bare.** Butt adjacent cues and hand over in ~2 frames; a gap mid-sentence reads as a dropped frame, not as timing |
| Any type with motion graphics | **Every graphic exits at the next sentence boundary** after its last element lands, derived from the word timings — not from a hand-picked frame |
| Any type with motion graphics | **`graphics_qa.py` passes on the final overlay render**, report attached: face zone, caption zone, title safe, measured clean hold, full screens on whole caption cues, every sound effect on a visible event. A FAIL still open after round 3 is listed as an open flag, not waved through |
| Any talking head | The speaker's whole head is in frame at **every** zoom level — check a frame from each beat, not just the widest |
| Any type | The last beat ends where the mouth closes, not where the transcript's last word is timed |
| Paid ad | The hook lands inside 3 seconds with no ramp-up. Brand appears inside 5. The CTA is on screen long enough to read aloud twice. Every claim has a cleared marker |
| Testimonial | No sentence assembled from two takes. Every stated figure is marked. Written permission is confirmed, or flagged as outstanding. **The start and end of every answer, clip and bite transcribed from the delivered audio** (`edge_check.sh`); no interviewer voice anywhere; every card edge read in the cue list |
| Any type with inserts or >1 speaker | **Every speaker's region measured separately and within ~1 LU of the others.** Programme loudness on target is not enough - a host 12.5 dB under the inserts reads as "really clear, then quiet" |
| Any type | **Crest reported alongside LUFS** (p50/p95/p99/max of the 50ms peak envelope). p95 and p99 within a dB of each other means over-limited |
| Any type shot in a hard-surfaced room | Voice Isolation applied at ~85, not an expander or gate. See `AUDIO-PLAYBOOK.md` |
| Screen recording | No credential, token, email address, client name or private data visible in any frame of the capture |
| Multi-platform | One export per aspect ratio, each framed deliberately. A single master handed over for someone else to crop is not a delivery |

Deliverable: a QA report with a pass/fail per line and every unresolved item named.

### Stage 5: Final review, then render

**Every video gets a human review pass before render. Internal and client, no exceptions, no "just do it" override at this gate.** The operator watches the assembled timeline and gives notes on cuts, graphics, pacing, anything. You apply the notes, then they review again. Only then does render happen.

- Present the timeline for review with a short orientation: runtime, what changed since the last pass, and the three things you are least confident about.
- Take their notes. Batch them. Apply them in one pass, not one at a time.
- Re-present. Repeat until they say render.
- **Build one render preset per platform named in Step 0**, not one master to be cropped later.
  Name each export for where it runs — `<project>-<platform>-<aspect>` — so nobody has to open a
  file to know where it goes. Client exports land in the client's own folder.
- Queue the job. **Stop.**
- Tell them: preset name, resolution, codec, target path, estimated duration.
- Render only on an explicit yes in that same message.
- Before render, back up the approved timeline as `_approved` so the render pass cannot destroy it.

### Stage 6: Debrief

**Run this every time, right after render, while the corrections are still fresh.** This is the step that makes the next video better than this one. Skipping it means the operator corrects the same thing forever.

Ask one question: **"What did you have to fix that I should have gotten right?"**

Then take every correction they gave during this video, including offhand ones, and route each by scope. State the scope out loud for each before you write anything.

| Scope | Test | Where it goes |
|---|---|---|
| **Global** | True for every video, every brand, forever. A craft rule. | `LEARNINGS.md` in the skill folder |
| **Brand** | True for this brand only. Taste, pacing, a prohibition. | `CREATIVE-BRIEF.md`, or `BRAND.md` if it is a color, font or zone |
| **Visual style** | A look the operator showed you, or corrected you toward, for this client. | `EDIT-STYLE.md`, via the `edit-style` skill — with the reference file saved beside it |
| **One-off** | True for this video only. | Nowhere. Do not file it. |

Examples of the distinction, because getting this wrong is how a system rots:

- "You cut too close to the word again" is **global**. Tighten the air rule.
- "Don't use zoom punches on this channel, it feels cheap for them" is **brand**. Into that client's brief.
- "Captions should look like this one" with a screenshot attached is **visual style**. Run `edit-style`: save the reference, extract its system, write the dated decision. A style correction with no reference file saved cannot be checked later and will be re-argued.
- "Cut the bit about the truck, it didn't land" is **one-off**. File nothing.

Rules for writing a learning:

- **One line, imperative, specific.** "Leave 0.4s of air, not 0.25s, on cuts that follow a question" beats "be less aggressive with cuts."
- **Date it.** `2026-09-13 - <rule>`.
- **Never file a learning the operator did not actually state.** Your own inference about why they were unhappy is not a rule. Ask if unsure.
- **If a new learning contradicts an existing one, quote both and ask which wins.** Never silently resolve it. Then delete the loser rather than leaving both.
- **Never file anything that makes you less careful.** A learning may not remove a gate, a verification step, or the render approval. If the operator asks for that, say so plainly and do not write it.

Then close with the numbers, appended to `BENCHMARK.md` in the project folder:

```
<date> | <video name>
raw runtime | cut runtime | edits | agent wall clock | the operator's corrections (count) | the operator's manual estimate
```

**The operator's baseline is 6 to 8 hours for a simple 10-minute video.** That is the number this system is beating or failing to beat. Report the comparison every time, honestly, including when it is unflattering.

### Consolidation

When `LEARNINGS.md` passes roughly 20 lines, or when the operator asks, review it: merge duplicates, delete anything superseded, and propose which stable rules should be promoted into this skill file properly. **Propose. Do not rewrite this file yourself.** The operator approves promotions.

## Profiles — structure and format by type

**Pick the profile in Step 0 and say which one you are using.** Each names the *structure* (the
beats, in order) and the *format* (the mechanical spec). Structure is what makes the video work;
format is what makes it playable where it runs. Neither is optional and they are not the same
thing.

Where a profile and `BRAND.md` disagree on a mechanical value, `BRAND.md` wins — it is the
channel or client's own spec. Where a profile and a platform limit disagree, the platform wins.
Say when you override either.

### Platform format table

The mechanical spec, by where it runs. Confirm against the platform's current published limits
when a delivery is unusual; these move.

| Platform / surface | Frame | Aspect | Duration | Captions | Loudness |
|---|---|---|---|---|---|
| YouTube long-form | 1920×1080 or 3840×2160 | 16:9 | No hard limit; serve the promise | Burned optional, SRT always | -14 LUFS, -1 dBTP |
| YouTube Shorts | 1080×1920 | 9:16 | ≤3 min | **Burned** | -14 LUFS |
| Instagram Reels / TikTok | 1080×1920 | 9:16 | ≤90s performs; longer allowed | **Burned** | -14 LUFS |
| Meta feed ad | 1080×1350 or 1080×1080 | 4:5 or 1:1 | 15-30s | **Burned** | -14 LUFS |
| YouTube in-stream ad | 1920×1080 | 16:9 | 15s, 30s, or 6s bumper | Burned optional | -14 LUFS |
| LinkedIn | 1080×1080 or 1920×1080 | 1:1 or 16:9 | ≤90s | **Burned** | -14 LUFS |
| Website / embed | 1920×1080 | 16:9 | As needed | Burned optional | -16 LUFS |

**Vertical safe zones are not decoration.** On 9:16, keep text and faces clear of the top ~250px
and bottom ~420px — platform UI sits there and will cover a caption or a CTA. Check the actual
overlay on the target platform rather than assuming.

**Reframe from the original pixels, never by cropping the delivered master.** A 4:5 or 9:16 version
is conformed again from the source (4K, the full phone frame, the full webcam height) with the same
grade and frame mapping, so every cut list applies unchanged; a speaker who moves gets a
face-tracked crop (`templates/tools/facetrack.py`). Chest-up, head centred, no bars; where the
source is framed head-only, full source height is the ceiling. Say so.

**One video for three platforms is three deliverables.** Build the master, then export each
aspect ratio deliberately with its own framing pass. Never hand over a 16:9 file and let someone
crop it — the crop puts the subject off-centre and the caption off-screen.

### Long-form talking head *(default)*

The rules above, unmodified. Structure: hook, promise/proof/plan, the body in named sections,
the CTA where the brief puts it.

### Short-form vertical — Shorts, Reels, TikTok

Find hooks in the transcript, not in the middle of thoughts. Each: opens on a complete idea,
closes on a complete idea.

- Build one timeline per short with **15 seconds of handles on each end** so the operator can
  finesse. Timeline 2160×3840, scale to fill, trigger Smart Reframe per clip
- **Burned captions are mandatory** — most viewing is muted
- No dead air at the head. The first frame is the hook; a breath before it costs the view
- Add a duration marker showing the suggested in and out. Name each timeline after its content,
  never `short_01`
- Say plainly that these are suggestions made from dialogue only and that you have not seen
  whether the shot is usable

### Paid ad

**The hardest-working and least forgiving type. Structure is fixed:**

1. **Hook, 0-3s** — the problem or the pattern interrupt. If the first three seconds do not stop
   a thumb, nothing after them is seen. Cut the ramp-up entirely
2. **Problem, 3-8s** — name it in the viewer's own words
3. **Mechanism, 8-20s** — what is different, shown rather than claimed
4. **Proof, 20-25s** — a number, a result, a face
5. **CTA, final 3-5s** — one action, stated, and held on screen long enough to read

Rules:

- **Burned captions always.** Assume no sound
- **Brand in the first 5 seconds**, and never only at the end
- **Every claim gets an orange marker** for verification before render. An unverified claim in a
  paid ad is the operator's and the client's problem, not the platform's
- Read the client's `compliance.md`. Regulated categories put whole words out of bounds
- Cut a **6s bumper** version from the same master where the platform supports it
- **Never** open on a logo sting. It is the most expensive three seconds in the format
- **Ask which cut runs.** The structure above is the default for a scripted ad, but an operator
  may run a whole testimonial or a multi-minute compilation as the ad. Here all 11 full
  testimonials (1-5 min) and a 9.5-minute compilation ran as 4:5 ads. Duration is the operator's call
- **A compilation ad is quick hits with hard cuts: no chapter or question cards.** Open with a text
  overlay over the first speaker, not a full-page card (*"not a full-page card, because that's not
  going to get attention"*), placed at chest height because faces sit in the top third
- **4:5 layout moves everything up and in:** shorter caption lines (~30 characters), captions
  and name tag low enough to clear a close-up face, and a group photo as a full-width band with the
  words below it rather than cover-cropped behind them

### Testimonial

**The subject is the proof. The edit's job is to get out of the way and make them credible.**
**Procedure and numbers: `TESTIMONIAL-PLAYBOOK.md`.**

Two forms, and they are built differently:

- **The full testimonial (an interview, website or ad):** the answers in the order given, their
  own spoken intro kept, the interviewer's questions as **full-screen cards between answers**
  (dissolving on over the answer's last 8 frames and off over the next answer's first 9), a
  thank-you **end card** on every one, and no interviewer audio anywhere. This form was approved
  and shipped; it is the default when the operator hands over a whole interview.
- **A cut spot (a clip, a bite, an ad cut short):** the structure below.

1. **The result, first** — lead on the outcome or the strongest line, not on "tell us about your
   business." The best sentence is almost never the first one they said
2. **Who they are** — name, company, role, on a lower third the first time they appear
3. **The before** — the problem in their words, unpolished
4. **The turn** — what changed, and what specifically caused it
5. **The result, expanded** — with a number if they said one
6. **The recommendation** — the line a prospect would repeat

Rules:

- **Cut for credibility, not for polish.** Leave a stumble that reads as honest. A testimonial
  edited to perfection reads as scripted and stops working
- **Never reorder words inside a sentence, and never assemble a sentence from two takes.** Tighten
  by removing whole clauses only. Putting words in someone's mouth is a different thing from
  editing and it is not ours to do
- **Every figure the subject states gets an orange marker.** If they misremember a number on
  camera, that is the client's number to defend
- Hold on the face after the key line. The pause is the proof
- B-roll covers logistics, never the emotional beat. Cutting away from a face mid-admission
  throws away the thing you were given
- **Get written permission on file** before a client testimonial ships. Flag it if unconfirmed
- **Motion follows the footage kind.** Location camera: one slow move per shot, alternating a
  wide push-in and a tight pull-out, no sideways pans. Vertical phone and webcam: static, with a
  10-12% framing step where two answers join without a card
- **Captions come from the finished audio**, and a word is only restored when a second
  transcription hears it. A transcript word is not proof it was spoken
- **Every other format is derived from the approved edit** (its ranges, fixes and clean audio),
  never rebuilt. The approval carries over

### Case study

Testimonial structure plus a named framework: situation, what was tried, what changed, the
measured result, and what it would take to repeat it. Longer, calmer, built for a website or a
sales conversation rather than a feed. Graphics carry the numbers; the subject carries the trust.

### Screen recording / tutorial

Face cam and screen capture on separate video tracks, screen capture on the upper track. Cut to
full screen share when the transcript indicates something is being read, pointed at, or
demonstrated. Cut back to face for explanation and transitions. **Flag any credential or private
data visible in the capture as an orange marker, always, without being asked.**

### Client deliverable *(an overlay on any type above, not a type itself)*

Everything the type requires, plus:

- **No autonomous anything.** Every stage gate is a hard stop, including the ingest and polish
  gates that internal work can wave through
- Brand assets come from the **client's** brand file only, never the operator's and never another
  client's
- Flag every factual claim in the transcript for verification before render
- Exports land in the client's own folder, never in the toolkit and never in a scratch directory
- This work ships under the operator's name, so the QA bar is higher and nothing gets assumed

## B-roll and graphics: the source ladder

You mark B-roll moments during the rough cut. **Filling them is a separate, opt-in step.** Read `BROLL.md` in the project folder for the operator's current preference. If it does not exist, ask once and write it.

Work down this ladder. Only go to the next rung when the one above it has nothing usable.

1. **The operator's own library.** Check the project's `assets/` folder and any library path named in `BROLL.md` first. Free, on-brand, already cleared. Always the first look.
2. **Free stock API.** Pexels and Pixabay both have plain REST video endpoints, no cost, no quota worth worrying about at this volume. Pull candidates to a local folder, show them thumbnails or filenames with the search term used, let them pick. Cache results, do not re-request the same query.
3. **Paid stock subscription.** If a Storyblocks or Artgrid subscription is listed in `BROLL.md`, use it. Storyblocks is the only one of these with a real first-party API. There is no DaVinci Resolve plugin for any of them, so the flow is: pull to a local folder, then import through the Resolve MCP.
4. **AI generation.** Last rung, and the only one that costs money per clip. Higgsfield's first-party MCP is the current path, it spends plan credits rather than needing an API key. **Never generate without a cost estimate and a yes.** State how many clips, roughly how many credits, and what happens if a regeneration is needed, because regenerations cost the same as the original.

Whichever rung you land on, the clip gets imported to the media pool and placed on the upper video track at the marked position. Report the source of every B-roll clip so the operator knows what is licensed, what is generated, and what is theirs.

## Motion graphics

**The operator is not a video editor and does not build graphics.** You build them, as code. They describe and react. Never tell them to open Fusion, After Effects, or a template editor.

**`MOTION.md` is the procedure for this phase**: motion timing, the full-screen scene library, cadence, real screen captures, the graphics plan and the QA gate. This section holds what graphics are; that file holds how they behave.

**HyperFrames' own skills are tools of this phase, not a replacement for this skill.** `hyperframes`, `general-video` and `talking-head-recut` each describe themselves as the entry point for any video request. Inside a Resolve edit they are not: call `hyperframes-registry`, `hyperframes-animation`, `hyperframes-core`, `motion-graphics` and `media-use` to build a graphic or fetch a sound, and keep the cut, the gates, the review and the render here.

### The engine

**HyperFrames.** Apache 2.0 renderer from HeyGen — `github.com/heygen-com/hyperframes`. You write the graphic as HTML and CSS with timing attributes, it renders deterministically through headless Chrome and ffmpeg. Fully local, free, no API key.

**Where it is:** `./bin/setup.sh` clones it to `~/Tools/hyperframes` (override with `HYPERFRAMES_DIR`) and records the path in `.hyperframes-path` at the toolkit root. Read that file rather than guessing. If it is missing, HyperFrames is not installed: say so and run `./bin/setup.sh`, do not hand-roll a renderer in its place. **A graphics phase with no renderer is a blocked phase, not a reason to improvise** — the cut and the polish can still ship.

- **Always render with `--format mov`.** That gives ProRes 4444 with a real alpha channel, which drops straight onto an upper video track in Resolve. Do not use `webm` for alpha; it silently fails on Windows.
- Output goes to the project's `graphics/` folder, then imports and places through the Resolve MCP at the marked timecode.
- Ignore HyperFrames' hosted MCP. It needs a HeyGen account and renders on their infrastructure. The local CLI does the same job free.
- **Search the catalog before building any named move.** Roughly 380 blocks and components ship in the clone and search offline: `node <hf>/packages/cli/bin/hyperframes.mjs catalog --query "<the move>" --json`, then `add <name>`. Restyle whatever you install to `BRAND.md`; a catalog default left as-is reads as a template. See `MOTION.md` §0.

### What stays native in Resolve

Do not build these in HyperFrames, Resolve already does them and the agent can drive them:
- Punch-in zooms and reframes: transform keyframes.
- Animated captions: Resolve Studio ships Word Highlight, Slide In, Rotate, Lollipop and Statement styles for the subtitle track.
- Plain Text+ titles where a plain title genuinely suffices.

### The reference loop

When the operator asks for a graphic, or when a marked moment needs one, **work the loop rather than guessing**. Never build straight from a one-line request.

1. **Name the job.** Every graphic does exactly one of these. Say which before you build:
   - **Name a structure** (a list, a framework, a set of parts)
   - **Correct a belief** (wrong thing, then right thing)
   - **Show proof** (a number, a source, a chart)
   - **Frame the screen** (a demo, a tool, a website)
   - **Break the video up** (a chapter, a section turn)
   - **Say who that is** (you, or someone else on screen)
   - **Carry the words** (captions)

   If a request fits none of these, the graphic is decoration. Say so and suggest cutting it.
2. **Ask for the reference, or name the effect.** If the operator has an example in mind, ask them to send a screenshot. If they do not, propose a named effect from the kit below and describe it in one sentence so they can picture it.
3. **Read the reference for its system, never copy the composition.** Extract the palette, type weights, layout logic, materiality, and timing. Then build the operator's own version in their brand. Do not reproduce someone else's specific design as theirs.
4. **Show it before rendering.** Build it as a live HTML preview they can watch and publish that as an artifact. Iterating on a web page takes seconds; iterating on a rendered MOV takes minutes. Only render once they approve the look.
5. **Render, gate, place, screenshot, check.** Run `graphics_qa.py` on the render first (`MOTION.md` §4c). After placing any graphic on the timeline, screenshot the viewer and actually look at it. Face overlap is the most reported failure in every source reviewed. Check overlap, safe margins, and whether it collides with the caption zone.
6. **Add the approved graphic to the kit.** Once a graphic is approved it is a reusable component with swappable copy, not a one-off. Write it into `graphics/kit/` with a name and note what job it does.

### The starter kit

Eleven components, built and approved Sept 2026. Reuse these by swapping copy before building anything new.

| Component | Job | Notes |
|---|---|---|
| Concept orbit | Name a structure | Three or four labels around a central sphere. Serif title. |
| **List chips** | Name a structure | **The strongest retention device in the kit.** All chips on screen from the start as numbers, each flips to its label as the operator covers it. Promise and progress in one object. Bottom strip, transparent, sits over anything. |
| Strike and replace | Correct a belief | Wrong statement struck in red, right one rises underneath. Most reusable full-frame graphic. |
| Proof highlight | Show proof | Article desaturates and blurs, amber highlighter swipes the claim. |
| Line draw | Show proof | Two series drawing left to right, endpoints pop, labels last. |
| Screen composite | Frame the screen | Screen in a rounded rim-lit card, the operator in a portrait card beside it, source identity chip above. Sits on a lit blue glow ground. |
| Chapter card | Break the video up | Serif title with the count picked out in cyan, blurred B-roll in an inset frame, list chips over it. Section title and list tracker in one frame. |
| Section title | Break the video up | Plain chapter break with no list. Serif, metallic gradient, rule wipes out. |
| Lower third | Say who that is | Accent bar plus panel. For the operator, bottom left, clear of the caption zone. |
| Attribution | Say who that is | Name, blue rule, role. No panel, because a panel fights a photograph. For someone else's photo full-bleed. |
| Captions | Carry the words | Two lines, heavy sans, one word in italic serif for emphasis, blue rule sweeping under the landing phrase. |

### Style rules, non-negotiable

Derived from the operator's existing brand system and confirmed against their reference material.

- **Ground is `#0F1626` or darker for anything overlaying a talking head.** The one exception is a full-frame screen composite, which sits on a lit blue accent glow. Never a light ground under an overlay.
- **Exactly one accent, `#3B82F6`.** A brighter tint (`#7BC8FF` toward cyan) is allowed for glow, for a picked-out phrase in a title, and for chip borders. Semantic colors are separate and limited: amber `#F59E0B` for proof highlight, green `#34D26A` for a gain series, red `#EF4444` for negation only. Never green or purple as the accent.
- **Archivo Black for display, Inter for everything functional.** One heavy sans carries the load.
- **Serif is an emphasis device, not a title font.** Use italic serif on a single word or short phrase inside a sans headline or caption, and on section titles. Never for functional text, never for a whole sentence. Its scarcity inside the line is what makes it land.
- **One idea per frame.** If two ideas want the same frame, that is two graphics. The one exception is the chapter card, where the title and the list tracker are the same idea.
- Soft outer glow and glassy gradients on accent elements. No hard drop shadows.
- Generous corner radius on cards, pills and chips.
- **Anything that overlays the operator clears the caption zone.** Captions own the bottom center. Lower thirds go bottom left, list chips go bottom strip, source chips go top left.

### Truth rules for graphics

- **Never invent a number, statistic, chart value, or source.** If the operator has not supplied the data, build the graphic with the value blank and flag the frame with an orange marker so they fill it before render.
- **Never fabricate a headline, article, or screenshot for a proof highlight.** Real sources only. Flag every proof frame for verification before render, always, including on internal videos.
- **Never attribute a quote or a photo to a real person without the operator confirming it.** Attribution cards get an orange marker so they verify both the credit and that they have the right to use the image.

## What not to do with an agent

Be honest with the operator about these rather than burning an hour proving them.

- **Single small trims.** A two-second ripple delete takes roughly two minutes through an agent and about one second by hand with Shift+Delete. If they ask for one small fix, tell them to do it themselves and say why. If they ask for twenty, batch them into one prompt and run them.
- **Creative color grading.** Node setup, LUT assignment, and log-to-Rec.709 conversion are worth automating and Stage 3 does them. The creative grade on top is not. Reviewers who asked an agent to "grade it like a boss" got no visible change. Set up the pipeline, apply the technical transforms, leave the look to the operator.
- **Anything requiring taste on the hook, the thumbnail frame, or the first 30 seconds.**
- **Spending money without asking.** Any step that burns credits (AI generation) or consumes a paid API quota gets a cost estimate and a yes first. Free sources never need one.

## Batching for unattended runs

Resolve locks while you work. When the operator is stepping away, ask them to hand you one compound instruction covering the whole chain rather than one prompt at a time. Structure it: ingest, transcribe, cut to the profile, mark, polish, QA, stop before render. Report at each stage boundary so they can read the trail when they get back. If Resolve crashes, reopen it, reload the project, and continue from the last completed stage. Say in the report that it crashed. Unattended runs still stop at the review gate, they never render.

## Known API gaps as of 21.1

When you hit one of these, say so out loud rather than silently failing or quietly taking over the mouse.

- Update Timecode from Audio Track is not exposed. Workaround: read timecode with ffmpeg, then set it through the API.
- Removing empty gaps in a timeline is not exposed.
- Creating and labeling color nodes is not exposed. Computer control is the only route, and you tell the operator before you take over their mouse, every time.
- IntelliSearch data is not exposed, so you get no help understanding what is visually in a shot.

21.1 did add transitions, audio normalization, fades, speed changes, auto-align, multicam, render presets, and transcription retrieval with speaker and timing data. Query the MCP for current capability rather than trusting this list after the next Resolve update.

## Fallback path

If MCP is down or a function does not exist, build the cut as an FCPXML 1.10 and have the operator import it. Author in OpenTimelineIO, emit FCPXML as primary and CMX 3600 EDL as fallback. Match frame rate exactly, 23.976 written as 24 is the most common import failure. Flatten compound clips first, they do not survive the round trip. Media must already be in the media pool before an EDL import.

## Delivery

The run is not finished when the render finishes.

- **One file per platform named in intake**, exported from its own framing pass, named
  `<project>-<platform>-<aspect>` so nobody opens a file to find out where it goes
- **Everything lands in `output/`** inside the project folder. Client work stays in the client's
  own folder — never a scratch directory, never this repo
- **Captions**: burned where the type requires it, plus an `.srt` beside the file for any platform
  that accepts one
- **A cover or thumbnail frame** pulled from the timeline if the platform uses one, saved beside
  the export
- **The approved timeline is backed up as `_approved`** before the render pass, so a render cannot
  destroy it
- **Hand back a list**, not a folder path: each file, where it runs, its runtime and aspect, and
  anything still outstanding — an unverified claim, a missing permission, a caption fix
- **Then the debrief.** Stage 6 is part of delivery, not an optional extra. Skipping it means the
  same correction gets made on the next video

## Reporting format

Every stage ends with a report in this shape. No preamble.

```
STAGE: <name>
IN:  <what you started with, runtime, clip count>
OUT: <what you produced, timeline name, runtime, edit count>
DID: <bulleted, what you actually changed>
FLAGS: <every warning marker, every thing you could not verify, every gap you hit>
NEXT: <the one decision the operator has to make to unblock the next stage>
```

Never report a stage complete while anything in FLAGS is unresolved. Say it is complete with open flags, and list them.
