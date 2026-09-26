#!/usr/bin/env python3
"""Rebuild LIBRARY.md and gallery.html from library.json.

  python3 build.py [LIBRARY_PATH]

library.json is the only file edited by hand (or by Claude when cataloguing).
Checks, every run:
  - every file an entry names exists
  - every image/clip in a job folder belongs to an entry (orphans are listed)
  - what is waiting in _inbox/ to be catalogued
Stills and clips both work: .png/.jpg/.webp show as images, .mp4/.mov/.webm as
looping muted video in the gallery.
"""
import html, json, os, sys

def library_root():
    """The library to build: an argument, else the library this script sits in
    (a copy in <library>/_tools/), else the skill's gitignored .library-path."""
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args:
        return os.path.abspath(os.path.expanduser(args[0]))
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(here, "library.json")):
        return here
    pf = os.path.join(here, ".library-path")
    if os.path.exists(pf):
        return os.path.expanduser(open(pf).read().strip())
    raise SystemExit("no library: pass its path, or run scripts/init_library.sh first")


ROOT = library_root()
MEDIA = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".webm", ".m4v")
VIDEO = (".mp4", ".mov", ".webm", ".m4v")
lib = json.load(open(os.path.join(ROOT, "library.json")))
jobs = {j["folder"]: j for j in lib["jobs"]}
by_job = {j["folder"]: [] for j in lib["jobs"]}
problems, named = [], set()
for e in lib["entries"]:
    if e["folder"] not in jobs:
        problems.append("entry %s: unknown folder %s" % (e["id"], e["folder"]))
        continue
    by_job[e["folder"]].append(e)
    for f in e["files"]:
        p = os.path.join(e["folder"], f)
        named.add(p)
        if not os.path.exists(os.path.join(ROOT, p)):
            problems.append("entry %s: missing file %s" % (e["id"], p))
orphans = sorted(os.path.join(d, f) for d in jobs if os.path.isdir(os.path.join(ROOT, d))
                 for f in os.listdir(os.path.join(ROOT, d))
                 if f.lower().endswith(MEDIA) and os.path.join(d, f) not in named)
inbox_dir = os.path.join(ROOT, "_inbox")
inbox = sorted(f for f in os.listdir(inbox_dir) if f.lower().endswith(MEDIA)) if os.path.isdir(inbox_dir) else []

# ---- LIBRARY.md
FIELDS = [("layout", "Layout"), ("system", "System"), ("motion", "Motion"), ("build", "Build it"),
          ("use", "Use when"), ("avoid", "Avoid")]
md = ["# Graphics reference library", "",
      "_Generated from `library.json` by `_tools/build.py`. Edit the JSON, not this file._", "",
      lib["about"], "",
      "**Find a graphic by the job it has to do**, then read the entry: layout, the system worth stealing,",
      "the motion (inferred on stills, measured on clips), and how to build our own version.", "",
      "| Job | Use when | Entries |", "|---|---|---|"]
for d, j in jobs.items():
    names = ", ".join("[%s](#%s)" % (e["id"], e["id"]) for e in by_job[d]) or "_none yet_"
    md.append("| **%s** | %s | %s |" % (j["title"], j["when"], names))
md.append("")
for d, j in jobs.items():
    if not by_job[d]:
        continue
    md += ["---", "", "## %s" % j["title"], "", "_%s_" % j["when"], ""]
    for e in by_job[d]:
        md += ['<a id="%s"></a>' % e["id"], "### %s" % e["id"], "",
               "Source: %s%s" % (e.get("source", "unknown"), "  ·  clip: yes" if any(f.lower().endswith(VIDEO) for f in e["files"]) else ""), ""]
        for f in e["files"]:
            p = "%s/%s" % (d, f)
            md.append(("[clip: %s](%s)" % (f, p.replace(" ", "%20"))) if f.lower().endswith(VIDEO)
                      else '<img src="%s" width="480">' % p.replace(" ", "%20"))
        md.append("")
        for k, label in FIELDS:
            if e.get(k):
                md.append("- **%s:** %s" % (label, e[k]))
        md.append("")
if inbox:
    md += ["---", "", "## Waiting in _inbox (not catalogued yet)", ""] + ["- %s" % f for f in inbox] + [""]
open(os.path.join(ROOT, "LIBRARY.md"), "w").write("\n".join(md))

# ---- gallery.html
def media(d, f):
    src = html.escape("%s/%s" % (d, f))
    if f.lower().endswith(VIDEO):
        return '<video src="%s" autoplay muted loop playsinline controls></video>' % src
    return '<a href="%s" target="_blank"><img src="%s" loading="lazy" alt="%s"></a>' % (src, src, html.escape(f))

cards = []
for d, j in jobs.items():
    if not by_job[d]:
        continue
    cards.append('<h2 id="%s">%s <small>%s</small></h2>' % (d, html.escape(j["title"]), html.escape(j["when"])))
    for e in by_job[d]:
        fields = "".join("<dt>%s</dt><dd>%s</dd>" % (label, html.escape(e[k])) for k, label in FIELDS if e.get(k))
        cards.append('<section class="entry" id="%s"><h3>%s</h3><div class="media">%s</div>'
                     '<p class="src">%s</p><dl>%s</dl></section>'
                     % (e["id"], e["id"], "".join(media(d, f) for f in e["files"]),
                        html.escape(e.get("source", "")), fields))
nav = " ".join('<a href="#%s">%s</a>' % (d, html.escape(j["title"])) for d, j in jobs.items() if by_job[d])
inbox_html = ('<h2>Waiting in _inbox</h2><ul>%s</ul>' % "".join("<li>%s</li>" % html.escape(f) for f in inbox)) if inbox else ""
page = """<!doctype html><html><head><meta charset="utf-8"><title>Graphics Reference Library</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#0e1420;--panel:#161e2e;--ink:#e8edf5;--dim:#9aa7bb;--acc:#ffcb47}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,Inter,Helvetica,sans-serif}
header{position:sticky;top:0;background:rgba(14,20,32,.96);padding:14px 20px;border-bottom:1px solid #243049;z-index:2}
header h1{margin:0 0 6px;font-size:20px} nav a{color:var(--acc);margin-right:14px;text-decoration:none;white-space:nowrap}
main{padding:10px 20px 60px;max-width:1400px;margin:0 auto}
h2{margin:34px 0 10px;font-size:22px;border-bottom:1px solid #243049;padding-bottom:6px}
h2 small{display:block;font-size:13px;color:var(--dim);font-weight:400}
.entry{background:var(--panel);border-radius:12px;padding:16px;margin:14px 0}
.entry h3{margin:0 0 10px;font-size:16px;color:var(--acc)}
.media{display:flex;gap:10px;flex-wrap:wrap}
.media img,.media video{max-height:260px;max-width:100%;border-radius:8px;border:1px solid #2a3650}
.src{color:var(--dim);font-size:13px;margin:8px 0}
dl{display:grid;grid-template-columns:110px 1fr;gap:4px 12px;margin:0}
dt{color:var(--dim);font-weight:600} dd{margin:0}
@media (max-width:640px){dl{grid-template-columns:1fr} dt{margin-top:6px}}
</style></head><body>
<header><h1>Graphics Reference Library</h1><nav>{{NAV}}</nav></header>
<main><p style="color:var(--dim)">{{ABOUT}}</p>{{CARDS}}{{INBOX}}</main></body></html>"""
page = (page.replace("{{NAV}}", nav).replace("{{ABOUT}}", html.escape(lib["about"]))
        .replace("{{CARDS}}", "\n".join(cards)).replace("{{INBOX}}", inbox_html))
open(os.path.join(ROOT, "gallery.html"), "w").write(page)

n = sum(len(v) for v in by_job.values())
print("%d entries, %d files catalogued; %d in _inbox" % (n, len(named), len(inbox)))
for p in problems:
    print("  PROBLEM:", p)
for o in orphans:
    print("  not catalogued:", o)
sys.exit(1 if problems else 0)
