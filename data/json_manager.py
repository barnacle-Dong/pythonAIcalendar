import json
import os
from datetime import datetime, date
import calendar


class CalendarStorage:
    # 초기화 메서드
    def __init__(self, path="calendar_data.json"):
        self.path = path
        self.data = self._load_or_init()

    def _load_or_init(self):
        if not os.path.exists(self.path):
            initial = {
                "days": {},
                "weeks": {},
                "months": {},
                "triggers": {
                    "daily": {},
                    "weekly": {},
                    "monthly": {}
                }
            }
            self._save(initial)
            return initial

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data=None):
        if data is None:
            data = self.data
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ===========================================================
    # DAY FUNCTIONS
    # ===========================================================

    def add_event(self, date_str: str, title: str, time="", memo="", priority=1, category="일상"):
        """ 일정 추가 """
        if date_str not in self.data["days"]:
            self.data["days"][date_str] = {"events": [], "ai_comment": ""}

        event = {
            "title": title,
            "time": time,
            "memo": memo,
            "priority": priority,
            "category": category
        }

        self.data["days"][date_str]["events"].append(event)

        # 트리거 세팅
        self._trigger_daily(date_str)
        self._trigger_week(date_str)
        self._trigger_month(date_str)

        self._save()

    def update_event(self, date_str: str, old_title: str, new_data: dict):
        """ 일정 수정 """
        if date_str not in self.data["days"]:
            return False

        updated = False
        for event in self.data["days"][date_str]["events"]:
            if event["title"] == old_title:
                event.update(new_data)
                updated = True
                break

        if updated:
            self._trigger_daily(date_str)
            self._trigger_week(date_str)
            self._trigger_month(date_str)
            self._save()

        return updated

    def remove_event(self, date_str: str, title: str):
        """ 일정 삭제 """
        if date_str not in self.data["days"]:
            return False

        before = len(self.data["days"][date_str]["events"])
        self.data["days"][date_str]["events"] = [
            e for e in self.data["days"][date_str]["events"] if e["title"] != title
        ]
        after = len(self.data["days"][date_str]["events"])

        if before != after:
            self._trigger_daily(date_str)
            self._trigger_week(date_str)
            self._trigger_month(date_str)
            self._save()

        return before != after

    def get_day(self, date_str: str):
        return self.data["days"].get(date_str, {"events": [], "ai_comment": ""})

    # ===========================================================
    # WEEK & MONTH HANDLING + 자동 결산
    # ===========================================================

    def _date_to_week_id(self, date_str):
        y, m, d = map(int, date_str.split("-"))
        dt = date(y, m, d)
        year, week, _ = dt.isocalendar()
        return f"{year}-W{week}"

    def _date_to_month_id(self, date_str):
        y, m, d = date_str.split("-")
        return f"{y}-{m}"

    def _trigger_daily(self, date_str):
        self.data["triggers"]["daily"][date_str] = True

    def _trigger_week(self, date_str):
        week_id = self._date_to_week_id(date_str)
        self.data["triggers"]["weekly"][week_id] = True

    def _trigger_month(self, date_str):
        month_id = self._date_to_month_id(date_str)
        self.data["triggers"]["monthly"][month_id] = True

    # ===========================================================
    # SUMMARY SAVE / GET
    # ===========================================================

    def save_week_summary(self, week_id: str, summary: dict, ai_comment=""):
        self.data["weeks"][week_id] = {
            "summary": summary,
            "ai_comment": ai_comment
        }
        self.data["triggers"]["weekly"][week_id] = False
        self._save()

    def get_week(self, week_id: str):
        return self.data["weeks"].get(week_id, {})

    def save_month_summary(self, month_id: str, summary: dict, ai_comment=""):
        self.data["months"][month_id] = {
            "summary": summary,
            "ai_comment": ai_comment
        }
        self.data["triggers"]["monthly"][month_id] = False  
        self._save()

    def get_month(self, month_id: str):
        return self.data["months"].get(month_id, {})
