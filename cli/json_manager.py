import json
import os
from datetime import datetime, date


class CalendarStorage:
    def __init__(self, path="calendar_data.json"):
        self.path = path
        self.data = {
            "days": {},
            "weeks": {},
            "months": {}
        }
        self._load()
        self._sync_all()

    # ----------------------------
    # 저장 / 로드
    # ----------------------------
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                print("[경고] JSON 파싱 실패. 새 구조로 초기화합니다.")

        # 스키마 보정
        for day in self.data.get("days", {}).values():
            day.setdefault("events", [])

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ----------------------------
    # 일정 추가, 수정, 삭제
    # ----------------------------
    def add_event(self, date_str, title, time, memo, priority, category):
        if date_str not in self.data["days"]:
            self.data["days"][date_str] = {"events": [], "ai_comment": ""}

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

        events = self.data["days"][date_str]["events"]
        for e in events:
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
        updated = [e for e in events if e["title"] != title]

        if len(updated) == len(events):
            return False

        self.data["days"][date_str]["events"] = updated
        self._sync_all()
        self._save()
        return True

    # ----------------------------
    # 주 / 월 재계산 (ai_comment 보존)
    # ----------------------------
    def _sync_all(self):
        self._recalculate_weeks()
        self._recalculate_months()

    def _recalculate_weeks(self):
        old = self.data.get("weeks", {})
        weeks = {}

        for date_str, info in self.data["days"].items():
            y, m, d = map(int, date_str.split("-"))
            dt = date(y, m, d)
            iso_year, iso_week, _ = dt.isocalendar()

            wkey = f"{iso_year}-W{iso_week:02d}"

            if wkey not in weeks:
                weeks[wkey] = {
                    "events": [],
                    "ai_comment": old.get(wkey, {}).get("ai_comment", "")
                }

            for e in info["events"]:
                obj = e.copy()
                obj["date"] = date_str
                weeks[wkey]["events"].append(obj)

        self.data["weeks"] = weeks

    def _recalculate_months(self):
        old = self.data.get("months", {})
        months = {}

        for date_str, info in self.data["days"].items():
            y, m, _ = map(int, date_str.split("-"))
            mkey = f"{y}-{m:02d}"

            if mkey not in months:
                months[mkey] = {
                    "events": [],
                    "ai_comment": old.get(mkey, {}).get("ai_comment", "")
                }

            for e in info["events"]:
                obj = e.copy()
                obj["date"] = date_str
                months[mkey]["events"].append(obj)

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
        wkey = f"{iso_year}-W{iso_week:02d}"

        raw = self.data["weeks"].get(wkey, {"events": []})
        result = {}
        for e in raw["events"]:
            d = e["date"]
            result.setdefault(d, {"events": []})
            result[d]["events"].append(e)
        return result

    def get_month(self, date_str):
        y, m, _ = map(int, date_str.split("-"))
        mkey = f"{y}-{m:02d}"

        raw = self.data["months"].get(mkey, {"events": []})
        result = {}
        for e in raw["events"]:
            d = e["date"]
            result.setdefault(d, {"events": []})
            result[d]["events"].append(e)
        return result
