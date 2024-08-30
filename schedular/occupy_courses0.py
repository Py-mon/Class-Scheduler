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
            if course_name == None: # not filled
                continue

            course = courses.loc[course_name]
            open_teacher_periods = get_open_teacher_periods(course, day)

            if period not in open_teacher_periods:
                debug(period, course_name, "teacher not available")
                return False

            if period not in course["Periods"]:
                debug(period, course_name, "not in morning/afternoon")
                return False

            result = find_room_configuration(
                course, day, course_name, section, period, grade
            )
            if not result:
                # continue
                #!
                return False

            courses_to_add.append(result)

            if len(course["Grades"]) > 1:
                for grade_ in course["Grades"]:
                    if grade_ == grade:
                        continue

                    config = find_room_configuration(
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

                    config = find_room_configuration(
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

        debug2()

        for grade, value in period_slots.items():
            for section, value in value.items():
                shuffle(period_slots[grade][section])

        generate_occupy_tables()

        do(period_slots)
        return 0, "done"

    return put_period, courses_to_add


def test_slot(period_slot, period):
    for day, course_name in period_slot.items():
        if course_name == None:
            continue

        course = courses.loc[course_name]
        open_teacher_periods = get_open_teacher_periods(course, day)

        if period not in open_teacher_periods:
            debug(period, course_name, "teacher not available")
            return False

        if period not in course["Periods"]:
            debug(period, course_name, "not in morning/afternoon")
            return False

        return True
    raise ValueError("bad")


def find_room_for_slot(period_slot, period):
    rooms = courses.loc[period_slot[DAYS[0]]]["Rooms"]
    for room in rooms:
        for day in period_slot.keys():
            room_periods = Occupied.rooms[room][day]

            if period not in room_periods.keys():
                debug("room", room, "not available at:", period, day, "for")
                break

            if room_periods[period] != None:
                debug("room", room, "being used at:", period, day, "for")
                break
        else:
            return room
    return None


def find_period(open_slots, period_slot, section, grade):
    for period in open_slots:
        room = find_room_for_slot(period_slot, period)
        if not room:
            continue

        if not test_slot(period_slot, period):
            continue

        for day, course_name in period_slot.items():
            course = courses.loc[course_name]
            occupy_course(
                period,
                course,
                room,
                day,
                course_name,
                section,
                grade,
            )
        open_slots.remove(period)

        debug("put", course_name, "in", room, period)
        return

    return ValueError("couldn't find period")


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
                if period_slot == {day: None for day in DAYS}:  # null slot
                    continue

                same_class_everyday = len(set(period_slot.values())) == 1
                if same_class_everyday:
                    find_period(open_slots, period_slot, section, grade)
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

                debug("ADDED ", courses_to_add[0][-3], " AT ", period)


def fits_requirements(period, course, room_name, day, section, grade):
    """Check if a configuration of a course fits all the requirements."""
    room_periods = Occupied.rooms[room_name][day]

    if period not in room_periods.keys():
        debug("room", room_name, "not available at:", period, day, "for", course.name)
        return False

    if room_periods[period] != None:
        debug("room", room_name, "being used at:", period, day, "for", course.name)
        return False

    return True


def find_room_configuration(course, day, course_name, section, period, grade):
    for possible_room in course["Rooms"]:
        if fits_requirements(period, course, possible_room, day, section, grade):
            return period, course, possible_room, day, course_name, section, grade

    debug("room not found for", course_name)
    return False
