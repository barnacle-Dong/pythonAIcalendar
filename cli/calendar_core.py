import calendar
import datetime


'''
년 단위 달력
월 단위 달력
주 단위 달력
'''
# cli main


def get_year_str_calendar(year=None):   
    if year is None:
          year=datetime.datetime.now().year

    str_cal= calendar.TextCalendar(firstweekday=6).formatyear(year)  
     
    return str_cal

def get_year_obj_calendar(year=None):
    if year is None:
          year=datetime.datetime.now().year
    obj_cal= calendar.TextCalendar(firstweekday=6)  

    return obj_cal

def get_month_str_calendar(year=None, month=None):   
    today= datetime.datetime.now()
    year= year if year is not None else today.year
    month = month if month is not None else today.month
    cal_str=calendar.TextCalendar(firstweekday=6).formatmonth(year,month)  
    
    return cal_str

def get_month_obj_calendar(year=None, month=None):   
    today= datetime.datetime.now()
    year= year if year is not None else today.year
    month = month if month is not None else today.month  
    cal_obj=calendar.TextCalendar(firstweekday=6)

    return cal_obj

def get_week_calendar(year=None, month=None, day=None):
    today = datetime.datetime.now()
    year = year if year is not None else today.year
    month = month if month is not None else today.month  
    day = day if day is not None else today.day
    
    d= datetime.date(year,month,day)
    iso_year, iso_week, iso_weekday = d.isocalendar()
    

    return iso_year,d.month, iso_week, iso_weekday

def get_day_str_calendar(year=None, month=None, day=None):
    
    today=datetime.datetime.now()
    year = year if year is not None else today.year
    month = month if month is not None else today.month
    day= day if day is not None else today.day
    date_str=datetime.date(year, month, day).strftime("%Y-%m-%d")
    
    
    return  date_str

def get_day_obj_calendar(year=None, month=None, day=None):
    
    today=datetime.datetime.now()
    year = year if year is not None else today.year
    month = month if month is not None else today.month
    day= day if day is not None else today.day
    date_obj=datetime.date(year, month, day)

    return date_obj

        


if __name__ == "__main__":
    print(get_year_str_calendar())
    print(get_year_obj_calendar())
    print(get_month_str_calendar())
    print(get_month_obj_calendar())
    print(get_week_calendar())
    print(get_day_str_calendar())
    print(get_day_obj_calendar())