# Spotify 메타데이터 연동 설정

Muker는 로컬 음악 파일의 메타데이터를 Spotify Web API로 보강할 수 있습니다.

## 기능

- 부족한 메타데이터 자동 보강 (앨범, 연도, 장르 등)
- 아티스트 정보 정확도 향상
- 트랙 번호 자동 할당

## 설정 방법

### 1. Spotify 개발자 계정 생성

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)에 접속
2. 로그인 또는 계정 생성
3. **"Create app"** 클릭

### 2. 앱 등록

1. **App name**: `Muker Music Player` (원하는 이름)
2. **App description**: `CLI music player` (원하는 설명)
3. **Redirect URI**: `http://localhost:8888/callback` (필수)
4. **APIs used**: `Web API` 선택
5. 약관 동의 후 **"Save"** 클릭

### 3. 인증 정보 확인

1. 생성된 앱 클릭
2. **"Settings"** 버튼 클릭
3. **Client ID**와 **Client Secret** 확인

### 4. 환경 변수 설정

**권장: .env 파일 사용 (가장 간단)**

1. 프로젝트 루트에 `.env` 파일 생성:
```bash
# .env.example을 복사
cp .env.example .env
```

2. `.env` 파일 편집:
```bash
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_actual_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
```

**대안: 시스템 환경 변수**

#### Windows (PowerShell):
```powershell
# 현재 세션에만 적용
$env:SPOTIFY_CLIENT_ID="your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret_here"

# 영구 적용 (시스템 환경 변수)
[Environment]::SetEnvironmentVariable("SPOTIFY_CLIENT_ID", "your_client_id_here", "User")
[Environment]::SetEnvironmentVariable("SPOTIFY_CLIENT_SECRET", "your_client_secret_here", "User")
```

#### Windows (CMD):
```cmd
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

#### Linux/Mac:
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"

# 적용
source ~/.bashrc  # 또는 source ~/.zshrc
```

### 5. 패키지 설치

```bash
pip install spotipy python-dotenv
```

또는 전체 requirements.txt 설치:
```bash
pip install -r requirements.txt
```

### 6. Muker 실행

```bash
python -m muker
```

## 작동 방식

1. 음악 파일 로드 시 로컬 메타데이터 먼저 추출
2. 아티스트/제목은 있지만 앨범/연도/장르가 없을 경우:
   - Spotify API에서 트랙 검색
   - 정확한 메타데이터로 보강
3. 모든 정보가 이미 있거나 검색 실패 시:
   - 로컬 메타데이터 사용

## 확인 방법

Muker 실행 시 다음 메시지가 표시되면 성공:
```
[INFO] Loaded environment variables from C:\...\muker-CLI\.env
[INFO] Spotify API client initialized successfully
[INFO] Spotify metadata enrichment enabled
```

.env 파일이 없고 시스템 환경 변수 사용 시:
```
[INFO] No .env file found, using system environment variables
[INFO] Spotify API client initialized successfully
[INFO] Spotify metadata enrichment enabled
```

환경 변수가 전혀 설정되지 않았으면:
```
[INFO] No .env file found, using system environment variables
[INFO] Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.
[INFO] Spotify not available - using local metadata only
```

## 문제 해결

### "Spotify credentials not found" 메시지
**방법 1: .env 파일 확인**
- `.env` 파일이 프로젝트 루트에 있는지 확인
- `.env` 파일 내용에 실제 Client ID/Secret이 있는지 확인
- `.env.example`이 아닌 `.env` 파일인지 확인

**방법 2: 시스템 환경 변수 확인**
- PowerShell에서 확인: `$env:SPOTIFY_CLIENT_ID`
- 환경 변수 설정 후 터미널 재시작

### "Failed to initialize Spotify client" 오류
- `.env` 파일의 Client ID와 Client Secret이 정확한지 확인
- 따옴표 없이 입력했는지 확인 (예: `SPOTIFY_CLIENT_ID=abc123`, 따옴표 X)
- 네트워크 연결 확인
- 패키지 설치 확인: `pip list | grep spotipy`
- python-dotenv 설치 확인: `pip list | grep python-dotenv`

### 메타데이터가 보강되지 않음
- 로컬 파일에 아티스트/제목 정보가 있는지 확인
- Spotify에 해당 트랙이 있는지 확인
- 디버그 로그에서 `[INFO] Enriched track from Spotify` 메시지 확인

## API 사용량

- Spotify API는 무료로 사용 가능
- 속도 제한: 초당 ~20 요청
- Muker는 필요할 때만 API 호출 (이미 메타데이터가 있으면 건너뜀)

## 옵션: Spotify 비활성화

Spotify 연동을 원하지 않으면 환경 변수를 설정하지 않으면 됩니다.
로컬 메타데이터만 사용하여 정상 작동합니다.
