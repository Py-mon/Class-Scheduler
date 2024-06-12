from typing import Any

import schedular.data as data
from schedular.data import grades, rooms, teachers


def create_occupy_table(iter) -> dict[str, dict[Any, dict[int, Any]]]:
    # [name][day][period] -> course
    return {
        name: {
            day: {int(period): None for period in value["Periods"]} for day in data.DAYS
        }
        for name, value in iter
    }


def generate_occupy_tables():
    Occupied.rooms = create_occupy_table(rooms.iterrows())

    Occupied.teachers = create_occupy_table(teachers.iterrows())

    # [grade][section][day][period] -> course
    Occupied.grades = {
        name: {
            section: {
                day: {int(period): None for period in data.PERIODS_RANGE}
                for day in data.DAYS
            }
            for section in grade["Sections"]
        }
        for name, grade in grades.iterrows()
    }


class Occupied:
    teachers = {}
    rooms = {}
    grades = {}


def occupy_course(
    period: int,
    course,
    room_name: str,
    day: str,
    course_name: str,
    section: str,
    grade: int,
):
    """Put the course in the occupied dictionaries."""

    Occupied.teachers[course["Teacher"]][day][period] = course_name

    Occupied.rooms[room_name][day][period] = course_name

    Occupied.grades[grade][section][day][period] = course_name
