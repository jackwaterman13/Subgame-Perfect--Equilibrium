import tkinter as tk
from tkinter import messagebox, filedialog


def load_game():

    file_path = filedialog.askopenfilename(title="Select a Game File",
                                           filetypes=[("Game Files", "*.game"), ("All Files", "*.*")])

    # If a file is selected
    if file_path:
        # For now, just show the selected file path. Replace this with your game loading logic.
        messagebox.showinfo("File Selected", f"Selected file: {file_path}")


class GameWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Subgame Perfect ε-Equilibrium Finder")
        self.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        # Title Label
        self.title_label = tk.Label(self, text="Subgame Perfect ε-Equilibrium Finder", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="n")

        # Create Game Button
        self.create_game_btn = tk.Button(self, text="Create Game", command=self.create_game, width=15)
        self.create_game_btn.grid(row=1, column=0, columnspan=2, pady=20, padx=20)

        # Load Game Button
        self.load_game_btn = tk.Button(self, text="Load Game", command=load_game, width=15)
        self.load_game_btn.grid(row=2, column=0, columnspan=2, pady=20, padx=20)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def create_game(self):
        # Remove current widgets
        self.title_label.grid_forget()
        self.create_game_btn.grid_forget()
        self.load_game_btn.grid_forget()

        # Input for number of players
        self.num_players_label = tk.Label(self, text="Number of Players:")
        self.num_players_label.grid(row=0, column=0, sticky="e", padx=(20, 10), pady=20)

        self.num_players_entry = tk.Entry(self)
        self.num_players_entry.grid(row=0, column=1, sticky="w", padx=(10, 20), pady=20)

        # Input for number of states
        self.num_states_label = tk.Label(self, text="Number of States:")
        self.num_states_label.grid(row=1, column=0, sticky="e", padx=(20, 10), pady=20)

        self.num_states_entry = tk.Entry(self)
        self.num_states_entry.grid(row=1, column=1, sticky="w", padx=(10, 20), pady=20)

        # Submit Button
        self.submit_btn = tk.Button(self, text="Submit", command=self.submit_values, width=15)
        self.submit_btn.grid(row=2, column=0, columnspan=2, pady=20)

    def submit_values(self):
        try:
            num_players = int(self.num_players_entry.get())
            num_states = int(self.num_states_entry.get())

            # For now, just show the values in a messagebox. You can replace this with game logic.
            messagebox.showinfo("Values", f"Number of Players: {num_players}\nNumber of States: {num_states}")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers!")


if __name__ == "__main__":
    app = GameWindow()
    app.mainloop()
