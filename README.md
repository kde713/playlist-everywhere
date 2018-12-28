# Playlist Everywhere

음원 서비스간 플레이리스트 이전, 공유가 어려운 점을 해결하기 위해 개발한 유틸리티입니다.

-----

## Disclaimer

- 본 유틸리티는 개인적인 용도로 개발되었습니다. 상업적 이용을 금합니다.
- 본 유틸리티 사용과정에서 발생한 문제에 대해 개발자는 책임지지 않습니다. 단, Issue를 올려주시면 최대한 도움을 드릴 수 있도록 노력하겠습니다.



## Pre-requirement

- 본 유틸리티는 Python 3.6+ 환경에서 동작합니다. 반드시 3.6 버전 이상의 파이썬이 설치되어 있어야합니다.



## Quick Start

- 본 Repository를 다운로드 합니다.

```bash
git clone git@github.com:kde713/playlist-everywhere.git
cd playlist_everywhere
```

-  의존 요소를 설치합니다.

```bash
pip3 install -r requirements.txt
```

- 유틸리티를 실행합니다.

```bash
python3 -m playlist_everywhere
``` 



## Specification

| 음원사 | 플레이리스트 다운로드 | 플레이리스트 업로드 |
| :----: | --------------------- | ------------------- |
| melon | dj(DJ 플레이리스트) | - |
| genie | - | 지원 |

현재 멜론 DJ 플레이리스트 다운로드와 지니 개인 플레이리스트 업로드 기능을 시범적으로 지원하고 있습니다.



## Contribution

본 프로젝트는 어떠한 형태의 기여라도 환영합니다. Issue 나 PR을 올려주시면 빠른 시간 안에 확인하겠습니다. 
기타 문의는 [kde713@gmail.com](mailto:kde713@gmail.com)으로 부탁드립니다.
