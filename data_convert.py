
def section_number_to_letter(number):
    """
    Get a letter from a section number.

    ```
    0 -> A
    1 -> B
    3 -> C
    """
    return ascii_uppercase[number]


def get_list(string):
    """
    Take a string and convert it to a python list.
    ```
    "1,2,3" -> ["1", "2", "3"]
    "5, 7, 1" -> ["5", "7", "1"]"""
    return tuple(s.strip() for s in str(string).split(","))


def get_periods(string):
    if string.lower() == "all":
        return PERIODS_RANGE
    return tuple(int(x) for x in get_list(string))


def get_days(string):
    if string.lower() == "all":
        return DAYS
    return tuple(x.lower() for x in get_list(string))


def get_grades(string):
    if not isinstance(string, int) and string.lower() == "all":
        return GRADES
    return tuple(int(x) for x in get_list(string))


def intersection(*x):
    return set.intersection(*map(set, x))


def precalculate_data():
    courses.insert(
        len(courses.columns), "Periods", [None for _ in range(len(courses))], True
    )
    courses.insert(
        len(courses.columns), "Rooms", [None for _ in range(len(courses))], True
    )
    courses.insert(
        len(courses.columns), "Same", [None for _ in range(len(courses))], True
    )

    for name, teacher in teachers.iterrows():
        teachers["Periods"][name] = get_periods(teacher["Periods"])

    for name, room in rooms.iterrows():
        rooms["Periods"][name] = get_periods(room["Periods"])

    for name, grade in grades.iterrows():
        new_sections = []
        for section in range(grade["Sections"]):
            letter = section_number_to_letter(section)
            new_sections.append(letter)
        grades["Sections"][name] = new_sections

    for course_name, course in courses.iterrows():
        courses["Grades"][course_name] = get_grades(course["Grades"])

        # Convert int "Sections" (2) to ["A", "B", ...]
        sections = course["Sections"]
        if isinstance(sections, float):
            courses["Sections"][course_name] = grades["Sections"][course["Grades"][0]]
        elif sections == "Same":
            courses["Sections"][course_name] = ["A", "B"]  #
            courses["Same"][course_name] = True
        else:
            courses["Sections"][course_name] = get_list(sections)

        courses["Days"][course_name] = get_days(course["Days"])

        courses["Periods"][course_name] = intersection(
            set(MORNING_RANGE if course["Type"] == "Core" else AFTERNOON_RANGE),
            teachers.loc[course["Teacher"]]["Periods"],
        )
        if course["Room Type"] in rooms["Type"].values:
            possible_rooms = rooms.loc[rooms["Type"] == course["Room Type"]]
            courses["Rooms"][course_name] = tuple(possible_rooms.index)
        elif str(course["Room Type"]).lower() == "any":
            courses["Rooms"][course_name] = tuple(rooms.index)
        elif course["Room Type"] in rooms.index:
            courses["Rooms"][course_name] = (course["Room Type"],)
        else:
            raise ValueError("UNKNOWN ROOM TYPE", course["Room Type"])
