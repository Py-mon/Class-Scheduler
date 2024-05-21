import pandas as pd
import logging
from typing import Any

logger = logging.getLogger(" ")
logging.basicConfig(
    filename="log.log", encoding="utf-8", level=logging.DEBUG, filemode="w"
)

data = pd.read_excel(
    "Book1.xlsx", sheet_name=["Teachers", "Rooms", "Courses"], header=0, index_col=0
)

teachers = data["Teachers"]
rooms = data["Rooms"]
courses = data["Courses"]
# TODO duties = data["Duties"]

# logger.debug("Teachers", teachers)
# logger.debug("Rooms", rooms)
# logger.debug("Courses", courses)


def get_list(string):
    """
    Take a string and convert it to a python list.
    ```
    "1,2,3" -> [1,2,3]
    "5, 7, 1" -> [5,7,1]"""
    return [s.strip() for s in string.split(",")]


rooms_filled: dict[Any, dict[int, None | int]] = {
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

# days_occupied: dict[Any, dict[int, None | int]] = {
#     label: {int(i): None for i in get_list(teacher["Periods"])}
#     for label, teacher in teachers.iterrows()
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


def decline(msg, period, course_name, room_name, day, course):
    logger.debug(
        "DECLINED"
        + " Period: "
        + str(period)
        + " Course: "
        + str(course_name)
        + " Room: "
        + str(room_name)
        + " Day: "
        + str(day)
        + str(msg),
    )


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

    room_periods = rooms_filled[room_name]

    # print(room_periods[1], period, room_periods[period])
    if room_periods[period] != None:
        decline("room full", *info)
        return False
    # room_empty = room_periods.get(period, 99) == None
    # period_available = room_periods.get(period, 99) != 99
    # print(room_empty, period_available)

    # if period_available or not room_empty:
    #     return False
    # if room_periods.get(period) != None:
    #     return False
    # for room_period, occupied in room_periods.items():
    #     if room_period == period and occupied == None:
    #         break
    # else:
    #     return False
    # print(room_periods, occupied, room_period, room_periods[period])

    on_all_days = course["Days"] == "ALL"
    on_day = day in get_list(course["Days"])
    if not on_day and not on_all_days:
        decline("wrong day", *info)
        return False

    core_class = course["Type"] == "Core"
    afternoon_class = period > 4
    if afternoon_class and core_class:
        decline("afternoon, core class", *info)
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
    teacher_working_periods = teachers_occupied[course["Teacher"]]
    teacher_working_periods[period] = course_name

    room_periods = rooms_filled[room_name]
    room_periods[period] = course_name

    # print(rooms_filled)

    grade_periods_occupied = grades_occupied[course["Grade"]]
    grade_periods_occupied[period] = course_name

    print(grades_occupied)

    print(period, course_name, room_name)  # no course on the same period and day


def try_combos():
    for course_name, course in courses.iterrows():
        for possible_room in [course["Room1"], course["Room2"], course["Room3"]]:
            if type(possible_room) == float:
                continue
            for i in range(7):
                if fits_requirements(
                    i + 1, course, possible_room, "Monday", course_name
                ):
                    add_course(i + 1, course, course_name, possible_room, "Monday")
                    break


try_combos()


# teacher_working_periods = get_list(teachers.loc[course["Teacher"]]["Periods"])

# time_available = str(period) in get_list(room["Periods"])
# if not time_available:
#     return False

# teacher_working = str(period) in teacher_working_periods
# if not teacher_working:
#     return False

# on_all_days = course["Days"] == "ALL"
# on_day = day in get_list(course["Days"])
# if not on_day and not on_all_days:
#     return False

# core_class = course["Type"] == "Core"
# afternoon_class = period > 4
# if afternoon_class and core_class:
#     return False

# morning_class = period <= 4
# if morning_class and not core_class:
#     return False

# return True


# def get_day(day):
#     courses_left = list(courses.iterrows())

#     teacher_classes = {i: 0 for i, _ in teachers.iterrows()}

#     for i in range(7):
#         used_rooms = []

#         print(i)

#         while True:
#             series = get_period(i + 1, day, courses_left, used_rooms)
#             if (
#                 isinstance(series, str)
#                 and series
#                 == "Couldn't enforce all the restrictions. Randomize the courses left and try again."
#             ):
#                 import random

#                 courses_left = list(courses.iterrows())
#                 random.shuffle(courses_left)

#                 print('END')

#                 return get_day(day)

#             if isinstance(series, str) and series == "No Courses":
#                 break
#             else:
#                 print(i+1, series.name)
#                 #print(series.name, series["Room"], series["Teacher"])


# get_day("Monday")


# TODO prerequisite (photography for 9th cant be when bible 9 is)
# classes that last multiple periods?

# (Skip lunch and passing time just put periods in)

# Teacher schedules need to have a specific number of preps and teaching hours based on their status (full-time vs. part-time) -2
# Weight given to courses and duties to try to balance staff responsibilities. For example: teaching a class might be weighted as a "3" and doing lunch duty or lobby duty might be rated as a "1" so those teaching less classes may be assigned more lobby duty or study halls, etc.

# Category for duties


# Additional duties that should be factored into staff schedules (lobby duty, study hall, door duty, lunch duty, etc.


# def get_period(period, day, courses_left, used_rooms):
#     # TODO breaks, preps

#     def find_room(course):
#         for possible_room in [course["Room1"], course["Room2"], course["Room3"]]:
#             if type(possible_room) == float:
#                 continue

#             possible_room = rooms.loc[possible_room]

#             room_available = possible_room.name not in used_rooms
#             if not room_available:
#                 continue

#             time_available = str(period) in get_list(possible_room["Periods"])
#             if not time_available:
#                 continue

#             # TODO add possible_room.name to course
#             course["Room"] = possible_room.name
#             used_rooms.append(possible_room.name)
#             break
#         else:
#             return "Couldn't enforce all the restrictions. Randomize the courses left and try again."

#     for i, course in courses_left:
#         teacher_available_periods = get_list(teachers.loc[course["Teacher"]]["Periods"])
#         # TODO used teachers
#         teacher_available = str(period) in teacher_available_periods
#         if not teacher_available:
#             continue

#         on_all_days = course["Days"] == "ALL"
#         on_day = day in get_list(course["Days"])

#         if not on_day and not on_all_days:
#             continue

#         core_class = course["Type"] == "Core"
#         afternoon_class = period > 4
#         if afternoon_class and core_class:
#             continue

#         morning_class = period <= 4
#         if morning_class and not core_class:
#             continue

#         find_room(course)

#         courses_left.remove((i, course))
#         return course

#     return "No Courses"


# def get_day(day):
#     courses_left = list(courses.iterrows())

#     teacher_classes = {i: 0 for i, _ in teachers.iterrows()}

#     for i in range(7):
#         used_rooms = []

#         print(i)

#         while True:
#             series = get_period(i + 1, day, courses_left, used_rooms)
#             if (
#                 isinstance(series, str)
#                 and series
#                 == "Couldn't enforce all the restrictions. Randomize the courses left and try again."
#             ):
#                 import random

#                 courses_left = list(courses.iterrows())
#                 random.shuffle(courses_left)

#                 print('END')

#                 return get_day(day)

#             if isinstance(series, str) and series == "No Courses":
#                 break
#             else:
#                 print(i+1, series.name)
#                 #print(series.name, series["Room"], series["Teacher"])


# get_day("Monday")
