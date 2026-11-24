"""One-way daily crawl of Google Flights. Usage: crawl.py ORIG DEST START END"""
import json, os, sys, time, random, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from selectolax.lexbor import LexborHTMLParser
from fast_flights import create_query, FlightQuery, fetch_flights_html

PROXY = os.environ.get("HTTPS_PROXY")

def parse_all(html):
    node = LexborHTMLParser(html).css_first(r"script.ds\:1")
    if node is None:
        raise RuntimeError("no ds:1 script")
    js = node.text()
    data = js.split("data:", 1)[1].rsplit(",", 1)[0]
    p = json.loads(data)
    out = []
    for idx in (2, 3):
        blk = p[idx]
        if not blk or not blk[0]:
            continue
        for k in blk[0]:
            try:
                price = k[1][0][1]
            except (IndexError, TypeError):
                continue
            if not price:
                continue
            f = k[0]
            legs = []
            for s in f[2]:
                dep = (s[8] or []) + [None, None]
                arr = (s[10] or []) + [None, None]
                legs.append({
                    "from": s[3], "to": s[6],
                    "dep": f"{dep[0] or 0:02d}:{dep[1] or 0:02d}",
                    "arr": f"{arr[0] or 0:02d}:{arr[1] or 0:02d}",
                    "arr_date": "-".join(f"{x:02d}" for x in s[21]) if s[21] else None,
                    "flight_no": f"{s[22][0]}{s[22][1]}" if len(s) > 22 and s[22] else None,
                })
            out.append({"price": price, "airline_code": f[0], "airlines": f[1], "legs": legs, "stops": len(legs) - 1})
    return out

def fetch(orig, dest, date, tries=4):
    path = f"{os.environ.get('OUTDIR', 'out')}/ow_{orig}_{dest}_{date}.json"
    if os.path.exists(path):
        return path, "cached"
    q = create_query(flights=[FlightQuery(date=date, from_airport=orig, to_airport=dest)],
                     trip="one-way", seat="economy", language="ko", currency="KRW")
    err = None
    for i in range(tries):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            flights = parse_all(fetch_flights_html(q, proxy=PROXY))
            json.dump({"orig": orig, "dest": dest, "date": date, "url": q.url(), "flights": flights},
                      open(path, "w"), ensure_ascii=False)
            return path, f"{len(flights)} flights, min {min((x['price'] for x in flights), default=None)}"
        except Exception as e:
            err = e
            time.sleep(3 * (i + 1))
    return path, f"FAILED: {err!r}"

if __name__ == "__main__":
    orig, dest, start, end = sys.argv[1:5]
    d0, d1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    dates = [(d0 + dt.timedelta(days=i)).isoformat() for i in range((d1 - d0).days + 1)]
    with ThreadPoolExecutor(max_workers=3) as ex:
        for date, (path, msg) in zip(dates, ex.map(lambda d: fetch(orig, dest, d), dates)):
            print(orig, dest, date, msg, flush=True)
