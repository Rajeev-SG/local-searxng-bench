# local-searxng-bench

A one-off, deliberately small evaluation of whether a **local SearXNG** instance
(run in OrbStack/Docker on macOS) is good enough to be worth integrating into
coding-agent search. 12 real queries across Google Ads / TikTok Ads / Pinterest
Ads / Meta Ads, top-5 results inspected per engine config.

**Verdict: KEEP AS FALLBACK** — usable for bulk/free searches and reliable for
current official ad-platform docs, but noticeably weaker and more fragile than a
paid API (e.g. Brave). Worth wiring in as a free fallback; not worth replacing a
paid engine yet.

## Instance

- Image: `docker.io/searxng/searxng:latest` (SearXNG 2026.9.21)
- Bound to `127.0.0.1:8888` (localhost only).
  - **Deviation:** the brief asked for `8080`; that port is held on this Mac by
    the rig's `com.rajeev.codex-model-router` launchd service (KeepAlive), so
    SearXNG was moved to `8888` rather than disturbing it.
- JSON output enabled — verified:
  `http://localhost:8888/search?q=test&format=json` → HTTP 200.
- Minimal persistent config in `config/settings.yml`. No Redis, no reverse proxy.

### Engine availability from this host

| Requested engine | Status |
|---|---|
| Google | **Blocked** — native engine returns 0 results (silent empty) |
| DuckDuckGo | Works once, then **CAPTCHA** on burst |
| Bing | **Blocked** — request timeout; also inserts junk (site homepages) |
| Startpage | **Does not ship** in this image (no such engine) |
| (substitute) google cse | Public Google Custom Search CX, **no API key** — works well |
| (substitute) mojeek | Independent index — works well |

`google cse` uses the public blackle.com CX baked into the image; no credential
is required and none was supplied.

## Method

- 12 queries × 5 engine configs = **60 HTTP searches**. Top 5 inspected each
  (300 inspected rows; 1,217 results returned in total).
- Configs: the SearXNG **aggregate** (all default-enabled general/web engines)
  vs. each single engine called via `engines=` — `google cse`, `mojeek`,
  `duckduckgo`, `brave`.
- Scoring is intentionally crude: for each query, was the *correct/current
  official* doc domain present at rank 1 and in the top 5. No fancy metrics.

## Scoreboard

| Engine config | Top-1 official | Top-5 official | Empty (0-result) | Median latency |
|---|---|---|---|---|
| google cse | 11/12 | 12/12 | 0/12 | 0.61s |
| mojeek | 10/12 | 12/12 | 0/12 | 0.84s |
| **SearXNG aggregate (default)** | 10/12 | 10/12 | 0/12 | 1.06s |
| brave | 3/12 | 3/12 | 9/12 | — |
| duckduckgo | 1/12 | 1/12 | 11/12 | — |

### Findings

- **Best underlying engine: `google cse`** (11/12 top-1, sub-second, never
  blocked). Mojeek is the best truly-independent fallback.
- **Aggregation default hurt, then helped after pruning.** Out of the box the
  aggregate scored *worse* than its best member (10/12 vs 11/12) because the
  blocked Bing engine injected homepage/junk results — e.g. *"Pinterest campaign
  objectives"* returned pinterest.com homepage/profile pages at #1–5 while the
  official help page sat below the cap. After disabling bing/wikidata and keeping
  google cse + mojeek, a re-test of the 5 previously-missed queries scored
  **5/5 top-1** at a 1.08s median.
- **Official/current docs were discoverable** with the right engines: current
  official docs (Google Ads Help, ads.tiktok.com, business-api.tiktok.com,
  help.pinterest.com, developers.pinterest.com, developers.facebook.com) appeared
  in the top 5 for all 12 queries under google cse and mojeek.
- **Blocking problems:** Google + Bing native engines do not work from this host;
  DuckDuckGo CAPTCHAs and Brave suspends under any burst (unusable for agent
  traffic without keys/proxies); no Startpage engine ships.

### Practical recommendation

If integrating, call the **pinned** engine set
`engines=google+cse,mojeek` rather than the aggregate — that combination was the
fastest reliable configuration (~0.65s, 4/4 top-1 on the re-test).

## Repo contents

- `docker-compose.yml`, `config/settings.yml` — the instance as run.
- `bench/run.py` — the benchmark harness (writes `bench/results.json`).
- `bench/score.py` — crude scorer.
- `bench/results.json` — raw top-5 results for all 60 searches.
- `results/scores.json` — per-engine totals + per-query flags.
- `results/RESULTS.md` — human-readable per-query result tables (300 rows).

## Reproduce

```bash
docker compose up -d
curl "http://localhost:8888/search?q=test&format=json"
python3 bench/run.py && python3 bench/score.py
```
