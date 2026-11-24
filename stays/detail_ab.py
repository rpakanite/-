"""Fetch listing detail pages and classify bathroom privacy."""
import re, json, os, sys, time, random
from ab_lib import client
CACHE = "ab_detail.json"
def load(): return json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def parse_detail(t):
    ov = re.search(r'"overview":\{"__typename":"StaysPdpOverview","title":"([^"]*)","items":\[([^\]]*)\]', t)
    cal = re.search(r'"availabilityCalendarDescriptionItems":\[([^\]]*)\]', t)
    items = json.loads("[" + ov.group(2) + "]") if ov else []
    cal_items = json.loads("[" + cal.group(1) + "]") if cal else []
    return {"overview_title": ov.group(1) if ov else None, "overview_items": items, "cal_items": cal_items}
def classify(info, room_type):
    txt = " ".join(info.get("overview_items", []) + info.get("cal_items", []))
    title = info.get("overview_title") or ""
    if any(k in txt for k in ("공동 사용 욕실", "공용 욕실", "공유 욕실", "욕실 없음", "간이 욕실", "공용 화장실", "공동 사용 화장실")):
        return "shared/none"
    if "다인실" in txt or "다인실" in title: return "dorm"
    if "전용 욕실" in txt or "단독 사용 욕실" in txt: return "private"
    if room_type == "entire" and re.search(r"욕실 [\d.]+개", txt): return "private"
    return "unclear"
def check(ids_types):
    cache, c = load(), client()
    for lid, rt in ids_types:
        if lid in cache: continue
        for t in range(3):
            try:
                time.sleep(random.uniform(1.0, 2.0))
                r = c.get(f"https://www.airbnb.co.kr/rooms/{lid}", params={"check_in": "2027-01-30", "check_out": "2027-02-03", "adults": "1", "currency": "KRW", "locale": "ko"})
                info = parse_detail(r.text); info["status"] = r.status_code
                info["bath"] = classify(info, rt)
                cache[lid] = info; break
            except Exception as e:
                cache[lid] = {"error": repr(e)}; time.sleep(4)
        json.dump(cache, open(CACHE, "w"), ensure_ascii=False)
        print(lid, rt, cache[lid].get("bath"), cache[lid].get("overview_title"), cache[lid].get("overview_items"), flush=True)
    return cache
if __name__ == "__main__":
    print(parse_detail(open(sys.argv[1]).read()))
