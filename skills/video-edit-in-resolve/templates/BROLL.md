# B-roll sources

Work down this ladder. Only move to the next rung when the one above has nothing usable.
Report the source of every clip placed.

## 1. The operator's own library  (FIRST, ALWAYS)

- `assets/` in this project folder
- Additional library path: TODO, add if one exists

Free, on-brand, already cleared.

## 2. Free stock APIs  (no approval needed)

- **Pexels** - `https://api.pexels.com/v1/videos/search`. Free key. 200 req/hour, 20,000/month.
- **Pixabay** - `https://pixabay.com/api/videos/`. Free key. 100 req/60s. Cache results 24 hours.

Pull candidates to `broll/candidates/`, show the operator the filenames with the search term used, let them pick. Do not re-request a query already cached.

API keys: TODO, add when obtained. Both are free to register.

## 3. Paid stock subscription

**None active.** Do not assume one exists. If the operator adds Storyblocks or Artgrid, record it here with the plan and whether API access is included. Storyblocks is the only one of these with a real first-party API.

## 4. AI generation  (OFF by default)

**Not enabled.** Do not generate AI B-roll unless the operator turns this on in this file.

If enabled: Higgsfield first-party MCP, spends plan credits, no API key needed. Before generating anything, state how many clips, roughly how many credits, and that regenerations cost the same as the original. Wait for an explicit yes.

## Placement

Whatever the source, the clip imports to the media pool and sits on the upper video track at the marked position. Never replace the talking-head track.
