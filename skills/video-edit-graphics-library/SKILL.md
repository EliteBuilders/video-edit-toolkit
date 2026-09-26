---
name: video-edit-graphics-library
description: Keep and use the operator's private graphics reference library - a swipe file of how other editors display information on screen, filed by the JOB each graphic does (process, comparison, spectrum, structure, who is speaking, proof, range, labels over the speaker, beats, screen and document). Use when the operator says "add the new references to the graphics library", "add this to the library", "catalogue the inbox", "what do we have for showing a comparison", "find me a treatment for this", or when planning graphics for any video. Works in Claude Code and Codex. The library itself is private and never enters the public toolkit repo.
triggers:
  - add the new references
  - add to the graphics library
  - graphics library
  - catalogue the inbox
  - what do we have for
  - find me a treatment
  - graphics reference
---

# Graphics library

**A swipe file filed by what the graphic has to DO**, so planning a graphic starts from "show a
comparison" and lands on real examples, their system, their motion, and how to build our own.

## Where it lives

- The library is a local folder the operator owns. Its path is in this skill's `.library-path`,
  which git ignores. **Read it; never guess a location.**
- **It never goes in the toolkit repo.** The repo is public and the library holds other people's
  frames. Only this skill (the method) is committed.
- No library yet (a new machine): `bash scripts/init_library.sh <folder>` creates the folders,
  an empty `library.json`, the README and `_tools/build.py`, and records the path. It is
  idempotent and never overwrites a catalogue. Point it at an existing library to adopt it.

## The shape of it

```
<library>/
  _inbox/                     new screenshots and clips land here
  01-process-and-steps/ ... 10-screen-and-document/     one folder per job
  library.json                the catalogue: jobs + entries (the only file edited by hand)
  LIBRARY.md, gallery.html    generated; LIBRARY.md is what you read, gallery.html what the operator browses
  _tools/build.py             regenerates both and checks the catalogue
```

An entry: `id`, `folder`, `files` (several frames or clips of one graphic are ONE entry),
`source`, `layout`, `system` (what is worth taking), `motion` (measured or inferred, and it says
which), `build` (our own version, in MOTION.md scene and catalog terms), `use`, `avoid`.

## Adding references (intake)

1. Read the library's `README.md` and `library.json`. New files are in `_inbox/`.
2. A long video or a link: run the `video-edit-reference-video` skill first and keep only the moments the
   operator picks, cut to 5-10s clips.
3. Look at every file. For a clip, measure the motion with
   `video-edit-reference-video/scripts/motion_timing.py` and write it as **measured** (frames, seconds, ease
   shape). For a still, the motion is **inferred** and must say so.
4. File by **job**: move it into the matching folder, renamed
   `<what-it-shows>--<source-short>--<original-name>`. A reference that fits no job gets a new
   numbered folder and a new job in `library.json`.
5. Write its entry. Describe the system, not the brand: no client names in `system` or `build`.
6. `python3 <library>/_tools/build.py`. It regenerates `LIBRARY.md` and `gallery.html`, exits
   non-zero on a missing file, and lists anything in a job folder that is not catalogued.
7. Report what was added as a short table by job, and anything you could not place.

## Using it when planning graphics

(`video-edit-in-resolve`, MOTION.md step 4a.) For every graphic in a plan: name its job, read that
job's entries in `LIBRARY.md`, pick the one it borrows from, and write the entry id in the plan
item's `ref` (or `none` when original). Then:

- **The system, never the design.** Layout, hierarchy, how much of the frame, colour logic,
  motion. Rebuilt in this client's brand.
- **Vary.** No entry used more than ~4 times in one video; the operator notices repeated
  panels and calls it slideware.
- **Respect `avoid`.** It records when a treatment fails.
- When nothing in the library fits a job, say so and propose an original treatment. That gap is
  also worth telling the operator: it is what to collect next.

## Keeping it useful

- Ask for **clips as well as stills** when the motion is what they like. From a clip the timing
  is measured; from a still it is guessed.
- Merge duplicates into one entry; a second example of the same treatment strengthens its
  `use`/`avoid`, it does not need a second entry.
- Build after every change and fix what the build reports before handing back.
