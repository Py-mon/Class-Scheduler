from enum import Enum
import datetime
from typing import Optional, Callable, Any, Self
import random
import copy
import customtkinter as tk


root = tk.CTk()

WIDTH, HEIGHT = 700, 500
root.geometry(f"{WIDTH}x{HEIGHT}")
# root.tk.call('tk', 'scaling', 8.0)

frame = tk.CTkScrollableFrame(
    root,
    width=WIDTH,
    height=HEIGHT * 50,
)

frame._scrollbar.configure(height=0)


large = tk.CTkFont(size=18)


class TextEntry:
    def __init__(self, label: str):
        tk.CTkLabel(frame, text=label).pack()

        self.entry = tk.CTkEntry(frame, width=70)

        self.entry.pack()


class Entry:
    def __init__(self, cls, multi=False, default_options=None, **kwargs) -> None:
        self.cls = cls
        self.kwargs = kwargs
        self.multi = multi
        self.default_options = default_options

        self.write_callbacks = []

    def create(self, parent):
        if self.write_callbacks:
            self.kwargs["textvariable"] = tk.StringVar()
            for callback in self.write_callbacks:
                self.kwargs["textvariable"].trace_add("write", callback)

        widget = self.cls(parent, **self.kwargs)
        if self.multi:
            widget._dropdown_menu.delete(0, "end")

            choices = {}
            widget.get = lambda: choices
            for v in self.multi:
                if self.default_options and v in self.default_options:
                    choices[v] = tk.IntVar(value=1)
                else:
                    choices[v] = tk.IntVar(value=0)

                widget._dropdown_menu.add_checkbutton(  # check box
                    label=v,
                    variable=choices[v],
                    onvalue=1,
                    offvalue=0,
                    selectcolor="white",
                )
        return widget


class TableEntry:
    def __init__(
        self,
        title: str,
        table_row: dict[str, Entry],
    ):  # make headers dict for nay entry type
        self.title = title
        self.frame = tk.CTkScrollableFrame(
            frame,
            fg_color="gray14",
            width=0,
            height=100,
        )
        self.frame.grid_anchor("center")

        self.frame._scrollbar.configure(height=0)

        self.table_row = table_row

        self.remove_row_callbacks = []
        self.add_row_callbacks = []

    def pack(self):
        self.table = []

        def add_row():
            rows = []
            for i, entry in enumerate(self.table_row.values()):
                obj = entry.create(self.frame)
                obj.grid(row=len(self.table) + 1, column=i + 1, pady=2, padx=2)
                rows.append(obj)
            self.table.append(rows)

        def update():
            add_row_button.grid_forget()
            add_row_button.grid(row=len(self.table) + 1, column=0, padx=5, pady=5)

            remove_row_button.grid_forget()

            if len(self.table) > 1:
                remove_row_button.grid(row=len(self.table), column=0, padx=5, pady=5)

        def add():
            add_row()
            update()

            if self.add_row_callbacks:
                for callback in self.add_row_callbacks:
                    callback()

        add_row_button = tk.CTkButton(
            self.frame, width=20, height=20, text="+", command=add
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

            update()

            if self.remove_row_callbacks:
                for callback in self.remove_row_callbacks:
                    callback()

        remove_row_button = tk.CTkButton(
            self.frame, width=20, height=20, text="-", command=remove
        )
        # remove_row_button.grid(row=len(self.table), column=0, pady=5)
        tk.CTkLabel(frame, text=self.title, font=large).pack()

        for i, header in enumerate(self.table_row.keys()):
            tk.CTkLabel(self.frame, text=header).grid(row=0, column=i + 1)

        remove_row_button.grid_forget()
        self.frame.pack(expand=False, fill="both")

    def _update_menu(self, entry):

        entry._dropdown_menu._add_menu_commands()

    def _multi_select(self, entry):
        entry._dropdown_menu.delete(0, "end")

        choices = {}
        entry.get = lambda: choices
        for v in entry._dropdown_menu._values:

            choices[v] = tk.IntVar(value=0)

            entry._dropdown_menu.add_checkbutton(  # check box
                label=v,
                variable=choices[v],
                onvalue=1,
                offvalue=0,
                selectcolor="white",
            )
            # entry._text_label.configure(text='HI')

    def link_to_entry_column(
        self,
        column: str,
        entry_column: str,
        entry_table: Self,
        multi_select: bool = False,
    ):
        def update_menu(*args):
            entries = [
                row[list(self.table_row.keys()).index(column)] for row in self.table
            ]
            for entry in entries:
                entry._dropdown_menu._values = entry_table.get_column_entries(
                    entry_column
                )

                if multi_select:
                    self._multi_select(entry)
                else:
                    self._update_menu(entry)

        entry_table.table_row[entry_column].write_callbacks.append(update_menu)
        entry_table.remove_row_callbacks.append(update_menu)
        entry_table.add_row_callbacks.append(update_menu)
        
        self.remove_row_callbacks.append(update_menu)
        self.add_row_callbacks.append(update_menu)

    def get_column_entries(self, column):
        return [
            row[list(self.table_row.keys()).index(column)].get() for row in self.table
        ]


starting_school_time = TextEntry("Starting School Time")
ending_school_time = TextEntry("Ending School Time")
max_hours_before_prep = TextEntry("Max Hours Before Prep")
passing_time = TextEntry("Passing Time")

BASIC_ENTRY = Entry(tk.CTkEntry, width=100)
SMALL_ENTRY = Entry(tk.CTkEntry, width=70)

create_multi_menu = lambda options, default: Entry(
    tk.CTkOptionMenu,
    multi=options,
    default_options=default,
    width=0,
    values=[""],
)
PERIOD = create_multi_menu(
    [
        "1st Period",
        "2nd Period",
        "3rd Period",
        "4th Period",
        "5th Period",
        "6th Period",
        "7th Period",
    ],
    [
        "1st Period",
        "2nd Period",
        "3rd Period",
        "4th Period",
        "5th Period",
        "6th Period",
        "7th Period",
    ],
)

courses = TableEntry(
    "Courses",
    {
        "Name": BASIC_ENTRY,
        "Teacher": Entry(tk.CTkOptionMenu, width=100, values=[""]),
        "Rooms": Entry(tk.CTkOptionMenu, width=0, values=[""]),
        "Days": create_multi_menu(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        ),
    },
)

teachers = TableEntry(
    "Teachers",
    {
        "Name": BASIC_ENTRY,
        "Availability": PERIOD,
    },
)
rooms = TableEntry(
    "Rooms",
    {
        "Name": BASIC_ENTRY,
        "Availability": PERIOD,
    },
)

courses.link_to_entry_column("Teacher", "Name", teachers)
courses.link_to_entry_column("Rooms", "Name", rooms, multi_select=True)

breaks = TableEntry(
    "Breaks", {"Name": BASIC_ENTRY, "Start": SMALL_ENTRY, "End": SMALL_ENTRY}
)


rooms.pack()
teachers.pack()
courses.pack()
breaks.pack()

frame.pack()

button = tk.CTkFrame(frame, width=200, height=30, fg_color="gray14")


tk.CTkLabel(button, text="Made by Jacob Ophoven").pack()
# tk.CTkLabel(button, text="Availability Syntax Examples: 8:55AM-9:21AM").pack()
# tk.CTkLabel(button, text="Time Syntax Examples: 8:55AM").pack()
button.pack_propagate(0)

button.pack(pady=10)
root.title("Scheduler")
root.mainloop()

# undo, save?
