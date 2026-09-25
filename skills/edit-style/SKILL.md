---
name: edit-style
description: Capture an editing-style reference — a screenshot, a frame, a link, a clip someone liked or hated — read it for its system rather than its content, and write what was extracted into that client's EDIT-STYLE.md so the next edit starts closer. Use when the operator drops in an example and says "make it look like this", "I like how they do captions", "this is the vibe", "don't do what they did here", "here's a reference", "use this style", or hands over a screenshot mid-edit. Also use to review what a client's accumulated style record now says before starting an edit. A reference video goes to the reference-video skill; a general treatment for any client goes to the graphics-library skill.
triggers:
  - here's a reference
  - make it look like this
  - this is the vibe
  - i like this style
  - use this style
  - edit style
  - style reference
  - what's this client's style
---

# Edit Style

**The mechanism that makes the next edit better than this one.** An edit gets closer to what
someone wanted when the system has seen what they actually like — not described in words, but
shown. This skill turns a dropped screenshot into a written, dated decision that
`resolve-ai-edit` reads at preflight.

One `EDIT-STYLE.md` per client project. It grows. It is the visual evidence; `CREATIVE-BRIEF.md`
stays the stable statement of intent, and `BRAND.md` stays the mechanical spec.

## The rule that matters most

**Read a reference for its *system*, never copy its composition.** Extract the palette logic, the
type weights and pairing, how much of the frame the graphic occupies, the materiality, the
animation timing, the pacing. Then build this client's own version of that system.

Reproducing someone else's specific design is not a style decision, it is copying, and it ships
under the operator's name. Say this out loud the first time a reference is supplied, then extract
rather than trace.

## Intake — every time a reference arrives

1. **Take the file.** Save it into the project's `reference/` folder, named
   `<YYYY-MM-DD>-<what-it-shows>.png`. A link gets a screenshot saved the same way, plus the URL
   recorded — links rot, and a style decision that cannot be re-examined is a rule with no reason.
   If it is a video or a YouTube link, hand it to the **`reference-video`** skill: it finds every
   graphic moment, the operator picks, and each pick comes back as a clip, a frame, timecodes and
   measured timing.
2. **Ask one question: what about this?** A reference handed over without a reason is ambiguous —
   the same frame can be shown for its captions, its grade, its pacing or its layout. Do not guess.
   "The captions" and "the way they hold on the face" lead to entirely different extractions.
3. **Look at it properly.** Open it. Describe what is actually there before deciding anything:
   how many elements, where they sit, the type sizes relative to frame height, the colours as hex
   where readable, how much empty space, what the eye lands on first.
4. **Extract the system, in writing.** Three to six lines. Mechanical and reusable, not
   impressionistic. "Two-line caption, roughly 6% of frame height, heavy sans, one word in italic
   serif" is usable. "Clean modern look" is not.
5. **Decide the scope, and say it out loud** before writing anything:

   | Scope | Test | Where it goes |
   |---|---|---|
   | **Adopt** | This becomes how we do it for this client from now on | `EDIT-STYLE.md`, as a dated decision |
   | **Try** | Worth one video to see | `EDIT-STYLE.md`, marked `TRY`, with what would confirm it |
   | **Reject** | Shown as an example of what *not* to do | `EDIT-STYLE.md` under Rejected, with the reason |
   | **One-off** | This video only | Nowhere. Do not file it |

6. **Write it.** Append to `EDIT-STYLE.md`. Never rewrite an earlier entry — supersede it, and say
   which entry it replaces.
7. **Check it against what already exists.** If the new reference contradicts a `BRAND.md` value, a
   `CREATIVE-BRIEF.md` prohibition, or an earlier adopted entry, **quote both and ask which wins.**
   Never silently resolve it. A style record that quietly contradicts itself is worse than none,
   because the editor follows whichever line they read first.

## Where a reference goes

- **This client's `EDIT-STYLE.md`**, when it is about THIS client's look ("make ours look like
  this"). That is this skill.
- **The operator's graphics library**, when it is a general example of how to DISPLAY a kind of
  information, useful on any client ("add the new references to the graphics library"). That is
  the **`graphics-library`** skill.
- **A reference VIDEO or link** is read by the **`reference-video`** skill first; its picks then
  come back here or go to the library.

## What a good entry looks like

```markdown
### 2026-09-18 — Caption treatment
**Reference:** `reference/2026-09-18-caption-style.png` (frame from a competitor short, 0:04)
**Shown for:** the captions
**Extracted:**
- Two lines maximum, never three. Breaks on the phrase, not the line width
- Cap height roughly 6% of frame height — large enough to read at thumb size
- Heavy sans, one word per caption in italic serif for emphasis
- Sits in the bottom third but clear of the platform UI zone
- Word-level highlight on the beat, not a fade
**Decision:** ADOPT for all short-form on this client.
**Supersedes:** 2026-08-02 caption entry (three lines, centre).
**Why:** the operator has corrected caption length on three consecutive videos.
```

## Before an edit starts

`resolve-ai-edit` reads `EDIT-STYLE.md` at preflight. When asked what a client's style is, read
the file and answer from it — adopted entries first, then anything still marked `TRY`, then the
rejected list, because knowing what was ruled out and why prevents proposing it again.

**If the file is long, propose a consolidation rather than doing one.** Merge duplicates, retire
superseded entries, and promote the stable rules into `CREATIVE-BRIEF.md` where they belong as
intent. Propose. The operator approves.

## What this skill does not do

- **It does not edit.** That is `resolve-ai-edit`.
- **It does not invent a style.** No reference, no entry. An extraction from nothing is a guess
  wearing a date.
- **It does not carry one client's style to another.** Every client's record is theirs. A treatment
  that worked elsewhere may be *proposed* with its source named, never applied silently.
- **It does not touch packaging, titles or thumbnails.** Different job, different skill, different
  repo.

---

## Keeping this skill current

**When something notable is learned, update this file at its root** — not in a note or a chat log.
A correction about how a *client* likes their edits goes in that client's `EDIT-STYLE.md`. A
correction about how *extraction itself* should work goes here.
