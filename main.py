from logging import DEBUG, basicConfig, getLogger
from random import randint, shuffle
from string import ascii_uppercase
from time import time
from typing import Any

import numpy
import pandas as pd

logger = getLogger(" ")
basicConfig(
    filename="log.log",
    encoding="utf-8",
    level=DEBUG,
    filemode="w",
    format="%(levelname)s: %(message)s",
)
logger.setLevel(9)

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

# Constants
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
PERIODS = 7
AFTERNOON_PERIOD = 5

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
    return [s.strip() for s in str(string).split(",")]


def precalculate_data():
    courses.insert(
        len(courses.columns), "Periods", [None for _ in range(len(courses))], True
    )

    for course_name, course in courses.iterrows():
        # Convert int "Sections" (2) to ["A", "B", ...]
        new_sections = []
        for section in range(course["Sections"]):
            letter = section_number_to_letter(section)
            new_sections.append(letter)
        courses["Sections"][course_name] = new_sections

        # Convert "Days" to list of lowercase days
        if "all" == course["Days"].lower():
            courses["Days"][course_name] = DAYS
        else:
            courses["Days"][course_name] = [
                day.lower() for day in get_list(course["Days"])
            ]

        courses["Periods"][course_name] = (
            MORNING_RANGE if course["Type"] == "Core" else AFTERNOON_RANGE
        )

        # TODO course["Grades"]

    for name, room in rooms.iterrows():
        rooms["Periods"][name] = get_list(room["Periods"])

    for name, teacher in teachers.iterrows():
        teachers["Periods"][name] = get_list(teacher["Periods"])


def calculate_period_slots():
    # TODO multiple grades allowed in class (same thing as vvv)
    # TODO 1 Section for all A, B etc (new page for grades?)
    period_slots = {
        9: {"A": [{} for _ in PERIODS_RANGE], "B": [{} for _ in PERIODS_RANGE]}
    }  # grade section period day - course
    # ? are period slots different for each section

    for course_name, course in courses.iterrows():
        for section in course["Sections"]:
            for day in course["Days"]:
                for i, period_slot in enumerate(
                    period_slots[course["Grades"]][section]
                ):  # break
                    if day in list(period_slot.keys()):
                        continue

                    period_slots[course["Grades"]][section][i][day] = course_name
                    break

    string = ""
    for key, grade in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in period_slots[9].items()
    }.items():
        string += key + "\n"
        string += grade + "\n\n"

    logger.debug("\n" + str(string))

    return period_slots


def create_occupy_table(iter) -> dict[str, dict[Any, dict[int, None | int]]]:
    return {
        name: {day: {int(period): None for period in value["Periods"]} for day in DAYS}
        for name, value in iter
    }


def generate_occupy_tables():
    rooms_occupied = create_occupy_table(rooms.iterrows())

    teachers_occupied = create_occupy_table(teachers.iterrows())

    grades_occupied = {
        course["Grades"]: {  # TODO
            section: {
                day: {int(period): None for period in PERIODS_RANGE} for day in DAYS
            }
            for section in course["Sections"]
        }
        for name, course in courses.iterrows()
    }
    # grade section day period - course
    return rooms_occupied, teachers_occupied, grades_occupied


def fits_requirements(period, course, room_name, day, section):
    """Check if a configuration of a course fits all the requirements."""
    teacher_working_periods = teachers_occupied[course["Teacher"]][day]

    worked_in_a_row_recently = 0
    for work_period, occupied in teacher_working_periods.items():
        if occupied == None:
            worked_in_a_row_recently = 0
            if work_period == period:
                break
        else:
            worked_in_a_row_recently += 1
    else:
        # "teacher teaching or not available"
        return False

    if worked_in_a_row_recently > 3:
        # "teacher needs a break", *info)
        return False

    room_periods = rooms_occupied[room_name][day]

    if room_periods.get(period, 99) == 99:
        # decline("room not available", *info)
        return False

    if room_periods[period] != None:
        # decline("room being used", *info)
        return False

    grade_periods_occupied = grades_occupied[course["Grades"]][section][day]
    if grade_periods_occupied[period] != None:
        # decline("Grade busy", *info)
        return

    return True


def occupy_course(period, course, room_name, day, course_name, section):
    """Put the course in the occupied dictionaries."""
    teachers_occupied[course["Teacher"]][day][period] = course_name

    rooms_occupied[room_name][day][period] = course_name

    grades_occupied[course["Grades"]][section][day][period] = course_name


def find_configuration(course, day, course_name, section):
    for possible_room in [
        course["Room1"],
        course["Room2"],
        course["Room3"],
    ]:  # precalculate
        if type(possible_room) in [float, numpy.float64]:  # empty
            continue

        for period in course["Periods"]:
            if fits_requirements(period, course, possible_room, day, section):
                return period, course, possible_room, day, course_name, section
    return False


def get_obeys(period_slot, section):
    global rooms_occupied, teachers_occupied, grades_occupied

    obeys = []
    for day, course_name in period_slot.items():
        course = courses.loc[course_name]
        result = find_configuration(course, day, course_name, section)
        if result:
            obeys.append(result)
        else:
            # error
            for grade, value in period_slots.items():
                for section, value in value.items():
                    shuffle(period_slots[grade][section])

            rooms_occupied, teachers_occupied, grades_occupied = (
                generate_occupy_tables()
            )

            do()
            return "done"
    return obeys


def do():
    for grade, sections in period_slots.items():
        for section, period_slots_ in sections.items():
            for period_slot in period_slots_:
                obeys = get_obeys(period_slot, section)

                if obeys == "done":
                    return

                for result in obeys:
                    occupy_course(*result)


precalculate_data()
rooms_occupied, teachers_occupied, grades_occupied = generate_occupy_tables()
period_slots = calculate_period_slots()

start = time()
do()
print(time() - start)


for key, grade in {
    key: str(pd.DataFrame.from_dict(day)) for key, day in grades_occupied[9].items()
}.items():
    print(key)
    print(grade)
    print()


# TODO assign rooms to different subjects
