import json, glob, datetime as dt, sys
def load(orig, dest):
    res = {}
    for p in glob.glob(f"out/ow_{orig}_{dest}_*.json"):
        d = json.load(open(p))
        fl = sorted(d["flights"], key=lambda x: x["price"])
        if fl:
            res[d["date"]] = fl
    return res
OUT, RET = load("SEL", "TYO"), load("TYO", "SEL")
def best(fl, direct_only=False):
    for f in fl:
        if not direct_only or f["stops"] == 0:
            return f
def fmt(f):
    l = f["legs"]
    return f'{f["price"]:>9,}원 {"/".join(f["airlines"])} {l[0]["from"]}{l[0]["dep"]}→{l[-1]["to"]}{l[-1]["arr"]}' + ("" if f["stops"] == 0 else f' (경유{f["stops"]})')
combos = []
for ds, ofl in OUT.items():
    d = dt.date.fromisoformat(ds)
    for n in range(2, 8):
        rs = (d + dt.timedelta(days=n)).isoformat()
        if rs not in RET: continue
        o, r = best(ofl, True), best(RET[rs], True)
        if o and r:
            combos.append((o["price"] + r["price"], ds, rs, n, o, r))
combos.sort(key=lambda x: x[0])
print(f"out dates {len(OUT)}, ret dates {len(RET)}, combos {len(combos)}")
print("\n== 전체 최저 왕복 조합 (직항, 편도 합산) TOP 15 ==")
for t, ds, rs, n, o, r in combos[:15]:
    print(f"{t:>9,}원 | {ds}~{rs} ({n}박) | 가는편 {fmt(o)} | 오는편 {fmt(r)}")
print("\n== 일정 길이별 최저 ==")
for n in range(2, 8):
    c = [x for x in combos if x[3] == n][:3]
    for t, ds, rs, _, o, r in c:
        print(f"{n}박 {t:>9,}원 | {ds}~{rs} | {fmt(o)} | {fmt(r)}")
json.dump([{"total": t, "out_date": ds, "ret_date": rs, "nights": n, "out": o, "ret": r} for t, ds, rs, n, o, r in combos],
          open("out/combos.json", "w"), ensure_ascii=False)
