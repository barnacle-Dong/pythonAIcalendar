# pythonAIcalendar
파이썬 AI 캘린더 프로젝트 리포지토리

## AI
- Ollama 0.13.1 사용  
- `cli/cli_cmd.py` 의 `MODEL` 변수 안의 모델명 사용

## 실행 방법
0. Windows 환경 기준  
1. Ollama 설치 후 로그인 → 클라우드 모델 설정 → 백그라운드 실행  
2. `main.py` 실행  
   - 샘플로 포함된 `calendar_data.json`을 사용하고 싶지 않다면 삭제 후 실행


### cli command line list
> **Documented commands (type help <topic>):**  
> ==============================================
> EOF | clear | exit | save | show_month | show_year | view  
> add | delete | help | show_day | show_week update  

- **help**  
  - List available commands with `help` or detailed help with `help <cmd>`.

- **EOF**  
  - 종료 (자동 저장)

- **clear**  
  - 화면 지우기

- **exit**  
  - 종료 (자동 저장)

- **save**  
  - 파일 저장

- **show_day, show_week, show_month, show_year**
  - 일간 정보 출력: `show_day [YYYY MM DD]`
  - 주간 달력 정보 출력: `show_week [YYYY MM DD]`
  - 월간 달력 출력: `show_month [YYYY MM]`
  - 연간 달력 출력: `show_year [YYYY]`

- **add, delete, update**
  - 일정 추가: `add YYYY-MM-DD`
  - 일정 삭제: `delete YYYY-MM-DD`
  - 일정 수정: `update YYYY-MM-DD`

- **view**
  - 일정 조회: `view day|week|month YYYY-MM-DD [ai]`
