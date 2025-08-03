# utils.py는 날짜/시간 파싱, 파싱된 날짜/시간 스트링 변환, 현재 시간 기준 이전/이후 아이템 여부 판별, 키 정렬 등의 도구 역할

from datetime import datetime, date, time
from .models import TodoItem

MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
}

def parse_date(s: str) -> date:
    try:
        day_str, mon_str, year_str = s.strip().upper().split("_")
        day = int(day_str)
        month = MONTHS[mon_str]
        year = int(year_str)
        return date(year, month, day)
    except Exception as e:
        raise ValueError(f"Invalid date format: '{s}'. Use DD_MON_YYYY")

def parse_time(s: str) -> time:
    try:
        hour_str, min_str = s.split("_")
        return time(int(hour_str), int(min_str))
    except Exception as e:
        raise ValueError(f"Invalid time format: '{s}'. Use HH_MM")


def format_date(d) -> str:
    if d is None:
        return ""
    return f"{d.day:02}.{d.strftime('%b').upper()}.{d.year}"
    
def format_time(t) -> str:
    if t is None:
        return ""
    return f"{t.hour:02}:{t.minute:02}"

def is_past(item: TodoItem) -> bool:
    now = datetime.now()
    if item.date_att is None and item.time_att is None:
        return False
    if item.date_att is not None and item.date_att < now.date():
        return True
    if item.date_att == now.date() and item.time_att is not None and item.time_att < now.time():
        return True
    return False

def sort_key(item: TodoItem):
    return (
        item.date_att is None,
        item.date_att or date.max,
        item.time_att is None,
        item.time_att or time.max
    )

