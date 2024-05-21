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
logger.setLevel(9)

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
    return [s.strip() for s in string.split(",")]


rooms_occupied: dict[Any, dict[int, None | int]] = {
    label: {int(i): None for i in get_list(room["Periods"])}
    for label, room in rooms.iterrows()
}
#    Room1  Room2  Room3  Room4
# 1 course
# 2
# 3
# 4
# 5
# 6
# 7

teachers_occupied: dict[Any, dict[int, None | int]] = {
    label: {int(i): None for i in get_list(teacher["Periods"])}
    for label, teacher in teachers.iterrows()
}
#   Teacher1 Teacher2 Teacher3
# 1 course
# 2
# 3
# 4
# 5
# 6
# 7

# needs to be 3D?
# days_occupied: dict[Any, dict[int, None | int]] = {
#     day: {int(i): None for i in range(1, 8)}
#     for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
# }
# #   Monday, Tuesday, Wednesday, Thursday
# # 1 course
# # 2
# # 3
# # 4
# # 5
# # 6
# # 7

grades_occupied: dict[Any, dict[int, None | int]] = {
    course["Grade"]: {int(i): None for i in range(1, 8)}
    for _, course, in courses.iterrows()
}

#   8,     9,    10
# 1 course
# 2
# 3
# 4
# 5
# 6
# 7


def fits_requirements(period, course, room_name, day, course_name):
    teacher_working_periods = teachers_occupied[course["Teacher"]]

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

    room_periods = rooms_occupied[room_name]

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

    grade_periods_occupied = grades_occupied[course["Grade"]]
    if grade_periods_occupied[period] != None:
        decline("Grade busy", *info)
        return

    return True


def add_course(period, course, course_name, room_name, day):
    teachers_occupied[course["Teacher"]][period] = course_name

    rooms_occupied[room_name][period] = course_name

    grades_occupied[course["Grade"]][period] = course_name

    # days_occupied[day][period] = course_name


def try_combos():
    for course_name, course in courses.iterrows():
        for possible_room in [course["Room1"], course["Room2"], course["Room3"]]:
            if type(possible_room) == float: # empty
                continue
            
            for i in range(7):
                if fits_requirements(
                    i + 1, course, possible_room, "monday", course_name
                ):
                    add_course(i + 1, course, course_name, possible_room, "monday")
                    break


try_combos()

#print(rooms_occupied)
print(grades_occupied)
#print(teachers_occupied)
