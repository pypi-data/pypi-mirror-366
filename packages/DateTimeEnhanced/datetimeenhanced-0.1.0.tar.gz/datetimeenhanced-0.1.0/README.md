# DateTimeEnhanced

`DateTimeEnhanced` is a lightweight Python utility class that simplifies working with dates and times. It provides enhanced formatting, week-day indexing, and easy retrieval of structured date/time information.

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
#### today(first_day_of_week: Literal["sunday", "monday", "iso"])
```bash
Sets the internal state to the current date and time, considering the specified start of the week.
```
#### last_n_day(last_n_day: int, first_day_of_week: Literal["sunday", "monday", "iso"])
```bash
Sets the date to a past day, n days before today.
```
#### last_n_week(last_n_week: int, first_day_of_week: Literal["sunday", "monday", "iso"])
``` bash
Sets the date to a past point, n weeks before today.
```
#### get_output_str(info_sequence: list[str], info_separator: str) -> str
``` bash
Returns a string with requested date/time components joined by the provided separator.

Arguments:
info_sequence: List containing any of "default", "date", "time", "day", "week_day"
info_separator: String used to join the elements
```
#### get_output_raw(info_sequence: list[str]) -> dict
```bash
Returns a dictionary of raw Python objects for the requested components.

Arguments:
info_sequence: List containing any of "default", "date", "time", "day", "week_day"
```
## Usage
```bash
from DateTimeEnhanced import DateTimeEnhanced

# Create an instance
dte = DateTimeEnhanced()

# Set today's date using ISO week numbering
dte.today(first_day_of_week="iso")

# Get a formatted string with selected date components
output = dte.get_output_str(
    info_sequence=["date", "time", "week_day"],
    info_separator=" | "
)
print(output)
# Example output: "2025-08-03 | 14:22:35.123456 | 31.7"

# Retrieve raw Python date/time objects
raw_output = dte.get_output_raw(
    info_sequence=["default", "day"]
)
print(raw_output)
# Example output: {'default': datetime.datetime(...), 'day': 'Sunday'}
```
