import datetime
import math
from typing import Union, Tuple

class PersianDate:
    """A class to represent and manipulate dates in the Persian (Jalali) calendar."""
    
    MONTH_DAYS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    MONTH_NAMES = [
        "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
        "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"
    ]
    PERSIAN_EPOCH = 1948321.5  # Adjusted epoch for correct conversion offsets
    
    def __init__(self, year: int, month: int, day: int) -> None:
        if not self._is_valid_date(year, month, day):
            raise ValueError(f"Invalid Persian date: {year}/{month}/{day}")
        self.year = year
        self.month = month
        self.day = day
    
    @staticmethod
    def _is_leap_year(year: int) -> bool:
        cycle = year - 474 if year > 0 else year - 473
        rem = cycle % 33
        return rem in (1, 5, 9, 13, 17, 22, 26, 30)
    
    def _is_valid_date(self, year: int, month: int, day: int) -> bool:
        if not (1 <= month <= 12):
            return False
        max_days = self.MONTH_DAYS[month - 1]
        if month == 12 and self._is_leap_year(year):
            max_days = 30
        return 1 <= day <= max_days and year != 0
    
    @classmethod
    def from_gregorian(cls, gregorian_date: datetime.date) -> 'PersianDate':
        jd = cls._gregorian_to_jd(gregorian_date)
        return cls._jd_to_persian(jd)
    
    @classmethod
    def _gregorian_to_jd(cls, date: datetime.date) -> float:
        year, month, day = date.year, date.month, date.day
        a = math.floor((14 - month) / 12)
        y = year + 4800 - a
        m = month + 12 * a - 3
        jd = (day + math.floor((153 * m + 2) / 5) + 365 * y +
              math.floor(y / 4) - math.floor(y / 100) +
              math.floor(y / 400) - 32045)
        return jd
    
    @classmethod
    def _persian_to_jd(cls, year: int, month: int, day: int) -> float:
        epbase = year - 474 if year >= 474 else year - 473
        epyear = 474 + (epbase % 2820)
        days = sum(cls.MONTH_DAYS[:month - 1]) + day
        if month == 12 and cls._is_leap_year(year):
            days += 1
        jd = (days +
              math.floor(((epyear * 682) - 110) / 2816) +
              (epyear - 1) * 365 +
              math.floor(epbase / 2820) * 1029983 +
              cls.PERSIAN_EPOCH)
        return jd
    
    @classmethod
    def _jd_to_persian(cls, jd: float) -> 'PersianDate':
        jd = math.floor(jd) + 0.5
        depoch = jd - cls._persian_to_jd(475, 1, 1)
        cycle = math.floor(depoch / 1029983)
        cyear = depoch - cycle * 1029983
        if cyear == 1029982:
            ycycle = 2820
        else:
            aux1 = math.floor(cyear / 366)
            aux2 = cyear % 366
            ycycle = math.floor((2134 * aux1 + 2816 * aux2 + 2815) / 1028522) + aux1 + 1
        year = int(ycycle + 2820 * cycle + 474)
        if year <= 0:
            year -= 1
        # Day of year
        day_of_year = int(jd - cls._persian_to_jd(year, 1, 1) + 1)
        # Compute month and day
        month = 1
        while month <= 12:
            mdays = cls.MONTH_DAYS[month - 1]
            if month == 12 and cls._is_leap_year(year):
                mdays += 1
            if day_of_year <= mdays:
                break
            day_of_year -= mdays
            month += 1
        day = day_of_year
        return cls(year, month, day)
    
    def to_gregorian(self) -> datetime.date:
        jd = self._persian_to_jd(self.year, self.month, self.day)
        y, m, d = self._jd_to_gregorian(jd)
        return datetime.date(y, m, d)
    
    @classmethod
    def _jd_to_gregorian(cls, jd: float) -> Tuple[int, int, int]:
        L = math.floor(jd) + 68569
        N = math.floor(4 * L / 146097)
        L = L - math.floor((146097 * N + 3) / 4)
        I = math.floor(4000 * (L + 1) / 1461001)
        L = L - math.floor(1461 * I / 4) + 31
        J = math.floor(80 * L / 2447)
        day = L - math.floor(2447 * J / 80)
        L = math.floor(J / 11)
        month = J + 2 - 12 * L
        year = 100 * (N - 49) + I + L
        return int(year), int(month), int(day)
    
    def __str__(self) -> str:
        return f"{self.year}/{self.month:02d}/{self.day:02d} ({self.MONTH_NAMES[self.month - 1]})"
    
    def __add__(self, other: datetime.timedelta) -> 'PersianDate':
        if isinstance(other, datetime.timedelta):
            gregorian = self.to_gregorian() + other
            return self.from_gregorian(gregorian)
        return NotImplemented
    
    def __sub__(self, other: Union['PersianDate', datetime.timedelta]) -> Union[int, 'PersianDate']:
        if isinstance(other, PersianDate):
            return (self.to_gregorian() - other.to_gregorian()).days
        elif isinstance(other, datetime.timedelta):
            gregorian = self.to_gregorian() - other
            return self.from_gregorian(gregorian)
        return NotImplemented
    
    @classmethod
    def today(cls) -> 'PersianDate':
        return cls.from_gregorian(datetime.date.today())
