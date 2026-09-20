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

- **`Tilt` at `Scaling = SCALE_FILL` — check for slack, do not assume there is none.** An
  earlier version of this file said tilt always pulls black bars in because the image fills the
  height exactly. **That is not reliably true.** On a 3840x2160 source in a 1080x1350 timeline
  there was ample vertical slack at zoom 1.00 and no bar appeared at `Tilt -60`. Render one
  frame at a deliberately large tilt and look before concluding either way.
- **A tighter zoom needs a proportionally larger tilt for the same framing.** Correcting a
  clipped head took `Tilt -60` at zoom 1.00 and `-200` at zoom 1.26 on the same shot.
- **`Pan` sign:** positive moves the window LEFT — i.e. the IMAGE moves right.
- **`Pan` units, measured 2026-09-20** on a 3840x2160 source in a 1080x1350 timeline:
  **1 unit = 2.2222 output px**, which is exactly `3840/1728`. It does **not** scale with
  `ZoomX` — +200 moved the image 444 px at zoom 1.00 and 444 px at zoom 1.26. So to move the
  visible window by a known number of SOURCE pixels:

  ```python
  pan = -shift_src_px * 0.28125 * zoom     # 0.28125 = 0.625 / 2.2222
  ```

  Calibrate once per project rather than trusting this: render the same frame at `Pan 0` and
  `Pan 200` and cross-correlate one horizontal band. It takes two 3-frame renders.
- **`GetProperty("Pan")` returns `None`** even straight after a `SetProperty("Pan", ...)` that
  demonstrably changed the render. Do not use the read-back to confirm a write; render a frame.

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

**`Transform.Center` reframes exactly when the comp is live.** It is normalised to the comp
(= source) resolution, so a shift needs no calibration:

```python
xf.Center = {1: 0.5 - shift_px/3840.0, 2: 0.5}   # +shift_px moves the WINDOW right
```

It composes with the keyframed `Size`, so the drift pivots on the offset centre.

**But do not assume the comp is live — prove it.** See the next entry.

## A clip Fusion comp can be silently inert, and nothing reports it

On one timeline (2026-09-20) every clip carried exactly one well-formed comp —
`MediaIn1 -> Transform1 -> MediaOut1`, no pass-through, correct frame format — and it had
**zero effect on the render**. `Center = 0.95` with `Size = 0.5` rendered **byte-identical** to
`Center = 0.5`. Deleting the comp and building a fresh one changed nothing. On another timeline
in the *same project*, built the same way, the identical code reframed correctly.

**Cause unknown, and one plausible theory is already disproven.** The first inert timeline had
been created at the project's 3840x2160 and switched to 1080x1350 afterwards, so "the comps
were built against a 4K timeline" looked like the answer. It is not: the next timeline was
created at 1080x1350 *before any comp existed* and its comps were inert too.

What is actually observable: **every timeline created by scripting in one session was inert,
while timelines built in an earlier session, in the same project, were live.** So it tracks
something about the application's state, not about how the timeline is constructed. Do not
spend a cycle theorising — run the test below and route around it.

**The 20-second test, worth running before building twelve comps:**

```python
xf.Center = {1: 0.95, 2: 0.5}          # deliberately absurd
# render 3 frames, then render 3 more at 0.5 and compare the files
```

If the two frames are identical, Fusion is not in the render path on that timeline. Fall back
to the Edit page `Pan`, which is calibratable and always applies.

**Losing Fusion costs the intra-clip zoom drift**, because `SetProperty` cannot keyframe. There
is no Edit-page substitute; a static zoom per beat is the fallback.

## `CreateEmptyTimeline` inherits the PROJECT resolution, not the last timeline's

A new timeline in a 3840x2160 project comes out 3840x2160 even when every other timeline in it
is 1080x1350. The render still honours `FormatWidth/Height`, so it completes cleanly and
**letterboxes the whole ad** — the 4K timeline is fitted into the 4:5 output. `Scaling` reads
back as `SCALE_FILL` on every clip the whole time, so the usual letterbox check passes.

Fixing it needs the undocumented spelling. `timelineUseCustomSettings` is **not** the key and
returns `false`; the key is **`useCustomSettings`**:

```python
tl.SetSetting("useCustomSettings", "1")             # this one, not timelineUseCustomSettings
for k, v in [("timelineResolutionWidth", "1080"), ("timelineResolutionHeight", "1350"),
             ("timelineOutputResolutionWidth", "1080"), ("timelineOutputResolutionHeight", "1350")]:
    assert tl.SetSetting(k, v)
```

Every `SetSetting` before `useCustomSettings` is set returns `false` and does nothing. Check the
return of each one, and read `timelineResolutionWidth` back.

## `AppendToTimeline` — `endFrame` is EXCLUSIVE

The docs read like an in/out pair, so `endFrame = src_out - 1` is the natural guess. It is
wrong: it produces a clip **one frame short**. With an explicit `recordFrame` per item that does
not shorten the timeline, it leaves a **one-frame gap before every beat** — a black flash at
each cut that survives to delivery. Pass `endFrame = src_out` and assert that consecutive items
touch:

```python
assert all(b.GetStart() == a.GetEnd() for a, b in zip(items, items[1:]))
```

## `DeleteClips` can leave a track that refuses new appends

After `tl.DeleteClips(items)`, `AppendToTimeline` returned a 12-item list — and the track stayed
empty. Re-fetching the timeline by index, re-selecting it, and switching pages all failed to
revive it. Appending to a **freshly created** timeline worked first time with identical code.
Treat a track that has been emptied with `DeleteClips` as unusable: build a new timeline
instead of trying to refill it.

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

**`TranscribeAudio()` returns `false` unless Resolve is on the Media page.** It fails silently
and `GetTranscription()` then returns `None`, which looks like "this clip cannot be
transcribed". `resolve.OpenPage("media")` first and it returns `true` immediately. Four clips
that all "failed" transcribed on the retry without changing anything else.

`MediaPoolItem.TranscribeAudio()` runs about 10x realtime. `GetTranscription()` returns
word-level timecodes — the basis for both cut lists and caption cues.

**It hallucinates across silence.** On a clip where the speaker wrote on a whiteboard mid
sentence, "decisions at the whiteboard level" came back as "decisions at the end of the day".
Read transcripts before trusting them, especially across pauses.

## `AddTransition` does NOT shift the timeline when handles exist

A centred cross dissolve normally shortens a timeline by its own duration, which would move
every downstream caption and graphic. **It does not, if both clips have handles** — media
beyond the cut, which they do whenever the cut exists to remove a pause. Resolve overlaps into
the handles instead.

Measured on a 13-segment timeline with 12 six-frame dissolves: `GetEndFrame()` stayed at 13237,
and every item kept its `GetStart()`, `GetEnd()` and `GetLeftOffset()`. So
`tl = src - src_in + tl_in` still held and the SRT generated straight off it.

**Read the positions back rather than trusting either outcome.** `GetItemListInTrack` returns
the transitions too, as items with `GetType() == "transition"` and a `None` left offset —
filter them out before zipping the list against a beat table.

```python
vids = [it for it in tl.GetItemListInTrack("video", 1) if it.GetType() == "video"]
```

## Frame rate is per PROJECT, not per timeline

`timelineFrameRate` is a project setting and Resolve locks it once the media pool has clips.
A 30fps deliverable inside a 23.976 project needs **a new project**, not a custom timeline —
`ProjectManager.CreateProject`, set the frame rate, then import. Resolution *is* per timeline
(`useCustomSettings`), frame rate is not.

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

### `SetLUT` returns `False` for a LUT Resolve has not indexed yet

A `.cube` copied into the LUT folder **after Resolve launched** does not exist as far as
`graph.SetLUT()` is concerned. It returns `False` for every clip and changes nothing. There is
no error, no warning, and the identical call against a LUT that *was* present at launch returns
`True` in the same loop — which is exactly what makes it look like a problem with the clips
rather than with the file.

```python
project.RefreshLUTList()          # then SetLUT starts returning True
```

Call it once after writing any new `.cube`, before applying it. Cost: one cycle on the WISE VSL,
2026-09-20, where six testimonial clips silently kept their ungraded look while the nine clips
around them graded correctly.

**And always read the LUT back** — `graph.GetLUT(1)` — rather than trusting the return value
alone. `SetLUT` returning `True` is the weaker of the two signals.

## `ExportCurrentFrameAsStill` is the fast verification loop

```python
project.ExportCurrentFrameAsStill("/path/frame.png")
```

Exports the current graded frame as an image in seconds, **at the timeline's resolution and
framing** — clip transform, zoom, pan and fill-crop all included. Use it instead of a test
render whenever the question is "does this look right". `tl.GrabAllStills(2)` grabs a middle
frame from every clip at once.

Two things that will waste a cycle:

- **The playhead can silently refuse to move.** On a just-created timeline, `SetCurrentTimecode`
  returned `true` while `GetCurrentTimecode` read back the *previous* position, and the export
  wrote the wrong frame — at 3840x2160 rather than the timeline resolution, which is the tell.
  **Always read the timecode back and compare** before trusting the still; if it disagrees,
  render three frames and pull them with ffmpeg instead. A still that comes out at the source
  resolution is never the timeline frame.
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

## HyperFrames: `data-width` / `data-height` decide the render size, not the CSS

A composition root without them **silently renders 1080x1920 portrait**, whatever the CSS says.
A 1920x1080 overlay came back portrait, Resolve then scaled it to fill, and every graphic was
about twice the intended size and cropped — after a nine-minute render.

```html
<div id="overlay" data-composition-id="overlay"
     data-width="1920" data-height="1080" data-fps="30" data-duration="447.2333">
```

**Probe the output before placing it:** `ffprobe -show_entries stream=width,height`. One second
there saves a full re-render.
