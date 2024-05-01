# import customtkinter

# root = customtkinter.CTk()
# root.geometry("800x300")
# customtkinter.CTkEntry(root).pack()
# customtkinter.CTkCheckBox(root, text="Checkbox").pack()
# customtkinter.CTkComboBox(root, values=["Option1", "Option2"]).pack()
# customtkinter.CTkSlider(root).pack()
# customtkinter.CTkScrollableFrame(root).pack()
# customtkinter.CTkSwitch(root, text="Switch").pack()
# root.mainloop()
from enum import Enum
import datetime
from typing import Optional, Callable, Any
import random
import copy
import customtkinter as tk


root = tk.CTk()

WIDTH, HEIGHT = 300, 500
root.geometry(f"{WIDTH}x{HEIGHT}")
# root.tk.call('tk', 'scaling', 8.0)

frame = tk.CTkScrollableFrame(
    root,
    width=WIDTH,
    height=HEIGHT,
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


# def clone(widget: tk.CTkBaseClass):
#     parent = widget.nametowidget(widget.winfo_parent())
#     cls = widget.__class__

#     print(cls, parent)

#     clone = cls(parent)
#     for key in widget.
#         print(key)
#         try:
#             clone.configure(**{key: widget.cget(key)})
#         except ValueError:
#             continue
#     return clone


class TableEntry:
    def __init__(
        self,
        title: str,
        headers: list[str],
        remove_callback: list[Optional[Callable[[], Any]]] = None,
    ):  # make headers dict for nay entry type
        self.title = title
        self.table_entry = tk.CTkScrollableFrame(
            frame,
            fg_color="gray14",
            width=400,
            height=75,
        )
        self.table_entry.grid_anchor("center")

        self.table_entry._scrollbar.configure(height=0)

        self.headers = headers

    def pack(self):
        tk.CTkLabel(frame, text=self.title, font=large).pack()

        for i, header in enumerate(self.headers):
            tk.CTkLabel(self.table_entry, text=header).grid(row=0, column=i)

        self.table_entry.pack()

    def add_column_entries(
        self,
        objs: list[tuple[Any, dict[str, Any]]],
        remove_callback: Optional[Callable[[], Any]] = None,
        add_callbacks: Optional[Callable[[], Any]] = None,
    ):
        self.table = []

        def add_row():
            rows = []
            for i, (cls, kwargs) in enumerate(objs):
                real_kwargs = kwargs.copy()

                if kwargs.get("write_callback"):
                    real_kwargs["textvariable"] = tk.StringVar()
                    real_kwargs["textvariable"].trace_add(
                        "write", kwargs["write_callback"]
                    )
                    del real_kwargs["write_callback"]

                obj = cls(self.table_entry, **real_kwargs)
                obj.grid(row=len(self.table) + 1, column=i)
                rows.append(obj)
            self.table.append(rows)

        def add():
            print("added")
            add_row()

            add_row_button.grid_forget()
            add_row_button.grid(row=len(self.table) + 1, column=0, pady=5)

            remove_row_button.grid_forget()
            remove_row_button.grid(row=len(self.table) + 1, column=1, pady=5)

            if add_callbacks:
                for callback in add_callbacks:
                    callback()

        add_row_button = tk.CTkButton(
            self.table_entry, width=22, height=22, text="+", command=add
        )
        add_row()
        add_row_button.grid(row=len(self.table) + 1, column=0, pady=5)

        def remove():
            if len(self.table) <= 1:
                return

            for i in self.table[-1]:
                i.grid_forget()
                i.destroy()
            self.table.pop()

            if remove_callback:
                remove_callback()

        remove_row_button = tk.CTkButton(
            self.table_entry, width=22, height=22, text="-", command=remove
        )
        remove_row_button.grid(row=len(self.table) + 1, column=1, pady=5)

    def create_option_menu_link_callback(self, column, entry_table):
        def f(*args):
            entries = [row[column] for row in self.table]
            # print(entries)
            for entry in entries:

                #tk.CTkOptionMenu()._dropdown_menu._add_menu_commands

                entry._dropdown_menu._values = entry_table.get_column_entries(0)
                entry._dropdown_menu.delete(0, 'end')
                for v in entry._dropdown_menu._values:
                    entry._dropdown_menu.add_checkbutton( # check box
                        label=v,
                        # variable=self.choices[choice],
                        # onvalue=1,
                        # offvalue=0,
                        command=lambda : print('add'),
                    )
                #entry._dropdown_menu._add_menu_commands()
                
                #tk.CTkCheckBox(entry._dropdown_menu).grid(row=0, column=0)

                # if column == 2:
                #     entry._dropdown_menu.insert_checkbutton(0)

        return f

    def get_column_entries(self, column):
        return [row[column].get() for row in self.table]


# will you enter an amount of periods? will there be
#


# make pack later and combine aadd column entries
courses = TableEntry("Courses", ["Name", "Teacher", "Rooms"])
teachers = TableEntry("Teachers", ["Name", "Availability"])
rooms = TableEntry("Rooms", ["Name", "Availability"])

update_courses = courses.create_option_menu_link_callback(1, teachers)
teachers.add_column_entries(
    [
        (tk.CTkEntry, {"width": 100, "write_callback": update_courses}),
        (tk.CTkEntry, {"width": 100}),
    ],
    update_courses,
)

update_rooms = courses.create_option_menu_link_callback(2, rooms)
rooms.add_column_entries(
    [
        (tk.CTkEntry, {"width": 100, "write_callback": update_rooms}),
        (tk.CTkEntry, {"width": 100}),
    ],
    update_rooms,
)
courses.add_column_entries(
    [
        (tk.CTkEntry, {"width": 100}),
        (
            tk.CTkOptionMenu,
            {
                "width": 100,
                "values": [""],
            },
        ),
        (
            tk.CTkOptionMenu,
            {
                "width": 100,
                "values": [""],
            },
        ),
    ],
    add_callbacks=[update_courses, update_rooms],
)


rooms.pack()
teachers.pack()
courses.pack()

# def f(s):
#     print("Hi")


# rooms.add_column_entries(
#     [
#         tk.CTkEntry(rooms.table_entry, width=100),
#         tk.CTkComboBox(rooms.table_entry, width=100, values=["in", "out"], command=f),
#     ]
# )


#     "Rooms",
#     {
#         "Name": (tk.CTkEntry, {"width": 100}),
#         "Availability": (tk.CTkEntry, {"width": 100}),
#     },
# )
# teachers = TableEntry(
#     "Teachers",
#     {
#         "Name": (tk.CTkEntry, {"width": 100}),
#         "Availability": (tk.CTkEntry, {"width": 100}),
#     },
# )
# print([""] + teachers.names)
# sv = StringVar()
# sv.trace("w", lambda name, index, mode, sv=sv: callback(sv))


# def f3(v):
#     for x in teachers.table:
#         v.x[0]


# TableEntry(
#     "Courses",
#     {
#         "Name": (tk.CTkEntry, {"width": 100}),
#         "Teacher": (tk.CTkComboBox, {"command": f3}),
#     },
# )
frame.pack()
root.mainloop()
