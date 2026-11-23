import json, glob, csv, datetime as dt
from analyze import OUT, RET, best
rows = []
WD = "월화수목금토일"
for label, data in (("가는편 SEL→TYO", OUT), ("오는편 TYO→SEL", RET)):
    print(f"\n== {label}: 직항 최저가 하위 10일 ==")
    items = sorted(((d, best(f, True)) for d, f in data.items() if best(f, True)), key=lambda x: (x[1]["price"], x[0]))
    for d, f in items[:10]:
        l = f["legs"][0]
        print(f'{d}({WD[dt.date.fromisoformat(d).weekday()]}) {f["price"]:>8,}원 {"/".join(f["airlines"])} {l["flight_no"]} {l["from"]}{l["dep"]}→{l["to"]}{l["arr"]}')
    for d, f in sorted(items):
        l = f["legs"][0]
        rows.append([label, d, WD[dt.date.fromisoformat(d).weekday()], f["price"], "/".join(f["airlines"]), l["flight_no"], l["from"], l["dep"], l["to"], l["arr"]])
with open("out/daily_min.csv", "w", newline="", encoding="utf-8-sig") as fp:
    w = csv.writer(fp); w.writerow(["방향","날짜","요일","최저가(원)","항공사","편명","출발","출발시각","도착","도착시각"]); w.writerows(rows)
# monthly averages
for label, data in (("가는편", OUT), ("오는편", RET)):
    for m in ("2027-01", "2027-02"):
        ps = [best(f, True)["price"] for d, f in data.items() if d.startswith(m) and best(f, True)]
        print(label, m, "평균", round(sum(ps)/len(ps)), "최저", min(ps), "최고", max(ps))
