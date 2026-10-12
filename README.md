# 랜덤인생게임 · Random Life

80억 명 중 한 명으로 무작위로 태어나 그 사람의 일생을 살아 보는 웹 게임입니다. 한국어·English·日本語·中文을 지원합니다.

- 플레이: https://randomlife-game.github.io/randomlife-game/
- 지금, 지난 세상(1950–2005년), 다가올 세상(2030–2100년) 중에서 태어날 때를 고를 수 있습니다. 출생지는 그해 나라별 출생 수에 비례해 뽑습니다.
- 사건과 선택지는 게임을 위한 허구지만, 그 확률과 문장 속 숫자는 공개 통계로 계산합니다.

## 데이터

`tools/fetch_sources.sh`로 원자료를 받고 `tools/build_world_data.py`로 가공하면 `data/world.json`이 만들어지고 `index.html` 안의 `WD` 상수가 갱신됩니다.

- UN 세계인구전망 2024 (CC BY 3.0 IGO): 출생 수, 기대수명, 사망 확률, 출산율 1950–2100
- 세계은행 WDI (CC BY 4.0; 원 출처 UN IGME, WHO, UNESCO UIS, ILO, UNAIDS, UNODC, UNICEF, FAO)
- UNDP 인간개발보고서 2023/24 (CC BY 3.0 IGO), 세계행복보고서(Our World in Data 경유, CC BY 4.0)
- Maddison Project 2020, Lee & Lee 2016(OWID 경유), UN 도시화 자료·HYDE(OWID 경유), UCDP/PRIO 무력분쟁 26.1 (모두 CC BY 4.0)

비어 있는 값은 같은 지역·소득 그룹의 중앙값으로 채우고 게임 안에 ≈로 표시합니다. 다른 해의 일부 값과 수명 모델은 추정입니다.
