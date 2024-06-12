from logging import DEBUG, basicConfig, getLogger
from random import randint, shuffle
from string import ascii_uppercase
from time import time
from typing import Any
from schedular.logger import logger

import numpy
import pandas as pd

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)

data = pd.read_excel(
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

logger.debug("\n" + str(teachers))
logger.debug("\n" + str(rooms))
logger.debug("\n" + str(courses))

# Constants
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday")
PERIODS = 7
AFTERNOON_PERIOD = 5
GRADES = (6, 7, 8)

# Precalculated Ranges
PERIODS_RANGE = range(1, PERIODS + 1)
MORNING_RANGE = range(1, AFTERNOON_PERIOD)
AFTERNOON_RANGE = range(AFTERNOON_PERIOD, PERIODS + 1)


def section_number_to_letter(number):
    """
    Get a letter from a section number.

    ```
    0 -> A
    1 -> B
    3 -> C
    """
    return ascii_uppercase[number]


def get_list(string):
    """
    Take a string and convert it to a python list.
    ```
    "1,2,3" -> ["1", "2", "3"]
    "5, 7, 1" -> ["5", "7", "1"]"""
    return tuple(s.strip() for s in str(string).split(","))


def get_periods(string):
    if string.lower() == "all":
        return PERIODS_RANGE
    return tuple(int(x) for x in get_list(string))


def get_days(string):
    if string.lower() == "all":
        return DAYS
    return tuple(x.lower() for x in get_list(string))


def get_grades(string):
    if not isinstance(string, int) and string.lower() == "all":
        return GRADES
    return tuple(int(x) for x in get_list(string))


def intersection(*x):
    return set.intersection(*map(set, x))


def precalculate_data():
    courses.insert(
        len(courses.columns), "Periods", [None for _ in range(len(courses))], True
    )
    courses.insert(
        len(courses.columns), "Rooms", [None for _ in range(len(courses))], True
    )
    courses.insert(
        len(courses.columns), "Same", [None for _ in range(len(courses))], True
    )

    for name, teacher in teachers.iterrows():
        teachers["Periods"][name] = get_periods(teacher["Periods"])

    for name, room in rooms.iterrows():
        rooms["Periods"][name] = get_periods(room["Periods"])

    for name, grade in grades.iterrows():
        new_sections = []
        for section in range(grade["Sections"]):
            letter = section_number_to_letter(section)
            new_sections.append(letter)
        grades["Sections"][name] = new_sections

    for course_name, course in courses.iterrows():
        courses["Grades"][course_name] = get_grades(course["Grades"])

        # Convert int "Sections" (2) to ["A", "B", ...]
        sections = course["Sections"]
        if isinstance(sections, float):
            courses["Sections"][course_name] = grades["Sections"][course["Grades"][0]]
        elif sections == "Same":
            courses["Sections"][course_name] = ["A", "B"]  #
            courses["Same"][course_name] = True
        else:
            courses["Sections"][course_name] = get_list(sections)

        courses["Days"][course_name] = get_days(course["Days"])

        courses["Periods"][course_name] = intersection(
            set(MORNING_RANGE if course["Type"] == "Core" else AFTERNOON_RANGE),
            teachers.loc[course["Teacher"]]["Periods"],
        )
        if course["Room Type"] in rooms["Type"].values:
            possible_rooms = rooms.loc[rooms["Type"] == course["Room Type"]]
            courses["Rooms"][course_name] = tuple(possible_rooms.index)
        elif str(course["Room Type"]).lower() == "any":
            courses["Rooms"][course_name] = tuple(rooms.index)
        elif course["Room Type"] in rooms.index:
            courses["Rooms"][course_name] = (course["Room Type"],)
        else:
            raise ValueError("UNKNOWN ROOM TYPE", course["Room Type"])


def calculate_period_slots():
    period_slots = {
        int(name): {  # type: ignore
            section: [{day: None for day in DAYS} for _ in PERIODS_RANGE]
            for section in grade["Sections"]
        }
        for name, grade in grades.iterrows()
    }  # grade section period day - course

    def get_open_index(from_, days_):
        for i, period in enumerate(from_):
            if all([period[day] == None for day in days_]):
                return i

    for course_name, course in sorted(
        list(courses.iterrows()), key=lambda x: len(x[1]["Days"]), reverse=True
    ):  # might not work
        x = course["Sections"]
        if course["Same"]:
            x = course["Sections"][0]
        for section in x:
            grade = course["Grades"][0]
            #for grade in course["Grades"]:
            index = get_open_index(period_slots[grade][section], course["Days"])
            for day in course["Days"]:
                period_slots[grade][section][index][day] = course_name  # type: ignore

    string = ""
    for Grade, _ in period_slots.items():
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))  # type: ignore
            for key, day in period_slots[Grade].items()
        }.items():
            string += key + "\n"
            string += grade + "\n\n"

    logger.debug("\n" + str(string))

    return period_slots


def create_occupy_table(iter) -> dict[str, dict[Any, dict[int, Any]]]:
    return {
        name: {day: {int(period): None for period in value["Periods"]} for day in DAYS}
        for name, value in iter
    }


def generate_occupy_tables():
    rooms_occupied = create_occupy_table(rooms.iterrows())

    teachers_occupied = create_occupy_table(
        teachers.iterrows()
    )  # name day period - course

    grades_occupied = {
        name: {
            section: {
                day: {int(period): None for period in PERIODS_RANGE} for day in DAYS
            }
            for section in grade["Sections"]
        }
        for name, grade in grades.iterrows()
    }
    # grade section day period - course
    return rooms_occupied, teachers_occupied, grades_occupied


def fits_requirements(
    period, course, room_name, day, section, course_name, grade, total_open
):
    """Check if a configuration of a course fits all the requirements."""
    room_periods = rooms_occupied[room_name][day]

    if room_periods.get(period, 99) == 99:
        debug("room not available", room_name, section, course["Teacher"], period, day)
        return False

    if room_periods[period] == None:
        return True

    # if course["Same"]:  # Same and there is a course already in the spot
    #     if room_periods[period][0] == course_name and (
    #         room_periods[period][1] != section  # or room_periods[period][2] != grade
    #     ):  # and period in total_open# and the other section is open
    #         return True
    #     elif not (
    #         room_periods[period][0] == course_name
    #         and room_periods[period][1]
    #         == section  # and room_periods[period][2] == grade
    #     ):
    #         debug(
    #             "room being used",
    #             room_name,
    #             section,
    #             course["Teacher"],
    #             period,
    #             day,
    #             grade,
    #             "elif not",
    #         )
    #         return False
    # else:
    debug(
        "room being used",
        room_name,
        section,
        course["Teacher"],
        period,
        day,
        grade,
        "here",
    )
    return False


def occupy_course(period, course, room_name, day, course_name, section, grade):
    """Put the course in the occupied dictionaries."""
    teachers_occupied[course["Teacher"]][day][period] = (course_name, section, grade)

    rooms_occupied[room_name][day][period] = (course_name, section, grade)

    # for grade in course["Grades"]: # * reason for Nones
    #     debug(grade, course_name, section, period, day)
    #     #
    grades_occupied[grade][section][day][period] = course_name


# def is_grade_occupied(course, period, section, day, course_name):
# for grade in course["Grades"]:
#     grade_periods_occupied = grades_occupied[grade][section][day]
#     print(grade_periods_occupied[period], course_name)
#     if grade_periods_occupied[period] != None and grade_periods_occupied[period] != course_name:
#         return False
# if any(
#         [
#             grades_occupied[grade][section][day][period] == course_name
#             for grade in course["Grades"]
#         ]):
#         print('TRUE')
#         return True
# for grade in course["Grades"]:
#     grade_periods_occupied = grades_occupied[grade][section][day]

#     if grade_periods_occupied[period] != None:
#         return False


def find_configuration(course, day, course_name, section, period, grade, total_open):
    # if is_grade_occupied(course, period, section, day, course_name) == False:
    #     return False  # TODO this is whether it works or not

    for possible_room in course["Rooms"]:
        if type(possible_room) in [float, numpy.float64]:  # empty
            continue

        if period not in rooms.loc[possible_room]["Periods"]:
            continue

        if fits_requirements(
            period, course, possible_room, day, section, course_name, grade, total_open
        ):
            return period, course, possible_room, day, course_name, section, grade

    return False


def get_open_teacher_periods(course, day, course_name, section):
    periods = teachers_occupied[course["Teacher"]][day]
    result = list(periods.keys())
    trues = 0
    for i, x in periods.items():

        # if course["Same"] and x and x[0] == course_name and x[1] != section:
        #     return [i]
        if x:
            result.remove(i)
            trues += 1
        else:
            trues = 0

        if trues == 3:
            try:
                result.remove(i + 1)
            except ValueError:
                pass
            try:
                result.remove(i - 3)
            except ValueError:
                pass
    return result


def get_slots():
    string = "\n"
    for Grade, _ in grades.iterrows():
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))  # type: ignore
            for key, day in period_slots[int(Grade)].items()  # type: ignore
        }.items():
            string += key + "\n"
            string += grade + "\n\n"
    return string


def find_slot_configuration(period_slot, section, open_slots, grade, total_open):
    global rooms_occupied, teachers_occupied, grades_occupied

    debug(total_open)
    debug(period_slot)

    obeys = []
    put_period = None

    def next_slot(period):
        for day, course_name in period_slot.items():
            if course_name == None:
                # obeys.append(False)
                continue

            course = courses.loc[course_name]
            open_teacher_periods = get_open_teacher_periods(
                course, day, course_name, section
            )
            if period not in intersection(open_teacher_periods, course["Periods"]):
                return False

            result = find_configuration(
                course, day, course_name, section, period, grade, total_open
            )
            if result:
                obeys.append(result)
                print(course_name, course["Grades"])
                if len(course["Grades"]) > 1:
                    print("MORE GRADES")
                    for grade_ in course["Grades"]:
                        if grade_ == grade:
                            continue

                        for possible_room in course["Rooms"]:
                            if type(possible_room) in [float, numpy.float64]:  # empty
                                continue

                            if period not in rooms.loc[possible_room]["Periods"]:
                                continue

                            result2 = find_configuration(
                                course,
                                day,
                                course_name,
                                section,
                                period,
                                grade_,
                                total_open,
                            )
                            obeys.append(result2)
                            break
                        else:
                            return False

                if course["Same"]:
                    print("SAME", course_name)

                    for section_ in course["Sections"]:
                        if section_ == section:
                            continue

                        for possible_room in course["Rooms"]:
                            if type(possible_room) in [float, numpy.float64]:  # empty
                                continue

                            if period not in rooms.loc[possible_room]["Periods"]:
                                continue

                            result2 = find_configuration(
                                course,
                                day,
                                course_name,
                                section_,
                                period,
                                grade,
                                total_open,
                            )
                            obeys.append(result2)
                            break
                        else:
                            return False
            else:
                return False
        return True

    for period in open_slots:
        x = next_slot(period)
        if x:
            put_period = period

            break
    else:
        logger.debug("COULDN'T FIND CONFIGURATION FOR")
        # display(grades_occupied)
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))
            for key, day in grades_occupied[8].items()
        }.items():
            debug(key)
            debug(grade)
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))
            for key, day in grades_occupied[7].items()
        }.items():
            debug(key)
            debug(grade)

        for grade, value in period_slots.items():
            for section, value in value.items():
                shuffle(period_slots[grade][section])

        rooms_occupied, teachers_occupied, grades_occupied = generate_occupy_tables()

        do()
        return 0, "done"

    return put_period, obeys


def do():
    all_open = {}
    for grade, sections in period_slots.items():
        grade_open = {}
        all_open[grade] = grade_open
        for section, period_slots_ in sections.items():
            open_slots = list(PERIODS_RANGE)
            grade_open[section] = open_slots

    for grade, sections in period_slots.items():
        for section, period_slots_ in sections.items():
            open_slots = list(PERIODS_RANGE)
            all_open[grade][section] = open_slots
            for period_slot in period_slots_:
                if period_slot == {day: None for day in DAYS}:
                    continue

                period, obeys = find_slot_configuration(
                    period_slot,
                    section,
                    open_slots,
                    grade,
                    all_open,  # intersection(*all_open)
                )

                if obeys == "done":
                    return

                for result in obeys:
                    if not result:
                        continue
                    occupy_course(*result)

                open_slots.remove(period)

                # period, course, possible_room, day, course_name, section, grade

                debug("ADDED ", obeys[0][-3], " AT ", period)

                for key, grade_ in {
                    key: str(pd.DataFrame.from_dict(day))
                    for key, day in grades_occupied[8].items()
                }.items():
                    debug(key)
                    debug(grade_)
                for key, grade_ in {
                    key: str(pd.DataFrame.from_dict(day))
                    for key, day in grades_occupied[7].items()
                }.items():
                    debug(key)
                    debug(grade_)


def display(occupied):
    for key, grade in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in occupied.items()
    }.items():
        print(key)
        print(grade)
        print()


def main():
    global rooms_occupied, teachers_occupied, grades_occupied, period_slots, p
    precalculate_data()
    logger.debug("\n" + str(teachers))
    logger.debug("\n" + str(rooms))
    logger.debug("\n" + str(courses))
    rooms_occupied, teachers_occupied, grades_occupied = generate_occupy_tables()
    period_slots = calculate_period_slots()
    p = [
        (section, period_slots_, grade)
        for grade, sections in period_slots.items()  # * knows the grade here
        for section, period_slots_ in sections.items()
    ]

    start = time()
    do()
    print(time() - start)

    display(grades_occupied[8])
    display(grades_occupied[7])
    # display(rooms_occupied)
    # display(teachers_occupied)


# print steps
if __name__ == "__main__":
    main()
