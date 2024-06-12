from string import ascii_uppercase
from typing import Any

from pandas import Series

import schedular.data as data
from schedular.data import courses, grades, rooms, teachers
from schedular.logger import debug
from schedular.occupy_tables import Occupied


def section_number_to_letter(number):
    """
    Get a letter from a section number.

    ```
    0 -> A
    1 -> B
    3 -> C
    """
    return ascii_uppercase[number]


def get_list(string) -> list[int] | list[str]:
    """
    Take a string and convert it to a integer or non-case sensitive list.

    ```
    "1,2,3" -> [1, 2, 3]
    "monday, tuEsday, FRIDAY" -> ["monday", "tuesday", "friday"]
    """
    lst = []
    items = str(string).split(",")
    for item in items:
        item = item.strip()
        if item.isdigit():
            item = int(item)
        lst.append(item)
    return lst


def keyword(string, keyword: str, result: Any):
    """
    Turn `string` non-case sensitive and get a value using a keyword.

    ```
    default("ALL", "all", 5) -> 5
    default("foO", "all", 5) -> "foo"
    """
    if isinstance(string, int):
        return string

    string = string.lower()
    if string == keyword.lower():
        return result
    return string


def all_keyword(string, all_result):
    string = keyword(string, keyword="all", result=all_result)
    if string == all_result:
        return string
    return get_list(string)


def get_periods(string):
    return all_keyword(string, all_result=tuple(data.PERIODS_RANGE))


def get_days(string):
    return all_keyword(string, all_result=data.DAYS)


def get_grades(string):
    return all_keyword(string, all_result=data.GRADES)


def intersection(*x):
    return set.intersection(*map(set, x))


def add_column(dataframe, name: str):
    # TODO potential speed up convert None to 0?
    dataframe.loc[:, name] = Series(None for _ in range(len(courses))).values


def precalculate_data():
    add_column(courses, "Periods")
    add_column(courses, "Rooms")
    add_column(courses, "Same")

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
            courses["Sections"][course_name] = ["A", "B"]  # TODO CLEAN
            courses["Same"][course_name] = True
        else:
            courses["Sections"][course_name] = get_list(sections)

        courses["Days"][course_name] = get_days(course["Days"])

        courses["Periods"][course_name] = intersection(
            set(
                data.MORNING_RANGE if course["Type"] == "Core" else data.AFTERNOON_RANGE
            ),
            # teachers.loc[course["Teacher"]]["Periods"], calculates this more @ get_open_teacher_periods
        )

        def set_available_rooms():
            if course["Room Type"] in rooms["Type"].values:
                possible_rooms = rooms.loc[rooms["Type"] == course["Room Type"]]
                courses["Rooms"][course_name] = tuple(possible_rooms.index)
            elif str(course["Room Type"]).lower() == "any":
                courses["Rooms"][course_name] = tuple(rooms.index)
            elif course["Room Type"] in rooms.index:
                courses["Rooms"][course_name] = (course["Room Type"],)
            else:
                raise ValueError("UNKNOWN ROOM TYPE", course["Room Type"])

        set_available_rooms()

    debug(courses, rooms, teachers)


def get_open_teacher_periods(course, day):
    # TODO might have bugs
    periods = Occupied.teachers[course["Teacher"]][day]
    result = list(periods.keys())
    teaching_in_a_row = 0
    for i, teaching_course in periods.items():
        if teaching_course:
            result.remove(i)
            teaching_in_a_row += 1
        else:
            teaching_in_a_row = 0

        if teaching_in_a_row == 3:
            try:
                result.remove(i + 1)
            except ValueError:
                pass
            try:
                result.remove(i - 3)
            except ValueError:
                pass
    return result
