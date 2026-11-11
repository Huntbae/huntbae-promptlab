# HUNT PROMPT LAB

huntbae.com 서브 메뉴 「Prompt Lab」용 정적 갤러리.

- `index.html` : 갤러리 본체 (데이터는 파일 안 `<script id="prompt-data">` JSON)
- `shorts-studio.html` : 9:16 AI 쇼츠 제작 스튜디오 (대본 분할·녹음·무음 제거·자막 싱크·프레임 체인·프롬프트·스토리보드·WebM 렌더). 브라우저 안에서만 동작
  → https://huntbae.github.io/huntbae-promptlab/shorts-studio.html
- 이미지 파일은 index.html 과 같은 위치(루트)에 둡니다 (`thumb`, `refimg` 값은 파일명)

## GitHub Pages 설정
Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save
→ https://huntbae.github.io/huntbae-promptlab/

## Google Sites 메뉴 연결
1. sites.google.com 에서 huntbae.com 사이트 열기 → 페이지 탭 → + 새 페이지 → 이름 "Prompt Lab"
2. 삽입 → 삽입(Embed) → URL 입력 → 위 Pages 주소 → "전체 페이지" 선택 → 삽입
3. 임베드 블록을 좌우 끝까지 늘리고 높이를 충분히(예: 1200px 이상) 늘림
4. 게시

### 쇼츠 스튜디오 메뉴 추가
위 2번에서 URL만 `https://huntbae.github.io/huntbae-promptlab/shorts-studio.html` 로 바꿔 새 페이지 「Shorts Studio」를 만듭니다. 녹음(마이크)·파일 저장이 막히면 임베드 대신 메뉴 링크(새 탭 열기)로 연결하세요.

## huntbae.com 사이트 (site/)
Google Sites 각 페이지의 '삽입(코드)' 블록이 아래 페이지를 iframe으로 불러옵니다. 디자인 수정은 이 저장소에 푸시하면 바로 반영됩니다.

| Sites 페이지 | 파일 | 블록 높이(px, 너비 1154 기준) |
|---|---|---|
| 홈 /main | site/index.html | 5460 |
| 서비스 /services | site/services.html | 2930 |
| 정부지원사업 /gov-support | site/gov.html | 2780 |
| 업무 영역 /services/all | site/areas.html | 2240 |
| 강연·자문 /talks | site/talks.html | 2390 |
| 커뮤니티 /community | site/community.html | 1910 |
| 자료실 /library | site/library.html | 2240 |
| 모빌리티 /mobility | site/mobility.html | 3210 |
| About·문의 /about | site/about.html | 4110 |

페이지 내용 길이가 바뀌면 Sites 편집기에서 블록 아래쪽 손잡이를 끌어 높이를 맞추세요.

### 정부지원사업 데이터
- `site/data/gov-live.json` — 기업마당·K-Startup 진행 중 공고. GitHub Actions(`.github/workflows/update-gov.yml`)가 매일 06:10·평일 12:10(KST)에 `scripts/update_gov.py`로 갱신
- 기업마당 공식 API 키가 생기면 저장소 Settings → Secrets and variables → Actions → New repository secret → 이름 `BIZINFO_API_KEY` 로 넣으면 자동으로 API 모드(사업 요약·해시태그 포함)로 바뀝니다
- `site/data/gov-curated.json` — 핵심 사업 가이드·연간 일정·2027 전망·공식 포털. Claude 예약 작업이 매주 공식 출처로 다시 확인해 갱신
