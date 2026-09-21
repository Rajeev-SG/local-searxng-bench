import json, statistics, urllib.parse
d=json.load(open("results.json"))

OFFICIAL = {
 "Google Ads": ["support.google.com/google-ads","developers.google.com/google-ads","ads.google.com","business.google.com"],
 "TikTok": ["ads.tiktok.com","business-api.tiktok.com","developers.tiktok.com","support.tiktok.com"],
 "Pinterest": ["help.pinterest.com","developers.pinterest.com","business.pinterest.com","policy.pinterest.com"],
 "Meta": ["developers.facebook.com","facebook.com/business","transparency.fb.com","www.facebook.com/business"],
}
def family(q):
    ql=q.lower()
    if "google ads" in ql: return "Google Ads"
    if "tiktok" in ql: return "TikTok"
    if "pinterest" in ql: return "Pinterest"
    return "Meta"
def is_official(q,u):
    u=(u or "").lower()
    return any(dom in u for dom in OFFICIAL[family(q)])

ENG=["duckduckgo","brave","mojeek","google cse","__aggregate__"]
totals={}
for e in ENG:
    top1=top5=junk=errs=0; lats=[]; zero=0
    for q in d:
        r=d[q][e]; res=r["results"]; lats.append(r["latency"])
        n=r["n"]; un=r.get("unresponsive") or []
        if r.get("error") or un: errs+=1
        if n==0: zero+=1
        o=[is_official(q,x["u"]) for x in res]
        if o and o[0]: top1+=1
        if any(o): top5+=1
        # junk: reddit/youtube/shorts in top5 without official above
        j=any(("reddit.com" in (x["u"] or "") or "youtube.com" in (x["u"] or "") or "shorts" in (x["u"] or "")) for x in res)
        if j and not any(o): junk+=1
    totals[e]={"top1":top1,"top5":top5,"junk_when_no_official":junk,"errs":errs,"empty":zero,
               "lat_med":round(statistics.median(lats),2),"lat_max":round(max(lats),2)}
print(f"{'engine':16}{'top1/12':>8}{'top5/12':>8}{'junk':>6}{'errs':>6}{'empty':>6}{'med_lat':>9}{'max_lat':>9}")
for e in ENG:
    t=totals[e]
    print(f"{e:16}{t['top1']:>8}{t['top5']:>8}{t['junk_when_no_official']:>6}{t['errs']:>6}{t['empty']:>6}{t['lat_med']:>9}{t['lat_max']:>9}")
json.dump(totals,open("totals.json","w"),indent=1)
