---
name: video-edit-creative-brief
description: Build or update the creative brief and brand guidelines for a video channel, before any editing or graphics happen. Use when starting a new video project or client channel, onboarding a client's brand, or when the operator says "set up the brief", "update the brand guidelines", "new client channel", "what's our creative direction for X", or asks why videos for a brand do not feel consistent. Interviews rather than guesses, and writes BRAND.md and CREATIVE-BRIEF.md that video-edit-in-resolve reads on every run.
---

# Video Creative Brief

This runs **before** any footage is touched. It produces the two files that give a channel its personality: `BRAND.md` (what it looks like) and `CREATIVE-BRIEF.md` (what it feels like and why).

Without these, every video gets edited to a generic default and every client's channel looks like every other client's channel. That is the failure this skill exists to prevent.

## Hard rules

1. **Interview, never assume.** You do not know a client's brand. Ask. One question at a time, wait for the answer, write it down before asking the next.
2. **Never invent a color, font, or logo.** If the operator does not have the value, write `TODO` and say what you need. A guessed hex code that ships on a client video is worse than a blank.
3. **Never copy another channel's look as the deliverable.** References are read for their *system* (palette logic, type weights, pacing, materiality), then a version is built in this brand. Say this out loud when a reference is supplied.
4. **Write as you go.** After each answered question, append to the file. Never batch the whole interview and write once at the end. Operators work in short bursts and get interrupted.
5. **The brief belongs to the channel it is for.** An in-house system — the operator's own channels, or a previous client's — is a starting shape at most, never a default to apply to a paying client. Different buyer, different brief.

## Two modes

Decide which before you start, and say which you picked.

**NEW** - no `CREATIVE-BRIEF.md` exists in the project folder. Run the full interview.

**UPDATE** - the files exist. Do not re-interview. Ask what changed, change only that, and record the change with a date at the bottom of the file under `## Revisions`. If the change contradicts something already in the file, quote both lines and ask which wins before writing.

## The interview

Ten questions, in this order. The order matters: strategy before taste, because taste questions answered without strategy produce decoration.

Skip any question the operator has already answered in this conversation. Never ask two at once.

### Strategy

1. **Whose channel is this, and who is it talking to?** Name the brand and describe the viewer in one sentence. Not a demographic, a situation. "A contractor who is good at the work and cannot figure out why the phone is quiet" beats "males 35 to 55."
2. **What is the promise of the channel?** If someone subscribes, what do they expect every time? This is what the graphics are in service of.
3. **What should a viewer feel in the first ten seconds?** One or two words. Urgency, relief, curiosity, respect, being caught out.
4. **What does this brand absolutely never do?** The prohibitions define a brand more sharply than the permissions. Hype, jargon, moralizing, fake scarcity, talking down.

### Voice and pacing

5. **How fast does this move?** Tight and relentless, or measured with room to breathe. This sets silence thresholds, cut density, and how often graphics appear.
6. **How much does the viewer already know?** Beginner, practitioner, or peer. This sets whether terms get defined on screen and whether graphics explain or just reinforce.

### Look

7. **Do you have a brand kit?** Colors as hex, fonts by name, logo file. Take what exists, write `TODO` for what does not. If they have a website, offer to pull the palette and type from it and confirm rather than guess.
8. **Send three to six reference frames.** Screenshots from channels whose edit style fits, or from the client's own existing material. **Read them for system, not composition:** palette logic, type weights and pairing, how much of the frame graphics occupy, materiality, animation timing. Write down what you extracted and which decisions it drove.
9. **What already exists that we must match?** Existing thumbnails, a website, a deck, printed material. Consistency with what the audience already sees beats a fresh idea.

### Operations

10. **Who approves, and what can never ship without a human?** For a client this is non-negotiable and usually stricter than the operator's own work. Record the name and the gate.

## What you write

Two files in the project folder.

### `BRAND.md`

The mechanical spec the editor reads on every run. Sections, in order:

- **Which brand** - name, one-line description, and the URL if there is one
- **Color** - a table of token, hex, and what it is used for. Mark the single accent explicitly. Semantic colors listed separately with the rule that they never become decoration
- **Type** - a table of role, typeface, weight. State any scarcity rules (for example, a display serif that only appears in two places)
- **Layout zones** - which overlay owns which part of the frame, so components never collide. Captions, lower third, list chips, source chips
- **Ground rule** - what backgrounds are allowed and when
- **Assets** - logo paths, safe areas, anything on disk
- **Loudness** - target LUFS and true peak

### `CREATIVE-BRIEF.md`

The judgment layer. The editor reads this when a decision is not covered by the mechanical spec. Sections:

- **The viewer** - the one-sentence situation, not a demographic
- **The promise** - what a subscriber expects every time
- **The feel** - first ten seconds, in one or two words
- **Pacing** - tight or measured, and the concrete numbers it implies: silence threshold, air on either side of a cut, roughly how often a graphic appears
- **Knowledge level** - and whether terms get defined on screen
- **Never do** - the prohibition list, in the client's words where possible
- **Reference read** - what was extracted from the supplied frames, and which decisions it drove. Keep this, because a year from now nobody will remember why the accent is that blue
- **Approval** - who signs off and what cannot ship without a human
- **Revisions** - dated log of every change made after the first version

## The personality paragraph

End `CREATIVE-BRIEF.md` with one paragraph, written in plain prose, that an editor could read cold and produce something that feels right. Not a summary of the sections above. The thing underneath them.

Then read it back and ask whether it sounds like the brand. If they hesitate, it is wrong. Rewrite it before anything else happens.

## Handing off

Once both files exist, say plainly:

- Which questions are still `TODO` and what is blocked by each
- That `video-edit-in-resolve` will read both files on preflight
- That the first graphic built for this brand should be previewed as a live HTML page before anything renders, so the brief gets tested against something visible rather than staying theoretical

## Client work

For a paying client, three extra rules.

- **Nothing is assumed from the operator's own brand.** Not the palette, not the type, not the pacing. Different buyer, different channel.
- **The brief is a deliverable.** It is a sellable artifact in its own right and it is what makes their channel look like theirs rather than like a template. Say so if the operator is scoping the engagement.
- **Every factual claim the client makes about themselves gets flagged** for verification before it appears on screen. Numbers, credentials, client counts, guarantees. This ships under the operator's name.
