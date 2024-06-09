from logging import DEBUG, basicConfig, getLogger
from random import randint, shuffle
from string import ascii_uppercase
from time import time
from typing import Any

import numpy
import pandas as pd

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)

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


def debug(*args):
    logger.debug(" ".join([str(s) for s in args]))


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
        for section in course["Sections"]:
            # grade = course["Grades"][0]
            for grade in course["Grades"]:
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

    if course["Same"]:
        if (
            room_periods[period][0] == course_name
            and room_periods[period][1]
            != section  # and period in total_open# and the other section is open
        ):
            return True
        elif not (
            room_periods[period][0] == course_name
            and room_periods[period][1] == section
        ):
            debug("room being used", room_name, section, course["Teacher"], period, day)
            return False
    else:
        debug("room being used", room_name, section, course["Teacher"], period, day)
        return False


def occupy_course(period, course, room_name, day, course_name, section, grade):
    """Put the course in the occupied dictionaries."""
    teachers_occupied[course["Teacher"]][day][period] = (course_name, section)

    rooms_occupied[room_name][day][period] = (course_name, section)

    for grade in course["Grades"]:
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

        if course["Same"] and x and x[0] == course_name and x[1] != section:
            return [i]
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


def find_slot_configuration(period_slot, section, open_slots, grade, total_open):
    global rooms_occupied, teachers_occupied, grades_occupied

    obeys = []
    for day, course_name in period_slot.items():
        if course_name == None:
            # period, course, possible_room, day, course_name, section
            obeys.append(False)
            continue
        course = courses.loc[course_name]
        open_teacher_periods = get_open_teacher_periods(
            course, day, course_name, section
        )
        debug(open_slots)
        # if course["Same"]:
        #     debug(set(total_open))
        #     inter = intersection(course["Periods"],open_teacher_periods, set(total_open))
        # else:
        inter = intersection(course["Periods"], open_slots, open_teacher_periods)

        for period in inter:
            result = find_configuration(
                course, day, course_name, section, period, grade, total_open
            )
            if result:
                obeys.append(result)
                break
        else:
            logger.debug("COULDNT FIND CONFIG FOR" + course_name + section + " ")
            # error
            string = ""
            for Grade, _ in grades.iterrows():
                for key, grade in {
                    key: str(pd.DataFrame.from_dict(day))
                    for key, day in period_slots[Grade].items()
                }.items():
                    string += key + "\n"
                    string += grade + "\n\n"

            logger.debug("\n" + str(string))

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
    for grade, sections in period_slots.items():  # * knows the grade here
        all_open = []
        for section, period_slots_ in sections.items():
            open_slots = list(PERIODS_RANGE)
            all_open.append(open_slots)
            for period_slot in period_slots_:
                if period_slot == {day: None for day in DAYS}:
                    continue

                debug(period_slot)

                obeys = find_slot_configuration(
                    period_slot, section, open_slots, grade, intersection(*all_open)
                )

                if obeys == "done":
                    return

                last_index = -1
                for result in obeys:
                    if not result:
                        continue
                    occupy_course(*result)
                    last_index = result[0]

                if last_index != -1:
                    open_slots.remove(last_index)


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
    display(rooms_occupied)
    display(teachers_occupied)


if __name__ == "__main__":
    main()
