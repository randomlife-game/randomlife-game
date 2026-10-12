#!/usr/bin/env python3
"""원자료를 나라별·연도별 게임 데이터로 가공해 index.html에 넣어요.

사용법:
  tools/fetch_sources.sh /tmp/src          # 원자료 내려받기
  python3 tools/build_world_data.py /tmp/src   # data/world.json 만들고 index.html 갱신

모든 값은 공개 원자료(세계은행 WDI, UN WPP 2024, UNDP HDR, World Happiness Report,
Maddison Project 2020, Lee-Lee 2016, UCDP/PRIO, UN 도시화 자료)에서 직접 계산해요.
비어 있는 값은 같은 지역·소득 그룹의 중앙값으로 채우고, 그 칸은 추정(est) 표시를 남겨요.
"""
import csv, gzip, json, re, sys, statistics, os
from pathlib import Path

SRC = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"

# ---------- 게임 안 나라 목록(지역·소득 그룹) ----------
html = HTML.read_text(encoding="utf-8")
CTRY = json.loads(re.search(r"const COUNTRIES=(\[.*?\]);\n", html).group(1))
ISO = [c[0] for c in CTRY]
REG = {c[0]: c[3] for c in CTRY}
INC = {c[0]: c[4] for c in CTRY}

# ---------- 1. 세계은행 WDI(가장 최근 값) ----------
# key, WDI 코드, 원 출처(게임 안 출처 표기용), 소수 자리
WB = [
    ("u5", "SH.DYN.MORT", 1), ("nmr", "SH.DYN.NMRT", 1), ("mmr", "SH.STA.MMRT", 0),
    ("smk", "SH.PRV.SMOK", 1), ("smkm", "SH.PRV.SMOK.MA", 1), ("smkf", "SH.PRV.SMOK.FE", 1),
    ("hexp", "SH.XPD.CHEX.PC.CD", 0), ("oop", "SH.XPD.OOPC.CH.ZS", 0),
    ("lit", "SE.ADT.LITR.ZS", 0), ("prim", "SE.PRM.CMPT.ZS", 0), ("lsec", "SE.SEC.CMPT.LO.ZS", 0),
    ("ter", "SE.TER.ENRR", 0), ("unemp", "SL.UEM.TOTL.ZS", 1), ("yunemp", "SL.UEM.1524.ZS", 1),
    ("flfp", "SL.TLF.CACT.FE.ZS", 0), ("agri", "SL.AGR.EMPL.ZS", 0), ("vuln", "SL.EMP.VULN.ZS", 0),
    ("hiv", "SH.DYN.AIDS.ZS", 1), ("art", "SH.HIV.ARTC.ZS", 0), ("hom", "VC.IHR.PSRC.P5", 1),
    ("road", "SH.STA.TRAF.P5", 1), ("suic", "SH.STA.SUIC.P5", 1), ("cm18", "SP.M18.2024.FE.ZS", 0),
    ("pov3", "SI.POV.DDAY", 1), ("pov4", "SI.POV.LMIC", 1), ("pov8", "SI.POV.UMIC", 1), ("gini", "SI.POV.GINI", 0),
    ("elec", "EG.ELC.ACCS.ZS", 0), ("water", "SH.H2O.BASW.ZS", 0), ("sani", "SH.STA.BASS.ZS", 0),
    ("net", "IT.NET.USER.ZS", 0), ("hunger", "SN.ITK.DEFC.ZS", 1), ("stunt", "SH.STA.STNT.ZS", 0),
    ("clab", "SL.TLF.0714.ZS", 0), ("adof", "SP.ADO.TFRT", 0), ("phys", "SH.MED.PHYS.ZS", 1),
    ("migr", "SM.POP.TOTL.ZS", 1), ("comm", "SH.DTH.COMM.ZS", 0), ("ncd", "SH.DTH.NCOM.ZS", 0),
    ("inj", "SH.DTH.INJR.ZS", 0), ("ncdp", "SH.DYN.NCOM.ZS", 0), ("alc", "SH.ALC.PCAP.LI", 1),
    ("gdp", "NY.GDP.PCAP.PP.CD", 0), ("urb", "SP.URB.TOTL.IN.ZS", 0), ("brtc", "SH.STA.BRTC.ZS", 0),
]
IND, EST, YEAR = {k: {} for k, _, _ in WB}, {}, {}
for key, code, _ in WB:
    p = SRC / "wb" / f"{code}.json"
    if not p.exists():
        print("missing", code); continue
    data = json.loads(p.read_text())
    rows = data[1] if len(data) > 1 and data[1] else []
    best = {}
    for r in rows:
        iso, v, y = r["countryiso3code"], r["value"], int(r["date"])
        if iso in REG and v is not None and (iso not in best or y > best[iso][1]):
            best[iso] = (v, y)
    for iso, (v, y) in best.items():
        IND[key][iso] = v; YEAR.setdefault(key, {})[iso] = y

# ---------- 2. UNDP 인간개발보고서 ----------
HDR = {"hdi": "hdi_2022", "mys": "mys_2022", "eys": "eys_2022", "gii": "gii_2022"}
for k in HDR: IND[k] = {}
with open(SRC / "hdr.csv", encoding="latin-1") as f:
    for r in csv.DictReader(f):
        if r["iso3"] in REG:
            for k, col in HDR.items():
                if r.get(col) not in (None, ""): IND[k][r["iso3"]] = float(r[col])

# ---------- 3. 세계행복보고서(가장 최근 3년 평균) ----------
IND["happy"] = {}
with open(SRC / "happy.csv") as f:
    best = {}
    for r in csv.DictReader(f):
        if r["code"] in REG and (r["code"] not in best or int(r["year"]) > best[r["code"]][1]):
            best[r["code"]] = (float(r["cantril_ladder_score"]), int(r["year"]))
    IND["happy"] = {k: v for k, (v, _) in best.items()}

KEYS = [k for k, _, _ in WB] + list(HDR) + ["happy"]
DEC = {k: d for k, _, d in WB} | {"hdi": 3, "mys": 1, "eys": 1, "gii": 3, "happy": 2}

# 결측치: 같은 지역+소득 → 같은 소득 → 같은 지역 → 전체 중앙값
def med(vals): return statistics.median(vals) if vals else None
for k in KEYS:
    have = IND[k]
    for iso in ISO:
        if iso in have: continue
        for grp in (lambda c: REG[c] == REG[iso] and INC[c] == INC[iso], lambda c: INC[c] == INC[iso],
                    lambda c: REG[c] == REG[iso], lambda c: True):
            v = med([have[c] for c in have if grp(c)])
            if v is not None:
                have[iso] = v; EST.setdefault(iso, set()).add(k); break

# ---------- 4. UN 세계인구전망 2024(연도별) ----------
TY = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2025, 2050, 2075, 2100]
TCOL = ["Births", "LExMale", "LExFemale", "Q5", "Q0040", "Q0060Male", "Q0060Female", "LE65Male", "LE65Female", "TFR"]
# 정수로 저장: 출생 수(100명 단위), 기대수명·65세 여명 ×10, 사망 확률(천 명당) Q5 ×10, Q40·Q60 그대로, 합계출산율 ×100
TMUL = [10, 10, 10, 10, 1, 1, 1, 10, 10, 100]
ts, world = {}, {}
want = set(TY)
with gzip.open(SRC / "wpp_demo.csv.gz", "rt", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        y = int(r["Time"])
        if y not in want: continue
        iso = r["ISO3_code"] or ("WLD" if r["Location"] == "World" else None)
        if iso == "GGY": iso = "CHI"   # 채널 제도: 건지+저지 합산 대신 건지 값을 대표로(출생 수는 아래에서 보정)
        if iso is None or (iso not in REG and iso != "WLD"): continue
        vals = []
        for c in TCOL:
            v = r[c]; vals.append(float(v) if v not in ("", None) else None)
        ts.setdefault(iso, {})[y] = vals
JEY = None
for iso in ISO:
    if iso not in ts: print("no WPP", iso)
TS = {}
for iso, byy in list(ts.items()):
    TS[iso] = [[round(byy[y][i] * TMUL[i]) for y in TY] for i in range(len(TCOL))]
# 출생 수: 채널 제도는 세계은행 추정 출생 수 비율로 보정
for c in CTRY:
    if c[0] == "CHI":
        r = c[5] / max(1, TS["CHI"][0][TY.index(2025)])
        TS["CHI"][0] = [round(v * r) for v in TS["CHI"][0]]

# ---------- 5. 도시 인구 비율(UN 기준, HYDE·UN 전망 결합, OWID 경유) ----------
UY = list(range(1950, 2051, 10))
urb = {}
with open(SRC / "urban2050.csv") as f:
    for r in csv.DictReader(f):
        y = int(r["year"])
        if r["code"] in REG and y in UY and r["urban_population"] and r["rural_population"]:
            u, ru = float(r["urban_population"]), float(r["rural_population"])
            urb.setdefault(r["code"], {})[y] = round(100 * u / (u + ru)) if u + ru else None
UR = {iso: [urb[iso].get(y) for y in UY] for iso in urb}

# ---------- 6. Maddison Project 2020: 1인당 GDP(2011년 국제달러) ----------
import pandas as pd
MY = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2018]
mpd = pd.read_excel(SRC / "mpd2020.xlsx", sheet_name="Full data")
MD = {}
for iso, g in mpd.groupby("countrycode"):
    if iso not in REG: continue
    s = dict(zip(g.year, g.gdppc))
    row = []
    for y in MY:
        v = s.get(y)
        if v is None or v != v:  # 가까운 해로 대체
            near = [yy for yy in s if s[yy] == s[yy] and abs(yy - y) <= 5]
            v = s[min(near, key=lambda yy: abs(yy - y))] if near else None
        row.append(None if v is None else round(v))
    if any(v is not None for v in row): MD[iso] = row

# ---------- 7. 평균 교육 연수(Lee-Lee 2016, 15–64세) ----------
SY = [1950, 1960, 1970, 1980, 1990, 2000, 2010]
sch = {}
with open(SRC / "school_long.csv") as f:
    col = None
    for r in csv.DictReader(f):
        col = col or [k for k in r if k not in ("entity", "code", "year")][0]
        y = int(r["year"])
        if r["code"] in REG and y in SY and r[col]: sch.setdefault(r["code"], {})[y] = round(float(r[col]), 1)
SC = {iso: [sch[iso].get(y) for y in SY] for iso in sch}

# 연도별 결측: 같은 지역·소득 나라의 '지금 대비 비율' 중앙값으로 추정
def fill_series(S, years, now_val, label):
    for iso in ISO:
        row = S.get(iso)
        if row and all(v is not None for v in row): continue
        peers = [c for c in S if REG[c] == REG[iso] and all(v is not None for v in S[c])] or \
                [c for c in S if all(v is not None for v in S[c])]
        base = now_val(iso)
        out = []
        for i in range(len(years)):
            if row and row[i] is not None: out.append(row[i]); continue
            ratios = [S[c][i] / now_val(c) for c in peers if now_val(c)]
            out.append(None if base is None or not ratios else round(base * statistics.median(ratios), 1))
        S[iso] = out; EST.setdefault(iso, set()).add(label)
fill_series(MD, MY, lambda c: (MD[c][-1] if c in MD and MD[c][-1] else None) or IND["gdp"].get(c), "md")
fill_series(SC, SY, lambda c: (SC[c][-1] if c in SC and SC[c][-1] else None) or IND["mys"].get(c), "sc")
fill_series(UR, UY, lambda c: (UR[c][7] if c in UR and UR[c][7] else None) or IND.get("urb", {}).get(c) or 50, "ur")
for iso in ISO:
    MD[iso] = [None if v is None else round(v) for v in MD[iso]]
    UR[iso] = [None if v is None else min(100, round(v)) for v in UR[iso]]

# ---------- 8. UCDP/PRIO 무력분쟁(1946–) ----------
GW = {2:"USA",40:"CUB",41:"HTI",42:"DOM",52:"TTO",55:"GRD",70:"MEX",90:"GTM",91:"HND",92:"SLV",93:"NIC",94:"CRI",95:"PAN",
100:"COL",101:"VEN",115:"SUR",130:"ECU",135:"PER",145:"BOL",150:"PRY",155:"CHL",160:"ARG",165:"URY",200:"GBR",210:"NLD",
220:"FRA",230:"ESP",310:"HUN",339:"ALB",343:"MKD",344:"HRV",345:"SRB",346:"BIH",350:"GRC",352:"CYP",359:"MDA",360:"ROU",
365:"RUS",369:"UKR",372:"GEO",373:"AZE",404:"GNB",420:"GMB",432:"MLI",433:"SEN",434:"BEN",435:"MRT",436:"NER",437:"CIV",
438:"GIN",439:"BFA",450:"LBR",451:"SLE",452:"GHA",461:"TGO",471:"CMR",475:"NGA",481:"GAB",482:"CAF",483:"TCD",484:"COG",
490:"COD",500:"UGA",501:"KEN",510:"TZA",516:"BDI",517:"RWA",520:"SOM",522:"DJI",530:"ETH",531:"ERI",540:"AGO",541:"MOZ",
552:"ZWE",560:"ZAF",570:"LSO",580:"MDG",581:"COM",600:"MAR",615:"DZA",616:"TUN",620:"LBY",625:"SDN",626:"SSD",630:"IRN",
640:"TUR",645:"IRQ",651:"EGY",652:"SYR",660:"LBN",663:"JOR",666:"ISR",670:"SAU",678:"YEM",680:"YEM",690:"KWT",698:"OMN",
700:"AFG",702:"TJK",703:"KGZ",704:"UZB",710:"CHN",713:"TWN",731:"PRK",732:"KOR",750:"IND",751:"IND",770:"PAK",771:"BGD",
775:"MMR",780:"LKA",790:"NPL",800:"THA",811:"KHM",812:"LAO",816:"VNM",817:"VNM",820:"MYS",835:"BRN",840:"PHL",850:"IDN",
900:"AUS",910:"PNG"}
W0, W1 = 1946, 2025
lvl = {}
ucdp = next((SRC / "ucdp").glob("*.csv"))
with open(ucdp) as f:
    for r in csv.DictReader(f):
        if r["type_of_conflict"] not in ("2", "3", "4"): continue
        y, it = int(r["year"]), int(r["intensity_level"])
        isos = {GW.get(int(c)) for c in r["gwno_loc"].split(",")}
        if "ISR" in isos: isos.add("PSE")
        if r["territory_name"] == "Kosovo": isos.add("XKX")
        for iso in isos:
            if iso in REG:
                a = lvl.setdefault(iso, [0] * (W1 - W0 + 1))
                a[y - W0] = max(a[y - W0], it)
WAR = {iso: "".join(map(str, a)) for iso, a in lvl.items()}

# ---------- 9. 소득과 지표의 관계(오늘날 나라들 사이의 기울기) ----------
# 지난 세상에서 오늘 값만 있는 지표를 옮길 때 쓰는 회귀식 [절편, 기울기]: 보급률은 logit, 위험은 log 를 1인당 소득(PPP) log 에 회귀(실제 값만 사용)
import math
def slope(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
EL = {}
for k, kind in [("elec", "c"), ("water", "c"), ("prim", "c"), ("lsec", "c"), ("lit", "c"), ("brtc", "c"),
                ("hunger", "r"), ("cm18", "r"), ("clab", "r"), ("stunt", "r")]:
    xs, ys = [], []
    for iso in ISO:
        if k in EST.get(iso, ()) or "gdp" in EST.get(iso, ()): continue
        v, g = IND[k].get(iso), IND["gdp"].get(iso)
        if v is None or not g: continue
        if kind == "c":
            p = min(99.5, max(0.5, v)) / 100; ys.append(math.log(p / (1 - p)))
        else:
            if v <= 0: continue
            ys.append(math.log(v))
        xs.append(math.log(g))
    b = slope(xs, ys); a = sum(ys) / len(ys) - b * sum(xs) / len(xs)
    EL[k] = [round(a, 3), round(b, 3)]
print("elasticities", EL)

# ---------- 출력 ----------
def rnd(v, d):
    if v is None: return None
    v = round(v, d); return int(v) if d == 0 else v
I = {iso: [rnd(IND[k].get(iso), DEC[k]) for k in KEYS] for iso in ISO}
E = {iso: [KEYS.index(k) if k in KEYS else k for k in sorted(EST[iso], key=str)] for iso in ISO if iso in EST}
out = {"k": KEYS, "I": I, "E": E, "ty": TY, "T": TS, "uy": UY, "U": UR, "my": MY, "M": MD, "sy": SY, "S": SC,
       "w0": W0, "W": WAR, "el": EL, "yr": {k: max(YEAR.get(k, {0: 0}).values()) for k, _, _ in WB}}
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "world.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
js = "const WD=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";"
a, b = "/*WD:BEGIN*/", "/*WD:END*/"
if a in html:
    html = html[:html.index(a) + len(a)] + js + html[html.index(b):]
    HTML.write_text(html, encoding="utf-8")
print("WD bytes", len(js), "estimated cells", sum(len(v) for v in EST.values()))
