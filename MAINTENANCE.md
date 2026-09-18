# Maintenance

These skills encode decisions that were wrong the first time and got corrected. That is the point of them. A skill that never changes is a skill that stopped learning.

## The rule

**When something notable is learned, update the skill at its root — not in a note, not in a task comment, not in chat.**

If the correction only lives in a conversation, the next run repeats the mistake. The skill file is the only place a lesson persists.

## What counts as notable

Update immediately when any of these happen:

| Trigger | What to change |
|---|---|
| A tool call returns garbage in a predictable way | Add the failure mode with the exact query that caused it |
| A recommendation gets rejected for a reason that generalises | Add it as a rule or a gate |
| A gate catches something real | Record the example — it teaches the gate's value |
| A gate misses something real | Add the missing gate |
| A published video over- or under-performs against the recipe | Update the recipe with the actual result |
| A platform, tool or pricing fact changes | Correct it and date the correction |
| A threshold proves wrong in practice | Change the number, note why |

## What does not count

- One-off preferences for a single video
- Facts about a specific niche (those belong in the research output, not the skill)
- Anything not yet observed twice, unless the single instance was expensive

## How to update

1. Edit the `SKILL.md` at its root. Not an appendix, not a changelog entry — change the instruction itself so it is impossible to follow the old version.
2. If the lesson came from real evidence, name it inline. "Verified failure: `<query>` returned unrelated content" beats "be careful with keywords."
3. Keep rules imperative and testable. "Channel-first, never keyword-first" beats "consider starting with channels."
4. Delete what is now wrong. Superseded advice left in place is worse than no advice.
5. Commit with a message saying what was learned, not what was edited.

## Worked examples from the build

These are the corrections that produced the current versions. They show the shape of a real update.

**Keyword-first returns garbage** → became the governing rule of `youtube-niche-research`, with the two verified failing queries named inline, because the abstract version of the advice was not convincing enough to follow.

**The payload trap** → a video idea was rejected because the format's credential served the author rather than the audience. Became Gate 2 in `youtube-video-greenlight`, with the diagnostic question "what does the viewer *get*?"

**Differentiation miss** → a planned video duplicated the niche's top performer, discovered only by pulling that video's transcript. Became Gate 4, marked hard fail, with a note that it is the gate most easily skipped.

**Search missed known channels** → discovery ranks on semantic similarity to the query wording, so channels the user already knew never surfaced. Became Step 0, ahead of all discovery.

**n=1 is not a pattern** → an early structural finding was presented with more confidence than one transcript supports. Became an explicit input requirement and an honesty rule about sample size.

## When a run breaks

A failure mid-run is the highest-value input this repo gets: it is a real condition nobody
predicted, observed under real use. `channel-next` holds the protocol — stop at the failure, name
what broke, decide whether it is fatal to the step or the phase, offer an honest labelled
fallback, keep what was produced, **then fix the skill in the same session.**

The test is whether the next person would hit it blind. If they would, the skill changes now. A
correction that lives only in a conversation guarantees the next run repeats it.

## Review cadence

- **After every published video** — did the recipe hold?
- **After every niche pass** — did any rule fail?
- **Quarterly** — re-read all three end to end and delete anything stale

## When adding assets

New source material (frameworks, transcripts, courses, competitor teardowns) should be **distilled into rules, not appended as references.** A skill that grows by accumulation becomes unusable. Every addition should either change an existing instruction or replace one.

If an asset does not change any instruction, it did not teach anything — do not add it.
