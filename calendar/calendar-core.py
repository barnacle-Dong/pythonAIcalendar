import calendar
import datetime


'''
년 단위 달력
월 단위 달력
주 단위 달력
'''
# cli main
def show_year_calendar(year=None):
    if year is None:
          year=datetime.datetime.now().year

    text_calendar=calendar.TextCalendar(firstweekday=6)
    result=text_calendar.formatyear(year)
        
    return result

def show_month_calendar(year=None, month=None):   
    if year is None or month is None :
        now=datetime.datetime.now()          #now 를 두번 호출하면 오류 생길수 있음
        if year is None :
             year=now.year
        
        if month is None:
            month=now.month
    
    text_calendar=calendar.TextCalendar(firstweekday=6)
    result = text_calendar.formatmonth(year,month)

    return result

def get_week_calendar(year=None, month=None, day=None):
    if year is None or month is None or day  is None:
        now=datetime.datetime.now()
        if year is None :
             year=now.year
        
        if month is None:
            month=now.month
        
        if day is None:
            day=now.day 
    
    get_date=datetime.date(year,month,day)
    iso_year, iso_week, iso_weekday = get_date.isocalendar()

    return iso_year,month, iso_week, iso_weekday

def get_day_calendar(year=None, month=None, day=None):
    if year is None or month is None or day  is None:
        now=datetime.datetime.now()
        if year is None :
             year=now.year
        
        if month is None:
            month=now.month
        
        if day is None:
            day=now.day 
    
    get_date=datetime.date(year,month,day)

    return get_date

        


if __name__ == "__main__":  # 메인 파일일 경우 실행_
     print(get_week_calendar())