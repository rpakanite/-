"""Crawl Airbnb Tokyo listings for 2027-01-30 ~ 02-03 (1 adult) by room type and nightly price bucket."""
import json, os, sys, time, random
from ab_lib import client, search
ROOM_TYPES = {"entire": "Entire home/apt", "private": "Private room", "hotel": "Hotel room"}
BUCKETS = [(0, 30000), (30000, 40000), (40000, 50000), (50000, 60000), (60000, 70000), (70000, 85000)]
OUT = "ab_raw.json"
data = json.load(open(OUT)) if os.path.exists(OUT) else {}
c = client()
for rt_key, rt in ROOM_TYPES.items():
    for lo, hi in BUCKETS:
        key = f"{rt_key}:{lo}-{hi}"
        if key in data: continue
        extra = {"room_types[]": rt, "price_min": str(lo), "price_max": str(hi),
                 "price_filter_num_nights": "4", "price_filter_input_type": "0"}
        items, cursors, err = [], [None], None
        try:
            res, cursors = search(c, extra); items += res
            for cur in cursors[1:15]:
                time.sleep(random.uniform(1.0, 2.0))
                for t in range(3):
                    try:
                        res, _ = search(c, extra, cur); items += res; break
                    except Exception as e:
                        err = repr(e); time.sleep(4 * (t + 1))
        except Exception as e:
            err = repr(e)
        for x in items: x["room_type"] = rt_key
        data[key] = items
        json.dump(data, open(OUT, "w"), ensure_ascii=False)
        print(key, "pages", len(cursors), "items", len(items), "unique", len({x['id'] for x in items}),
              "min", min((x["total"] for x in items if x["total"]), default=None), err or "", flush=True)
        time.sleep(random.uniform(1.0, 2.0))
