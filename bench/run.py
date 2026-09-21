import json, time, urllib.parse, urllib.request, os

BASE = "http://localhost:8888/search"
QUERIES = [
 "Google Ads AI Max setup",
 "Google Ads enhanced conversions setup",
 "Google Ads conversion tracking documentation",
 "TikTok Search Ads Campaign setup",
 "TikTok Smart+ documentation",
 "TikTok Events API documentation",
 "Pinterest Performance+ setup",
 "Pinterest Conversions API documentation",
 "Pinterest campaign objectives",
 "Meta Advantage+ campaigns",
 "Meta Conversions API documentation",
 "Meta campaign objectives documentation",
]
ENGINES = ["duckduckgo","brave","mojeek","google cse"]   # aggregate handled separately
OUT = os.path.expanduser("~/searxng/bench")

def fetch(q, engines=None, retries=1):
    p = {"q": q, "format": "json"}
    if engines: p["engines"] = engines
    url = BASE + "?" + urllib.parse.urlencode(p)
    last = None
    for _ in range(retries+1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                d = json.loads(r.read().decode())
            dt = time.time() - t0
            return d, dt, None
        except Exception as e:
            dt = time.time() - t0
            last = (dt, repr(e))
    return None, last[0], last[1]

report = {}
for qi, q in enumerate(QUERIES, 1):
    report[q] = {}
    d, dt, err = fetch(q)   # aggregate (all enabled engines)
    report[q]["__aggregate__"] = {"latency": round(dt,2), "error": err,
        "results": [{"t":x.get("title"),"u":x.get("url"),"e":x.get("engine")} for x in (d or {}).get("results",[])[:5]],
        "n": len((d or {}).get("results",[])),
        "unresponsive": (d or {}).get("unresponsive_engines")}
    print(f"[{qi}/12] {q[:40]:42} aggregate n={len((d or {}).get('results',[]))} {dt:.1f}s", flush=True)
    for e in ENGINES:
        d, dt, err = fetch(q, engines=e)
        report[q][e] = {"latency": round(dt,2), "error": err,
            "results": [{"t":x.get("title"),"u":x.get("url"),"e":x.get("engine")} for x in (d or {}).get("results",[])[:5]],
            "n": len((d or {}).get("results",[])),
            "unresponsive": (d or {}).get("unresponsive_engines")}
        print(f"      {e:14} n={len((d or {}).get('results',[])):3} {dt:.1f}s err={err}", flush=True)

json.dump(report, open(f"{OUT}/results.json","w"), indent=1)
print("SAVED", f"{OUT}/results.json")
