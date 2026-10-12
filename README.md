# 랜덤인생게임 · Random Life

80억 명 중 한 명으로 무작위로 태어나 그 사람의 일생을 살아 보는 웹 게임입니다. 한국어·English·日本語·中文을 지원합니다.

- 플레이: https://randomlife-game.github.io/randomlife-game/
- 출생지는 세계은행(World Bank Open Data, CC BY 4.0) 통계로 추정한 국가별 연간 출생 수에 비례해 뽑습니다.
- 사건과 선택지는 게임을 위한 허구입니다.

## 공유 미리보기 (`s/`)

카카오톡·X 같은 곳에 링크를 붙이면 그 주소의 제목과 그림이 미리보기로 떠요. GitHub Pages는 판마다 다른 페이지를 만들 수 없어서, 나라×성별×언어별 작은 페이지(`s/ko/TCD-f.html` 등)와 나라별 그림(`s/img/TCD.jpg`)을 미리 만들어 둡니다. 각 페이지는 열리자마자 첫 화면으로 넘어갑니다.

나라 목록이나 그림을 바꾸면 다시 만들어 주세요.

```
python3 -m http.server 8765 &
node tools/make-share-pages.js
```
