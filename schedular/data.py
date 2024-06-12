from pandas import read_excel, set_option

from schedular.logger import debug

set_option("display.max_rows", 500)
set_option("display.max_columns", 500)

data = read_excel(
    "Book1.xlsx",
    sheet_name=["Teachers", "Rooms", "Courses", "Grades"],
    header=0,
    index_col=0,
    dtype=object,
)

teachers = data["Teachers"]
rooms = data["Rooms"]
courses = data["Courses"]
grades = data["Grades"]
# TODO duties = data["Duties"]

debug(teachers)
debug(rooms)
debug(courses)

# Constants
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday")
PERIODS = 7
AFTERNOON_PERIOD = 5
GRADES = (6, 7, 8)

# Precalculated Ranges
PERIODS_RANGE = range(1, PERIODS + 1)
MORNING_RANGE = range(1, AFTERNOON_PERIOD)
AFTERNOON_RANGE = range(AFTERNOON_PERIOD, PERIODS + 1)
