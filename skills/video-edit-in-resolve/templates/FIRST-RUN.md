# First run: paste this into Claude Code

Open Claude Code in the project folder, then paste the block below. It stops before anything is rendered and before anything is deleted.

---

Use the video-edit-in-resolve skill.

Run preflight first and report the results before doing anything else. Confirm Resolve is reachable over MCP, confirm it is Studio 21.1 or later, read BRAND.md, CREATIVE-BRIEF.md and BROLL.md, and tell me what you found.

Then, on a NEW Resolve project named AGENT_TEST, using the file in raw/:

1. Import the media and transcribe it with speaker detection. Tell me the elapsed time when it finishes. Do not call it a timeout.
2. Build a cut list as text, with timecodes and a reason for every cut. Do not touch the timeline yet.
3. Stop and show me the list.

Do not build a timeline, do not place a single graphic, do not queue or start a render. Do not delete anything.

At the end give me the stage report in the format the skill specifies.

---

## What to record for the benchmark

The point of this run is six numbers. Write them down.

| Metric | Value |
|---|---|
| Raw runtime | |
| Transcription wall clock | |
| Cut list wall clock | |
| Cuts proposed | |
| Cuts you disagreed with | |
| Your estimate of doing this cut by hand | |

Baseline to beat: 6 to 8 hours for a simple 10-minute video.

If the agent is slower than you are and the cuts are wrong, that is a real answer and it is worth knowing on video one rather than video ten.

## Then, only if the cut list looks right

Say: "build the timeline from that list."

Review the timeline. Then say: "run stage 3 polish, then QA, then stop."

Do not let it render on the first test.
