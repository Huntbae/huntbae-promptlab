#!/usr/bin/env python3
"""huntbae.com 정부지원사업 허브 데이터 갱신 스크립트.

수집원
- 기업마당(bizinfo.go.kr): BIZINFO_API_KEY 환경변수가 있으면 공식 API, 없으면 '진행 중 공고' 목록 화면을 읽음
- K-Startup(k-startup.go.kr): '모집중' 목록 화면을 읽음

결과: site/data/gov-live.json  (기존 파일보다 건수가 크게 줄면 덮어쓰지 않음)
사용: python3 scripts/update_gov.py [--max-pages N]
"""
import json, os, re, sys, time, html, datetime as dt
import urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "data", "gov-live.json")
UA = "Mozilla/5.0 (compatible; huntbae-gov-hub/1.0; +https://www.huntbae.com)"
KST = dt.timezone(dt.timedelta(hours=9))
TODAY = dt.datetime.now(KST).date()

def get(url, data=None, timeout=30, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:  # noqa
            last = e; time.sleep(2 + i * 3)
    raise last

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(html.unescape(s))).strip()

# ---------- 분류 ----------
CAT_RULES = [
    ("rnd", r"R&D|R＆D|연구개발|기술개발|기술혁신|실증|테스트베드|TIPS|팁스|과제"),
    ("fund", r"융자|정책자금|보증|대출|이차보전|자금지원|금융|투자유치|펀드|IR\b"),
    ("voucher", r"바우처"),
    ("cert", r"인증|확인서|벤처기업|이노비즈|메인비즈|부설연구소|지정|특허|지식재산|IP\b"),
    ("export", r"수출|해외|글로벌|무역|박람회|전시회|KOTRA|바이어"),
    ("hr", r"인력|채용|고용|일자리|장려금|인턴|구직|취업"),
    ("startup", r"창업|스타트업|예비창업|초기창업|사업화|액셀러|보육|입주|창업사관"),
    ("ai_digital", r"AI|인공지능|디지털|스마트공장|스마트상점|데이터|클라우드|플랫폼|DX|메타버스"),
    ("smallbiz", r"소상공인|자영업|전통시장|상권|골목|점포|가게|상인"),
    ("edu", r"교육|멘토링|컨설팅|아카데미|캠프|세미나|설명회|포럼|네트워킹|데모데이|행사"),
    ("mgmt", r"판로|마케팅|홍보|브랜드|온라인|쇼핑|입점|공공구매|조달|경영|컨설팅|ESG|안전|환경개선"),
]
FIELD_MAP = {  # 원본 분야 → 기본 분류
    "금융": "fund", "기술": "rnd", "인력": "hr", "수출": "export", "내수": "mgmt", "창업": "startup",
    "경영": "mgmt", "사업화": "startup", "창업교육": "edu", "멘토링ㆍ컨설팅ㆍ교육": "edu",
    "시설ㆍ공간ㆍ보육": "startup", "행사ㆍ네트워크": "edu", "융자": "fund", "글로벌": "export",
    "기술개발(R&D)": "rnd", "인력": "hr",
}
REGIONS = ["서울","부산","대구","인천","광주","대전","울산","세종","경기","강원","충북","충남","전북","전남","경북","경남","제주"]
REGION_FULL = {"전남광주통합특별시":"전남","서울특별시":"서울","부산광역시":"부산","대구광역시":"대구","인천광역시":"인천","광주광역시":"광주","대전광역시":"대전","울산광역시":"울산","세종특별자치시":"세종","경기도":"경기","강원특별자치도":"강원","강원도":"강원","충청북도":"충북","충청남도":"충남","전북특별자치도":"전북","전라북도":"전북","전라남도":"전남","경상북도":"경북","경상남도":"경남","제주특별자치도":"제주"}

def classify(title, field="", extra=""):
    text = f"{title} {extra}"
    cats = []
    base = FIELD_MAP.get(field.strip())
    if base: cats.append(base)
    for cid, pat in CAT_RULES:
        if re.search(pat, text, re.I) and cid not in cats:
            cats.append(cid)
    return cats[:3] or ["etc"]

def region_of(title, agency="", operator=""):
    m = re.match(r"\s*\[([^\]]+)\]", title or "")
    if m:
        for r in REGIONS:
            if m.group(1).startswith(r): return r
    for k, v in REGION_FULL.items():
        if k in (agency or "") or k in (operator or ""): return v
    for r in REGIONS:
        if (agency or "").startswith(r): return r
    return "전국"

def parse_dates(period):
    ds = re.findall(r"(\d{4})[.\-](\d{1,2})[.\-](\d{1,2})", period or "")
    ds = [f"{y}-{int(m):02d}-{int(d):02d}" for y, m, d in ds]
    start = ds[0] if ds else None
    end = ds[-1] if len(ds) >= 2 else (ds[0] if ds and "~" not in (period or "") and "마감" in (period or "") else None)
    return start, end

# ---------- 기업마당 ----------
def bizinfo_api(key):
    url = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do?" + urllib.parse.urlencode({"crtfcKey": key, "dataType": "json", "searchCnt": "0"})
    data = json.loads(get(url, timeout=90))
    rows = data.get("jsonArray") or data.get("items") or []
    out = []
    for r in rows:
        title = clean(r.get("pblancNm"))
        period = clean(r.get("reqstBeginEndDe"))
        s, e = parse_dates(period)
        field = clean(r.get("pldirSportRealmLclasCodeNm"))
        agency = clean(r.get("jrsdInsttNm")); op = clean(r.get("excInsttNm"))
        link = r.get("pblancUrl") or ""
        if link.startswith("/"): link = "https://www.bizinfo.go.kr" + link
        out.append({
            "src": "bizinfo", "id": r.get("pblancId"), "title": title, "field": field,
            "period": period, "start": s, "end": e, "agency": agency, "operator": op,
            "reg": (clean(r.get("creatPnttm")) or "")[:10], "url": link,
            "summary": clean(r.get("bsnsSumryCn"))[:180], "hashtags": clean(r.get("hashtags"))[:120],
        })
    return out

def bizinfo_scrape(max_pages=200):
    out, seen = [], set()
    base = "https://www.bizinfo.go.kr/sii/siia/selectSIIA200View.do"
    for p in range(1, max_pages + 1):
        h = get(f"{base}?rows=15&cpage={p}&schEndAt=N")
        body = h[h.find("<tbody"):h.find("</tbody>")]
        trs = re.findall(r"<tr>([\s\S]*?)</tr>", body)
        if not trs: break
        new = 0
        for tr in trs:
            tds = re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr)
            if len(tds) < 7: continue
            m = re.search(r"pblancId=(PBLN_\d+)", html.unescape(tr))
            pid = m.group(1) if m else None
            if not pid or pid in seen: continue
            seen.add(pid); new += 1
            title = clean(tds[2]); period = clean(tds[3]); s, e = parse_dates(period)
            out.append({
                "src": "bizinfo", "id": pid, "title": title, "field": clean(tds[1]), "period": period,
                "start": s, "end": e, "agency": clean(tds[4]), "operator": clean(tds[5]), "reg": clean(tds[6]),
                "url": f"https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId={pid}",
            })
        if new == 0: break
        time.sleep(0.6)
    return out

# ---------- K-Startup ----------
def kstartup_scrape(max_pages=60):
    out, seen = [], set()
    base = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    for p in range(1, max_pages + 1):
        h = get(f"{base}?page={p}")
        i = h.find('id="bizPbancList"')
        if i < 0: break
        seg = h[i:h.find("</ul>", i + 100000) if h.find("</ul>", i) > 0 else len(h)]
        lis = re.findall(r"<li class=\"notice\">([\s\S]*?)</li>", seg)
        if not lis: break
        new = 0
        for li in lis:
            m = re.search(r"go_view\((\d+)\)", li)
            if not m or m.group(1) in seen: continue
            sn = m.group(1); seen.add(sn); new += 1
            flags = [clean(x) for x in re.findall(r"<span class=\"flag[^\"]*\">([\s\S]*?)</span>", li)]
            title = clean((re.search(r"<p class=\"tit\">([\s\S]*?)</p>", li) or [None, ""])[1])
            lists = [clean(x) for x in re.findall(r"<span class=\"list\">([\s\S]*?)</span>", li)]
            info = {}
            for x in lists:
                mm = re.match(r"(등록일자|시작일자|마감일자|조회)\s*(.*)", x)
                if mm: info[mm.group(1)] = mm.group(2)
            plain = [x for x in lists if not re.match(r"(등록일자|시작일자|마감일자|조회)", x)]
            kind = next((f for f in flags if f not in ("민간", "공공") and not f.startswith("D-") and f != "오늘마감"), "")
            out.append({
                "src": "kstartup", "id": sn, "title": title, "field": kind,
                "sector": next((f for f in flags if f in ("민간", "공공")), ""),
                "period": f"{info.get('시작일자','')} ~ {info.get('마감일자','')}".strip(" ~"),
                "start": info.get("시작일자") or None, "end": info.get("마감일자") or None,
                "agency": plain[1] if len(plain) > 1 else "", "operator": plain[1] if len(plain) > 1 else "",
                "program": plain[0] if plain else "", "reg": info.get("등록일자", ""),
                "url": f"{base}?schM=view&pbancSn={sn}",
            })
        if new == 0: break
        time.sleep(0.6)
    return out

def norm_title(t):
    t = re.sub(r"^\s*\[[^\]]*\]", "", t or "")
    t = re.sub(r"[\s.,·ㆍ\-_:;!?\"'’‘“”「」『』()\[\]<>《》]", "", t)
    return re.sub(r"^20\d\d년?(도)?", "", t)

def finalize(items):
    res, seen = [], {}
    for it in items:
        key = norm_title(it.get("title"))
        first = seen.get(key)
        if key and first is not None and first.get("src") != it.get("src"):
            if it.get("url"): first["alt_url"] = it["url"]
            continue
        if key and first is None: seen[key] = it
        it["cats"] = classify(it["title"], it.get("field", ""), it.get("program", "") + " " + it.get("summary", "") + " " + it.get("hashtags", ""))
        it["region"] = region_of(it["title"], it.get("agency", ""), it.get("operator", ""))
        it["level"] = "local" if it["region"] != "전국" or re.search(r"자치단체|시청|군청|구청|도청|테크노파크", (it.get("agency","")+it.get("operator",""))) else "national"
        it.pop("dday", None)
        if it.get("end"):
            try:
                d = dt.date.fromisoformat(it["end"])
                if d < TODAY: continue  # 이미 마감
                it["dday"] = (d - TODAY).days
            except ValueError:
                pass
        res.append({k: v for k, v in it.items() if v not in (None, "", [])})
    res.sort(key=lambda x: (x.get("dday", 9999), x.get("title", "")))
    return res

def main():
    if "--reclassify" in sys.argv:  # 수집 없이 기존 파일 재분류(오프라인 점검용)
        prev = json.load(open(OUT, encoding="utf-8"))
        items = finalize(prev.get("items", []))
        prev.update({"count": len(items), "items": items})
        json.dump(prev, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(len(items)); return
    max_pages = int(sys.argv[sys.argv.index("--max-pages") + 1]) if "--max-pages" in sys.argv else 200
    prev = {}
    if os.path.exists(OUT):
        try: prev = json.load(open(OUT, encoding="utf-8"))
        except Exception: prev = {}
    status, items = {}, []
    key = os.environ.get("BIZINFO_API_KEY", "").strip()
    try:
        b = bizinfo_api(key) if key else bizinfo_scrape(max_pages)
        status["bizinfo"] = {"ok": True, "count": len(b), "mode": "api" if key else "list"}
        items += b
    except Exception as e:
        status["bizinfo"] = {"ok": False, "error": str(e)[:200]}
        items += [x for x in prev.get("items", []) if x.get("src") == "bizinfo"]
    try:
        k = kstartup_scrape(min(max_pages, 60))
        status["kstartup"] = {"ok": True, "count": len(k), "mode": "list"}
        items += k
    except Exception as e:
        status["kstartup"] = {"ok": False, "error": str(e)[:200]}
        items += [x for x in prev.get("items", []) if x.get("src") == "kstartup"]
    items = finalize(items)
    prev_n = len(prev.get("items", []))
    if prev_n and len(items) < prev_n * 0.5:
        print(f"[guard] 새 결과 {len(items)}건이 기존 {prev_n}건의 절반 미만이라 저장하지 않습니다.", file=sys.stderr)
        sys.exit(2)
    out = {"updated_at": dt.datetime.now(KST).isoformat(timespec="minutes"), "status": status, "count": len(items), "items": items}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"count": len(items), "status": status}, ensure_ascii=False))

if __name__ == "__main__":
    main()
