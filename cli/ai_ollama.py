import json
import datetime
import requests

MODEL = "gpt-oss:120b-cloud"    # Ollama Cloud Model name

def ask_ai(prompt: str) -> str:
    """Ollama 모델 호출"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "(응답 없음)")
    except Exception as e:
        return f"[오류 발생] {e}"


def analyze_schedule(calendar_data: dict, mode: str, date_str: str) -> str:
    """
    JSON 전체를 넘기지 않도록 수정.
    → 필요한 일정(events)만 넘김.
    → 응답 길이 제한 추가.
    """
    try:
        base_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "[입력 오류] 날짜 형식은 YYYY-MM-DD 여야 합니다."

    mode = mode.lower()
    days = calendar_data.get("days", {})
    weeks = calendar_data.get("weeks", {})
    months = calendar_data.get("months", {})

    # -----------------------------
    # DAY MODE
    # -----------------------------
    if mode == "day":
        day_data = days.get(date_str)
        if not day_data or not day_data.get("events"):
            return f"{date_str}에는 등록된 일정이 없습니다."

        events = day_data["events"]

    # -----------------------------
    # WEEK MODE
    # -----------------------------
    elif mode == "week":
        iso_year, iso_week, _ = base_date.isocalendar()
        wkey = f"{iso_year}-W{iso_week:02d}"
        week_data = weeks.get(wkey)

        if not week_data or not week_data.get("events"):
            return f"{wkey} 주에 일정이 없습니다."

        events = week_data["events"]

    # -----------------------------
    # MONTH MODE
    # -----------------------------
    elif mode == "month":
        mkey = f"{base_date.year}-{base_date.month:02d}"
        month_data = months.get(mkey)

        if not month_data or not month_data.get("events"):
            return f"{mkey} 월에는 일정이 없습니다."

        events = sorted(month_data["events"], key=lambda x: (x["date"], x["time"]))

        event_lines = "\n".join(
            f"- {e['date']} {e['time']} / {e['title']} ({e['category']})"
            for e in events
        )

        prompt = f"""
            당신은 일정 데이터를 기반으로 조언을 제공하는 사실 기반 일정 코치입니다.

            아래는 이번 달의 일정 목록입니다:
            {event_lines}

            이번 달 전체를 '월간 결산'하는 느낌으로 정리하세요.

            - 이번 달의 전반적인 리듬, 일정 밀도, 작업 강도 변화 등을 1~2문단으로 요약.
            - 개별 일정 설명보다, 한 달을 관통하는 특징·흐름을 중심으로 작성.
            - 다음 달을 위해 조정하면 좋은 루틴이나 시간 관리 전략을 2~3문장으로 제안.
            - 응답은 최대 4~5문장, 120~200자 이내로 간결하게.
            - 불필요한 디테일, 반복, 지나친 설명 금지.
            - 자연스러운 한국어 문장만 사용.

            mode: month
            date: {date_str}
            """

        return ask_ai(prompt)

    # -----------------------------
    # 프롬프트 생성
    # -----------------------------
    event_lines = "\n".join(
        f"- {e.get('date','')} {e['time']} / {e['title']} ({e['category']})"
        for e in events
    )

    # 🔥 AI 답변 길이 제한 추가: "최대 4~5문장" + "100~200자"
    length_limit = (
        "응답은 최대 4~5문장, 100~200자로 제한해 주세요. "
        "핵심만 간결하게 말하고 불필요한 서론과 군더더기는 제거하세요."
    )

    # 기존 프롬프트 내용 유지 + 길이 제한 + JSON 전체 제거
    prompt = f"""
        당신은 사용자의 일정 데이터를 분석하여 조언을 해주는 '사실 기반 일정 코치'입니다.

        아래는 분석 대상 일정 목록입니다:
        {event_lines}

        요청 모드: {mode}
        기준 날짜: {date_str}

        분석 규칙:
        1. 일정에 없는 정보를 지어내지 말 것.
        2. 날짜와 시간은 바꾸지 말 것.
        3. 지나치게 장황한 설명 금지.
        4. {length_limit}

        출력 형식:
        - 자연스러운 한국어 문장만 사용.
        - 마크다운, 리스트, 번호, 표 금지.

        이제 {mode} 분석을 작성하세요.
        """

    return ask_ai(prompt)
