from enum import Enum
import datetime
from typing import Optional, Callable, Any
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

import customtkinter as tk

root = tk.CTk()

WIDTH, HEIGHT = 300, 500
root.geometry(f"{WIDTH}x{HEIGHT}")

frame = tk.CTkScrollableFrame(
    root,
    width=WIDTH,
    height=HEIGHT - 50,
)

frame._scrollbar.configure(height=0)


large = tk.CTkFont(size=18)


class Entry:
    def __init__(self, label: str):
        global rows

        tk.CTkLabel(frame, text=label).pack()

        self.entry = tk.CTkEntry(frame, width=70)

        self.entry.pack()


starting_school_time = Entry("Starting School Time")
ending_school_time = Entry("Ending School Time")


class TableEntry:
    def __init__(
        self, title: str, headers: dict[str, tuple[Any, dict[str, Any]]]
    ):  # make headers dict for nay entry type

        tk.CTkLabel(frame, text=title, font=large).pack()
        self.table_entry = tk.CTkScrollableFrame(
            frame,
            fg_color="gray14",
            width=400,
            height=75,
        )
        self.table_entry.grid_anchor("center")

        self.table_entry._scrollbar.configure(height=0)

        for i, header in enumerate(headers):
            tk.CTkLabel(self.table_entry, text=header).grid(row=0, column=i)

        self.table = []

        def add_row():
            rows = []
            for i, obj in enumerate(headers.values()):
                row = obj[0](
                    self.table_entry, **obj[1]
                )  # tk.CTkEntry(self.table_entry, width=100)
                row.grid(row=len(self.table) + 1, column=i)
                rows.append(row)
            self.table.append(rows)

        def add():
            add_row()

            add_row_button.grid_forget()
            add_row_button.grid(row=len(self.table) + 1, column=0)

            remove_row_button.grid_forget()
            remove_row_button.grid(row=len(self.table) + 1, column=1)

        add_row_button = tk.CTkButton(self.table_entry, width=28, text="+", command=add)
        add_row()
        add_row_button.grid(row=len(self.table) + 1, column=0)

        def remove():
            if len(self.table) <= 1:
                return

            for i in self.table[-1]:
                i.grid_forget()
                i.destroy()
            self.table.pop()

        remove_row_button = tk.CTkButton(
            self.table_entry, width=28, text="-", command=remove
        )
        remove_row_button.grid(row=len(self.table) + 1, column=1)

        self.table_entry.pack()

# will you enter an amount of periods? will there be 
#
TableEntry(
    "Rooms",
    {
        "Name": (tk.CTkEntry, {"width": 100}),
        "Availability": (tk.CTkEntry, {"width": 100}),
    },
)
TableEntry(
    "Teachers",
    {
        "Name": (tk.CTkEntry, {"width": 100}),
        "Availability": (tk.CTkEntry, {"width": 100}),
    },
)

# TODO SAVING


# tk.CTkTextbox(root).pack()

# tk.CTkEntry(root).pack()
# tk.CTkCheckBox(root, text="Checkbox").pack()
# tk.CTkComboBox(root, values=["Option1", "Option2"]).pack()
# tk.CTkSlider(root).pack()
# tk.CTkScrollableFrame(root).pack()
# tk.CTkSwitch(root, text="Switch").pack()
frame.pack()
root.mainloop()


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
