<div align="center">

# 🎵 Muker CLI

### 터미널 기반 음악 플레이어

<p align="center">
  <strong>실시간 오디오 비주얼라이저를 탑재한 다기능 CLI 음악 플레이어</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge" alt="Platform">
</p>

---

</div>

## ✨ 주요 기능

| 기능 | 설명 |
|:---:|:---|
| 🎵 **다양한 포맷 지원** | MP3, WAV, FLAC, OGG 파일 재생 |
| 🎨 **실시간 비주얼라이저** | 스펙트럼, 파형, VU 미터 등 다양한 시각화 스타일 |
| 📝 **플레이리스트 관리** | 플레이리스트 생성, 저장, 불러오기 |
| 🎛️ **완벽한 재생 제어** | 재생, 일시정지, 탐색, 볼륨 조절 |
| 🔀 **셔플 & 반복** | 다양한 재생 모드 |
| 🖥️ **모던 TUI** | Textual 기반의 현대적인 터미널 UI |
| ⚡ **고성능** | 30-60 FPS의 부드러운 비주얼라이저 업데이트 |
| 🎼 **상세한 트랙 정보** | 비트레이트, 샘플레이트, 채널 등 메타데이터 표시 |
| 🌐 **Spotify 연동** | Spotify Web API를 통한 메타데이터 자동 보완 (선택) |

---

## 📋 요구 사항

- **Python** 3.10 이상
- **운영체제** Windows / Linux / macOS

---

## 🚀 설치 방법

### 기본 설치

핵심 의존성 설치:

```bash
pip install -r requirements.txt
```

### 선택: Spotify 연동

Spotify Web API를 통한 메타데이터 보완 기능 활성화:

1. **선택적 의존성 설치** (spotipy, python-dotenv):
   ```bash
   pip install spotipy python-dotenv
   ```

2. **설정 가이드 참조**: [SPOTIFY_SETUP.md](SPOTIFY_SETUP.md)

### Poetry 사용

```bash
poetry install
```

---

## 🎮 사용 방법

```bash
python -m muker
```

또는 Poetry를 통해 설치한 경우:

```bash
poetry run muker
```

---

## ⌨️ 키보드 단축키

| 키 | 기능 |
|:---:|:---|
| `Space` | 재생 / 일시정지 |
| `n` | 다음 트랙 |
| `p` | 이전 트랙 |
| `+` / `-` | 볼륨 조절 |
| `s` | 셔플 토글 |
| `r` | 반복 모드 변경 |
| `v` | 비주얼라이저 스타일 변경 |
| `q` | 종료 |

---

## 🛠️ 개발

### 테스트 실행

```bash
pytest
```

### 코드 포맷팅

```bash
black muker/
```

### 타입 체크

```bash
mypy muker/
```

---

## 📁 아키텍처

```
muker/
├── core/          # 비즈니스 로직 (플레이어, 플레이리스트, 비주얼라이저, 라이브러리)
├── ui/            # Textual UI 컴포넌트 및 위젯
├── models/        # 데이터 모델 (Track 등)
├── services/      # 외부 API 연동 (Spotify)
└── utils/         # 유틸리티 함수 (파일 스캐너 등)
```

---

## 📊 트랙 정보 표시

Muker는 다음과 같은 상세한 트랙 정보를 표시합니다:

| 라인 | 표시 내용 |
|:---:|:---|
| **1번 라인** | 아티스트 및 트랙 제목 |
| **2번 라인** | 트랙 번호, 앨범명, 발매년도, 장르 |
| **3번 라인** | 오디오 포맷 (MP3, FLAC 등), 비트레이트, 샘플레이트, 채널 |

---

## 🎧 Spotify 메타데이터 보완

활성화 시, Muker는 자동으로:

- ✅ 불완전한 메타데이터가 있는 트랙을 Spotify에서 검색
- ✅ 누락된 앨범, 연도, 장르, 트랙 번호 정보 채우기
- ✅ Spotify의 정확한 아티스트명 사용
- ✅ Spotify 연결 불가 시 로컬 메타데이터로 대체

> 📖 설정 방법은 [SPOTIFY_SETUP.md](SPOTIFY_SETUP.md)를 참조하세요.

---

## 📄 라이선스

MIT License

---

<div align="center">

### 👤 제작자

**AMAN**

---

<sub>🎶 음악과 함께 즐거운 시간 되세요! 🎶</sub>

</div>
