import calendar
schedules={}     #일정 딕셔너리 
                 # 딕셔너리 저장 예시 {2025-11-27 :[일정 내용들]<-- 리스트 형태}
def show_calendar():            #월 단위 달력 출력
    tc=calendar.TextCalendar(firstweekday=6)
    ch_year = int(input(" 달력의 년도를 입력하세요 "))
    ch_month = int(input(" 달력의 달을 입력하세요 "))
    print(tc.formatmonth(ch_year, ch_month))

def add_schedule():       #일정추가
    date=input("날짜를 입력하세요: (예:2025-11-27)")
    content = input("일정 내용을 입력하세요:")
    schedules.setdefault(date,[]).append(content) #일정 기입 및 일정 중복 차단
    print(f"\n[{date}]에 {content}일정이 추가되었습니다\n")
    


def view_schedule_date():        #일정 보기
    date=input("일정을 조회할 날짜를 입력하세요 (예:2025-11-27")

    if date in schedules:
        print(f"{date}에 있는 일정:\n")
        for i , show_content in enumerate(schedules[date], start=1) :        # enumerate로 일정을 번호로 구분하고 출력 
                print(f"\n{i}.{show_content}\n")
    
    else:
         print(f"{date}에 등록된 일정이 없습니다")

def delete_schedule():  #일정 삭제
    date=input("삭제할 일정의 날짜를 입력해주세요 (예시:2025-11-27)")

    if date in schedules:       #해당 날짜의 일정을 보여주기
          for i , show_content in enumerate(schedules[date],start=1):
            print(f"{i}.{schedules[date]}")
    
    try:            #오류(일정 번호를 문자로 입력) 발생을 막기 위해 try사용 
        num = int(input("삭제할 일정 번호를 입력하시오:"))
        if num<1 or num>len(schedules[date]):
             print("번호를 잘못 입력하셨습니다 다시 입력해주세요")
             return
        
    except ValueError:
         print("번호를 입력해주세요\n")
         return
    
    pop_schedule = schedules[date].pop(num-1) #pop함수로 일정값을 반환하면서 삭제
    print(f"{pop_schedule}일정이 삭제되었습니다")

    if len(schedules[date])==0:
         del schedules[date]         # 날짜의 일정이 사라지면 해당 날짜의 리스트 삭제
      