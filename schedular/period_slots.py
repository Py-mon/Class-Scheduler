import pandas as pd

from schedular.data import DAYS, PERIODS_RANGE, courses, grades
from schedular.logger import debug


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
        x = course["Sections"]
        if course["Same"]:
            x = course["Sections"][0]
        for section in x:
            grade = course["Grades"][0]
            # for grade in course["Grades"]:
            index = get_open_index(period_slots[grade][section], course["Days"])
            for day in course["Days"]:
                period_slots[grade][section][index][day] = course_name  # type: ignore

    string = ""
    for Grade, _ in period_slots.items():
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day)) # type: ignore
            for key, day in period_slots[Grade].items()
        }.items():
            string += key + "\n"
            string += grade + "\n\n"

    debug("\n" + str(string))

    return period_slots
