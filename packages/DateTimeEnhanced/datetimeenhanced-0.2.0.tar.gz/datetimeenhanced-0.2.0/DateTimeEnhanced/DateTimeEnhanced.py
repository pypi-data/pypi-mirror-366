import datetime
from typing import Literal
from dateutil.relativedelta import relativedelta

_first_day_of_week_option = Literal["sunday", "monday", "iso"]
_info_sequence = list[Literal["default", "date", "time", "day", "month", "year", "week"]]


class DateTimeEnhanced:
    def __init__(self):
        self._default: str = ""
        self._date: str = ""
        self._time: str = ""
        self._day: str = ""
        self._month: str = ""
        self._year: str = ""
        self._week: str = ""

    @staticmethod
    def _try_cast_to_int(value):
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return value

    def set_value(self, date_time: datetime.datetime, first_day_of_week: _first_day_of_week_option, all_integer: bool):
        self._default = str(date_time)
        self._date = date_time.strftime("%Y-%m-%d")
        self._time = date_time.strftime("%H:%M:%S.%f")
        self._day = {
            "sunday": f"{(date_time.weekday() + 1) % 7}",
            "monday": f"{date_time.weekday()}",
            "iso": f"{date_time.isocalendar().weekday}"
        }.get(first_day_of_week) if all_integer else date_time.strftime("%A")
        self._month = date_time.strftime("%m") if all_integer else date_time.strftime("%B")
        self._year = date_time.strftime("%Y")
        self._week = {
            "sunday": f"{int(date_time.strftime('%U')) + 1}",
            "monday": f"{int(date_time.strftime('%W')) + 1}",
            "iso": f"{date_time.isocalendar().week}.{date_time.isocalendar().weekday}"
        }.get(first_day_of_week)

    def today(self, first_day_of_week: _first_day_of_week_option, all_integer: bool):
        self.set_value(datetime.datetime.today(), first_day_of_week, all_integer=all_integer)

    def last_n_day(self, last_n_day: int, first_day_of_week: _first_day_of_week_option, all_integer: bool):
        self.set_value(datetime.datetime.today() - datetime.timedelta(days=last_n_day), first_day_of_week, all_integer=all_integer)

    def last_n_week(self, last_n_week: int, first_day_of_week: _first_day_of_week_option, all_integer: bool):
        self.set_value(datetime.datetime.today() - datetime.timedelta(weeks=last_n_week), first_day_of_week, all_integer=all_integer)

    def last_n_month(self, last_n_month: int, first_day_of_week: _first_day_of_week_option, all_integer: bool):
        self.set_value(datetime.datetime.today() - relativedelta(months=last_n_month), first_day_of_week, all_integer=all_integer)

    def get_output_str(self, info_sequence: _info_sequence, info_separator: str):
        info_data = {
            "default": self._default,
            "date": self._date,
            "time": self._time,
            "day": self._day,
            "month": self._month,
            "year": self._year,
            "week": self._week
        }
        return info_separator.join({key: info_data[key] for key in info_sequence if key in info_data}.values())

    def get_output_raw(self, info_sequence: _info_sequence):
        info_data = {
            "default": datetime.datetime.fromisoformat(self._default),
            "date": datetime.date.fromisoformat(self._date),
            "time": datetime.time.fromisoformat(self._time),
            "day": self._try_cast_to_int(self._day),
            "month": self._try_cast_to_int(self._month),
            "year": self._try_cast_to_int(self._year),
            "week": self._try_cast_to_int(self._week)
        }
        return {key: info_data[key] for key in info_sequence if key in info_data}
