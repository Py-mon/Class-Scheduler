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


def find_configuration(course, day, course_name, section, period, grade, total_open):
    # TODO  Check if All Grades can make it to the class without having another class that is just for them
    # for grade in course["Grades"]:
    #     if grades_occupied[grade][section][day][period] != None and not grades_occupied[grade][section][day][period]["Grades"] == (grade,): # this might not work havent tested
    #         return False

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
