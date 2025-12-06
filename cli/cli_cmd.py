import cmd
import os
import datetime
from cli.json_manager import CalendarStorage
import cli.calendar_core as cal_view
from cli.ai_ollama import analyze_schedule


class CalendarCLI(cmd.Cmd):
    intro = "\n=== AI Calendar CLI ===\n도움말은 help 명령으로 확인하세요.\n"
    prompt = "(calendar) "

    def __init__(self):
        super().__init__()
        self.store = CalendarStorage("calendar_data.json")  # 내부 JSON dict 보유

    # =========================
    # 0) claer 기능
    # =========================
    def do_clear(self, arg):
        """화면 지우기: clear"""
        os.system('cls' if os.name == 'nt' else 'clear')

    # =========================
    # 1) 달력 출력
    # =========================
    def do_show_month(self, arg):
        """월간 달력 출력: show_month [YYYY MM]"""
        args = arg.split()
        today = datetime.datetime.now()

        if len(args) == 2:
            year, month = map(int, args)
        else:
            year, month = today.year, today.month

        print(cal_view.get_month_str_calendar(year, month))

    def do_show_year(self, arg):
        """연간 달력 출력: show_year [YYYY]"""
        args = arg.split()
        today = datetime.datetime.now()
        year = int(args[0]) if args else today.year

        print(cal_view.get_year_str_calendar(year))

    def do_show_week(self, arg):
        """주간 달력 정보 출력: show_week [YYYY MM DD]"""
        args = arg.split()
        today = datetime.datetime.now()

        if len(args) == 3:
            y, m, d = map(int, args)
        else:
            y, m, d = today.year, today.month, today.day

        iso_year, month, iso_week, iso_day = cal_view.get_week_calendar(y, m, d)
        print(f"ISO Week: {iso_year}-W{iso_week}")
        print(f"Weekday: {iso_day}")

    def do_show_day(self, arg):
        """일간 정보 출력: show_day [YYYY MM DD]"""
        args = arg.split()
        today = datetime.datetime.now()

        if len(args) == 3:
            y, m, d = map(int, args)
        else:
            y, m, d = today.year, today.month, today.day

        print(cal_view.get_day_str_calendar(y, m, d))

    # =========================
    # 2) 일정 추가 / 수정 / 삭제
    # =========================
    def do_add(self, arg):
        """
        일정 추가: add YYYY-MM-DD
        """
        date_str = arg.strip()
        if not date_str:
            print("날짜를 입력하세요: add YYYY-MM-DD")
            return

        title = input("제목: ")
        time = input("시간: ")
        memo = input("메모: ")
        priority = int(input("중요도(1(높음)~5(낮음)): ") or 1)
        category = input("카테고리(운동/공부/일상 등): ") or "일상"

        self.store.add_event(date_str, title, time, memo, priority, category)
        print("일정이 추가되었습니다.")

    def do_update(self, arg):
        """일정 수정: update YYYY-MM-DD"""
        date_str = arg.strip()
        if not date_str:
            print("update YYYY-MM-DD")
            return

        old_title = input("수정할 일정 제목: ")
        print("변경값이 없으면 엔터.")

        new_data = {}
        title = input("새 제목: ")
        if title:
            new_data["title"] = title

        time = input("새 시간: ")
        if time:
            new_data["time"] = time

        memo = input("새 메모: ")
        if memo:
            new_data["memo"] = memo

        pr = input("새 중요도: ")
        if pr:
            new_data["priority"] = int(pr)

        cat = input("새 카테고리: ")
        if cat:
            new_data["category"] = cat

        ok = self.store.update_event(date_str, old_title, new_data)
        print("수정 완료." if ok else "수정 실패: 일정이 없습니다.")

    def do_delete(self, arg):
        """일정 삭제: delete YYYY-MM-DD"""
        date_str = arg.strip()
        if not date_str:
            print("delete YYYY-MM-DD")
            return

        title = input("삭제할 일정 제목: ")
        ok = self.store.remove_event(date_str, title)
        print("삭제 완료." if ok else "삭제 실패: 일정이 없습니다.")

    # =========================
    # 3) 일정 조회 (AI 코멘트 on/off)
    # =========================
    def do_view(self, arg):
        """
        일정 조회
        view day|week|month YYYY-MM-DD [ai]
        """
        args = arg.split()
        if len(args) < 2:
            print("view day|week|month YYYY-MM-DD [ai]")
            return

        mode = args[0]
        date_str = args[1]
        ai_flag = (len(args) >= 3 and args[2] == "ai")

        # ---------------- DAY ----------------
        if mode == "day":
            data = self.store.get_day(date_str)
            print(f"\n[일정 - {date_str}]")
            for e in data["events"]:
                print(f"- ({e['priority']}) {e['title']} / {e['time']} / {e['category']}")

            if ai_flag:
                print("\nAI 분석 중...\n")
                print(analyze_schedule(self.store.data, "day", date_str))

        # ---------------- WEEK ----------------
        elif mode == "week":
            print(f"\n[주간 일정 - {date_str}]")
            week_data = self.store.get_week(date_str)

            for d, info in week_data.items():
                print(f"\n[{d}]")
                for e in info["events"]:
                    print(f"- ({e['priority']}) {e['title']} / {e['time']} / {e['category']}")

            if ai_flag:
                print("\nAI 분석 중...\n")
                print(analyze_schedule(self.store.data, "week", date_str))

        # ---------------- MONTH ----------------
        elif mode == "month":
            print(f"\n[월간 일정 - {date_str}]")
            month_data = self.store.get_month(date_str)

            for d, info in month_data.items():
                print(f"\n[{d}]")
                for e in info["events"]:
                    print(f"- ({e['priority']}) {e['title']} / {e['time']} / {e['category']}")

            if ai_flag:
                print("\nAI 분석 중...\n")
                print(analyze_schedule(self.store.data, "month", date_str))

        else:
            print("mode는 day/week/month 입니다.")

    # =========================
    # 4) 저장 / 종료
    # =========================
    def do_save(self, arg):
        """파일 저장"""
        self.store._save()
        print("저장 완료.")

    def do_exit(self, arg):
        """종료 (자동 저장)"""
        print("저장 후 종료합니다.")
        self.store._save()
        return True

    do_EOF = do_exit   # Ctrl + D

def run_cli():
    CalendarCLI().cmdloop()

if __name__ == "__main__":
    run_cli()
