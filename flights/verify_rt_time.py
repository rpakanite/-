"""Verify time-filtered round trips: outbound dep < 12:00, return dep >= 15:00."""
import json, sys, time, random
from fast_flights import create_query, FlightQuery, fetch_flights_html
from crawl import parse_all, PROXY
import os
OUTDIR = os.environ.get("OUTDIR", "out")
combos = json.load(open(f"{OUTDIR}/combos_time.json"))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
seen, pairs = set(), []
for c in combos:
    k = (c["out_date"], c["ret_date"])
    if k not in seen:
        seen.add(k); pairs.append(c)
    if len(pairs) >= n: break
res = []
for c in pairs:
    q = create_query(flights=[FlightQuery(date=c["out_date"], from_airport="SEL", to_airport="TYO", latest_departure_hour=11),
                              FlightQuery(date=c["ret_date"], from_airport="TYO", to_airport="SEL", earliest_departure_hour=15)],
                     trip="round-trip", seat="economy", language="ko", currency="KRW")
    fl, err = [], None
    for i in range(5):
        try:
            time.sleep(random.uniform(1, 2))
            fl = sorted(parse_all(fetch_flights_html(q, proxy=PROXY)), key=lambda x: x["price"]); err = None; break
        except Exception as e:
            err = repr(e)[:120]; time.sleep(5 * (i + 1))
    ok = [f for f in fl if f["stops"] == 0 and f["legs"][0]["dep"] < "12:00"]
    top = ok[0] if ok else None
    deps = sorted({f["legs"][0]["dep"] for f in fl})
    res.append({**c, "rt_url": q.url(), "rt_min": top and top["price"], "rt_flight": top, "error": err})
    print(c["out_date"], c["ret_date"], "sum", c["total"], "rt", top and top["price"],
          top and (top["airlines"], top["legs"][0]["flight_no"], top["legs"][0]["dep"]),
          f"n={len(fl)}", err or "", flush=True)
json.dump(res, open(f"{OUTDIR}/verified_time.json", "w"), ensure_ascii=False)
