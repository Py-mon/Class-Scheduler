from time import time

from schedular.data_convert import convert_data
from schedular.display import display
from schedular.occupy_courses import do
from schedular.occupy_tables import Occupied, generate_occupy_tables
from schedular.period_slots import calculate_period_slots


def main():
    convert_data()

    period_slots = calculate_period_slots()
    p = [
        (section, period_slots_, grade)
        for grade, sections in period_slots.items()  # * knows the grade here
        for section, period_slots_ in sections.items()
    ]
    generate_occupy_tables()

    start = time()
    do(period_slots)
    print(time() - start)

    for x in [7, 8, 9]:
        display(Occupied.grades[x], x)

    # display(Occupied.rooms)
    # display(Occupied.teachers)


# print steps
if __name__ == "__main__":
    main()
