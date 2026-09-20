#!/usr/bin/env python3
"""Cue table -> SRT, with the guards that stop bad captions shipping.

CLIENT-AGNOSTIC TEMPLATE. Copy into <project>/tools/, set EMPHASIS to the
brand's emphasis colour from BRAND.md, and write the cue table beside it.

Why a cue table and not hand-authored subtitles: Resolve's subtitle track
exposes no styling to the API at all, so captions are generated outside it and
burned in from a composition. The SRT this writes ships as the platform
sidecar; the burn-in is generated from the SAME table, so the two can never
drift apart.

A cue is (start_frame, end_frame, [line, ...]) in TIMELINE frames. A line is:

    "TEXT"                         plain
    ("TEXT", "gold")               emphasised
    ("TEXT", "italic")             italic
    {"t": "TEXT", "g": True,       emphasised, and pinned to the exact frame
     "at": 1814}                   its FIRST word is spoken
    "A {em:WORD} INSIDE A LINE"    emphasis on part of a line

**Use the dict form with "at" whenever a second line's words come noticeably
later than the first.** A fixed lag is what puts a word on screen before the
speaker says it.

Timecode maths uses the 24fps label even on 23.976 footage - see the skill's
RESOLVE-API-TRAPS.md.

`build()` returns a list of problems. Lines starting with "NOTE" are advisory;
everything else is a FAIL and must be fixed before the build is trusted. Print
them and act on them - they are the whole point of this file.
"""
import re

EMPHASIS        = "#ffcb47"   # from the project's BRAND.md
MAX_LINE        = 27          # hard ceiling at phone size
WARN_LINE       = 22          # preferred ceiling
MIN_LINE_FRAMES = 12          # 0.5s. Below this a line reads as a flash
FPS_LABEL       = 24.0        # timecode label, not the real rate
FPS_REAL        = 23.976      # only used to report seconds in warnings
TRAILING        = (",", ".")  # a block vanishes as a unit; see the guard below
MIN_WORDS       = 3           # a one- or two-word cue reads as a flash of noise

# A cue that ends on one of these leaves the reader mid-phrase, waiting for the
# noun. Push the dangling word onto the next cue instead.
DANGLING = {
  "a", "an", "the", "of", "to", "and", "or", "in", "on", "for", "with", "at",
  "as", "from", "by", "but", "so", "if", "when", "than", "that", "this",
  "these", "those", "your", "their", "our", "my", "his", "its", "is", "are",
  "was", "were", "be", "been", "more", "most", "very", "into", "about",
  "what", "which", "who", "how", "not", "no", "can", "will", "would", "they",
}


def f2t(f):
    ms = round(f / FPS_LABEL * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def render_line(line):
    if isinstance(line, dict):
        text = line["t"]
        return f'<font color="{EMPHASIS}">{text}</font>' if line.get("g") else text
    if isinstance(line, tuple):
        text, style = line
        if style == "gold":
            return f'<font color="{EMPHASIS}">{text}</font>'
        if style == "italic":
            return f"<i>{text}</i>"
        raise ValueError(style)
    return re.sub(r"\{em:([^}]*)\}", rf'<font color="{EMPHASIS}">\1</font>', line)


def plain(line):
    text = line["t"] if isinstance(line, dict) else (
        line[0] if isinstance(line, tuple) else line)
    return re.sub(r"\{em:([^}]*)\}", r"\1", text)


def build(cues, path, seg_of=None):
    """`seg_of` maps a cue's START FRAME to the index of the timeline segment it
    falls on. Pass it whenever the cut has more than one clip: it is the only
    way this file can check that no cue spans an edit, which is the caption bug
    reviewers notice fastest - one speaker's words over the next speaker's face.
    """
    problems = []
    for i, (s, e, lines) in enumerate(cues):
        words = " ".join(plain(ln) for ln in lines).split()

        # A cue may never span a cut.
        if seg_of is not None and i + 1 < len(cues):
            here, nxt = seg_of.get(s), seg_of.get(cues[i + 1][0])
            if here is not None and nxt is not None and here != nxt and e > cues[i + 1][0]:
                problems.append("cue %d: runs past the cut into segment %s" % (i + 1, nxt))

        if len(words) < MIN_WORDS and i + 1 < len(cues):
            problems.append("cue %d: only %d word(s) (%r) - merge it into a neighbour on "
                            "the same side of the cut" % (i + 1, len(words), " ".join(words)))

        # Never leave the reader mid-phrase.
        if words and words[-1].lower().strip(".,!?") in DANGLING and i + 1 < len(cues):
            problems.append("cue %d: ends on the dangling word %r - push it onto the next "
                            "cue" % (i + 1, words[-1]))

        # Never open a cue with the word that closed the last sentence.
        if i and words:
            prev = " ".join(plain(ln) for ln in cues[i - 1][2]).split()
            if words[0].rstrip().endswith((".", "!", "?")) and prev and not prev[-1].endswith(
                    (".", "!", "?")):
                problems.append("cue %d: opens with %r, the end of the PREVIOUS sentence - "
                                "fit it on the previous cue" % (i + 1, words[0]))

        # A gap with no caption on screen mid-sentence reads as a dropped frame.
        if i + 1 < len(cues):
            gap = cues[i + 1][0] - e
            if 0 < gap <= 9:
                problems.append("NOTE cue %d: %d-frame gap before the next cue - butt them "
                                "together and hand over in ~2 frames, or the frame goes bare"
                                % (i + 1, gap))

        for ln in lines:
            # A caption block appears and vanishes as a unit, so a comma on its
            # LAST line punctuates nothing - the pause it marks is the cut.
            if ln is lines[-1] and plain(ln).rstrip().endswith(TRAILING):
                problems.append(
                    "cue %d: %r ends a block with a comma or period - the block vanishes, "
                    "so the stop punctuates nothing. Drop it (punctuation only between "
                    "items inside one visible block). ? and ! are tone, and stay."
                    % (i + 1, plain(ln)))
            # A line pinned near its cue's end is on screen for almost no time.
            # This caught a line showing for 4 frames because it was pinned to
            # its LAST word rather than its first.
            if isinstance(ln, dict) and "at" in ln:
                on = e - ln["at"]
                if on < MIN_LINE_FRAMES:
                    problems.append(
                        "cue %d: %r is on screen %d frames (%.2fs) - pin it to its FIRST "
                        "word, or end the cue later" % (i + 1, plain(ln), on, on / FPS_REAL))
            n = len(plain(ln))
            if n > MAX_LINE:
                problems.append("cue %d: line %d chars over hard ceiling %d: %r"
                                % (i + 1, n, MAX_LINE, plain(ln)))
            elif n > WARN_LINE:
                problems.append("NOTE cue %d: line %d chars over preferred %d: %r"
                                % (i + 1, n, WARN_LINE, plain(ln)))
        if e <= s:
            problems.append("cue %d: end %d <= start %d" % (i + 1, e, s))
        if i + 1 < len(cues) and e > cues[i + 1][0]:
            problems.append("cue %d: overlaps next (%d > %d)" % (i + 1, e, cues[i + 1][0]))
        if len(lines) > 2:
            problems.append("cue %d: %d lines, max 2" % (i + 1, len(lines)))

    out = []
    for i, (s, e, lines) in enumerate(cues, 1):
        out.append(str(i))
        out.append("%s --> %s" % (f2t(s), f2t(e)))
        out.extend(render_line(ln) for ln in lines)
        out.append("")
    with open(path, "w") as fh:
        fh.write("\n".join(out))
    return problems
