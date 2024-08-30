import pandas as pd

from schedular.data import grades
from schedular.logger import debug
from schedular.occupy_tables import Occupied


def display(occupied, key1):
    for key, grade in {
        key: str(pd.DataFrame.from_dict(day)) for key, day in occupied.items()
    }.items():
        print(str(key1) + str(key))
        print(grade)
        print()


def debug2():
    for x in [7, 8, 9]:
        for key, grade_ in {
            key: str(pd.DataFrame.from_dict(day))
            for key, day in Occupied.grades[x].items()
        }.items():
            debug(key)
            debug(grade_)
        # for key, grade_ in {
        #     key: str(pd.DataFrame.from_dict(day)) for key, day in Occupied.rooms.items()
        # }.items():
        #     debug(key)
        #     debug(grade_)
