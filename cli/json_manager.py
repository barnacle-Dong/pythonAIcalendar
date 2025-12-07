import json
import os
from datetime import date


class CalendarStorage:
    def __init__(self, path="calendar_data.json"):
        # 프로젝트 root(main.py)의 경로로 변경
        project_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.path = os.path.join(project_root, path)

        self.data = {
            "days": {},
            "weeks": {},
            "months": {}
        }

        self._load()       # 파일 로드 or 생성
        self._sync_all()   # 주/월 자동 재계산

    # ----------------------------
    # JSON 로드 / 생성
    # ----------------------------
    def _load(self):
        # 파일 없으면 새로 생성
        if not os.path.exists(self.path):
            print("[INFO] JSON 파일이 없어 새 파일을 생성합니다.")

            # 기본 구조로 reset
            self.data = {
                "days": {},
                "weeks": {},
                "months": {}
            }

            # 초기 구조 계산 후 파일 생성
            self._sync_all()
            self._save()
            return

        # 파일이 있을 경우 로드
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            print("[경고] JSON 파싱 실패. 새 파일로 재생성합니다.")

            self.data = {
                "days": {},
                "weeks": {},
                "months": {}
            }

            self._sync_all()
            self._save()
            return

        # 스키마 보정
        for day in self.data.get("days", {}).values():
            day.setdefault("events", [])
            # day.setdefault("ai_comment", "")

    # ----------------------------
    # JSON 저장
    # ----------------------------
    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ----------------------------
    # 일정 추가 / 수정 / 삭제
    # ----------------------------
    def add_event(self, date_str, title, time, memo, priority, category):
        if date_str not in self.data["days"]:
            self.data["days"][date_str] = {"events": []}
            # self.data["days"][date_str] = {"events": [], "ai_comment": ""}

        self.data["days"][date_str]["events"].append({
            "title": title,
            "time": time,
            "memo": memo,
            "priority": priority,
            "category": category
        })

        self._sync_all()
        self._save()

    def update_event(self, date_str, old_title, new_data):
        if date_str not in self.data["days"]:
            return False

        for e in self.data["days"][date_str]["events"]:
            if e["title"] == old_title:
                e.update(new_data)
                self._sync_all()
                self._save()
                return True

        return False

    def remove_event(self, date_str, title):
        if date_str not in self.data["days"]:
            return False

        events = self.data["days"][date_str]["events"]
        filtered = [e for e in events if e["title"] != title]

        if len(events) == len(filtered):
            return False

        self.data["days"][date_str]["events"] = filtered
        self._sync_all()
        self._save()
        return True

    # ----------------------------
    # 주 / 월 재계산
    # ----------------------------
    def _sync_all(self):
        self._recalc_weeks()
        self._recalc_months()

    def _recalc_weeks(self):
        old = self.data.get("weeks", {})
        weeks = {}

        for date_str, day_info in self.data["days"].items():
            y, m, d = map(int, date_str.split("-"))
            dt = date(y, m, d)
            iso_year, iso_week, _ = dt.isocalendar()

            key = f"{iso_year}-W{iso_week:02d}"

            if key not in weeks:
                weeks[key] = {
                    "events": [],
                    # "ai_comment": old.get(key, {}).get("ai_comment", "")
                }

            # 이벤트 복사 + 날짜 포함
            for e in day_info["events"]:
                event = e.copy()
                event["date"] = date_str
                weeks[key]["events"].append(event)

        self.data["weeks"] = weeks

    def _recalc_months(self):
        old = self.data.get("months", {})
        months = {}

        for date_str, day_info in self.data["days"].items():
            y, m, _ = map(int, date_str.split("-"))
            key = f"{y}-{m:02d}"

            if key not in months:
                months[key] = {
                    "events": [],
                    # "ai_comment": old.get(key, {}).get("ai_comment", "")
                }

            for e in day_info["events"]:
                event = e.copy()
                event["date"] = date_str
                months[key]["events"].append(event)

        self.data["months"] = months

    # ----------------------------
    # 조회용
    # ----------------------------
    def get_day(self, date_str):
        return self.data["days"].get(date_str, {"events": []})

    def get_week(self, date_str):
        y, m, d = map(int, date_str.split("-"))
        dt = date(y, m, d)
        iso_year, iso_week, _ = dt.isocalendar()

        key = f"{iso_year}-W{iso_week:02d}"

        output = {}
        for e in self.data["weeks"].get(key, {}).get("events", []):
            d = e["date"]
            output.setdefault(d, {"events": []})
            output[d]["events"].append(e)

        return output

    def get_month(self, date_str):
        y, m, _ = map(int, date_str.split("-"))
        key = f"{y}-{m:02d}"

        output = {}
        for e in self.data["months"].get(key, {}).get("events", []):
            d = e["date"]
            output.setdefault(d, {"events": []})
            output[d]["events"].append(e)

        return output
