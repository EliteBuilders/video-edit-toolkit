# Video Graphics Reference

A library of how other editors put information on screen, filed by the **job** the graphic does
(show a process, a comparison, a position on a spectrum, proof, who's speaking...). It is the
reference Claude checks when planning graphics for any client's video.

## Adding to it

1. **Drop files into `_inbox/`.** Screenshots are fine. When it's the *motion* you like, also save
   a short screen recording (5-10s, `.mp4` or `.mov`) of that moment: from a clip the timing and
   easing can be measured; from a still they can only be guessed.
2. Optional: name the file with a hint, e.g. `stat-counter-i-like-the-bounce.mp4`, or note the
   source video. Anything is better than nothing; Claude will rename it.
3. Tell Claude: **"add the new references to the graphics library."** Claude looks at each file,
   files it into the right job folder with a descriptive name, writes its entry in `library.json`
   and rebuilds `LIBRARY.md` and `gallery.html`.

## Using it

- **`gallery.html`**: open in a browser to browse everything visually, by job.
- **`LIBRARY.md`**: the same content as text; this is what Claude reads.
- **`library.json`**: the source of both. Edit this (or ask Claude to), then run
  `python3 _tools/build.py`. The build also lists anything not yet catalogued.

## Folders

| Folder | The job |
|---|---|
| `01-process-and-steps` | A sequence, framework or acronym |
| `02-comparison` | Old vs new, them vs us, two paths |
| `03-spectrum-and-position` | Where something sits between two ends, or how far along |
| `04-structure-and-breakdown` | What something is made of |
| `05-who-is-speaking` | Introducing a person |
| `06-proof-photos` | Real events, people, results |
| `07-range-and-audience` | Breadth of who it's for |
| `08-labels-over-speaker` | Short terms shown without leaving the face |
| `09-beats-and-kinetic-text` | A pause, a question, a pivot line |
| `10-screen-and-document` | A real app, page or document |

New jobs get a new numbered folder when a reference doesn't fit any of these.

## The rule

These are other people's designs. Take the **system**: layout, hierarchy, how much of the frame,
colour logic, the motion. Never the exact design. Keep this folder private: it is not in the
public `video-edit-toolkit` repo, only a pointer to it is.
