# 공휴일 데이터 (한국천문연구원 특일정보)

매일 03:07(한국시간) GitHub Actions가 천문연 API를 불러 `docs/<연도>.json`을 갱신하고,
GitHub Pages로 `https://<아이디>.github.io/<저장소>/2026.json` 주소에 공개합니다.

형식: `{"2026-10-05": ["대체공휴일(개천절)"], ...}`

설정: Settings → Secrets and variables → Actions → `KASI_KEY` (공공데이터포털 일반 인증키 Decoding)
