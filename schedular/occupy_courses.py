from random import shuffle

import numpy
import pandas as pd

from schedular.data import DAYS, PERIODS_RANGE, courses, rooms
from schedular.data_convert import get_open_teacher_periods, intersection
from schedular.display import debug2
from schedular.logger import debug
from schedular.occupy_tables import Occupied, generate_occupy_tables, occupy_course


def find_slot_configuration(
    period_slots, period_slot, section, open_slots, grade, total_open
):
    debug(total_open)
    debug(period_slot)

    courses_to_add = []
    put_period = None

    def slot_can_fit(period):
        for day, course_name in period_slot.items():
            if course_name == None:
                continue

            course = courses.loc[course_name]
            open_teacher_periods = get_open_teacher_periods(course, day)
            if course_name == "Spanish1":
                debug(period, open_teacher_periods, course["Periods"])
            if period not in intersection(open_teacher_periods, course["Periods"]):
                return False

            result = find_configuration(
                course, day, course_name, section, period, grade
            )
            if not result:
                continue

            courses_to_add.append(result)

            if len(course["Grades"]) > 1:
                for grade_ in course["Grades"]:
                    if grade_ == grade:
                        continue

                    config = find_configuration(
                        course,
                        day,
                        course_name,
                        section,
                        period,
                        grade_,
                    )
                    if config:
                        courses_to_add.append(config)
                    else:
                        return False

            if course["Same"]:
                for section_ in course["Sections"]:
                    if section_ == section:
                        continue

                    config = find_configuration(
                        course,
                        day,
                        course_name,
                        section_,
                        period,
                        grade,
                    )
                    if config:
                        courses_to_add.append(config)
                    else:
                        return False
        return True

    for period in open_slots:
        if slot_can_fit(period):
            put_period = period
            break
    else:
        debug("COULDN'T FIND CONFIGURATION FOR")
        debug(Occupied.teachers["Lutio"])
        # debug(courses)

        # display(Occupied.grades)
        debug2()

        for grade, value in period_slots.items():
            for section, value in value.items():
                shuffle(period_slots[grade][section])

        generate_occupy_tables()

        do(period_slots)
        return 0, "done"

    return put_period, courses_to_add


def do(period_slots):
    all_open = {}  # TODO speed up potential
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

                period, courses_to_add = find_slot_configuration(
                    period_slots,
                    period_slot,
                    section,
                    open_slots,
                    grade,
                    all_open,  # intersection(*all_open)
                )

                if courses_to_add == "done":
                    return

                for result in courses_to_add:
                    if not result:
                        continue
                    occupy_course(*result)

                open_slots.remove(period)

                # debug("ADDED ", courses_to_add[0][-3], " AT ", period)

                # debug2()


def fits_requirements(period, course, room_name, day, section, grade):
    """Check if a configuration of a course fits all the requirements."""
    room_periods = Occupied.rooms[room_name][day]

    if room_periods.get(period, 99) == 99:
        debug("room not available", room_name, section, course["Teacher"], period, day)
        return False

    if room_periods[period] == None:
        return True

    debug(
        "room being used",
        course.name,
        room_name,
        section,
        course["Teacher"],
        period,
        day,
        grade,
        "here",
    )
    return False


def find_configuration(course, day, course_name, section, period, grade):
    # TODO  Check if All Grades can make it to the class without having another class that is just for them
    # for grade in course["Grades"]:
    #     if Occupied.grades[grade][section][day][period] != None and not Occupied.grades[grade][section][day][period]["Grades"] == (grade,): # this might not work havent tested
    #         return False

    for possible_room in course["Rooms"]:
        if type(possible_room) in [float, numpy.float64]:  # empty
            continue

        if course_name == "Spanish1":
            debug(possible_room, course["Rooms"])

        if period not in rooms.loc[possible_room]["Periods"]:
            debug(period, possible_room, rooms.loc[possible_room]["Periods"])
            continue

        if fits_requirements(period, course, possible_room, day, section, grade):

            return period, course, possible_room, day, course_name, section, grade

    return False
