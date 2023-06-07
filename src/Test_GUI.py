import tkinter as tk
import Game_Render
import matplotlib
import Image_Frame
import Equilibrium
import itertools
import os
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import ImageTk, Image


class GUI:
    def __init__(self):
        self.name = 'new_test'
        self.game = Equilibrium.Game(self.name)
        self.window = tk.Tk()
        self.window.geometry('1600x800')

        self.tree_frame = None
        self.tk_image = None
        self.output_text = None
        self.canvas = None
        self.left_b1 = None
        self.right_b2 = None
        self.game_image = None
        self.tree = None
        self.admissible = None

        self.viacomp = None
        self.plateau_keys = []

        self.treeview_output()
        self.add_buttons()
        self.create_scrollable_image(self.name)
        self.window.columnconfigure(0, weight=1)

        self.game_loop()
        self.window.mainloop()

    def create_scrollable_image(self, game_id: str):
        del self.game_image
        file_path = f'graph-renders/{game_id}.gv.png'
        self.game_image = Image_Frame.MainWindow(self.window, file_path)

    def add_buttons(self):
        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=2, column=0)

        self.left_b1 = tk.Button(button_frame, text="Button 1")
        self.left_b1.grid(row=0, column=0, padx=5, pady=5)

        self.right_b2 = tk.Button(button_frame, text="Continue", command=self.step_viable)
        self.right_b2.grid(row=0, column=1, padx=5, pady=5)

    def treeview_output(self, new_headings=None, new_values=None):
        if new_values is None:
            new_values = []
        if new_headings is None:
            new_headings = ['']
        if self.tree_frame is not None:
            self.tree_frame.destroy()

        self.tree_frame = ttk.Frame(self.window)
        self.tree_frame.grid(row=1, column=0, sticky="n")

        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 10))
        style.configure("Custom.Treeview.Heading", font=("Arial", 11, "bold"))

        # Create and grid the treeview widget with the desired width
        self.tree = ttk.Treeview(self.tree_frame, columns=new_headings, show="headings", style="Custom.Treeview")
        self.tree.grid(row=0, column=0, sticky="n")

        # Create and grid the horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Create and grid the vertical scrollbar
        y_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure the treeview to use the scrollbars
        self.tree.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        for i, heading in enumerate(new_headings):
            self.tree.heading("#" + str(i + 1), text=heading)
        for value in new_values:
            self.tree.insert("", tk.END, values=value)

    def game_loop(self):
        alpha = self.game.get_alpha_dict()

        headings = ['State', '\u03B1']
        values = [(str(state), str(alpha[state])) for state in alpha]

        self.treeview_output(headings, values)

    def step_viable(self):
        viable = self.game.get_viable_plans()

        headings = [f'State: {state}' for state in viable]
        values = build_dict_values_list(viable)

        self.treeview_output(headings, values)
        self.right_b2.configure(text="Continue", command=self.step_alpha_plateaus)

    def step_alpha_plateaus(self):
        alpha_plateau = self.game.get_alpha_plateaus()

        headings = [f'{key}' for key in alpha_plateau]
        values = build_dict_values_list(alpha_plateau)

        self.treeview_output(headings, values)
        self.left_b1.configure(text="Back", command=self.step_alpha_plateaus)
        self.right_b2.configure(text="Continue", command=self.step_U_compatible)

    def step_U_compatible(self):
        U_comp = self.game.get_U_compatible()

        headings = [f'{key}' for key in U_comp]
        values = build_dict_values_list(U_comp)
        self.treeview_output(headings, values)

        safe_file_name = f'safe_steps_{self.name}'
        Game_Render.render_safe_steps(self.game.game, U_comp, safe_file_name)
        self.create_scrollable_image(safe_file_name)

        self.left_b1.configure(text="Back", command=self.step_U_compatible)
        self.right_b2.configure(text="Continue", command=self.step_viacomp)

    def step_viacomp(self):
        self.viacomp = self.game.get_viable_compatible()

        self.treeview_output(*build_nested_dict(self.viacomp, 'Viacomp'))
        self.left_b1.configure(text="Back", command=self.step_U_compatible)
        self.right_b2.configure(text="Continue", command=self.step_admissible)

    def step_admissible(self):
        self.admissible = self.game.get_admissible()
        self.treeview_output(*build_nested_dict(self.admissible, 'Admissible'))
        self.left_b1.configure(text="Back", command=self.step_viacomp)
        self.right_b2.configure(text="Continue", command=self.step_beta)

    def step_beta(self):
        self.beta = self.game.get_beta()

        print(self.beta)


def build_nested_dict(main_dict, title='', beta=False):
    headings = []
    all_values = []

    for key in main_dict:
        headings.append(f'{key} \u2192 {title}')
        current_values = []
        for plateau in main_dict[key]:
            if beta:
                current_values.extend(plateau)
                continue
            current_values.extend(build_list_values(plateau))
        all_values.append(current_values)

    values = build_all_values(all_values)

    return headings, values


def build_all_values(all_values: list):
    values = []

    for index in range(max(len(lst) for lst in all_values)):
        row = []
        for lst in all_values:
            row.append(str(list_get(lst, index)))
        values.append(tuple(row))

    return values

def build_beta_values(beta_plateau):

    row = []
    for state in beta_plateau:



def build_list_values(plateau):
    values = [f'F={list(plateau.keys())}']

    for key in plateau:
        for plan in plateau[key]:
            values.append(f'{key}={plan}')
    values.append('\n')

    return values


def build_dict_values_list(dictionary: dict):
    all_lists = [dictionary[key] for key in dictionary]
    max_length = max(len(lst) for lst in all_lists)
    values = []

    for index in range(max_length):
        row = []
        for lst in all_lists:
            row.append(str(list_get(lst, index)))
        values.append(tuple(row))

    return values


def list_get(lst, index):
    return lst[index] if index < len(lst) else ''


def build_dict_list_str(dictionary: dict, output=None):
    if output is None:
        output = ''
    dictionary.keys()
    for key in dictionary:
        output += f'\nViacomp({key}, U, \u03B1) \u2192 \n'
        for item in dictionary[key]:
            output += f'{item}\n'

    return output


if __name__ == "__main__":
    GUI()
