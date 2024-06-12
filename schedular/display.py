import pandas as pd
from schedular.data import grades


def get_slots():
    string = "\n"
    for Grade, _ in grades.iterrows():
        for key, grade in {
            key: str(pd.DataFrame.from_dict(day))
            for key, day in period_slots[int(Grade)].items()
        }.items():
            string += key + "\n"
            string += grade + "\n\n"
    return string


def display(occupied):
    for key, grade in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in occupied.items()
    }.items():
        print(key)
        print(grade)
        print()
