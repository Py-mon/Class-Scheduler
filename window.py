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
        self, title: str, headers: list[str]
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

    def add_column_entries(self, objs: list[tuple[Any, dict[str, Any]]]):
        self.table = []

        # self.var = []  # {i: "" for i in range(len(objs))}
        self.var = tk.Variable()

        def add_row():
            print(len(self.table))
            rows = []
            for i, (cls, kwargs) in enumerate(objs):

                if kwargs.get("textvariable"):

                    def callback(a):
                        print(a.get())
                        self.var.set(a.get())

                    sv = tk.StringVar()
                    sv.trace_add("write", lambda name, index, mode, sv=sv: callback(sv))
                    del kwargs["textvariable"]
                    x = True

                obj = cls(self.table_entry, **kwargs)
                try:
                    obj.values = ["BYE"]
                except:
                    pass
                obj.grid(row=len(self.table) + 1, column=i)
                rows.append(obj)
            self.table.append(rows)
            print(self.table)

        def add():
            print("added")
            add_row()

            add_row_button.grid_forget()
            add_row_button.grid(row=len(self.table) + 1, column=0, pady=5)

            remove_row_button.grid_forget()
            remove_row_button.grid(row=len(self.table) + 1, column=1, pady=5)

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

        remove_row_button = tk.CTkButton(
            self.table_entry, width=22, height=22, text="-", command=remove
        )
        remove_row_button.grid(row=len(self.table) + 1, column=1, pady=5)

        self.table_entry.pack()


# will you enter an amount of periods? will there be
#

rooms = TableEntry("Rooms", ["Name", "Availability"])
rooms.add_column_entries(
    [
        (tk.CTkEntry, {"width": 100}),
        (tk.CTkEntry, {"width": 100}),
    ]
)
rooms2 = TableEntry("Rooms", ["Name", "Availability"])


def f(s):
    print(rooms.var)


x = ["hi"]
# do x = combobox(...);-- not copy tho rooms2.add(x)
rooms2.add_column_entries(
    [
        (tk.CTkEntry, {"width": 100}),
        (
            tk.CTkComboBox,
            {"width": 100, "values": x, "command": f, "variable": rooms.var},
        ),
    ]
)
rooms2 = TableEntry("Rooms", ["Name", "Availability"])

x.append("bye")

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
