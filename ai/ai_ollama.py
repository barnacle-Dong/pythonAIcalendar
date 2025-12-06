import json
import datetime
import requests


# -----------------------------
# 1) Ollama Qwen 호출 함수
# -----------------------------
def ask_ai(prompt: str) -> str:
    """Ollama qwen3:4b 모델에 프롬프트를 보내고 응답을 문자열로 반환."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gpt-oss:120b-cloud",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "(응답 없음)")
    except Exception as e:
        return f"[오류 발생] {e}"


# -----------------------------
# 2) 날짜 → 주/월 키 변환 유틸 함수
# -----------------------------
def get_week_keys_from_date(base_date: datetime.date) -> tuple[str, str]:
    """
    ISO 주차 기준으로 주 키 두 가지를 만든다.
    - padded: 2025-W02
    - plain : 2025-W2
    JSON에서 어떤 형식으로 저장되어 있어도 둘 다 시도해보기 위함.
    """
    iso_year, iso_week, _ = base_date.isocalendar()
    padded = f"{iso_year}-W{iso_week:02d}"
    plain = f"{iso_year}-W{iso_week}"
    return padded, plain


def get_month_key_from_date(base_date: datetime.date) -> str:
    """
    월 키: YYYY-MM 형식으로 만든다. 예) 2025-01
    """
    return f"{base_date.year}-{base_date.month:02d}"


# -----------------------------
# 3) AI 분석 함수 (JSON 전체 그대로 넘김)
# -----------------------------
def analyze_schedule(calendar_data: dict, mode: str, date_str: str) -> str:
    """
    calendar.json 전체 + mode(day/week/month) + 기준 날짜(YYYY-MM-DD)를
    AI에게 넘겨서 조언을 생성한다.
    단, 해당 날짜/주/월에 데이터가 없으면 AI를 호출하지 않고 바로 메시지를 반환한다.
    """

    # 날짜 형식 검증
    try:
        base_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "[입력 오류] 날짜 형식은 YYYY-MM-DD 여야 합니다."

    mode = mode.lower()
    if mode not in ("day", "week", "month"):
        return "[입력 오류] mode는 day / week / month 중 하나여야 합니다."

    days = calendar_data.get("days", {})
    weeks = calendar_data.get("weeks", {})
    months = calendar_data.get("months", {})

    # 🔹 1) day 모드: 해당 날짜에 진짜 일정이 있는지 먼저 확인
    if mode == "day":
        day_data = days.get(date_str)
        if not day_data or not day_data.get("events"):
            return f"{date_str}에는 등록된 일정이 없습니다."
        # 여기서부터는 AI 호출 가능 상태

    # 🔹 2) week 모드: 해당 날짜가 속한 ISO 주 키(두 가지 형식)를 확인
    if mode == "week":
        padded_key, plain_key = get_week_keys_from_date(base_date)

        # 필요하면 디버그 출력 (나중에 귀찮으면 주석 처리)
        print(f"[DEBUG] 계산된 week_key (padded) = {padded_key}")
        print(f"[DEBUG] 계산된 week_key (plain)  = {plain_key}")
        print(f"[DEBUG] JSON weeks 키 목록       = {list(weeks.keys())}")

        week_data = weeks.get(padded_key) or weeks.get(plain_key)
        if not week_data or not week_data.get("summary"):
            return f"{padded_key} / {plain_key} 주에 대한 요약 데이터가 없습니다."
        # 여기서부터는 AI 호출 가능 상태

    # 🔹 3) month 모드: 해당 월 키가 있는지 확인
    if mode == "month":
        month_key = get_month_key_from_date(base_date)

        print(f"[DEBUG] 계산된 month_key         = {month_key}")
        print(f"[DEBUG] JSON months 키 목록      = {list(months.keys())}")

        month_data = months.get(month_key)
        if not month_data or not month_data.get("summary"):
            return f"{month_key}에 대한 월간 요약 데이터가 없습니다."
        # 여기서부터는 AI 호출 가능 상태

    # 여기까지 내려왔으면 → 최소한 해당 날짜/주/월 데이터는 존재함

    # JSON 원본 통째로 문자열화
    calendar_json_str = json.dumps(calendar_data, ensure_ascii=False, indent=2)

    # 🔥 백틱, 코드블록 전부 없이 프롬프트 만들기
    #    + "절대 JSON이나 딕셔너리로 답하지 말 것"을 아주 강하게 명시
    prompt = f"""
당신은 일정 데이터를 기반으로 사용자의 공부·일·운동·휴식 루틴을 도와주는
'사실 기반 일정 코치' AI입니다.

가장 중요한 원칙은 다음과 같습니다.

1. 반드시 calendar.json 안에 있는 정보만 사용해야 합니다.
   - JSON에 없는 일정, 날짜, 이벤트를 새로 만들어 내지 마세요.
   - '다음 주에도 세미나가 있다'처럼 사용자가 주지 않은 미래 일정은 추측하지 마세요.
2. 날짜, 요일, 시간, priority를 잘못 바꾸지 마세요.
   - 예를 들어 JSON에 1월 9일에 퀴즈 대비가 있으면, 1월 10일 퀴즈라고 쓰면 안 됩니다.
3. 응답은 항상 순수한 한국어 문장으로만 작성합니다.
   - 표, 머리글(예: [WEEK], [MONTH]), 리스트, 번호 목록, 마크다운, JSON 형식은 사용하지 마세요.
   - 줄바꿈은 1~2번 정도만 사용하고, 전체가 1~2개의 자연스러운 문단처럼 보이게 쓰세요.

-----------------------------------------
아래는 calendar.json 전체 데이터입니다.
여기에 있는 내용만 보고 판단해야 합니다.

=== BEGIN JSON ===
{calendar_json_str}
=== END JSON ===
-----------------------------------------

요청 정보:
- mode = {mode}
- date = {date_str}

이제 mode에 따라 다르게 행동하세요.

[mode = "day"]
- date에 해당하는 하루의 events만 보고, 그 날의 흐름을 2~3문장 정도로 요약하세요.
- priority가 높은 일정(숫자가 작을수록 중요한 것으로 가정)을 우선 언급하세요.
- 이어서 2~3문장 정도로, 그 날을 더 잘 마무리하거나 내일을 준비하기 위한
  구체적인 행동 조언을 제시하세요.
- 전체 분량은 4~6문장 사이가 되도록 하세요.

[mode = "week"]
- date가 포함된 ISO Week에 속한 날짜들의 events만 사용하세요.
- 그 주 안에서 어떤 요일에 어떤 종류의 일정(학교, 공부, 운동, 휴식 등)이 있었는지를
  자연스럽게 요약하되, 요일과 중요한 일정 이름은 가능하면 언급하세요.
- 단, 다른 주(이전 주, 다음 주)나 한 달 전체를 분석하려고 하지 마세요.
  오직 그 주에 속한 일정만 기준으로 분석합니다.
- 먼저 2~3문장으로 이번 주의 패턴을 설명하고,
  이어서 2~4문장으로 사용자가 다음 번에 같은 패턴의 주간을 보낼 때
  더 잘 활용할 수 있는 구체적인 행동 조언을 제시하세요.
- 예를 들어 “어느 요일에 마감이 몰리는지”, “운동과 공부의 균형이 어떤지”를 짚고,
  “마감 전날 몇 분 정도 점검 시간을 확보하라”, “운동 뒤에 짧은 스트레칭을 추가하라”
  같은 식으로 바로 실행 가능한 제안을 하세요.
- 전체 분량은 4~7문장 정도로, 하나 또는 두 개의 자연스러운 문단으로 작성하세요.
- 표, 목록, 머리글([WEEK], [MONTH] 등)은 절대 사용하지 마세요.

[mode = "month"]
- 해당 월에 속한 days와 months 요약을 참고하되,
  한 달 전체의 경향을 3~4문장 정도로 간단히 정리하세요.
- 이어서 2~3문장 정도로, 다음 달에 시도해 볼 만한 구체적인 루틴 조정
  (예: 운동 빈도, 공부 시간대, 휴식 방식 등)을 제안하세요.
- 역시 표나 리스트 대신, 자연스러운 문장 형태의 1~2개 문단으로만 작성하세요.

말투 스타일:
- 보고서처럼 딱딱하지 말고, 일정표를 잘 읽어주는 똑똑한 비서처럼 말하세요.
- “이번 주에는 ~한 점이 특히 좋았어요.”, “다음에는 ~을 한 번 시도해 보세요.”처럼
  긍정적인 피드백과 현실적인 조언을 함께 제시하세요.
"""




    return ask_ai(prompt)


# -----------------------------
# 4) CLI 실행 진입부
# -----------------------------
def main():
    print("\n=== LOCAL QWEN 일정 분석기 (RAW JSON 입력) ===\n")

    path = input("calendar.json 경로 입력 → ").strip()
    if not path:
        print("경로가 없습니다. 종료합니다.")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[JSON 로드 실패] {e}")
        return

    while True:
        mode = input("\nmode 선택 (day / week / month | 엔터 시 종료) → ").strip().lower()
        if not mode:
            print("\n종료합니다.")
            break

        date_str = input("기준 날짜 입력 (YYYY-MM-DD) → ").strip()
        if not date_str:
            print("⚠ 날짜 미입력. 다시 입력해 주세요.")
            continue

        print("\n🧠 AI 일정 분석 중...\n")
        result = analyze_schedule(data, mode, date_str)

        print("====== AI COMMENT / SYSTEM MESSAGE ======")
        print(result)
        print("=========================================\n")


if __name__ == "__main__":
    main()
