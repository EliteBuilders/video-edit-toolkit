# Learnings

Corrections the operator has given that apply to **every** video, every brand, forever.
`resolve-ai-edit` reads this on preflight and treats it as binding, ranking below SKILL.md but above its own defaults.

## Rules

- One line, imperative, specific, dated.
- Only file what the operator actually said. Your inference about why they were unhappy is not a rule.
- Brand-specific taste does not go here. That belongs in that project's CREATIVE-BRIEF.md.
- One-off notes about a single video do not go here at all.
- Nothing filed here may remove a gate, a verification step, or the render approval.
- If a new learning contradicts an existing one, quote both, ask which wins, delete the loser.
- **Grouped by theme, not by date.** Past ~20 entries a flat list stops being readable and people
  stop reading it. Keep the dates on the entries; keep the headings stable.

## Baseline

- 2026-09-13 - The operator's manual baseline is 6 to 8 hours for a simple 10-minute video. Report every edit against that number, honestly, including when unflattering.

---

## The cut

- 2026-09-20 - Cut dead air and production asides, never explanation. Confirm the runtime target before cutting: dropping elaboration to shorten a video is a decision for the operator, not a default.
- 2026-09-20 - Cut on the frame the mouth closes, not on the transcript's last frame. Word-level transcription pads the end of a word; the padding ships as the speaker holding a look at the lens.
- 2026-09-20 - Trim pauses from the AUDIO, never from the transcript. `ffmpeg silencedetect=noise=-30dB:d=1.0` on the rendered file finds them in seconds; word-level transcription both buries silence inside a segment boundary and hallucinates speech across it, and it hid two 3.9s dead spots a viewer caught immediately.
- 2026-09-20 - A transcript can invent a word inside a silence. Before trusting a trailing word, check it against `silencedetect`: one stranded "and" sat entirely inside 0.5s of room tone and was never spoken.
- 2026-09-20 - Never trust part numbers in filenames to mean sequence. Diff the transcripts against each other before cutting: "Part 2/3/4" of one delivery turned out to contain two retakes of passages, each broken in the earlier take and complete in the later one.
- 2026-09-20 - Re-verify every testimonial soundbite by transcribing the EXTRACTED clip, never by trusting the in/out in a soundbite bank. Two of four had a stray leading or trailing word that changed how the line read.
- 2026-09-20 - Hide a silence trim with a short cross dissolve, not a scale change, whenever the source has no resolution to spare. A 20-30% zoom on footage already being upscaled makes the softness pulse from cut to cut; on a locked-off shot a 6-frame dissolve is invisible and costs nothing.
- 2026-09-20 - Never let Resolve conform a cross-frame-rate clip. `startFrame` is read in TIMELINE frames for one and the conversion is not a clean ratio - in-points drifted up to 42 frames. Pre-conform the clip to the timeline's exact format with ffmpeg first.
- 2026-09-20 - Declare a re-cut as a list of (frame, delta) and apply it programmatically to hand-measured graphic timings. Re-typing 40 measured frames after lengthening one segment is how one of them gets mistyped.

## Framing and camera

- 2026-09-19 - When someone writes or draws on camera, frame what they are writing. When they talk to camera, frame them. Follow the action, do not split the difference.
- 2026-09-19 - Never leave a hard jump cut between beats. Change scale 20-30% at the cut, and drift slowly in or out within each beat, alternating direction.
- 2026-09-20 - Frame per beat, not per video, whenever the camera is operated rather than locked. Measure the subject's position off gridded source frames at each beat's midpoint before setting any offset.
- 2026-09-20 - When "not centered" survives a horizontal fix, measure VERTICALLY - and measure the FACE, not the frame. A detector that latches onto a chair back or a bookshelf will report a subject as centred while their nose sits 120px off; draw a ruler on a still and read the nose.
- 2026-09-20 - **Tilt is bounded by zoom: `max |tilt| = (height / 2) * (zoom - 1)`.** Exceed it and the frame edge shows as a black bar whose height is exactly the overshoot. If the subject must move further, ZOOM more - never raise the tilt. At maximum tilt a feature `y` px down the source lands at `y * zoom`, which tells you before rendering whether a head will clear a title bar.
- 2026-09-20 - Keep the speaker's whole head in frame at every zoom level; each zoom needs its own vertical offset, and by the rule above the offset it can afford is capped.
- 2026-09-20 - Alternate scale on every hard cut within one continuous setup, but scale pan and tilt by the same ratio. They are output pixels about frame centre, so a zoom change moves the subject proportionally and un-does the centring on every other beat.
- 2026-09-20 - When type and a subject collide, the type is usually the cheaper thing to move. Shrinking a title bar by 10px of font size beat cropping the speaker to a tight head-and-shoulders that no longer matched the other speakers.

## Colour

- 2026-09-20 - One shoot is not one lighting setup. Measure a neutral in EVERY distinct location before grading, and give each its own ColorGroup - two rooms on the same shoot differed by 4.5 units of blue, and three ads shipped with a yellow cast before it was caught.
- 2026-09-20 - Estimate a white point from every bright, low-saturation pixel in the frame, never from a sample box placed by eye. Hand-placed boxes landed on a shirt, on title text and on a blue graphic across three attempts, each time giving a confident wrong number.
- 2026-09-20 - If the whole-frame white point finds too few qualifying pixels, do NOT fall back to hand-picked patches, and do NOT lower the threshold until something passes - what passes will be the subject's clothing. Take the correction from a sibling clip of the same setup and verify by eye.
- 2026-09-20 - Match the grade to what the footage IS, not to the project's house look. Flat log footage needs contrast and saturation; already-full-range camera or webcam footage needs white balance and nothing else, and the house look would crush its blacks and blow its highlights.

## Audio

- 2026-09-20 - Level-match inserted footage to the host footage BEFORE mixing, measuring each with ebur128. Testimonial bites arrived 12-18 dB hotter than the narration; a master limiter cannot fix that, it just crushes the loud part and the programme LRA gives it away (15.3 vs 4.6 once matched).
- 2026-09-20 - `ReplaceClip` refreshes a clip's VIDEO but not its cached AUDIO. Prove a re-levelled insert actually landed by measuring that region of the render, not by trusting the call's return value.
- 2026-09-20 - `loudnorm`'s JSON summary prints at INFO level. Running the measurement pass with `-v error` swallows it and the parse dies with "substring not found". Use `-hide_banner -nostats`, and assert the JSON parsed before using it.

## Captions

- 2026-09-20 - A caption cue may never span an edit. Break the grouping at every segment boundary, always - a cue that starts on one clip and finishes on the next puts one person's words over another person's face, and the reviewer sees it instantly.
- 2026-09-20 - Never end a caption cue on a function word (a, the, of, to, more, your, that...). The reader gets "a more valuable" and has to wait for the noun. Push the dangling word onto the next cue.
- 2026-09-20 - Never start a cue with the last word of the sentence just spoken. If the next word closes a sentence and still fits, absorb it rather than breaking before it.
- 2026-09-20 - A cue may not carry a sentence boundary in its middle. Any pass that MOVES a word between cues must re-check the receiving cue - the dangling-word push created blocks spanning two sentences because nothing re-examined them afterwards.
- 2026-09-20 - Strip a trailing comma or period from the last word of a caption block; the edge of the plate already does that job. Keep `?` and `!`, which are tone, and keep all punctuation mid-cue. (Supersedes the earlier comma-only version of this rule.)
- 2026-09-20 - Butt adjacent caption cues together and hand over in ~2 frames. A gap where no caption is on screen mid-sentence reads to a reviewer as a dropped frame, not as a timing choice.
- 2026-09-20 - The LAST cue on a segment runs to its cut, not to the transcriber's end-of-word. Word end times land on the last clean sample, not on the mouth closing, so a cue that stops there vanishes while the speaker is still finishing. Cap the extension so it can never hold a plate over a long tail.
- 2026-09-20 - **Clamp word durations to about a second.** A longer one has swallowed the pause behind it, and every downstream rule then goes wrong: gap detection computes zero, no break fires, and the cue holds words finished seconds ago. One 99-frame "small" caused exactly that.
- 2026-09-20 - No cue under three words. Fold a runt into whichever neighbour on its own side of the cut is shorter, so the merge evens the blocks out instead of building one giant cue.
- 2026-09-20 - Correct a mis-heard transcript word by FRAME-ANCHORED override, never by global replace - fixing "alive" to "live" must not touch a place the speaker really said "alive".
- 2026-09-20 - One generator for one set of captions. The burned captions and the sidecar `.srt` must come from the same cue list, speed-corrected for the delivered file; two generators drift and nobody notices until a viewer turns CC on.
- 2026-09-20 - A "blip" or "weird transition" a reviewer reports may be the CAPTION dropping out, not the picture cutting. Measure YMAX across the region first: burned captions are usually the only pure white in frame, so a 255 -> 237 dip with no scene change localises it in one pass.

## Graphics

- 2026-09-20 - A graphic must outlast its own build. Check that every element's reveal frame is earlier than the graphic's end - a bio card ended 95 frames before its last row was due to appear, so that row never existed.
- 2026-09-20 - Measure how long a finished graphic is actually on screen before its exit begins, in frames. A payoff diagram that read as "held" was clean for 8 frames; the caption min-duration guard does not cover graphics.
- 2026-09-20 - Every graphic exits at the next sentence boundary after its final element lands, not at a hand-guessed frame. Derive the exit from the same word timings the captions use, and only ever let it SHORTEN the hand-set end.
- 2026-09-20 - A real document or prop held on camera is the proof the video is selling. Show it first, and put any rebuilt, legible version of it AFTER - never lay the graphic over the thing it redraws.
- 2026-09-20 - A wipe or band that covers a cut must be CENTRED on the cut frame, and you must check how long it is actually opaque. Starting the tween at the cut puts the covered window after it. Verify by measuring the alpha channel at the cut frame, not by watching it.
- 2026-09-20 - GSAP's "power2" is CUBIC, not quadratic. An ease chosen for a transition that must cover a join races through the middle - power2.inOut left a full-frame band opaque for under two frames where power1.inOut gave four.
- 2026-09-20 - A group photo takes most of the frame for a few seconds or it does not go in at all; at lower-third size it is a smudge. Crop it to the card's aspect DELIBERATELY - a centre crop removed the subject from his own photo, because he stood at 83% across it.
- 2026-09-20 - Caption a photograph only as accurately as you can defend. "A recent workshop cohort" overclaims when the people in it attended a different programme; say what is true of all of them.

## Structure and offer

- 2026-09-19 - A spoken "attend my training" or "join the workshop" IS a complete call to action for a paid social ad. Do not treat a missing "link below" as a missing CTA; on Meta the click goes to the link.
- 2026-09-19 - For paid social, a different body under the same hook is a DIFFERENT ad, not another take. Decompose footage into hook / body / CTA and count deliverables that way before quoting a number.
- 2026-09-19 - Verify a claim about footage by sampling frames across the whole clip, never from one frame. A clip that looked like a blank whiteboard at its midpoint had the thesis line written onto it.
- 2026-09-20 - **Default** testimonials to AFTER the offer and the proof: social proof arriving before the viewer knows what is being sold reads as abrupt. **This is a default, not a prohibition** - clients do test proof-first cuts, and one asked for exactly that variant. When leading with proof, open on a title card naming who these people are, and build it as an ORDER over the same beat table rather than as a second cut.

## Pipeline and tooling

- 2026-09-20 - Anything measured goes in code that diffs - the cut, the cues, the grade, the loudness recipe. Never a one-off command in a chat message.
- 2026-09-20 - A variant of a film is a PERMUTATION of one canonical beat table, never a second table. Carry each measured cue to the same moment with a remap; re-measuring per variant is how two versions of one video drift apart.
- 2026-09-20 - Make every render pipeline stage resumable and cache its measurements. A 12GB ProRes intermediate plus a loudness measurement should never be recomputed because a later stage had a typo; guard stage 1 with `[[ -f "$TMP" && "$TMP" -nt "$IN" ]]`.
- 2026-09-20 - In zsh, BRACE every variable inside an ffmpeg filter string. `$SPEED[v]` parses as an ARRAY SUBSCRIPT and expands to nothing; `$LIMIT:l` parses as the LOWERCASE MODIFIER and eats the next option. Both fail late, after the expensive stage has already run.
- 2026-09-20 - Animating `scale` on a large `<img>`, and any full-frame CSS `filter: blur()`, forces Chrome to re-rasterize every frame and can make a HyperFrames capture 3-4x slower. Bake dim, blur and saturation into the source image with ffmpeg instead - identical result, no per-frame cost.
- 2026-09-20 - **Tell the operator which pipeline stage you are in, by number.** "Rendering" means nothing to someone looking at three Resolve jobs sitting at 100%; Resolve's queue never shows a finished video, and the only reliable signal is the deliverable's modified time. See `PIPELINE.md`.
