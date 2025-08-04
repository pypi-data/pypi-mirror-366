# DateTimeEnhanced

`DateTimeEnhanced` is a lightweight Python helper for working with dates and times. It lets you:

- choose the start of the week (`"sunday"`, `"monday"`, or `"iso"`).
- switch between human-readable names and integers via the `all_integer` flag.
- and export selected components as either a joined string or raw Python objects.

> **Note (4 Aug 2025):** `week` now returns **only the week number** in all modes (including `"iso"`). No weekday suffix
> is appended.

---

## Installation

Install via pip:

```bash
pip install DateTimeEnhanced
```

## API Reference

#### DateTimeEnhanced()

```bash
Initializes a new instance of the class.
```
#### set_value(date_time: datetime.datetime, first_day_of_week: Literal["sunday","monday","iso"], all_integer: bool) -> None
```bash
Populate the internal fields from an explicit datetime. 
"first_day_of_week" controls weekday indexing and week numbering basis
"all_integer" toggles numeric vs name forms for day/month. 

Weekday index when all_integer=True:
"sunday" → Sun=0..Sat=6
"monday" → Mon=0..Sun=6
"iso" → Mon=1..Sun=7

(All derived from the mapping in set_value.) 
```
#### today(first_day_of_week: Literal["sunday","monday","iso"], all_integer: bool) -> None

```bash
Set fields to the current local date/time with the given mode/format. 
```

#### last_n_day(last_n_day: int, first_day_of_week: Literal["sunday","monday","iso"], all_integer: bool) -> None

```bash
Set fields to N days before today. 
```

#### last_n_week(last_n_week: int, first_day_of_week: Literal["sunday","monday","iso"], all_integer: bool) -> None

``` bash
Set fields to N weeks before today. 
```
#### last_n_month(last_n_month: int, first_day_of_week: Literal["sunday","monday","iso"], all_integer: bool) -> None

``` bash
Set fields to N months before today. (Uses dateutil.relativedelta.) 
```

#### get_output_str(info_sequence: list[Literal["default","date","time","day","month","year","week"]], info_separator: str) -> str

``` bash
Example

dte.get_output_str(["date","time","day","month","year","week"], " | ")
# → "2025-08-04 | 10:44:31.320780 | 1 | 08 | 2025 | 32"
```
#### get_output_raw(info_sequence: list[Literal["default","date","time","day","month","year","week"]]) -> dict

```bash
Return a dict of raw Python objects:
default: datetime.datetime
date: datetime.date
time: datetime.time
day, month, year: int when stored numerically; otherwise str
week: int (ISO/Sunday/Monday bases all yield a numeric week). ```
```

## Usage

```bash
from DateTimeEnhanced import DateTimeEnhanced

dte = DateTimeEnhanced()

# Use Monday as the start of the week; get names (not numbers)
dte.today(first_day_of_week="monday", all_integer=False)
print(
    dte.get_output_str(
        info_sequence=["default", "date", "time", "day", "month", "year", "week"],
        info_separator="|"
    )
)
# Example: "2025-08-04 10:44:31.320474|2025-08-04|10:44:31.320474|Monday|August|2025|32"

# Switch to all integers (Sunday-based indexing for weekday; zero-padded month)
dte.today("sunday", all_integer=True)
print(dte.get_output_str(["default", "date", "time", "day", "month", "year", "week"], "|"))
# Example: "2025-08-04 10:44:31.320532|2025-08-04|10:44:31.320532|1|08|2025|32"

# ISO mode: Monday=1..Sunday=7 (for the weekday index when all_integer=True);
# week is still the numeric ISO week (no ".D" suffix)
dte.today("iso", all_integer=True)
print(dte.get_output_str(["date", "time", "week"], "|"))
# Example: "2025-08-04|10:44:31.320649|32"

# Raw objects (datetime/date/time + ints/strings as appropriate)
print(dte.get_output_raw(["default", "date", "time", "day", "month", "year", "week"]))
# Example:
# {
#   'default': datetime.datetime(2025, 8, 4, 10, 44, 31, 320956),
#   'date': datetime.date(2025, 8, 4),
#   'time': datetime.time(10, 44, 31, 320956),
#   'day': 1, 'month': 8, 'year': 2025, 'week': 32
# }
