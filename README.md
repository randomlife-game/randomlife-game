# 랜덤인생게임 · Random Life

같은 날 정반대 형편에서 태어난 두 아이의 일생을 나란히 살아 보는 웹 게임입니다. 한국어·English·日本語·中文을 지원합니다.

- 플레이: https://randomlife-game.github.io/randomlife-game/
- 지금, 예전 어느 해(1950–2005년), 앞으로 어느 해(2030–2100년) 중에서 태어날 때를 고를 수 있습니다. 출생지는 그해 나라별 출생 수에 비례해 뽑습니다.
- 사건과 선택지는 게임을 위한 허구지만, 그 확률과 문장 속 숫자는 공개 통계로 계산합니다.

## 데이터

`tools/fetch_sources.sh`로 원자료를 받고 `tools/build_world_data.py`로 가공하면 `data/world.json`이 만들어지고 `index.html` 안의 `WD` 상수가 갱신됩니다.

- UN 세계인구전망 2024 (CC BY 3.0 IGO): 출생 수, 기대수명, 사망 확률, 출산율 1950–2100
- 세계은행 WDI (CC BY 4.0; 원 출처 UN IGME, WHO, UNESCO UIS, ILO, UNAIDS, UNODC, UNICEF, FAO)
- UNDP 인간개발보고서 2023/24 (CC BY 3.0 IGO), 세계행복보고서(Our World in Data 경유, CC BY 4.0)
- Maddison Project 2020, Lee & Lee 2016(OWID 경유), UN 도시화 자료·HYDE(OWID 경유), UCDP/PRIO 무력분쟁 26.1 (모두 CC BY 4.0)

비어 있는 값은 같은 지역·소득 그룹의 중앙값으로 채우고 게임 안에 ≈로 표시합니다. 다른 해의 일부 값과 수명 모델은 추정입니다.

## 공유 미리보기 (`s/`)

카카오톡·X 같은 곳에 링크를 붙이면 그 주소의 제목과 그림이 미리보기로 떠요. GitHub Pages는 판마다 다른 페이지를 만들 수 없어서, 나라×성별×언어별 작은 페이지(`s/ko/TCD-f.html` 등)와 나라별 그림(`s/img/TCD.jpg`)을 미리 만들어 둡니다. 각 페이지는 열리자마자 첫 화면으로 넘어갑니다.

나라 목록이나 그림을 바꾸면 다시 만들어 주세요.

```
python3 -m http.server 8765 &
node tools/make-share-pages.js
```

## 플레이 카운터 (`counter/`)

첫 화면에 "오늘 두 아이의 일생을 끝까지 산 판" 수를 보여 줘요. 결말까지 간 판마다 숫자 하나만 올라가고, 누가 했는지는 저장하지 않아요. 숫자가 100보다 작으면 대신 나라 수를 보여 줘요.

- Cloudflare Workers + Durable Object(SQLite)로 돌아가요. 무료 요금제로 충분해요.
- `counter/` 아래 파일이 바뀌면 GitHub Actions(`.github/workflows/deploy-counter.yml`)가 배포해요. 저장소 Secrets에 `CLOUDFLARE_API_TOKEN`과 `CLOUDFLARE_ACCOUNT_ID`가 필요해요.
- 주소: `GET /count` → `{today, total}`, `POST /done` → 1 올림. 날짜는 한국 시간 기준이에요.
