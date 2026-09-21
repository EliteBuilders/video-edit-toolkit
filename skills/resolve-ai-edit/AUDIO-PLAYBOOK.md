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
2. **Set the level in the timeline**, with the operator listening
3. **Render audio only**, pad to the video duration, apply any speed change
4. **Balance per speaker region** if any two differ by more than ~1 LU
5. **Trim** to the peak ceiling. No boosting, no limiting unless explicitly agreed
6. **Mux with `-c:v copy`** and prove the video stream is untouched by MD5
7. **Report LUFS, true peak, LRA and crest** — not just LUFS
