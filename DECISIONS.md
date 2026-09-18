# Decisions

Why the video layer is built the way it is. The SKILL.md files say *what* to do; this says
*why*, so a session picking this up cold does not re-litigate settled questions or quietly
undo a rule that exists for a reason.

Research date: 13 September 2026. Anything marked **verify** moves with the software.

---

## The founding decision: do not build an integration

**Decided:** use Blackmagic's own MCP server. Build the instruction layer only.

DaVinci Resolve Studio **21.1** shipped 7 September 2026 with a native MCP server, enabled at
`File > Setup AI Assistants`. It works with Claude Code. The agent calls Resolve's scripting
API directly rather than driving the GUI.

The same release **removed Python scripting from the free edition entirely**. Blackmagic's
stated reason: the API "was being used to hack studio features into the free version." So
Studio is a hard requirement, not a preference, and most community Resolve MCP tooling built
before September is dead.

**Consequence:** there is no free path and no fallback to the free edition. If Studio is not
installed, nothing here works.

## The reference set

Five videos were read in full before anything was written. Two are worth revisiting; three are
superseded.

| Source | Date | Still useful for |
|---|---|---|
| Team 2 Films, "Resolve 21.1 BEST New Feature TESTED" | 8 Sep 2026 | The real tutorial. Most of the stage mechanics and every named API gap came from here |
| Creator Magic, "I Let GPT-6 Astra Edit In DaVinci Resolve MCP" | 8 Sep 2026 | Honest wall-clock timing. 75 min to 21:59 across 96 edits in 30 minutes. Then 2 minutes for a 2-second trim |
| Jason Cooperson, "How I Fully Automated My Video Editing" | 29 Jun 2026 | One lesson only: 2 hours of hand-fixing graphics on a 47-second intro, because the rough cut was not locked first |
| Sandy Lee AI, same title | 20 Jul 2026 | Two ideas, both adopted: a brand file the agent reads, and a reference screenshot folder |
| Dan Kieft, "I Tried AI Video Editing for 8 Days" | 12 Jun 2026 | Superseded. Predates 21.1 entirely, covers asset generation not editing |

**The convergence that mattered:** five creators, three different stacks, no coordination, and
all of them land on the same boundary. The agent produces a good rough cut fast and a
bad-to-mediocre polish slowly. That boundary is why the stages are gated.

## Why the rough cut is a hard gate

Cooperson locked nothing and spent two hours re-prompting graphics that sat on top of a cut
that kept changing. That is the single most expensive failure mode in the reference set and it
is structural, not a skill issue.

**Rule:** the rough cut is approved as a text cut list before a timeline is built, and locked
before a single graphic is placed. Do not remove this gate to save a step.

## Why nothing renders without an explicit yes

Blackmagic has published **no documentation** on permissions, destructive-operation safeguards,
or logging for the MCP server. At least one community server warns outright that it can delete
project data.

The render gate and the never-delete rule are not politeness. They are the only safeguards that
exist. **Nothing filed as a learning may remove them.**

## Reversed decisions

Recorded because the superseded version is wrong and looks reasonable.

### Fusion templates, reversed

**Was:** build branded title templates by hand in Fusion, save as Edit Templates, let the API
place them and set `StyledText`.

**Why it was wrong:** the premise was that the operator could build them. They are not a video editor and
does not build graphics. The whole approach collapses on that.

**Now:** Claude authors every graphic as HTML and CSS, renders to transparent ProRes 4444 via
HyperFrames, and places it on an upper track. The operator describes and reacts. They never open Fusion.

### "Serif only on section titles", reversed

**Was:** italic serif appears only on section title cards; scarcity is what makes it read as
expensive.

**Why it was wrong:** the reference material uses italic serif on a *single word inside a sans
line*, in both captions and headlines. It works because it is one word against heavy sans.

**Now:** serif on one word or a short phrase inside a sans line, plus section titles. Never
functional text, never a whole sentence.

### "Never a light ground", reversed

**Was:** ground is `#0F1626` or darker, always.

**Why it was wrong:** screen-recording composites sit on a lit blue glow, and that glow is what
makes the screen card read as floating rather than pasted on.

**Now:** dark ground under anything overlaying a talking head. Full-frame screen composites may
sit on a lit accent glow.

### Progress chips, rebuilt

**Was:** small numbered squares in a corner that light up as you advance.

**Why it was weak:** the reference does something better. All chips are on screen from the
start as numbers, and each flips to its written label as the point is covered. The viewer sees
how many are left *and* what has been said. Promise and progress in one object.

**Now:** the strongest retention device in the kit, not a corner afterthought.

## Stolen from 1of10

1of10 announced an AI video editor in September 2026. It is a waitlist landing page, not a
product: no demo asset served, no Wayback captures, not linked from their own navigation. Two
of its six announced features exposed real gaps here and were adopted.

- **Auto Retakes.** Repeated takes are now presented side by side with timecode, duration and
  what differs, for a human to pick. Previously the skill silently kept the last complete
  take, which is guessing at a creative decision.
- **Log to Rec.709 auto-detection.** A technical conversion with a right answer, so Stage 3
  reads clip metadata and applies the correct input transform per clip. The creative grade on
  top stays manual.

**Their surprising miss, worth watching:** their editor has no stated connection to their
outlier data. That was their one structural advantage over Gling and Recut and they did not
claim it. If they ship that, reassess.

**Ruled out for client work regardless:** their privacy policy covers YouTube API data only and
says nothing about uploaded video files, storage, deletion, or training on footage.

## Tools evaluated and rejected

| Tool | Why not |
|---|---|
| Descript, Gling, Recut, TimeBolt, Opus Clip | $15-40/mo wrappers around the transcript-to-XML trick already owned inside the Studio license |
| Tella as a pre-cut step | Its exports are a playback "compatibility copy", not the camera original, with no relink path. Frame rate locked to 30/60. Use Tella end to end for quick internal video, or Resolve end to end. Never chain them |
| WhisperX | Redundant. 21.1 exposes Resolve's own transcription with speaker and word-level timing |
| AutoPod | $29/mo, runs inside Resolve Studio. Revisit only if multicam podcast switching becomes regular |
| Google Drive auto-transcripts | Segment-level timing only. Fine for show notes and repurposing, useless for deciding a cut point |

## The benchmark

**The operator's manual baseline is 6 to 8 hours for a simple 10-minute video.** Every edit reports
against that number, in `BENCHMARK.md` in the project folder, honestly, including when
unflattering.

This number is more forgiving than the reference set implies. The videos worry about agents
being slower than a skilled editor on fine work, which is true and documented. Against a
6-to-8-hour baseline there is an enormous margin, and the fine-work warning matters much less.

## Hardware

Apple Silicon M4 Pro, which clears Blackmagic's stated 16 GB unified-memory floor for Studio
AI features. Their floor for background rendering and analysis is 32 GB. **verify against the
readme in the installer.** If transcription drags on a 24 GB machine, 21.1 added a Media page
preference to run AI tools against proxy media.

## Known API gaps as of 21.1

Not exposed to the agent. The skill says so out loud rather than failing quietly:

- Update Timecode from Audio Track (workaround: read with ffmpeg, set via API)
- Removing empty gaps in a timeline
- Creating and labeling color nodes (needs computer control, and it warns before taking the mouse)
- IntelliSearch data, so there is no help understanding what is visually in a shot

21.1 **added** transitions, audio normalization, fades, speed changes, auto-align, multicam,
render presets, and transcription retrieval with speaker and timing. **verify** by asking the
MCP directly rather than trusting this list after the next Resolve update.

## Where the rest lives

Not everything is in this repo. These are the other homes:

- **Motion kit visual reference.** The eleven components animating live, in brand:
  `https://claude.ai/code/artifact/e2e5e1a4-6226-427b-b04f-46d68fce25b3`
  The SKILL.md table names them; this is what they actually look like.
- **Build brief and 1of10 comparison.** The operator's own Claude project, at
  `claude/2026-09-13-resolve-ai-editing-build-brief.md` and
  `claude/2026-09-13-1of10-video-editor-comparison.md`
- **Decision thread.** ClickUp task `86e38b946` in G.S.D. > Execution carries the full
  running record, including options considered and discarded.

## Status

`resolve-ai-edit` has **never been run against real footage.** It is written from research,
five reference videos, and Blackmagic's release notes. The first run is deliberately
constrained to a text-only cut list on a throwaway project. See
`skills/resolve-ai-edit/templates/FIRST-RUN.md`.

Until that run happens and six real numbers exist, treat every timing claim here as inherited
from someone else's test, not measured on this machine.
