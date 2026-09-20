# Resolve API traps

Verified against **DaVinci Resolve Studio 21.1.0.14** on macOS, 2026-09-19, by hitting each one
on a real job. Every entry cost a debugging cycle. Read this before driving Resolve.

These are facts about the API, not operator taste — that belongs in `LEARNINGS.md`.

## Writes fail silently when the UI is blocked

Reads work, every write returns `null` or `false`, and nothing says why. `GetCurrentPage()`
returning `null` while a project is open is the tell: a modal dialog or the Project Manager is
in front.

**Preflight check:** `resolve.GetCurrentPage()`. If it is `null`, stop and ask the operator to
close whatever is open in Resolve. Do not keep issuing calls.

## The page matters for more than you would expect

`CreateSubtitlesFromAudio` returns `false` from the Deliver page and succeeds from Edit, with
no error either way. **`resolve.OpenPage("edit")` before captions.**

## `ImportMedia` — the documented form imports nothing

```python
mp.ImportMedia([{"FilePath": path}])   # returns []  — silently imports nothing
mp.ImportMedia([path])                 # works
```

The dict form is what the stub documents. Pass a bare list of path strings.

## `SetRenderSettings` is all-or-nothing

One invalid value makes the **whole dict** return `false` — `TargetDir`, `CustomName` and
everything else in the same call are discarded. Always check the return value.

`SubtitleFormat` accepts **`"BurnIn"`** only. `"burn"`, `"burn_in"`, `"burnin"` and `"Burn In"`
are all rejected. Without `{"ExportSubtitle": True, "SubtitleFormat": "BurnIn"}` a render
completes cleanly and silently contains no captions.

## Timecode maths: 24 labels, 23.976 real

Timecode counts **24 frames per second label** on 23.976 footage. Convert with 24, divide by
23.976 only when converting to seconds.

## Transform

- **`Tilt` is unusable at `Scaling = SCALE_FILL`.** The image fills the height exactly, so any
  tilt pulls black bars into frame. Vertical repositioning requires zoom > 1 first.
- **`Pan` sign:** positive moves the window LEFT, negative moves it RIGHT.
- **`Pan` units are not source pixels** and not a clean output-pixel mapping either. Do not
  derive the value — render two or three candidates and look at them.

## Keyframes: there is no transform keyframe API

`SetProperty` writes static values only. `DynamicZoomEnabled` can be set but its start/end
rectangles are not exposed, and enabling it alone produces no visible move.

A slow move inside a clip must be built as a **Fusion comp**:

```python
comp = ti.AddFusionComp()
comp.Lock()
mi, mo = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")
xf = comp.AddTool("Transform", -32768, -32768)
xf.ConnectInput("Input", mi); mo.ConnectInput("Input", xf)
xf.Size = comp.BezierSpline()
xf.Size[0] = 1.00
xf.Size[ti.GetDuration() - 1] = 1.06
comp.Unlock()
```

Comp frame range is clip-relative, `0` to `duration - 1`. **Delete existing comps first** or the
clip carries two and the wrong one renders.

**Deleting and adding in the same loop does not work.** Iterating `GetFusionCompNameList()` and
calling `DeleteFusionCompByName` on each, then `AddFusionComp()` in the same pass, silently
leaves the old comp in place — every clip ended up with `Composition 1` *and* `Composition 2`.
Called on its own afterwards the identical delete returned `true` and worked. **Delete in a
separate pass, then add, then assert `GetFusionCompCount() == 1`** on every clip.

**`Transform.Center` is the reliable way to reframe**, not the Edit page `Pan`. It is normalised
to the comp (= source) resolution, so a shift is exact and needs no calibration:

```python
xf.Center = {1: 0.5 - shift_px/3840.0, 2: 0.5}   # +shift_px moves the WINDOW right
```

It composes with the keyframed `Size` — the drift then pivots on the offset centre, which is
what you want. Use this instead of `Pan` whenever the shift has to be a known number of source
pixels.

## Subtitles

- Subtitle items expose **no properties**: `GetProperty()` returns empty, every named lookup
  returns `false`, and `SetName()` returns `false`. Text is not editable in place.
- To correct captions: read `GetStart()` / `GetDuration()` / `GetName()`, write an SRT, fix the
  text, `tl.DeleteClips(items)`, `mp.ImportMedia([srt])`, then
  `mp.AppendToTimeline([{"mediaPoolItem": item, "mediaType": 3}])`.
- **Resolve parses HTML tags out of an imported SRT and applies them as styling.**
  `<font color="#rrggbb">`, `<i>`, `<b>`, `<u>` all work, including on one line of a two-line
  cue. `GetName()` returns the text with tags stripped; the line break survives as `U+2028`.
  This means per-phrase colour is scriptable — no Text+ layer needed.
- The character ceiling is **per line, not per cue**.

## `AddMarker` silently rejects the colour "Orange"

**There is no Orange marker in Resolve.** `tl.AddMarker(f, "Orange", ...)` returns `false` and
adds nothing, with no error. This matters because the convention in `SKILL.md` is written
around "orange warning markers" — every one of those calls fails and the warnings never appear
on the timeline.

The 16 colours Resolve 21.1 actually accepts, verified by probing each one:

```
Blue  Cyan  Green  Yellow  Red  Pink  Purple  Fuchsia
Rose  Lavender  Sky  Mint  Lemon  Sand  Cocoa  Cream
```

**Use `Sand` where the convention says orange** — it is the closest hue and reads as a warning
against the blue/green markers. Always check `AddMarker`'s return value; a failed marker is
invisible and a missed claim in a paid ad is the operator's problem, not the platform's.

## Project manager

`CreateProject` returns a usable object even when `LoadProject`, `DeleteProject` and
`GetProjectListInCurrentFolder` cannot see the project — the API's project library and the one
the UI has open can differ. **Use the object `CreateProject` returns**; do not round-trip
through `LoadProject` by name.

## Rendering

Poll by watching the **output file size settle**. `IsRenderingInProgress()` alone is not
reliable enough to gate on.

## Transcription

`MediaPoolItem.TranscribeAudio()` runs about 10x realtime. `GetTranscription()` returns
word-level timecodes — the basis for both cut lists and caption cues.

**It hallucinates across silence.** On a clip where the speaker wrote on a whiteboard mid
sentence, "decisions at the whiteboard level" came back as "decisions at the end of the day".
Read transcripts before trusting them, especially across pauses.

## Grading is fully scriptable — and savable

Do not treat grade as a GUI-only step. The whole chain has an API:

- **`project.AddColorGroup(name)` + `ti.AssignToColorGroup(g)`** — one grade shared by every
  clip in the group, via `g.GetPreClipNodeGraph()`. The right primitive for a batch of ads cut
  from one shoot: grade once, every deliverable inherits, change it once and they all update.
- **`ti.ExportLUT(resolve.EXPORT_LUT_33PTCUBE, path)`** — bake the look to a `.cube`. The
  portable, version-controllable artifact. `graph.SetLUT(nodeIndex, path)` applies one.
- **`ti.CopyGrades([targets])`** — one-to-many copy without a group.
- **`graph.ApplyGradeFromDRX(path, gradeMode)`** — apply a saved still's grade.
- **`ti.SetCDL({"NodeIndex", "Slope", "Offset", "Power", "Saturation"})`** — primitive grading
  as numbers, so a base balance can live in code and diff like code.
- **`graph.ResetAllGrades()`**, `GetNumNodes()`, `SetNodeEnabled()` for node-level control.

## `ExportCurrentFrameAsStill` is the fast verification loop

```python
project.ExportCurrentFrameAsStill("/path/frame.png")
```

Exports the current graded frame as an image in seconds, **at the timeline's resolution and
framing** — clip transform, zoom, pan and fill-crop all included. Use it instead of a test
render whenever the question is "does this look right". `tl.GrabAllStills(2)` grabs a middle
frame from every clip at once.

Two things that will waste a cycle:

- **The output directory must already exist.** It returns `false` and writes nothing if the
  folder is missing, with no error. `mkdir -p` first, and check the return value.
- A **retracted claim, 2026-09-19:** an earlier version of this file said the still export
  ignores framing and letterboxes the source. That was wrong. The letterboxing was
  `Scaling` being set to `SCALE_FIT` — see below — not a fault in the export.

## `Scaling` — `SCALE_FILL` is 3, and the names are not guessable

```python
SCALE_USE_PROJECT = 0    SCALE_CROP = 1    SCALE_FIT = 2    SCALE_FILL = 3    SCALE_STRETCH = 4
```

**Never pass the integer.** `it.SetProperty("Scaling", 2)` looks like "fill" if you are
counting from the wrong end and is actually **Fit**, which letterboxes a 16:9 source inside a
4:5 timeline. It writes cleanly, reads back as `2`, and nothing warns you — the whole ad is
delivered with black bars top and bottom, which for a Meta feed or Reels placement is the one
thing that must not happen.

Pass the constant: `it.SetProperty("Scaling", resolve.SCALE_FILL)`.

The timeline-level default is separate and does not save you: `timelineInputResMismatchBehavior`
defaults to `scaleToFit`, so a clip left at `SCALE_USE_PROJECT` also letterboxes. Set the
per-clip value explicitly and verify with a still.

## Two sessions must not drive one Resolve project

Resolve has no locking here. If a second agent or a human is working the same project,
timeline edits and grades will clobber each other silently. Confirm who owns the project before
writing to it.
