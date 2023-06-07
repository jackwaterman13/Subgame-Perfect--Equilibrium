import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Create a Tkinter window
window = tk.Tk()
window.title("Table Display")

# Define the table data
data = [
    ['John', 25, 'New York'],
    ['Jane', 30, 'London']
]

# Create a Matplotlib figure and axes
fig = Figure(figsize=(5, 3), dpi=100)
ax = fig.add_subplot(111)

# Create the table
table = ax.table(cellText=data, colLabels=['Name', 'Age', 'City'], loc='center')

# Hide the axes
ax.axis('off')

# Create a Tkinter canvas to display the table
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack()

# Start the Tkinter event loop
window.mainloop()