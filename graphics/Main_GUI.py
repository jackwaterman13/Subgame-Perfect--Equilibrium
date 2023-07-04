from itertools import zip_longest
from .Image_Frame import *
from .Game_Render import *


class GUI:
    def __init__(self, game):
        self.name = 'new_test'
        self.game = game
        render_game(self.game.game, self.name)

        self.window = tk.Tk()
        self.window.geometry('1600x800')

        self.itr_num = None
        self.tree_frame = None
        self.tk_image = None
        self.output_text = None
        self.canvas = None
        self.left_b1 = None
        self.right_b2 = None
        self.game_image = None
        self.tree = None
        self.admissible = None
        self.converged = None

        self.viacomp = None
        self.plateau_keys = []

        self.treeview_output()
        self.add_buttons()
        self.create_scrollable_image(self.name)
        self.window.columnconfigure(0, weight=1)

        self.start_game_loop()
        self.window.mainloop()

    def create_scrollable_image(self, game_id: str):
        del self.game_image
        file_path = f'graph-renders/{game_id}.gv.png'
        self.game_image = MainWindow(self.window, file_path)

    def add_buttons(self):
        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=2, column=0)

        self.left_b1 = tk.Button(button_frame, text="Button 1")
        self.left_b1.grid(row=0, column=0, padx=5, pady=5)

        self.right_b2 = tk.Button(button_frame, text="Continue", command=self.iteration)
        self.right_b2.grid(row=0, column=1, padx=5, pady=5)

    def treeview_output(self, new_headings=None, new_values=None, title=''):
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

        super_heading_label = ttk.Label(self.tree_frame, text=title, style="Custom.Treeview.Heading",
                                        justify='center')
        super_heading_label.grid(row=0, column=0, columnspan=len(new_headings))

        # Create and grid the treeview widget with the desired width
        self.tree = ttk.Treeview(self.tree_frame, columns=new_headings, show="headings", style="Custom.Treeview")
        self.tree.grid(row=1, column=0, sticky="n")

        # Create and grid the horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        x_scrollbar.grid(row=2, column=0, sticky="ew")

        # Create and grid the vertical scrollbar
        y_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        y_scrollbar.grid(row=1, column=1, sticky="ns")

        # Configure the treeview to use the scrollbars
        self.tree.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        for i, heading in enumerate(new_headings):
            self.tree.heading("#" + str(i + 1), text=heading)

        if len(new_headings) == 1:
            self.tree.column("#0", width=200)

        for value in new_values:
            self.tree.insert("", tk.END, values=value)

    def start_game_loop(self):

        self.itr_num = 1
        self.converged = False
        self.step_alpha()

    def iteration(self):

        if self.converged:
            self.step_alpha(f'Final Alpha')
        else:
            self.right_b2.configure(text="Continue", command=self.step_viable())

    def step_alpha(self, title='Alpha Vector'):
        alpha = self.game.get_alpha_dict()

        headings = ['State', '\u03B1']
        values = [(str(state), str(alpha[state])) for state in alpha]
        self.treeview_output(headings, values, title)

    def step_viable(self):
        viable = self.game.get_viable_plans()

        headings = [f'State: {state}' for state in viable]
        values = build_dict_values_list(viable)

        self.treeview_output(headings, values, 'Viable Plans')
        self.left_b1.configure(text="Back", command=self.step_alpha)
        self.right_b2.configure(text="Continue", command=self.step_alpha_plateaus)

    def step_alpha_plateaus(self):
        alpha_plateau = self.game.get_alpha_plateaus()

        headings = [f'{key}' for key in alpha_plateau]
        values = []

        all_states = [plateau.states for plateau in alpha_plateau]
        max_length = max(len(lst) for lst in all_states)

        for index in range(max_length):
            row = []
            for lst in all_states:
                row.append(str(list_get(lst, index)))
            values.append(tuple(row))

        self.treeview_output(headings, values, 'Alpha Plateaus')
        self.left_b1.configure(text="Back", command=self.step_viable)
        self.right_b2.configure(text="Continue", command=self.step_U_compatible)

    def step_U_compatible(self):
        U_comp = self.game.get_U_compatible()

        headings = [f'{plat}' for plat in U_comp]
        max_length = max(len(U_comp[plat]) for plat in U_comp)

        columns = []
        for plateau in U_comp:
            u_map = U_comp[plateau]
            col = []
            for key in u_map:
                col.append(f'{key} \u2192 {u_map[key]}')
            while len(col) < max_length:
                col.append('')
            columns.append(col)

        values = []
        for index in range(max_length):
            row = []
            for col in columns:
                row.append(col[index])
            values.append(tuple(row))

        self.treeview_output(headings, values, 'Safe Steps')
        safe_file_name = f'safe_steps_{self.name}'
        render_safe_steps(self.game.game, U_comp, safe_file_name)
        self.create_scrollable_image(safe_file_name)

        self.left_b1.configure(text="Back", command=self.step_U_compatible)
        self.right_b2.configure(text="Continue", command=self.step_viacomp)

    def step_viacomp(self):
        viacomp = self.game.get_viable_compatible()

        self.treeview_output(*build_nested_dict(viacomp), 'Viable Compatible Plans')
        self.left_b1.configure(text="Back", command=self.step_U_compatible)
        self.right_b2.configure(text="Continue", command=self.step_alpha_exits)

    def step_alpha_exits(self):
        alpha_exits = self.game.get_alpha_exits()

        if not alpha_exits:
            return self.step_admissible()

        headings = ['Edge', 'X']
        values = []

        for alpha_exit in alpha_exits:
            values.append((str(alpha_exit.edge), alpha_exit.subset_X))

        self.treeview_output(headings, values, 'Legitimate Alpha Exits')
        self.left_b1.configure(text="Back", command=self.step_U_compatible)
        self.right_b2.configure(text="Continue", command=self.step_admissible)

    def step_admissible(self):
        admissible = self.game.get_admissible()

        self.treeview_output(*build_nested_dict(admissible), 'Admissible Plans')
        self.left_b1.configure(text="Back", command=self.step_alpha_exits)
        self.right_b2.configure(text="Continue", command=self.step_beta)

    def step_beta(self):
        beta = self.game.get_beta()

        self.treeview_output(*build_nested_dict(beta, True), 'Beta')
        self.left_b1.configure(text="Back", command=self.step_admissible)
        self.right_b2.configure(text="Continue", command=self.step_gamma)

    def step_gamma(self):
        gamma = self.game.get_gamma()

        self.game.update_delta()

        self.converged = gamma['Converged']

        if not self.converged:
            heading = ['Ut= ', str(gamma['U'])]
            values = [('g= ', str(gamma['Plan'])), ('\u03C6t= ', str(gamma['Plan'].state_payoff))]

            self.treeview_output(heading, values, 'Gamma')

        self.left_b1.configure(text="Back", command=self.step_beta)
        self.right_b2.configure(text="Continue", command=self.iteration)


def build_nested_dict(main_dict, beta=False):
    headings = []
    columns = []
    max_length = 0

    for plat in main_dict:
        headings.append(f'{plat}')
        col = []
        for plat_map in main_dict[plat]:
            for u_map in plat_map:
                col.append(f'U \u2192 {u_map}')
                if beta:
                    col.append(f'\u03C6t:{plat_map[u_map].state_payoff} {plat_map[u_map]}')
                else:
                    col.extend(str(plan) for plan in plat_map[u_map])

                col.append('\n')

        columns.append(col)
        max_length = max(max_length, len(col))

    values = list(zip_longest(*columns, fillvalue=''))

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
        pass


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
