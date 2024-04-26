from enum import Enum
import datetime
from typing import Optional, Callable
import random

class Weekdays(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4


ALL_WEEK_DAYS = [
    Weekdays.Monday,
    Weekdays.Tuesday,
    Weekdays.Wednesday,
    Weekdays.Thursday,
    Weekdays.Friday,
]


class Availability(Enum):
    Morning = -1
    Anytime = 0
    Afternoon = 1


class CourseType(Enum):
    Core = 0
    Elective = 1


class Teacher:
    def __init__(self, name: str, availability: Availability):
        self.name = name
        self.availability = availability

        # prep period/break


class Room:
    def __init__(self, name: str):
        self.name = name
        # distance?


class Course:
    def __init__(
        self,
        name: str,
        room: Room,
        grade_prerequisite: Callable[[int], bool],
        type_: CourseType,
        teacher: Teacher,
        days: list[Weekdays],
    ):  # get time
        self.name = name
        self.room = room
        self.grade_prerequisite = grade_prerequisite
        self.type_ = type_
        self.teacher = teacher
        self.days = days
        
    def __repr__(self) -> str:
        return self.name


class Break:
    def __init__(self, name, duration) -> None:
        self.name = name
        self.duration = duration



# -----,.
# give teachers with minimal classes


class DoorDuty:
    pass  # get teacher and time


class LunchDuty:
    pass  # get teacher and time


class StudyHall:
    pass  # get teacher and time


# ----
# detention duty?

_format = "%I:%M%p"

STARTING_SCHOOL_TIME = datetime.datetime.strptime("8:20AM", _format)
ENDING_SCHOOL_TIME = datetime.datetime.strptime("3:05PM", _format)

Gym = Room("Gym")
a201 = Room("a201")
a202 = Room("a202")

Hawkinson = Teacher("Hawkinson", Availability.Anytime)
Stockman = Teacher("Stockman", Availability.Anytime)
Hanson = Teacher("Hanson", Availability.Afternoon)

Lunch = Break("Lunch", 30)
PassingTime = Break("PassingTime", 4)


def grade_prerequisite_equal_to(grade: int):
    def f(x):
        return x == grade

    return f


def grade_prerequisite_greater_than(grade: int):
    def f(x):
        return x > grade

    return f


Bible_10A = Course(
    "Bible 10A",
    a201,
    grade_prerequisite_equal_to(10),
    CourseType.Core,
    Hawkinson,
    ALL_WEEK_DAYS,
)
Bible_10B = Course(
    "Bible 10B",
    a201,
    grade_prerequisite_equal_to(10),
    CourseType.Core,
    Hawkinson,
    ALL_WEEK_DAYS,
)

# def get_period_length(breaks: list[Break], passing_time: int, periods: int):
#     passing_time = passing_time * (periods - 3) # 1, 2, 3, 4,   # -8
#     print(passing_time)
#     period_time = (ENDING_SCHOOL_TIME - STARTING_SCHOOL_TIME).total_seconds() / 60 - passing_time - 25
#     print(period_time / periods)

# get_period_length([Lunch], PassingTime.duration, 7)

PERIODS = 7

monday = []

courses_left = [Bible_10A, Bible_10B]

# Morning core classes
for course in courses_left:
    core_class = course.type_ == CourseType.Core
    teacher_available = course.teacher.availability != Availability.Afternoon
    on_monday = Weekdays.Monday in course.days
    if core_class and teacher_available and on_monday:
        monday.append(course)
        courses_left.remove(course)

for course in courses_left:
    # check if still in the morning
    if len(monday) > PERIODS // 2:
        teacher_available = course.teacher.availability != Availability.Afternoon
    else:
        teacher_available = course.teacher.availability != Availability.Morning
        
    on_monday = Weekdays.Monday in course.days
    if teacher_available and on_monday:
        monday.append(course)
        courses_left.remove(course)

print(monday)
