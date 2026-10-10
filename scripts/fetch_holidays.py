# -*- coding: utf-8 -*-
"""
한국천문연구원 특일정보(공휴일) API → docs/<연도>.json 생성

- 인증키는 GitHub Secrets의 KASI_KEY(일반 인증키 Decoding)에서 읽음
- 올해·내년 2개 연도를 월별로 조회 (하루 24회 호출)
- 출력 형식: {"2026-10-05": ["대체공휴일(개천절)"], ...}  (holidays.hyunbin.page와 동일)
- 조회 실패/자료 부족 시 기존 파일을 덮어쓰지 않음
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")


def fetch_month(key, year, month):
    q = urllib.parse.urlencode({
        "serviceKey": key, "solYear": year, "solMonth": f"{month:02d}", "numOfRows": 50,
    })
    with urllib.request.urlopen(f"{API}?{q}", timeout=20) as r:
        xml = r.read().decode("utf-8")
    root = ET.fromstring(xml)
    code = root.findtext(".//resultCode")
    if code not in ("00", "0000"):
        msg = root.findtext(".//resultMsg") or root.findtext(".//returnAuthMsg") or xml[:200]
        raise RuntimeError(f"{year}-{month:02d} API 오류: {msg}")
    days = {}
    for it in root.iter("item"):
        if (it.findtext("isHoliday") or "Y") != "Y":
            continue
        d = it.findtext("locdate") or ""
        if len(d) == 8:
            days.setdefault(f"{d[:4]}-{d[4:6]}-{d[6:]}", []).append(it.findtext("dateName") or "공휴일")
    return days


def main():
    key = os.environ.get("KASI_KEY", "").strip()
    if not key:
        sys.exit("KASI_KEY 시크릿이 없습니다.")
    if "%" in key:                      # Encoding 키를 넣었어도 동작하게
        key = urllib.parse.unquote(key)
    os.makedirs(OUT_DIR, exist_ok=True)
    this_year = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).year
    failed = False
    for year in (this_year, this_year + 1):
        try:
            days = {}
            for m in range(1, 13):
                days.update(fetch_month(key, year, m))
        except Exception as e:
            print(f"[실패] {year}: {e}")
            failed = True
            continue
        # 내년 자료는 보통 6월쯤 월력요항 발표 후 채워짐 → 적으면 저장 안 함
        if len(days) < 10:
            print(f"[건너뜀] {year}: {len(days)}일 (아직 발표 전으로 보임)")
            continue
        path = os.path.join(OUT_DIR, f"{year}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(days.items())), f, ensure_ascii=False, indent=1)
        print(f"[저장] {year}.json  {len(days)}일")
    if failed:
        sys.exit(1)   # Actions에 실패로 표시 → 이메일 알림


if __name__ == "__main__":
    main()
