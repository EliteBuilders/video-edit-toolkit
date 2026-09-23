# Audio playbook

What to do, in order, when audio is the problem. Written after a long round of getting it wrong
on a client VSL; every number here was measured, and every mistake listed was actually made.

**The one-line version:** fix the source with the right tool, set the level in the timeline where
the operator can hear it, and then only ever *trim* on the way out.

---

## 1. Room echo / reverb

**Use Resolve Studio's Voice Isolation.** It is a neural de-reverb and nothing in ffmpeg is close.

```python
tl.SetVoiceIsolationState(1, {"isEnabled": True, "amount": 85})   # per track
item.SetVoiceIsolationState({"isEnabled": True, "amount": 85})    # per clip
```

Blackmagic's guidance is **~85**; 100 can add watery artifacts on sibilants. Start at 85.

**Do NOT reach for an expander, gate or "duck the reverb tails".** It is the obvious idea and it
is wrong: it hides reverb by deleting the dynamics that make speech sound alive. Measured on one
hotel-corridor testimonial —

| | envelope dip (higher = drier) |
|---|---|
| untreated | 31.8 |
| tuned downward expander | 33.4 |
| **Voice Isolation** | **36.8** |
| clean room from the same shoot | 36.0 |

— the expander scored *close* and sounded *worse*, because the metric cannot tell "reverb removed"
from "dynamics removed". The operator can.

**Applying it costs a minute, not an hour.** Render audio only and re-mux:

```python
project.LoadRenderPreset("Audio Only")
project.SetRenderSettings({"ExportVideo": False, "ExportAudio": True,
                           "AudioCodec": "lpcm", "AudioBitDepth": 24,
                           "AudioSampleRate": 48000, "CustomName": "voiceiso"})
```
```bash
ffmpeg -i finished.mp4 -i new-audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k out.mp4
# then PROVE the picture is untouched:
ffmpeg -v error -i finished.mp4 -map 0:v -c copy -f md5 -   # must equal the same on out.mp4
```

Two gotchas: an audio-only render stops at the footage end, so **pad to the video's duration**
(`apad,atrim=end=<dur>`) or the mux truncates; and if the delivery applies a speed change, the
audio needs the same `atempo`.

---

## 2. Level: trim, never boost

**The timeline is the reference.** Whatever the operator approved while listening is the target;
the delivery's job is to carry it, not to improve it.

The mistake, in one line: a timeline already peaking at **−4.3 dBFS** needed a **1.8 dB trim** to
meet a −6 ceiling. Adding **+15 dB and limiting to −6** instead produced this —

| 50 ms peak envelope | timeline | over-limited delivery |
|---|---|---|
| p50 | −29.4 | −14.4 |
| p95 | −13.8 | −6.9 |
| p99 | −7.3 | −6.9 |
| max | −4.3 | −6.7 |
| **crest** | **25.1 dB** | **7.7 dB** |

— and the operator said immediately that it did not sound like their timeline. **When p95 and p99
are within a dB of each other, everything is pinned against the limiter.**

**If the deliverable must be louder, raise the fader in the timeline and re-render the audio.**
The operator can hear that change; you cannot. Manufacturing loudness downstream with gain into a
limiter is how a mix that was approved stops being the mix that ships.

Corollary: **integrated loudness alone will not catch this.** Always report crest or the p50/p95/
p99/max envelope alongside LUFS.

---

## 3. Balance the speakers against each other

Programme loudness can be perfectly on target while the film is unlistenable, because one speaker
is far below another. On one VSL:

| | loudness |
|---|---|
| host narration | −34.4 LUFS |
| inserted testimonials | −21.9 LUFS |

**12.5 dB apart.** The operator described it as "it goes from really clear to quiet". Measure each
speaker's regions separately, then correct per region and re-check that every region lands within
about 0.5 LU of the others.

Where the correction lands matters: raising the quiet speaker to meet the loud one pushed peaks
over the ceiling, so the fix was **+7.8 dB on the host and −4.7 dB on the testimonials**, meeting
in the middle at −26.6 LUFS with peaks still at −6.

### The ramp must finish before the cut

A per-region gain change needs a short ramp or it clicks — but **centring the ramp on the join is
a bug**. It gives the first frames of the incoming clip the outgoing clip's gain:

```
WRONG   ramp 301.255 -> 301.405, cut at 301.33
        the first 75ms of the new clip runs 8 dB hot; peak came in 3.5 dB over the ceiling

RIGHT   ramp 301.18 -> 301.33   (finishes AT the cut, ideally during the silence before it)
        or start the ramp at the cut and rise over ~100ms
```

Check the 0.3 s either side of every join first. If the outgoing side is near silence — it often
is, at a cut — the ramp is free and inaudible.

---

## 4. Loudness normalisation

`loudnorm` **silently abandons linear mode** when the gain it needs exceeds the true-peak headroom,
and dynamic mode is content-dependent. Two cuts of identical material, measured within 0.05 LU of
each other, came out **2.8 LU apart**. Test before trusting it:

```
if (target_I - measured_I) > (target_TP - measured_TP):   # you are in dynamic mode
```

Prefer a measured static gain plus a limiter, which is reproducible. And **loudness-match A/B
variants to each other**, or the louder cut wins a test for a reason that is not the edit.

---

## 5. Order of operations

1. **Fix the source** — Voice Isolation, noise reduction, level-match inserts to the host
2. **Set the level in the timeline**, with the operator listening. Sound effects (§6) and the
   music bed (§7) are already in the timeline at this point, so they are heard in context and
   measured in the programme, never added after the loudness pass
3. **Render audio only**, pad to the video duration, apply any speed change
4. **Balance per speaker region** if any two differ by more than ~1 LU
5. **Trim** to the peak ceiling. No boosting, no limiting unless explicitly agreed
6. **Mux with `-c:v copy`** and prove the video stream is untouched by MD5
7. **Report LUFS, true peak, LRA and crest** — not just LUFS

---

## 6. Sound effects

Sound effects come **from the graphics plan, never free-placed**. Each one belongs to something
the viewer can see land: a card entering, a row sliding in, a check popping, a number striking
through, a cut to a full screen. A sound with nothing under it is a mistake the viewer hears
immediately; a one-shot AI edit shipped scissor sounds where nothing was being cut.

**The vocabulary.** One sound per kind of event, the same sound every time in a video:

| Visible event | Sound | Bundled name |
|---|---|---|
| Cut to a full-screen scene | soft whoosh-in or low hit | `whoosh`, `impact-bass-1` (sparingly) |
| Panel or card enters | short whoosh | `whoosh-short` |
| Row, chip or item lands | tick or click | `click`, `pop` |
| Check mark or success state | light chime | `ping`, `chime` |
| Strike-through or correction | quick swipe | `whoosh-short` |
| Count-up running | nothing, or `typing` very low | — |
| Exits | **nothing** | — |
| Captions | **nothing, ever** | — |

**Rules.**
- **On the event frame, ±2 frames.** Write every sound into the cue's `sfx` list in
  `graphics-plan.json`; `graphics_qa.py` fails any sound not on a cue's start, end or `events`.
- **Under the voice.** Start at about 18 dB below dialogue peak and adjust by ear with the
  operator. Never on a stressed syllable: move the sound, not the word.
- **Sparse.** At most one sound per ~2 s on average, and not on consecutive list items faster
  than ~0.4 s apart: the group gets one sound on its first item.
- **Retimed graphic, regenerated sounds.** Any change to a cue's timing orphans its sounds.
  Re-derive them from the plan and re-run the gate.
- Own track: **A3 `SFX`**, below dialogue, above music. Placed through the MCP at the frame.

**Where the sounds come from.** In order: the operator's `assets/sfx/` library, then the
bundled HyperFrames set (21 files, free, offline, with a `manifest.json` of placement hints):

```bash
ls "$(cat .hyperframes-path)/skills/media-use/audio/assets/sfx/"
```

`media-use` can also retrieve from HeyGen's online library, which needs a HeyGen login. Record
the source of every sound in the plan so licensing is traceable.

---

## 7. Music bed

**Opt-in per video**, named in the brief with the exact file. Never picked silently.

- **Trim to where the music actually starts.** `silencedetect` on the track and cut the lead-in
  silence so the bed starts on sound, not on nothing.
- **Level relative to the voice, measured.** Start the bed about **20 LU under** the dialogue's
  integrated loudness (dialogue at −14 LUFS → bed near −34 LUFS), then set it by ear with the
  operator. A flat clip gain of about −18 to −20 dB on a mastered track lands in that range;
  measure rather than trust it.
- **Fade in over ~1 s, out over ~2 s**, and end on a musical phrase if one falls within a
  second of the programme end.
- **Ducking is a separate opt-in.** A bed that is already 20 LU under rarely needs it.
- Own track: **A4 `MUSIC`**. Then run the loudness pass (§4–5) on the whole programme.
- **Licensing.** The operator's own licensed track, or a library that clears YouTube Content ID
  for their channel. A HeyGen catalog track (`media-use --type bgm`) needs its licence checked
  for the platform before it ships. Note the source in the delivery list.

