"""Combos with time filters: outbound dep < OUT_BEFORE, return dep >= RET_AFTER (direct only)."""
import json, sys, datetime as dt
from analyze import OUT, RET, fmt
OUT_BEFORE, RET_AFTER = "12:00", "15:00"
def pick(fl, ok):
    return next((f for f in fl if f["stops"] == 0 and ok(f["legs"][0]["dep"])), None)
o_ok = lambda t: t < OUT_BEFORE
r_ok = lambda t: t >= RET_AFTER
combos = []
for ds, ofl in OUT.items():
    o = pick(ofl, o_ok)
    if not o: continue
    d = dt.date.fromisoformat(ds)
    for n in range(2, 8):
        rs = (d + dt.timedelta(days=n)).isoformat()
        r = pick(RET.get(rs, []), r_ok)
        if r: combos.append((o["price"] + r["price"], ds, rs, n, o, r))
combos.sort(key=lambda x: (x[0], x[1]))
WD = "월화수목금토일"
w = lambda s: f"{s[5:]}({WD[dt.date.fromisoformat(s).weekday()]})"
print("== TOP 15 ==")
for t, ds, rs, n, o, r in combos[:15]:
    print(f"{t:>9,}원 | {w(ds)}~{w(rs)} {n}박 | {o['legs'][0]['flight_no']} {fmt(o)} | {r['legs'][0]['flight_no']} {fmt(r)}")
print("\n== 일정 길이별 ==")
for n in range(2, 8):
    for t, ds, rs, _, o, r in [x for x in combos if x[3] == n][:2]:
        print(f"{n}박 {t:>9,}원 | {w(ds)}~{w(rs)} | {o['legs'][0]['flight_no']} {o['legs'][0]['dep']} | {r['legs'][0]['flight_no']} {r['legs'][0]['dep']}")
print("\n== 가는편(12시 전) 최저 10일 ==")
for ds, f in sorted(((d, pick(f, o_ok)) for d, f in OUT.items() if pick(f, o_ok)), key=lambda x: (x[1]["price"], x[0]))[:10]:
    print(w(ds), f["legs"][0]["flight_no"], fmt(f))
print("\n== 오는편(15시 이후) 최저 10일 ==")
for ds, f in sorted(((d, pick(f, r_ok)) for d, f in RET.items() if pick(f, r_ok)), key=lambda x: (x[1]["price"], x[0]))[:10]:
    print(w(ds), f["legs"][0]["flight_no"], fmt(f))
json.dump([{"total": t, "out_date": ds, "ret_date": rs, "nights": n, "out": o, "ret": r} for t, ds, rs, n, o, r in combos],
          open("out/combos_time.json", "w"), ensure_ascii=False)
