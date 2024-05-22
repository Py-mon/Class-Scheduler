import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(" ")
logging.basicConfig(
    filename="log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    filemode="w",
    format="%(levelname)s: %(message)s",
)
logger.setLevel(0)

logging.addLevelName(2, "DECLINED")


def decline(msg, period, course_name, room_name, day, course):
    if logger.level >= 2:
        logger._log(
            2,
            "Period: "
            + str(period)
            + " Course: "
            + str(course_name)
            + " Room: "
            + str(room_name)
            + " Day: "
            + str(day)
            + " "
            + str(msg),
            (),
        )


data = pd.read_excel(
    "Book1.xlsx", sheet_name=["Teachers", "Rooms", "Courses"], header=0, index_col=0
)

teachers = data["Teachers"]
rooms = data["Rooms"]
courses = data["Courses"]
# TODO duties = data["Duties"]

logger.debug("\n" + str(teachers))
logger.debug("\n" + str(rooms))
logger.debug("\n" + str(courses))


def get_list(string):
    """
    Take a string and convert it to a python list.
    ```
    "1,2,3" -> [1,2,3]
    "5, 7, 1" -> [5,7,1]"""
    return [s.strip() for s in str(string).split(",")]


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]


def create_occupy_table(
    iter, periods, label
) -> dict[str, dict[Any, dict[int, None | int]]]:
    return {
        label(name, value): {
            day: {
                int(period): None
                for period in periods(name, value)
            }
           for day in DAYS
        }
        for name, value in iter
    }


def label(name, _):
    return name


def periods_column(_, value):
    return get_list(value["Periods"])


# rooms_occupied: dict[str, dict[Any, dict[int, None | int]]] = {
#     day: {
#         label: {
#             int(i): None for i in get_list(room["Periods"])
#         }
#         for label, room in rooms.iterrows()
#     }
#     for day in DAYS
# }
rooms_occupied = create_occupy_table(rooms.iterrows(), periods_column, label)

# teachers_occupied: dict[Any, dict[int, None | int]] = {
#     label: {int(i): None for i in get_list(teacher["Periods"])}
#     for label, teacher in teachers.iterrows()
# }
teachers_occupied = create_occupy_table(teachers.iterrows(), periods_column, label)

# grades_occupied: dict[Any, dict[int, None | int]] = {
#     get_list(course["Grades"])[0]: {int(i): None for i in range(1, 8)}
#     for _, course, in courses.iterrows()
# }
grades_occupied = create_occupy_table(
    courses.iterrows(),
    lambda _, __: range(1, 8),
    lambda _, value: get_list(value["Grades"])[0],
)


def fits_requirements(period, course, room_name, day, course_name):

    teacher_working_periods = teachers_occupied[course["Teacher"]][day]

    info = (period, course_name, room_name, day, course)

    worked_in_a_row_recently = 0
    for work_period, occupied in teacher_working_periods.items():
        if occupied == None:
            worked_in_a_row_recently = 0
            if work_period == period:
                break
        else:
            worked_in_a_row_recently += 1
    else:
        decline("not available", *info)
        return False

    if worked_in_a_row_recently > 3:
        decline("needs a break", *info)
        return False

    room_periods = rooms_occupied[room_name][day]

    if room_periods.get(period, 99) == 99:
        decline("room not available", *info)
        return False

    if room_periods[period] != None:
        decline("room full", *info)
        return False

    on_all_days = course["Days"].upper() == "ALL"
    on_day = day in [x.lower() for x in get_list(course["Days"])]
    if not on_day and not on_all_days:
        decline("wrong day", *info)  # can speed up by putting this outside
        return False

    core_class = course["Type"] == "Core"
    afternoon_class = period > 4
    if afternoon_class and core_class:
        decline(
            "afternoon, core class", *info
        )  # can speed up by looping only over the periods
        return False

    morning_class = period <= 4
    if morning_class and not core_class:
        decline("morning, non-core class", *info)
        return False

    for grade in get_list(course["Grades"]):
        grade_periods_occupied = grades_occupied[grade][day]
        if grade_periods_occupied[period] != None:
            decline("Grade busy", *info)
            return

    return True


def add_course(period, course, course_name, room_name, day):
    teachers_occupied[course["Teacher"]][day][period] = course_name

    rooms_occupied[room_name][day][period] = course_name

    # course["Letter"]
    for grade in get_list(course["Grades"]):
        grades_occupied[grade][day][period] = course_name

    # days_occupied[day][period] = course_name


def try_combos():
    for day in DAYS:
        for course_name, course in courses.iterrows():
            for possible_room in [course["Room1"], course["Room2"], course["Room3"]]:
                if type(possible_room) == float:  # empty
                    continue

                for i in range(7):
                    if fits_requirements(
                        i + 1, course, possible_room, day, course_name
                    ):
                        add_course(i + 1, course, course_name, possible_room, day)
                        break


try_combos()

print(rooms_occupied)
import random

x = list(grades_occupied.items())
random.shuffle(x)
print(x)
print(teachers_occupied)
