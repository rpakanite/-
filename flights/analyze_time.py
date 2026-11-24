"""Combos with time filters: outbound dep < OUT_BEFORE, return dep >= RET_AFTER (direct only).
Usage: analyze_time.py [MIN_OUT_DATE [NIGHTS]]  e.g. 2027-01-04 4  (skip Oshogatsu, 4-night trips only)."""
import json, os, sys, datetime as dt
from analyze import OUT, RET, fmt
OUT_BEFORE, RET_AFTER = "12:00", "15:00"
MIN_OUT = sys.argv[1] if len(sys.argv) > 1 else "0000-00-00"
NIGHTS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else list(range(2, 8))
def pick(fl, ok):
    return next((f for f in fl if f["stops"] == 0 and ok(f["legs"][0]["dep"])), None)
o_ok = lambda t: t < OUT_BEFORE
r_ok = lambda t: t >= RET_AFTER
combos = []
for ds, ofl in OUT.items():
    if ds < MIN_OUT: continue
    o = pick(ofl, o_ok)
    if not o: continue
    d = dt.date.fromisoformat(ds)
    for n in NIGHTS:
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
for n in NIGHTS:
    for t, ds, rs, _, o, r in [x for x in combos if x[3] == n][:2]:
        print(f"{n}박 {t:>9,}원 | {w(ds)}~{w(rs)} | {o['legs'][0]['flight_no']} {o['legs'][0]['dep']} | {r['legs'][0]['flight_no']} {r['legs'][0]['dep']}")
print("\n== 가는편(12시 전) 최저 10일 ==")
for ds, f in sorted(((d, pick(f, o_ok)) for d, f in OUT.items() if d >= MIN_OUT and pick(f, o_ok)), key=lambda x: (x[1]["price"], x[0]))[:10]:
    print(w(ds), f["legs"][0]["flight_no"], fmt(f))
print("\n== 오는편(15시 이후) 최저 10일 ==")
for ds, f in sorted(((d, pick(f, r_ok)) for d, f in RET.items() if d >= MIN_OUT and pick(f, r_ok)), key=lambda x: (x[1]["price"], x[0]))[:10]:
    print(w(ds), f["legs"][0]["flight_no"], fmt(f))
json.dump([{"total": t, "out_date": ds, "ret_date": rs, "nights": n, "out": o, "ret": r} for t, ds, rs, n, o, r in combos],
          open(f"{os.environ.get('OUTDIR', 'out')}/combos_time.json", "w"), ensure_ascii=False)
