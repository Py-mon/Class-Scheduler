from random import shuffle

import numpy
import pandas as pd

from schedular.data import DAYS, PERIODS_RANGE, courses, rooms
from schedular.data_convert import get_open_teacher_periods, intersection
from schedular.logger import debug
from schedular.occupy_tables import generate_occupy_tables, occupy_course
from schedular.occupy_tables import Occupied

def find_slot_configuration(
    period_slots, period_slot, section, open_slots, grade, total_open
):
    debug(total_open)
    debug(period_slot)

    obeys = []
    put_period = None

    def next_slot(period):
        for day, course_name in period_slot.items():
            if course_name == None:
                continue

            course = courses.loc[course_name]
            open_teacher_periods = get_open_teacher_periods(course, day)
            if period not in intersection(open_teacher_periods, course["Periods"]):
                return False

            result = find_configuration(
                course, day, course_name, section, period, grade, total_open
            )
            if result:
                obeys.append(result)

                if len(course["Grades"]) > 1:
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
        debug("COULDN'T FIND CONFIGURATION FOR")
        # display(Occupied.grades)
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))
            for key, day in Occupied.grades[8].items()
        }.items():
            debug(key)
            debug(grade)
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))
            for key, day in Occupied.grades[7].items()
        }.items():
            debug(key)
            debug(grade)

        for grade, value in period_slots.items():
            for section, value in value.items():
                shuffle(period_slots[grade][section])

        Occupied.rooms, Occupied.teachers, Occupied.grades = generate_occupy_tables()

        do(period_slots)
        return 0, "done"

    return put_period, obeys


def do(period_slots):
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
                    period_slots,
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
                    for key, day in Occupied.grades[8].items()
                }.items():
                    debug(key)
                    debug(grade_)
                for key, grade_ in {
                    key: str(pd.DataFrame.from_dict(day))
                    for key, day in Occupied.grades[7].items()
                }.items():
                    debug(key)
                    debug(grade_)


def fits_requirements(
    period, course, room_name, day, section, course_name, grade, total_open
):
    """Check if a configuration of a course fits all the requirements."""
    room_periods = Occupied.rooms[room_name][day]

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
    #     if Occupied.grades[grade][section][day][period] != None and not Occupied.grades[grade][section][day][period]["Grades"] == (grade,): # this might not work havent tested
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
