import json, sys
sys.path.insert(0, ".")
from detail_ab import classify
cand = {x["id"]: x for x in json.load(open("ab_cand.json"))}
det = json.load(open("ab_detail.json"))
rows = []
for lid, info in det.items():
    if "error" in info or lid not in cand: continue
    x = cand[lid]; info["bath"] = classify(info, x["room_type"])
    rows.append((x["total"], lid, x, info))
json.dump(det, open("ab_detail.json", "w"), ensure_ascii=False)
rows.sort(key=lambda r: r[0])
from collections import Counter
print(Counter(r[3]["bath"] for r in rows))
print("checked price range", rows[0][0], "~", rows[-1][0])
for t, lid, x, info in rows:
    if info["bath"] == "private":
        print(f"{t:>8,}원 {x['room_type']:7} {info['overview_title']} | {info['overview_items']} | {x['name'][:45]} | {x['rating']} | https://www.airbnb.co.kr/rooms/{lid}")
