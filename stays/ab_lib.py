import os, re, json, base64, time, random
from primp import Client
BASE = "https://www.airbnb.co.kr/s/Tokyo--Japan/homes"
COMMON = {"checkin": "2027-01-30", "checkout": "2027-02-03", "adults": "1", "currency": "KRW", "locale": "ko"}
def client():
    return Client(impersonate="chrome_145", impersonate_os="macos", referer=True,
                  proxy=os.environ.get("HTTPS_PROXY"), cookie_store=True)
def parse(html):
    m = re.search(r'<script[^>]+id="data-deferred-state-0"[^>]*>(.*?)</script>', html, re.S)
    if not m: raise RuntimeError("no deferred state")
    d = json.loads(m.group(1))
    ss = d["niobeClientData"][0][1]["data"]["presentation"]["staysSearch"]["results"]
    out = []
    for r in ss["searchResults"]:
        if r.get("__typename") != "StaySearchResult": continue
        lab = (r["structuredDisplayPrice"]["primaryLine"] or {}).get("accessibilityLabel") or ""
        nums = re.findall(r"₩([\d,]+)", lab)
        total = int(nums[-1].replace(",", "")) if nums else None
        # if discounted, label has original and discounted; discounted is usually the first one
        if len(nums) >= 2: total = min(int(x.replace(",", "")) for x in nums)
        lid = base64.b64decode(r["demandStayListing"]["id"]).decode().split(":")[-1]
        sc = r.get("structuredContent") or {}
        lines = [x.get("body") for x in (sc.get("primaryLine") or []) + (sc.get("secondaryLine") or [])]
        loc = r["demandStayListing"].get("location", {}).get("coordinate", {})
        expl = r["structuredDisplayPrice"].get("explanationData") or {}
        disclaimer = [x.get("content") for x in expl.get("priceDetails", []) if x.get("__typename") == "DisplayPriceExplanationDisclaimer"]
        out.append({"id": lid, "title": r.get("title"), "name": r.get("subtitle"), "area": r.get("eyebrowLocation"),
                    "lines": lines, "total": total, "price_label": lab, "rating": r.get("avgRatingLocalized"),
                    "lat": loc.get("latitude"), "lng": loc.get("longitude"), "room_variant": disclaimer,
                    "badges": [b.get("text") for b in r.get("badges") or []]})
    cursors = (ss.get("paginationInfo") or {}).get("pageCursors") or []
    return out, cursors
def search(c, extra, cursor=None):
    p = dict(COMMON); p.update(extra)
    if cursor: p["cursor"] = cursor
    r = c.get(BASE, params=p)
    if r.status_code != 200: raise RuntimeError(f"HTTP {r.status_code}")
    return parse(r.text)
