import json
BAD = ("공동 사용 욕실", "공용 욕실", "공유 욕실", "욕실 없음", "간이 욕실")
d = json.load(open("ab_raw.json"))
uniq = {}
for k, v in d.items():
    for x in v:
        if x["total"] and (x["id"] not in uniq or x["total"] < uniq[x["id"]]["total"]):
            uniq[x["id"]] = x
allx = sorted(uniq.values(), key=lambda x: x["total"])
cand = [x for x in allx if "다인실" not in (x["title"] or "") and not any(b in " ".join(x["lines"]) for b in BAD)
        and not any(w in (x["name"] or "") for w in ("캡슐", "カプセル", "도미토리", "dormitory", "Dormitory", "공용욕실", "공용 욕실", "共用"))]
print("unique", len(allx), "after prefilter", len(cand))
json.dump(cand, open("ab_cand.json", "w"), ensure_ascii=False)
for x in cand[:15]: print(x["total"], x["room_type"], x["title"], x["lines"], (x["name"] or "")[:40])
