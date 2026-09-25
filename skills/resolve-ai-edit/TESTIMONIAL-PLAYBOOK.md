# Testimonial playbook

How a raw testimonial becomes an approved edit, and how one approved edit becomes every other
format — landing-page clips, 4:5 ads and a compilation. Written from an 11-testimonial job
(September 2026): hotel-corridor 4K interviews, vertical phone selfies, Zoom/webcam recordings
and exports another editor had already cut. It shipped 11 full edits, 11 landing-page clips,
11 4:5 ads and a 9-minute compilation. **Round one went out as a batch of all 11 and every
pipeline defect came back multiplied by 11.** From round two it went one video at a time, and
each later video took one or two rounds instead of five.

Read `SKILL.md`'s Testimonial profile first — the rules there (never reorder words, never splice
two takes, figures get orange markers, written permission) still govern. This file is the
procedure and the numbers.

---

## 0. The review loop — decide it before cutting anything

- **One video per round.** Finish, verify and hand over one person (or one person's pair) before
  starting the next. The operator: *"Let's just do one at a time and really fine-tune it."*
- **The new version replaces the old in the same step.** Suffix every review file `v2`, `v3`, and
  delete the previous one when the new one lands: *"Always delete the old ones when you upload
  the new version so I can see the most up-to-date."* Never leave two versions of one video side
  by side.
- **The first approved video becomes the standard** for every other one of its footage kind.
  Name it and copy its settings; do not re-invent per person.
- Nothing goes to the delivery folder without an explicit yes. Review files live in `review/`.

## 1. Know what each source IS before touching it

Every source falls into one of four kinds, and each has different framing, motion and grading
rules. Record the kind, crop, focus and grade per clip in one config table (`tcfg.py` shape:
`kind`, `crop`/`pcrop`, `focus`, `zmin`, `zrange`, `grade`, `static`, `motion`).

| Kind | What it is | Framing | Motion |
|---|---|---|---|
| **hotel / location** | 4K camera, interviewer off-camera | Crop in SOURCE pixels, stomach-up. *"I shouldn't be able to see his legs"* | One slow move per shot (§5) |
| **pillar** | Vertical phone selfie | Belly-up crop from the full-res vertical frame with headroom for movement, the whole thing centred on a brand-colour ground. *"It's not going to fill the whole screen"* | **Static.** No zooms, no pans |
| **webcam** | Zoom / webcam recording, 720p, already chest-up | A fixed crop, which also removes the platform's name label | **Static** |
| **pre-edited** | Someone else's export | Full frame | Gentle moves (`zrange` 0.15), and their cuts count as shots (§5) |

**Checks on every new source, before any cut:**

- `ffprobe -show_entries stream=color_transfer,color_primaries`. **HLG / BT.2020 camera footage
  decoded as ordinary video goes yellow-green, and an output that keeps the bt2020 tag is decoded
  differently again by players** (the operator saw "a red tint"). Convert first
  (`colorspace=all=bt709:iall=bt2020:itrc=bt2020-10`), grade lightly, and tag every encode bt709.
- **Sample the pixel luma of the first and last ~2s at the source frame rate.** Exported clips
  arrive with fades baked onto the head, the tail, or both, and they pass every cheap check —
  frame count, duration, `start_pts=0`, no ffmpeg error. If the speech sits outside the fade, cut
  it off. If a line is spoken *during* the fade, divide the fade out per frame (it multiplies
  toward video black and scales chroma with luma, so it inverts exactly), correct one frame
  further than you keep, and end a few frames into the fade so a held last frame matches the plateau.
- **Variable frame rate** (phones average 29.997 / 30.006): conform to 30fps CFR by duplication
  (`fps=30`), never interpolation, and cut against the conform, never the original. Every later
  stage indexes frames as `t*30`.
- **Grade to what the footage is.** Camera log/HLG needs conversion plus a light grade; phone and
  webcam footage needs white balance only, no levels stretch. Judge every person's grade on frames.

## 2. The cut

Cut as text first: a decisions file per clip listing `remove` ranges with a reason each, the
interviewer's `questions` (with source time and card text), `emphasis` phrases, pull quotes,
the on-screen name and role, and per-video `phrase_fixes` for mishearings.

- **Other voices go, by diarisation, not by transcript time.** Word timings on an interview run
  up to **0.7s late**, so a cut drawn on them keeps the interviewer's "Perfect". Remove every
  stretch the diariser credits to another speaker, then **snap every cut edge into measured
  silence** on the audio. On phone clips the off-camera voice sits 15–20 dB under the subject;
  find it by level. **Proof is transcribing the finished audio**, not reading the decisions.
- **Keep the subject's own spoken intro** ("<name>, <firm>, <city>") and cut only the prompt that
  asked for it. Agents tend to cut spoken intros as slate.
- **Dead air: two passes, measured on the CLEAN (Voice Isolation) audio**, because room tone
  hides pauses on the raw track:
  - At an answer edge, always trim: the answer ends ~0.2s after its last word and starts ~0.13s
    before its first. Drop a dangling trailing "and/so", and remove word-less slivers
    (*"a jump cut to him just standing there. That can just be removed"*).
  - Mid-answer, only pauses **over 0.8s**, and never leaving a piece **under 2s**. Trimming every
    0.5s pause turned one speaker into 44 shots, some under a second, each with a zoom change.
  - **Static footage gets no mid-answer trims at all** — there is no zoom move to hide the jump.
- **Head fillers: only true fillers** (and / so / um / uh / hey, and a leading "you know,").
  Cutting "Well," off *"Well, there's so many"* left a fragment the transcriber then heard as "If".
- **A filler fused into the next word has no pause to snap to** — "Yeah, I think", "practice. So",
  "Um, I listened". Edge-snapping silently puts it back. Mark that edge **exact**, place it from a
  per-frame level trace (RMS per 1/30s; the dip between the words), and confirm with a second
  transcription of the join (`templates/tools/level_trace.py`, `edge_check.sh`).
- **A caption word is not proof it was spoken.** A transcriber heard *"that you're right,
  tripping"* across a join that was pure silence at −62 dB. The operator asked to cut "right";
  cutting harder to remove a word that was never there made the join look fake. Before cutting a
  word, check the envelope and a second transcription. If it is not in the audio, fix the caption.
- **Transcribers drop the last words of a file** ("…a whole 'nother animal" became "…a whole").
  Check the tail of every cut against a second transcription, or the edge-trim pass will read the
  missing words as dead air and cut them.

## 3. Audio

Voice Isolation at **85** on the cut audio (never an expander or gate; see `AUDIO-PLAYBOOK.md`),
proven from the file by md5 and noise floor. Render it once on the first cut; **every later
re-cut is taken from that render by copying kept segments** (8ms fades at each join), so a
re-cut never needs Resolve again unless it adds material the render does not contain. Loudness:
two-pass `loudnorm` to −16 LUFS / −1.5 dBTP for web, and **check it stayed in linear mode**
(`AUDIO-PLAYBOOK.md`); fall back to static gain plus `alimiter attack=1`.

## 4. Question cards and the end card

The interviewer's questions become **full-screen cards between answers** — not corner chips.
The operator: *"instead of having the question in the top left … we just do cut screens … a full
screen before the next question is answered."*

- Card: brand ground, a small label ("The question"), the question in italic serif, **~2s**,
  inserted INTO the timeline — the picture holds underneath, the audio is silence.
- **The card dissolves ON over the last 8 frames of the live answer**, with captions cleared
  first, and **dissolves OFF over the first 9 frames of the next answer**. The card and the
  answer after it are **one shot**: a card that faded off over a held frame at its own zoom and
  then cut to the next zoom read as *"zoomed in and then it jump cuts."*
- **The name tag clears before the first card.** A short intro gets a shorter tag, never under 2s.
- **End card on every testimonial:** a thank-you naming the person over the group photo, ~5s,
  with **0.8s of the last picture before it dissolves on** so the final line lands.
- **That lead plays LIVE footage, not a frozen frame.** A frozen last frame plus a fresh zoom move
  starting under the dissolve read as *"it cuts to just a still image and then it goes to the end
  screen."* The live run stops at the first of: the end of the source; a baked fade (stop at the
  first frame darker than 90% of the last kept one); **a cut an earlier editor made in the source**;
  and **3 frames before the speaker's next word**. The live frames play silent, so a speaker who
  carries straight on talking shows moving lips with no sound. Whatever is left is held under the
  opaque card. **The end-card stretch is never its own shot**; the last shot's move continues under it.

## 5. Motion

- **One move per shot.** Land wide (stomach-up, zoom 1.0) and push in, or land tighter (up to
  ~1.23) and pull out. Alternate, vary the amounts, and **no sideways pans**. The operator: *"we're
  just kind of panning all over the place"* and *"doesn't have to be nipple-up all the time."*
- A shot is a stretch between cuts; **a card plus the answer after it is one shot**; on
  pre-edited footage the earlier editor's jump cuts are shot boundaries too (find them with
  `select='gt(scene,0.07)'` — same framing scores low).
- Zoom downstream of Resolve (`RESOLVE-API-TRAPS.md`: Fusion transforms render inert): select the
  kept frames, loop a frame under each card, **upscale to 4× with lanczos before `zoompan`**, and
  build the zoom as eased per-phase ramps. Keep the head in frame at every zoom level.
- **Static footage joining two answers without a card** (a clip, a compilation bite): hold still
  within each answer and **step the framing in 10–12% at the join**, so the hard cut reads as a
  cut and not a jump. 10% on 720p webcams, 12% on sharper sources.

## 6. Captions and on-screen text

The shared caption rules in `LEARNINGS.md` all apply. Specific to testimonials:

- **Captions come from the FINISHED audio.** Transcribe the final cut; the transcriber's words
  are the timing source. Copy spelling and punctuation from the source transcript where they
  match, but keep the transcriber's punctuation where the source has none. A caption can then
  only show a word that is actually heard.
- **Restore a word the transcriber missed only when a second transcription hears it between the
  same two neighbours.** Timing gaps alone "restored" words that had been cut ("them", a doubled "to").
- **Butted cues hard-swap on the same frame.** A fade-out then fade-in left the plate empty for 3
  frames per change and read as flicker.
- **Settle each word's side of a join before snapping starts to onsets, and never snap across a
  join.** Otherwise a word timed across a card lands on the wrong side of it.
- Always-emphasised brand terms and names go in one list, applied on every occurrence; per-video
  mishearings go in the decisions file, frame-anchored.
- **Italic or script emphasis clips its own letters** under `background-clip:text` (an italic
  leans past its box): pad every side and give it back with negative margins, and **keep the
  left margin small** or the lean eats the word space in front ("THEGrand Canyon"). Emphasis
  that pops (scales) squeezes its neighbours for a few frames; judge spacing on a settled frame.
- **Name tag:** first name plus last initial, role (and city where known), no firm. Unnamed
  subjects get a role-only tag. **A pull quote never shares the screen with the name tag.**
- Numbers: a number plus its unit is one unbreakable token ("1-year course", "2.5 days").

## 7. The order of operations per video

```
conform → cut (diarisation + silence snap) → cut audio → Voice Isolation (render once)
→ transcribe → tighten (edge + pause trims, measured on clean audio) → re-cut → resync audio
→ transcribe again (or re-stamp if segments unchanged) → picture (moves) → overlay (captions,
cards, tags) → compose (cards' silence, loudness, bt709) → verify → review file
```

Verify before handing over: frames at the name tag, both sides of every card, a pull quote, the
end card; the start and end of every answer transcribed from the delivered audio; loudness and
true peak measured on the delivered file.

---

## Derived formats — built FROM the approved edit, never from scratch

Every derived format is **a list of kept source ranges over an approved edit**. It inherits that
edit's removes, phrase fixes, emphasis, grade, crop and Voice Isolation render. The approval
carries over and nothing is re-litigated. A derived clip's audio is cut from the same VI render,
so **its caption words are the base's approved transcription, remapped** base timeline → source
frames → clip timeline (`map_words.py` shape). Keep a word whose middle falls inside a kept
stretch, drop a sliver under half its length, and there is no re-transcription per clip.

### Short clips for a landing page (20–60s)

- Pick bites that back up what the PAGE promises (a specific client situation, the mechanism in
  their words, what they did next), not general praise. When nothing in the footage hits the
  promise, say so and propose the closest honest bites.
- **Open on the point within the first second.** Trimming a lead-in ("Well, I would say, you
  know,") before a sentence starts is fine; reordering words is not.
- One continuous answer where possible. Two answers from one person join with a hard cut and a
  zoom change (§5), never a dissolve and never a question card.
- Propose ranges as a table (speaker, source in/out, length, the words, why it fits) and get a
  yes before building. Deliver in their own review subfolder.

### 4:5 ads (1080×1350)

- **Ask whether the ad is the clip or the whole testimonial.** Here the operator wanted the
  full testimonial: *"these are going to be ads so I just want to play the whole testimonial."*
- **Reframe from the ORIGINAL pixels, never by cropping the 16:9 edit.** Hotel 4K: a 4:5 window
  about 1.12× the 16:9 crop's height. Phone: 1080×1350 straight from the vertical frame. Webcam
  and pre-edited: **the full source height**, which is the widest 4:5 without bars. Same grade,
  same fps conversion, so frame n of the 4:5 conform is frame n of the 16:9 one and every cut
  list applies unchanged. Check that frame counts match; a composite can drop one final frame.
- **Face-track the narrow crops.** *"His head is not centered … since he's moving we probably
  need to do a little bit of face tracking."* Detect every 0.2s, fill gaps, take a 1.4s median then
  a 2.4s average, sample every 0.5s, and clamp so the window never reveals a platform label
  (`templates/tools/facetrack.py`). Drive the crop with **`sendcmd`**: an ffmpeg expression fails
  past ~40 piecewise terms.
- **Chest-up, head centred, no bars.** If a source is framed head-only (a webcam user sitting
  close), full source height is the ceiling. Say so rather than letterboxing.
- **Pull zoom back on tight sources** (pre-edited: zoom 1.0, range ≤ 0.08). *"Too zoomed in."*
- Layout: shorter caption lines (≤ 30 characters at ~46px on a 1080-wide frame, ≤ 48 for a
  sentence-finishing second line), captions low (bottom ~110px), the name tag at collar height
  (bottom ~250px). At the 16:9 height it sat on a close-up speaker's chin. The end card becomes
  **the group photo as a full-width band on top, fading into the brand colour, words below**:
  cover-cropping a 16:9 group photo to 4:5 left six of the people.

### A compilation (5–10 min)

- **Propose the lineup as a table first** (bite, speaker, the line, length, the order) and get a
  yes. Keep claims-heavy bites flagged for sign-off.
- **For an ad: quick hits, hard cuts, no chapter or question cards.** *"I don't even think we
  need to create the cards or have the questions … quick hits of their experience."* Open with an
  **overlay** over the first speaker, not a full-page card (*"not a full-page card, because that's
  not going to get attention"*), for ~4s. Put it **at chest height, not the top**: every source
  has the face in the top third. Hold the first name tag until it clears.
- Each speaker gets a name tag on first appearance only (match by person, not by source). One
  person filmed twice is one speaker.
- Every bite is its own derived clip (no end card, no card inside). Check each bite's first and
  last word by transcription, fixing fused fillers with exact edges. Assemble with plain concat,
  one dissolve into a group thank-you card, and one final linear loudness gain.
