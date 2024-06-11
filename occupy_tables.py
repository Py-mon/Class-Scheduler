
def create_occupy_table(iter) -> dict[str, dict[Any, dict[int, Any]]]:
    return {
        name: {day: {int(period): None for period in value["Periods"]} for day in DAYS}
        for name, value in iter
    }


def generate_occupy_tables():
    rooms_occupied = create_occupy_table(rooms.iterrows())

    teachers_occupied = create_occupy_table(
        teachers.iterrows()
    )  # name day period - course

    grades_occupied = {
        name: {
            section: {
                day: {int(period): None for period in PERIODS_RANGE} for day in DAYS
            }
            for section in grade["Sections"]
        }
        for name, grade in grades.iterrows()
    }
    # grade section day period - course
    return rooms_occupied, teachers_occupied, grades_occupied

def occupy_course(period, course, room_name, day, course_name, section, grade):
    """Put the course in the occupied dictionaries."""
    teachers_occupied[course["Teacher"]][day][period] = (course_name, section, grade)

    rooms_occupied[room_name][day][period] = (course_name, section, grade)

    # for grade in course["Grades"]: # * reason for Nones
    #     debug(grade, course_name, section, period, day)
    #     #
    grades_occupied[grade][section][day][period] = course_name