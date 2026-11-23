"""Verify round-trip totals for top combos via real round-trip searches."""
import json, os, sys, time, random
from fast_flights import create_query, FlightQuery, fetch_flights_html
from crawl import parse_all, PROXY
combos = json.load(open("out/combos.json"))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
seen, pairs = set(), []
for c in combos:
    k = (c["out_date"], c["ret_date"])
    if k not in seen:
        seen.add(k); pairs.append(c)
    if len(pairs) >= n: break
res = []
for c in pairs:
    q = create_query(flights=[FlightQuery(date=c["out_date"], from_airport="SEL", to_airport="TYO"),
                              FlightQuery(date=c["ret_date"], from_airport="TYO", to_airport="SEL")],
                     trip="round-trip", seat="economy", language="ko", currency="KRW")
    for i in range(3):
        try:
            time.sleep(random.uniform(1, 2))
            fl = sorted(parse_all(fetch_flights_html(q, proxy=PROXY)), key=lambda x: x["price"])
            break
        except Exception as e:
            fl = []; time.sleep(3)
    top = fl[0] if fl else None
    top_direct = next((f for f in fl if f["stops"] == 0), None)
    res.append({**c, "rt_url": q.url(), "rt_min": top and top["price"], "rt_min_flight": top,
                "rt_min_direct": top_direct and top_direct["price"], "rt_min_direct_flight": top_direct})
    print(c["out_date"], c["ret_date"], "sum", c["total"], "rt", top and top["price"],
          top and top["airlines"], "rt_direct", top_direct and top_direct["price"], flush=True)
json.dump(res, open("out/verified.json", "w"), ensure_ascii=False)
