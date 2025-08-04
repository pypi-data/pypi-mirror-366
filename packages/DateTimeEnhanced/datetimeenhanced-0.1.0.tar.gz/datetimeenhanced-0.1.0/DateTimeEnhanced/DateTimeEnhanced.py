import datetime
from typing import Literal


class DateTimeEnhanced:
    def __init__(self):
        self.__date: str = ""
        self.__time: str = ""
        self.__day: str = ""
        self.__week_day: str = ""
        self.__default: str = ""

    def set_value(self, date_time: datetime.datetime, first_day_of_week: Literal["sunday", "monday", "iso"]):
        self.__date = date_time.strftime("%Y-%m-%d")
        self.__time = date_time.strftime("%H:%M:%S.%f")
        self.__day = date_time.strftime("%A")
        self.__week_day = {
            "sunday": f"{int(date_time.strftime('%U')) + 1}.{(date_time.weekday() + 1) % 7}",
            "monday": f"{int(date_time.strftime('%W')) + 1}.{date_time.weekday()}",
            "iso": f"{date_time.isocalendar().week}.{date_time.isocalendar().weekday}"
        }.get(first_day_of_week)
        self.__default = str(date_time)

    def today(self, first_day_of_week: Literal["sunday", "monday", "iso"]):
        self.set_value(datetime.datetime.today(), first_day_of_week)

    def last_n_day(self, last_n_day: int, first_day_of_week: Literal["sunday", "monday", "iso"]):
        self.set_value(datetime.datetime.today() - datetime.timedelta(days=last_n_day), first_day_of_week)

    def last_n_week(self, last_n_week: int, first_day_of_week: Literal["sunday", "monday", "iso"]):
        self.set_value(datetime.datetime.today() - datetime.timedelta(weeks=last_n_week), first_day_of_week)

    def get_output_str(self, info_sequence: list[Literal["default", "date", "time", "day", "week_day"]], info_separator: str):
        info_data = {"default": self.__default, "date": self.__date, "time": self.__time, "day": self.__day, "week_day": self.__week_day}
        return info_separator.join({key: info_data[key] for key in info_sequence if key in info_data}.values())

    def get_output_raw(self, info_sequence: list[Literal["default", "date", "time", "day", "week_day"]]):
        info_data = {
            "default": datetime.datetime.fromisoformat(self.__default),
            "date": datetime.date.fromisoformat(self.__date),
            "time": datetime.time.fromisoformat(self.__time),
            "day": self.__day,
            "week_day": self.__week_day
        }
        return {key: info_data[key] for key in info_sequence if key in info_data}
