# 외부데이터 가져오기 — 5가지 사례 샘플

비개발자 강의용 Streamlit 샘플 모음. 주식 매매 대시보드 맥락.

---

## 0. 파이썬 설치 (이미 있다면 1번으로)

> 📌 **권장 버전: Python 3.10 ~ 3.13**
> - 3.10 미만은 streamlit/pandas 최신 버전이 안 깔립니다.
> - 3.14처럼 갓 출시된 버전은 일부 패키지 wheel이 아직 없어 설치가 실패할 수 있습니다.
> - 옆 사람과 버전이 달라도 됩니다. venv가 각자 격리된 환경을 만들어주기 때문에 서로 영향을 주지 않습니다.

### 설치 여부 확인

터미널을 열고:

- **Windows**: `Win + R` → `cmd` 입력 → 엔터
- **macOS**: `Cmd + Space` → `terminal` 입력 → 엔터

다음 명령을 실행:

```bash
python --version
```

`Python 3.10` 이상이 보이면 설치된 것. macOS는 `python3 --version`도 같이 시도해보세요.
명령을 못 찾는다는 에러(`command not found`, `'python'은(는) 내부 또는 외부 명령... 아닙니다`)가 나오면 아래 설치 단계로.

### Windows 설치

1. https://www.python.org/downloads/windows/ 에서 **최신 안정판 (3.12 이상)** Installer 다운로드
2. 설치 마법사 실행 시 **첫 화면 맨 아래 `Add python.exe to PATH` 체크박스를 반드시 체크** ⚠️
3. `Install Now` 클릭
4. 설치 후 새 cmd 창을 열고 `python --version` 으로 확인

> ❗ **PATH 체크박스를 깜빡한 경우**: 제어판에서 Python을 제거 후 재설치하거나, 아래 "환경변수 직접 추가" 절을 따르세요.

### macOS 설치

가장 쉬운 방법 두 가지 중 택1.

**A. 공식 설치 파일 (가장 단순)**
1. https://www.python.org/downloads/macos/ 에서 `.pkg` 다운로드
2. 더블클릭 후 안내대로 설치
3. 터미널에서 `python3 --version`

**B. Homebrew (추천)**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
python3 --version
```

> macOS는 `python` 대신 **`python3`** 명령을 사용합니다. 이 README의 모든 명령에서 Windows의 `python`을 macOS는 `python3`로 바꿔 실행하세요.

---

## 0-1. 파이썬은 깔았는데 명령어가 안 먹을 때 (PATH 문제)

증상: `python --version`을 쳤는데 "명령을 찾을 수 없습니다", "외부 명령이 아닙니다" 가 뜸.

### Windows — 환경변수에 직접 추가

1. `Win` 키 → **"환경 변수"** 검색 → `시스템 환경 변수 편집` 클릭
2. `환경 변수(N)...` 버튼 클릭
3. 아래쪽 **시스템 변수**에서 `Path` 선택 → `편집(E)...`
4. `새로 만들기(N)`로 두 줄 추가 (경로는 본인 사용자명에 맞게):
   ```
   C:\Users\<본인사용자명>\AppData\Local\Programs\Python\Python312\
   C:\Users\<본인사용자명>\AppData\Local\Programs\Python\Python312\Scripts\
   ```
   > 정확한 경로는 파일 탐색기 주소창에 `%LOCALAPPDATA%\Programs\Python` 을 붙여넣어 확인하세요.
5. 모든 창에서 `확인` → **새 cmd 창**을 열어 `python --version`

### macOS — PATH에 추가

zsh(기본 셸):
```bash
echo 'export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
python3 --version
```

> Apple Silicon(M1/M2/M3/M4)은 Homebrew 경로가 `/opt/homebrew/bin`, Intel Mac은 `/usr/local/bin`. 둘 다 넣어두면 안전.

---

## 1. 가상환경 만들기

프로젝트 폴더로 이동:

**Windows**
```cmd
cd C:\Users\<본인사용자명>\Desktop\KSA\datas
python -m venv .venv

```
> "venv라는 Python 모듈을 실행해서 .venv 폴더에 가상환경 만들어"

**macOS**
```bash
cd ~/Desktop/KSA/datas
python3 -m venv .venv
```

> ⚠️ **`.venv/` 폴더는 절대 다른 PC로 복사해서 쓰지 마세요.** 폴더 안에 그 PC의 파이썬 절대경로와 OS별 실행 파일이 박혀 있어서, USB로 복사하면 동작하지 않습니다. 각자 자기 PC에서 위 명령으로 새로 만들고, 공유는 `requirements.txt` 로만 합니다.

### 한 PC에 파이썬이 여러 개 깔려 있을 때

`python` 명령이 어떤 버전을 가리키는지 헷갈릴 수 있습니다. (예: Anaconda 3.11 + 별도 설치 3.13이 같이 있는 경우) Windows는 `py` 런처로 버전을 명시해 venv를 만들 수 있어요:

```cmd
py -0                          :: 설치된 파이썬 목록 확인
py -3.13 -m venv .venv         :: 3.13으로 venv 생성
py -3.11 -m venv .venv         :: 3.11로 venv 생성
```

생성 후 버전 확인:
```cmd
.venv\Scripts\python.exe --version
```

macOS는 `python3.13 -m venv .venv` 처럼 버전을 직접 지정합니다.

> 💡 **이렇게 하면 좋은 이유**: 시스템 `python` 명령이 다른 버전을 가리키더라도, `py -3.13`으로 만든 venv 안에서는 항상 3.13이 동작합니다. venv 활성화 후 `python` 명령은 그 버전을 가리키게 됩니다.

### 활성화

| OS / 셸 | 명령 |
|---|---|
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| Windows Git Bash | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

활성화되면 프롬프트 앞에 `(.venv)` 표시가 붙습니다. 비활성화는 `deactivate`.

> ❗ **PowerShell에서 "이 시스템에서 스크립트를 실행할 수 없으므로..." 에러**가 나면, PowerShell을 **관리자 권한**으로 열고 한 번만 실행:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 2. 패키지 설치

가상환경 활성화 상태에서:

```bash
pip install -r requirements.txt
```

> macOS에서 활성화하지 않고 쓰려면 `pip` 대신 `pip3`.

---

## 3. 실행

```bash
streamlit run 1_file_krx.py
streamlit run 2_api_fdr.py
streamlit run 3_api_weather.py
streamlit run 4_crawl_naver_news.py
streamlit run 5_crawl_playwright.py
streamlit run 6_realtime_upbit.py
streamlit run 7_db_sqlite.py
streamlit run 8_db_supabase.py
```

활성화 없이 직접 호출:

- **Windows**: `.venv\Scripts\streamlit.exe run 2_api_fdr.py`
- **macOS**: `.venv/bin/streamlit run 2_api_fdr.py`

브라우저가 자동으로 열리지 않으면 터미널에 출력된 `http://localhost:8501` 주소를 직접 클릭하세요.

---

## 카테고리 매핑

| 파일 | 카테고리 | 데이터 소스 |
|---|---|---|
| 1_file_krx.py | 파일 기반 | KRX 정보데이터시스템 CSV |
| 2_api_fdr.py | API 기반 | FinanceDataReader (인증 불필요) |
| 3_api_weather.py | API 기반 | 기상청 단기예보 (공공데이터포털 키 필요) |
| 4_crawl_naver_news.py | 크롤링 | 네이버 금융 뉴스 (requests) |
| 5_crawl_playwright.py | 크롤링 | 네이버 금융 뉴스 (Playwright) |
| 6_realtime_upbit.py | 실시간 | 업비트 WebSocket |
| 7_db_sqlite.py | DB 연동 | SQLite 매매일지 (로컬 파일) |
| 8_db_supabase.py | DB 연동 | Supabase (클라우드 PostgreSQL) |

## 강의 진행 시 준비물

- **1번** 실행 전: http://data.krx.co.kr/ 에서 [전종목 시세] CSV 다운로드 (회원가입 필요)
- **3번** 실행 전: data.go.kr 회원가입 후 기상청 단기예보 API 키 발급 → `.env.local` 파일에 `WEATHER_API_KEY=발급받은키` 저장
- **4~5번** 실행 전: 네이버 금융 robots.txt 와 매너(sleep, User-Agent)에 대한 안내
- **5번** 실행 전: `playwright install chromium` (브라우저 설치, 최초 1회)
- **6번**: 즉시 실행 가능 (인증 불필요)
- **7번**: 사이드바 "샘플 데이터 넣기" 버튼으로 즉시 시연 가능
- **8번** 실행 전: Supabase 프로젝트 생성 후 URL/anon 키를 `.env.local` 파일에 입력

---

## 바이브코딩 프롬프트 예시

아래 프롬프트를 Claude / ChatGPT 에 그대로 붙여넣으면 비슷한 코드를 생성할 수 있습니다.
필요에 따라 종목명, 컬럼명, 화면 구성 등을 바꿔서 써보세요.

> 📁 **실습 파일은 `project` 폴더 안에 만들어주세요.**
> 각 프롬프트 마지막 줄에 "project 폴더 안에 저장해줘"가 포함되어 있습니다.
> 강의 샘플 파일과 섞이지 않도록 합니다.

---

### 1번 — 파일 기반 (KRX CSV)

> 💡 **첨부 방법**: KRX에서 받은 CSV 파일을 Claude에 첨부하세요.


```
첨부한 CSV 파일은 KRX(한국거래소)에서 받은 전종목 시세 데이터야.
이 파일을 분석하는 Streamlit 대시보드를 만들어줘.

[원하는 화면]
- CSV 파일을 직접 업로드할 수 있는 버튼
- 코스피 / 코스닥 / 전체 중 선택할 수 있는 필터
- 오늘 가장 많이 오른 종목 TOP 10 막대그래프
- 오늘 거래가 가장 많았던 종목 TOP 10 표
- 전체 데이터를 스크롤해서 볼 수 있는 테이블

코드는 project 폴더 안에 저장해줘.
```

---

### 2번 — API 기반 (FinanceDataReader)

```
FinanceDataReader 라이브러리로 한국 주식 시세를 가져와서
여러 종목을 한 화면에서 비교할 수 있는 Streamlit 대시보드를 만들어줘.

[원하는 화면]
- 삼성전자, SK하이닉스, 카카오, 네이버, 현대차 등 여러 종목을 체크박스로 선택
- 조회 기간 시작일 / 종료일 선택
- 선택한 종목들의 수익률을 같은 기준으로 비교하는 꺾은선 그래프
  (예: 시작일에 모두 100으로 맞추고 얼마나 올랐는지 비교)
- 종목별 현재가, 최고가, 최저가, 수익률을 카드로 표시
- 전체 시세 데이터 표

코드는 project 폴더 안에 저장해줘.
```

---

### 3번 — API 기반 (기상청 단기예보)

> 💡 **첨부 방법**: `weather/` 폴더의 두 파일을 첨부하세요.
> - `기상청41_단기예보 조회서비스_오픈API활용가이드_241128.docx` (API 명세)
> - `기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도(2510).xlsx` (지역별 격자 좌표)

```
@weather\ 폴더 읽고
기상청 단기예보 API를 호출해서 날씨를 보여주는
Streamlit 대시보드를 만들어줘.

[원하는 화면]
- 사이드바에서 시/도 → 시/군/구 순서로 지역 선택 (xlsx에서 목록 읽어올 것)
- 현재 기온, 습도, 강수확률, 강수형태, 풍속을 카드로 표시
- 오늘 24시간 기온 변화 꺾은선 그래프
- 오늘 24시간 강수확률 막대그래프

API 인증키는 .env.local 에 WEATHER_API_KEY로 저장했음
코드는 project 폴더 안에 저장해줘.
```

---

### 4번 — 크롤링 (네이버 금융 뉴스, requests)

```
네이버 금융(https://finance.naver.com)에서
특정 종목의 최신 뉴스 10개를 가져와서 보여주는 Streamlit 앱을 만들어줘.

[원하는 화면]
- 종목코드를 입력하는 텍스트박스 (기본값: 005930 삼성전자)
- "뉴스 가져오기" 버튼
- 뉴스 제목, 언론사, 날짜를 표로 표시
- 제목 클릭하면 원문 기사로 이동

크롤링할 때 서버에 부담 주지 않도록 매너있게 요청하고,
같은 종목은 5분 동안 캐시해줘.

코드는 project 폴더 안에 저장해줘.
```

---

### 5번 — 크롤링 (Playwright)

> 💡 **사전 준비**: 아래 명령어를 먼저 실행하세요. MCP가 아니라 python이 실행하기 위해 필요
> ```
> playwright install chromium
> ```

```
Playwright를 사용해서 네이버 금융(https://finance.naver.com)에서
특정 종목의 최신 뉴스 10개를 가져와서 보여주는 Streamlit 앱을 만들어줘.

4번에서 만든 requests 방식과 기능은 동일하게 만들되,
코드 상단 주석에 두 방식의 차이를 설명해줘.
- requests 방식: 어떤 경우에 적합한지
- Playwright 방식: 어떤 경우에 더 필요한지

[원하는 화면]
- 종목코드 입력 텍스트박스 (기본값: 005930 삼성전자)
- "뉴스 가져오기" 버튼
- 뉴스 제목, 언론사, 날짜를 표로 표시
- 제목 클릭하면 원문 기사로 이동

코드는 project 폴더 안에 저장해줘.
```

---

### 6번 — 실시간 (업비트 WebSocket)

```
업비트 공개 WebSocket API를 사용해서 코인 시세를 실시간으로 받아
Streamlit 화면에 1초마다 갱신하는 앱을 만들어줘.
인증키 없이 무료로 사용 가능한 업비트 공개 API를 쓸 것.

[원하는 화면]
- BTC, ETH, XRP, SOL, DOGE 중 원하는 종목을 다중 선택
- "▶ 시작" 버튼 클릭 시 실시간 수신 시작
- 종목별 카드: 현재가, 1초 전과 비교한 변화량, 등락률
- 가격이 오르면 📈, 내리면 📉, 변화 없으면 ➡️ 표시

코드는 project 폴더 안에 저장해줘.
```

---

### 7번 — DB 연동 (SQLite)

```
내 주식 매매 기록을 저장하고 분석하는 Streamlit 앱을 만들어줘.
별도 서버 없이 파일 하나(trades.db)로 동작하는 SQLite를 사용할 것.

[저장할 데이터]
매매 기록 한 건당: 날짜, 종목명, 매수/매도 구분, 수량, 단가, 수수료

[원하는 화면]
- 왼쪽 사이드바: 새 매매 기록 입력 폼
- 왼쪽 사이드바: 샘플 데이터 자동 입력 버튼 (테스트용)
- 메인: 전체 매매 내역 표
- 메인: 종목별로 현재 보유 수량, 평균 매수 단가, 실현 손익 요약
- 메인: 월별 거래 횟수 막대그래프

코드와 DB 파일 모두 project 폴더 안에 저장해줘.
```

---

### 8번 — DB 연동 (Supabase)

> 💡 **사전 준비**: Supabase 대시보드에서 조회할 테이블의 RLS를 Public read로 설정하세요.
> (Supabase 대시보드 → Table Editor → 테이블 선택 → RLS 설정)

```
Supabase에 연결해서 테이블 데이터를 조회하는 Streamlit 앱을 만들어줘.
연결 정보는 .env.local 파일에 있어.

[원하는 화면]
- 사이드바: 조회할 테이블 이름 입력
- 사이드바: 최대 몇 개까지 가져올지 슬라이더
- 메인: 조회한 데이터를 표로 표시
- 새로고침 버튼 클릭 시 최신 데이터 다시 가져오기
- 연결 실패나 테이블이 없을 때 알기 쉬운 에러 메시지 표시

코드는 project 폴더 안에 저장해줘.
```

---

## 자주 만나는 트러블슈팅

| 증상 | 원인 / 해결 |
|---|---|
| `python: command not found` (Windows) | PATH 미설정 → 위 "환경변수 직접 추가" 참고하거나 Python 재설치 시 `Add to PATH` 체크 |
| `command not found: python` (macOS) | `python3` 로 시도. 그래도 안 되면 Homebrew로 설치 |
| `Activate.ps1 ... 실행할 수 없음` | PowerShell `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `pip` 도 안 먹음 | `python -m pip ...` 형태로 호출 (macOS는 `python3 -m pip`) |
| 패키지 설치가 매우 느리거나 설치불가능 | 사내망이면 프록시 문제 가능, IT담당자에게 요청 |
| streamlit 실행 후 브라우저 안 열림 | `http://localhost:8501` 직접 입력 |
| 한글 CSV가 깨져 보임 | 1번 코드는 cp949/utf-8 자동 시도. 그래도 깨지면 엑셀에서 한 번 열어 UTF-8로 다시 저장 |

