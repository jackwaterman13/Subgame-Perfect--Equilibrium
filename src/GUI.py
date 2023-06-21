import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from game_solver import *
from graphics.Game_Render import *
from functools import partial

idt = '   '


def create_output_text(game_node, itr):
    global idt
    output = f'Iteration {itr}:\n'
    itr_data = game_node.itr_data
    plateau = game_node.plateau_u
    gamma = itr_data.gamma

    output += f'{idt}- The admissible plan selected to update the alpha vector this iteration was: '
    output += f'{gamma[plateau]} \u2208 ADMISS({gamma[plateau].state},U,\u03B1)\n{idt}'

    output += f'- Here F(U) = {plateau.states} and'

    for state in plateau.u_map:
        output += f' U({state}) = {plateau.u_map[state]},'
    output = output[:-1] + '.'
    alpha_exits = itr_data.alpha_exits

    threat_pair = gamma[plateau].threat_pair

    if threat_pair is not None:
        output += f'\n{idt}- This plan is admissible due to condition AD-iv: ' \
                  f'threat pair ({threat_pair.state_x}, {threat_pair.plan_v}).'

    if alpha_exits:
        X_alpha = ''
        sequences_i = []
        for exit_i in alpha_exits:
            X_alpha += f'{exit_i.subset_x}, '

            if exit_i.legitimate_sequences is not None:
                if exit_i.legitimate_sequences:
                    sequences_i.append(legitimate_sequences_output(exit_i))

        output += f'\n{idt}- The set X(\u03B1) = [{X_alpha}'
        output = output[:-2] + '].'

        if sequences_i:
            for sequence_i in sequences_i:
                output += f'\n{idt}- {sequence_i}'

    return output


def legitimate_sequences_output(exit_i):
    if not exit_i.legitimate_sequences:
        return ''
    sequences_i = f'The set X={exit_i.subset_x} has following legitimate \u03B1-exit sequences'
    for sequence in exit_i.legitimate_sequences:
        sequences_i += f'\n{idt}{idt}-The edge {sequence.edge} is an (\u03B1,{sequence.subset_z}) exit sequence.'

    if sequences_i == f'The set X={exit_i.subset_x} has following legitimate \u03B1-exit sequences':
        print('we')

    return sequences_i


class Ui_solver_window(object):

    def __init__(self, solver_window):
        self.name = 'new_test'
        self.game_solver = Game_Solver()

        self.game_paths = self.game_solver.get_game_paths()
        self.set_up_fonts()

        self.img_names = ["game_img", "safe_step_img", "admiss_img"]
        self.img_pos = [QtCore.QRect(0, 0, 500, 500), QtCore.QRect(500, 0, 500, 500), QtCore.QRect(1000, 0, 500, 500)]

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


img_labels = {"game_img": 'Alpha Values', "safe_step_img": 'Safe Steps', "admiss_img": 'Updated Alpha Values'}
img_labels_pos = {"game_img": QtCore.QRect(0, 500, 500, 25),
                  "safe_step_img": QtCore.QRect(500, 500, 500, 25),
                  "admiss_img": QtCore.QRect(1000, 500, 500, 25)}


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
    label = QtWidgets.QLabel(text, tab)
    label.setGeometry(QtCore.QRect(0, 525, 1500, 275))
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


def create_img_renders(game_node, img_names):
    game_start = game_node.game_start
    safe_steps = game_node.itr_data.safe_steps
    game_end = game_node.game_end
    it = IterationSolver(game_end, '')
    end_safe = it.get_end_game_safe_steps()

    return [render_game(game_start, img_names[0]),
            render_safe_steps(game_start, safe_steps, img_names[1]),
            render_safe_steps(game_end, end_safe, img_names[2])]


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
