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
