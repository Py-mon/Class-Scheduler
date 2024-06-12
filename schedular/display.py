import pandas as pd

from schedular.data import grades
from schedular.logger import debug
from schedular.occupy_tables import Occupied


def display(occupied):
    for key, grade in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in occupied.items()
    }.items():
        print(key)
        print(grade)
        print()


def debug2():
    for key, grade_ in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in Occupied.grades[8].items()
    }.items():
        debug(key)
        debug(grade_)
    for key, grade_ in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in Occupied.grades[7].items()
    }.items():
        debug(key)
        debug(grade_)
