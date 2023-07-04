import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from game_solver import *
from graphics.Game_Render import *
from functools import partial

idt = '   '


def create_output_text(game_node: GameNode, itr):
    global idt
    width = 286

    admissible_plans = game_node.admissible_plans

    lines = [f'ITERATION {itr}:'.center(width), '']
    for subset in admissible_plans:

        for u_set in admissible_plans[subset]:
            u_list = list(u_set)

            line = f'ADMISS(t, {[t[0] for t in u_list]}, \u03B1), with '
            for item in u_list:
                line += f'U({item[0]}) = {item[1]}, '
            line = line[:-2]
            lines.append(line.center(width))

            for plan in admissible_plans[subset][u_set]:
                lines.append(f'{plan}'.center(width))

            lines.append('')

    end_alpha = game_node.end_alpha
    lines.append(f'Updated Alpha:'.center(width))

    line = ''
    for state in end_alpha:
        line += f'\u03B1({state}) = {end_alpha[state]}{2 * idt}'

    lines.append(line.center(width))

    output = ''

    for line in lines:
        output += line + '\n'

    return output


class Ui_solver_window(object):

    def __init__(self, solver_window):
        self.name = 'new_test'
        self.game_solver = GameSolver()

        self.game_paths = self.game_solver.game_path
        self.set_up_fonts()

        self.img_names = ["game_img", "safe_step_img"]
        self.img_pos = [QtCore.QRect(175, 0, 500, 500), QtCore.QRect(825, 0, 500, 500)]

        self.solver_window = solver_window
        self.setupUi()

    def setupUi(self):
        self.solver_window.setObjectName("solver_window")
        self.solver_window.resize(1500, 850)

        self.central_widget = QtWidgets.QWidget(self.solver_window)

        # Create a QVBoxLayout for the central widget
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Create the menu bar
        self.solver_menu = QtWidgets.QMenuBar(self.solver_window)

        self.menuEquilibrium = QtWidgets.QMenu("Equilibrium", self.solver_menu)
        self.equilibria = []

        for eq_num, game_path in enumerate(self.game_paths, start=1):
            new_action = QtWidgets.QAction(f"Equilibrium {eq_num}", self.solver_window)
            new_action.triggered.connect(partial(self.load_iterations, eq_num - 1))
            self.equilibria.append(new_action)
            self.menuEquilibrium.addAction(new_action)

        self.solver_menu.addMenu(self.menuEquilibrium)
        self.create_tab_widget()
        # Set the menu bar of the main window
        self.solver_window.setMenuBar(self.solver_menu)

    def load_iterations(self, game_path_num, checked):
        self.tabWidget.clear()
        self.tabs = []

        itr = 1
        for game_node in self.game_paths[game_path_num]:
            img_names = [f'{name}_{itr}' for name in self.img_names]
            img_paths = create_img_renders(game_node, img_names)
            self.tabs.append(create_tab('tab', img_names, self.img_pos, img_paths, self.tab_img_label_font))
            output = create_output_text(game_node, itr)
            create_output_label(self.tabs[-1], output)
            self.add_tab(self.tabs[-1], f'Iteration {itr}')
            itr += 1

        self.solver_window.setCentralWidget(self.central_widget)

    def create_tab_widget(self):
        self.tabWidget = QtWidgets.QTabWidget(self.central_widget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1500, 830))
        self.tabWidget.setIconSize(QtCore.QSize(15, 15))
        self.tabWidget.setObjectName("tabWidget")

    def add_tab(self, tab, label):
        self.tabWidget.addTab(tab, label)

    def set_up_fonts(self):
        self.tab_img_label_font = QtGui.QFont()
        self.tab_img_label_font.setFamily("Arial")
        self.tab_img_label_font.setPointSize(14)


def create_tab(name, img_names, img_pos, img_paths, font):
    tab = QtWidgets.QWidget()
    tab.setObjectName(name)

    for name, pos, path in zip(img_names, img_pos, img_paths):
        create_tab_img(name, tab, pos, path, font)

    return tab


def create_tab_img(name, tab, img_pos, img_path, font):
    img = QtWidgets.QLabel(tab)
    img.setGeometry(img_pos)
    img.setFrameShape(QtWidgets.QFrame.Box)
    img.setText("")
    img.setPixmap(QtGui.QPixmap(img_path))
    img.setScaledContents(True)
    img.setObjectName(name)
    create_tab_img_label(font, name[:-2], tab)


img_labels = {"game_img": 'Alpha Values', "safe_step_img": 'Safe Steps'}
img_labels_pos = {"game_img": QtCore.QRect(175, 500, 500, 25),
                  "safe_step_img": QtCore.QRect(825, 500, 500, 25)}


def create_tab_img_label(font, name, tab):
    global img_labels, img_labels_pos
    img_label = QtWidgets.QLabel(img_labels[name], tab)
    img_label.setGeometry(img_labels_pos[name])
    img_label.setFont(font)
    img_label.setFrameShape(QtWidgets.QFrame.Box)
    img_label.setAlignment(QtCore.Qt.AlignCenter)
    img_label.setObjectName(f'{name}_img_label')

    return img_label


def create_output_label(tab, text):
    scroll_area = QtWidgets.QScrollArea(tab)
    scroll_area.setGeometry(QtCore.QRect(0, 525, 1500, 275))
    scroll_area.setWidgetResizable(True)

    content_widget = QtWidgets.QWidget()
    scroll_area.setWidget(content_widget)

    vbox = QtWidgets.QVBoxLayout(content_widget)

    label = QtWidgets.QLabel(text, content_widget)
    font = QtGui.QFont()
    font.setPointSize(11)
    label.setFont(font)
    label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    label.setFrameShape(QtWidgets.QFrame.Box)
    label.setFrameShadow(QtWidgets.QFrame.Plain)
    label.setLineWidth(2)
    label.setMidLineWidth(2)
    label.setTextFormat(QtCore.Qt.PlainText)
    label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    label.setStyleSheet("margin: 10px;")
    label.setObjectName("output_label")
    label.setWordWrap(True)
    vbox.addWidget(label)

    return scroll_area


def create_img_renders(game_node, img_names):
    game_graph = game_node.game_graph

    return [render_game(game_graph.neighbours_map, game_node.start_alpha, img_names[0]),
            render_safe_steps(game_graph.neighbours_map, game_node.start_alpha, game_node.safe_steps, img_names[1])]


ui = None


def start_gui():
    global ui
    app = QtWidgets.QApplication(sys.argv)
    solver_window = QtWidgets.QMainWindow()
    ui = Ui_solver_window(solver_window)
    solver_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    start_gui()
