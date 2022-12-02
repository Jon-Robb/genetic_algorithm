from abc import ABC, abstractmethod

import gacvm
import uqtwidgets

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSize, QPointF, QRectF
from PySide6.QtWidgets import  (QApplication, QMainWindow, QWidget,
                                QLabel, QScrollBar, QComboBox, QPushButton, QPlainTextEdit, QCheckBox,
                                QGroupBox, QSplitter, QTabWidget,
                                QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy,
                                QMessageBox)
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter, QFont, QPen, QBrush, QColor




from __feature__ import snake_case, true_property


QtWidgets.QFileDialog.getSaveFileName = QtWidgets.QFileDialog.get_save_file_name




class QGAAdapter(QObject):

    started = Signal()
    ended = Signal()
    evolved = Signal()
    reseted = Signal()

    class _SignalEmitter(gacvm.Observer):
        def __init__(self, adapter):
            super().__init__()
            self._adapter = adapter

        def update(self, engine):
            if self._adapter.state == gacvm.GeneticAlgorithm.State.RUNNING: # prevent useless update if paused
                self._adapter.evolved.emit()
            QApplication.process_events() # monothread simplification -> should be multithreaded or, at least, managed with Qt's signal

    def __init__(self):
        super().__init__()
        self.genetic_algorithm = gacvm.GeneticAlgorithm()
        self.genetic_algorithm.add_observer(QGAAdapter._SignalEmitter(self))

    @property
    def parameters(self):
        return self.genetic_algorithm.parameters

    @parameters.setter
    def parameters(self, value):
        self.genetic_algorithm.parameters = value

    @property
    def problem_definition(self):
        return self.genetic_algorithm.problem_definition

    @problem_definition.setter
    def problem_definition(self, value):
        self.genetic_algorithm.problem_definition = value

    @property
    def state(self):
        return self.genetic_algorithm.state

    def evolve(self):
        self.started.emit()
        self.genetic_algorithm.evolve()
        self.ended.emit()

    def stop(self):
        self.genetic_algorithm.stop()

    def pause(self):
        self.genetic_algorithm.pause()

    def resume(self):
        self.genetic_algorithm.resume()

    def reset(self, default_parameters, problem_definition):
        self.parameters = default_parameters
        self.problem_definition = problem_definition
        self.genetic_algorithm.reset()
        self.reseted.emit()





class QGAControlWidget(QGroupBox):

    # Signals are available from this control panel
    # But, in most case, the user should use the signals emitted from QGAAdapter!
    started = Signal()
    stopped = Signal()
    paused = Signal()
    resumed = Signal()

    def __init__(self, ga_adapter, solution_panels, parent=None):
        super().__init__(parent)

        self.title = 'Control'
        self._ga_adapter = ga_adapter
        self._solution_panels = solution_panels

        self._state_machine_info = {
                # index, start_btn_enab, pause_btn_enab, start_btn_txt, pause_btn_txt, start_nxt_state, pause_nxt_state, text 
                gacvm.GeneticAlgorithm.State.IDLE : (0, True, False, 'Start', 'Pause', 'RUNNING', 'IDLE', 'Idle'),
                gacvm.GeneticAlgorithm.State.RUNNING : (1, True, True, 'Stop', 'Pause', 'IDLE', 'PAUSED', 'Running'),
                gacvm.GeneticAlgorithm.State.PAUSED : (2, True, True, 'Stop', 'Resume', 'IDLE', 'RUNNING', 'Paused')                    
            }

        self._start_stop_button = QPushButton()
        self._pause_resume_button = QPushButton()
        self._start_stop_button.size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self._pause_resume_button.size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self._current_state_label = QLabel()
        self._current_state_label.alignment = Qt.AlignCenter
        self._current_epoch_label = QLabel()
        self._current_epoch_label.alignment = Qt.AlignCenter

        button_layout = QHBoxLayout()
        button_layout.add_widget(self._start_stop_button)
        button_layout.add_widget(self._pause_resume_button)

        layout = QVBoxLayout(self)
        layout.add_layout(button_layout)
        layout.add_widget(self._current_state_label)
        layout.add_widget(self._current_epoch_label)

        self._start_stop_button.clicked.connect(self._next_start_stop_state)
        self._pause_resume_button.clicked.connect(self._next_pause_resume_state)

        self._ga_adapter.started.connect(self._update_since_evolution)
        self._ga_adapter.ended.connect(self._update_since_evolution_ended)
        self._ga_adapter.evolved.connect(self._update_since_evolution)

        self._update_gui()

    def _update_gui(self):
        state_info = self._state_machine_info[self._ga_adapter.state]
        self._start_stop_button.enabled = state_info[1]
        self._pause_resume_button.enabled = state_info[2]
        self._start_stop_button.text = state_info[3]
        self._pause_resume_button.text = state_info[4]

        self._current_state_label.text = state_info[7]

        epoch_prefix = 'Current epoch : '
        epoch_detail = f'{ "-na-" if self._ga_adapter.state is gacvm.GeneticAlgorithm.State.IDLE else self._ga_adapter.genetic_algorithm.current_epoch }'
        self._current_epoch_label.text = f'{epoch_prefix}{epoch_detail}'

    @Slot()
    def _next_start_stop_state(self):
        if self._ga_adapter.state is not gacvm.GeneticAlgorithm.State.IDLE:
            self._ga_adapter.stop()
            self.stopped.emit()
        else:
            self._ga_adapter.problem_definition = self._solution_panels.problem_definition
            self.started.emit()
            self._ga_adapter.evolve()

        self._update_gui()

    @Slot()
    def _next_pause_resume_state(self):
        if self._ga_adapter.state is gacvm.GeneticAlgorithm.State.RUNNING:
            self._ga_adapter.pause()
            self.paused.emit()
        elif self._ga_adapter.state is gacvm.GeneticAlgorithm.State.PAUSED:
            self._ga_adapter.resume()
            self.resumed.emit()

        self._update_gui()

    @Slot()
    def _update_since_evolution_ended(self):
        self._update_gui()

    @Slot()
    def _update_since_evolution(self):
        self._update_gui()



# class HistoryGraph(QChartView):
class QHistoryGraph(QLabel): # QtCharts will be available with Qt 6.1 (https://www.qt.io/blog/add-on-support-in-qt-6.0-and-beyond)! Damn!
    def __init__(self, ga_adapter, parent=None):
        super().__init__(parent)
        self._ga_adapter = ga_adapter

        self._update_graph = True
        self.minimum_width = 500
        self.minimum_height = 300

        self._figure = Figure(figsize=(self.width / 100.0, self.height / 100.0), dpi=100)
        self._canvas = FigureCanvas(self._figure)
        self._axes = self._figure.add_subplot()

        self._update_mpl()

    @Slot()
    def updateGraph(self, value):
        self.update_graph = value

    @property
    def update_graph(self):
        return self._update_graph

    @update_graph.setter
    def update_graph(self, value):
        self._update_graph = bool(value)

        if not self._update_graph:
            self._axes.clear()
            self._update_mpl_image()

    def _update_mpl_image(self):
        self._canvas.draw()
        w, h = self._canvas.get_width_height()
        self._image = QImage(self._canvas.buffer_rgba(), w, h, w * 4, QImage.Format_ARGB32)
        self.update()

    def _update_mpl(self):
        if self._update_graph:
            self._axes.clear()
            self._axes.set_title('Evolution')
            self._axes.set_xlabel('Epoch')
            self._axes.set_ylabel('Fitness')

            if self._ga_adapter.genetic_algorithm.history.count >= 2:
                self._axes.plot(self._ga_adapter.genetic_algorithm.history.epoch, self._ga_adapter.genetic_algorithm.history.history[:,0], color=[0., 1., 0.], label = "Best") # color are BGR
                self._axes.plot(self._ga_adapter.genetic_algorithm.history.epoch, self._ga_adapter.genetic_algorithm.history.history[:,1], color=[0., 0., 1.], label = "Worst")
                self._axes.plot(self._ga_adapter.genetic_algorithm.history.epoch, self._ga_adapter.genetic_algorithm.history.history[:,2], color=[1., 0., 0.], label = "Average")

                self._axes.legend()

            self._update_mpl_image()

    def paint_event(self, event):
        painter = QPainter(self)
        painter.set_render_hint(QPainter.Antialiasing)
        painter.draw_image(0, 0, self._image)

    def show_event(self, event):
        self._update_mpl()

    def resize_event(self, event):
        self._figure.set_size_inches(self.width / 100.0, self.height / 100.0, forward=True)
        self._update_mpl()

    @Slot()
    def update_history(self):
        self._update_mpl()

class QEvolutionInfoWidget(QGroupBox):
    def __init__(self, ga_adapter, parent=None):
        super().__init__(parent)
        self._ga_adapter = ga_adapter

        self.title = 'Evolution information'

        self._info_widget = QPlainTextEdit()

        my_font = self._info_widget.font
        my_font.set_family('Courier New')
        self._info_widget.font = my_font

        self._info_widget.read_only = True
        self._info_widget.placeholder_text = 'No evolution'

        layout = QGridLayout(self)
        layout.add_widget(self._info_widget)

        self.update()

    @Slot()
    def clear(self):
        self._info_widget.plain_text = ''

    @Slot()
    def update(self):
        if self._ga_adapter.genetic_algorithm.current_epoch == 0:
            self._info_widget.plain_text = ''
        else:
            solution_info = 'Solution : '
            for i in range(self._ga_adapter.problem_definition.domains.dimension):
                solution_info += f'\n    - {self._ga_adapter.problem_definition.domains.names[i]} : {self._ga_adapter.genetic_algorithm.history.best_solution[i]}'

            self._info_widget.plain_text = f'''Current epoch : {self._ga_adapter.genetic_algorithm.current_epoch}
Problem dimension : {self._ga_adapter.genetic_algorithm.problem_definition.domains.dimension}
Fitness : 
    - best    : {self._ga_adapter.genetic_algorithm.history.best_fitness:>16.6f}
    - worst   : {self._ga_adapter.genetic_algorithm.history.worst_fitness:>16.6f}
    - average : {self._ga_adapter.genetic_algorithm.history.average_fitness:>16.6f}
    - std dev : {self._ga_adapter.genetic_algorithm.history.standard_deviation_fitness:>16.6f}
    - median  : {self._ga_adapter.genetic_algorithm.history.median_fitness:>16.6f}
{solution_info}'''


class QGAParametersWidget(QGroupBox):

    parameter_changed = Signal()

    def __init__(self, ga_adapter, parent=None):
        super().__init__(parent)

        self._ga_adapter = ga_adapter
        self.title = 'Parameters'
        layout = QFormLayout(self)

        self._maximum_epoch_widget, maximum_epoch_layout = uqtwidgets.create_scroll_int_value(10, 250, 10000)
        self._population_size_widget, population_size_layout = uqtwidgets.create_scroll_int_value(5, 25, 250)
        self._elitism_rate_widget, elitism_rate_layout = uqtwidgets.create_scroll_real_value(0., 0.05, 1., 2, 100., value_suffix = " %")
        self._selection_rate_widget, selection_rate_layout = uqtwidgets.create_scroll_real_value(0.01, 0.75, 1., 2, 100., value_suffix = " %")
        self._mutation_rate_widget, mutation_rate_layout = uqtwidgets.create_scroll_real_value(0., 0.10, 1., 2, 100., value_suffix = " %")

        self._selection_strategies = [gacvm.RouletteWheelSelectionStrategy]
        self._crossover_strategies = [gacvm.WeightedAverageCrossoverStrategy]
        self._mutation_strategies = [gacvm.GeneMutationStrategy]

        self._selection_strategy_combo = QComboBox()
        self._crossover_strategy_combo = QComboBox()
        self._mutation_strategy_combo = QComboBox()
        self._selection_strategy_combo.add_items([strategy.name() for strategy in self._selection_strategies])
        self._crossover_strategy_combo.add_items([strategy.name() for strategy in self._crossover_strategies])
        self._mutation_strategy_combo.add_items([strategy.name() for strategy in self._mutation_strategies])

        layout.add_row('Maximum epoch', maximum_epoch_layout)
        layout.add_row('Population size', population_size_layout)
        layout.add_row('Elitism rate', elitism_rate_layout)
        layout.add_row('Selection rate', selection_rate_layout)
        layout.add_row('Mutation rate', mutation_rate_layout)
        layout.add_row('Selection strategy', self._selection_strategy_combo)
        layout.add_row('Crossover strategy', self._crossover_strategy_combo)
        layout.add_row('Mutation strategy', self._mutation_strategy_combo)

        self._maximum_epoch_widget.valueChanged.connect(self.parameter_changed)
        self._population_size_widget.valueChanged.connect(self.parameter_changed)
        self._elitism_rate_widget.valueChanged.connect(self.parameter_changed)
        self._selection_rate_widget.valueChanged.connect(self.parameter_changed)
        self._mutation_rate_widget.valueChanged.connect(self.parameter_changed)
        self._selection_strategy_combo.currentIndexChanged.connect(self.parameter_changed)
        self._crossover_strategy_combo.currentIndexChanged.connect(self.parameter_changed)
        self._mutation_strategy_combo.currentIndexChanged.connect(self.parameter_changed)

        self.parameter_changed.connect(self._update_adapter)
        self.update_from_adapter()

    def add_selection_strategy(self, strategy):
        # to do validate strategy
        self._selection_strategies.append(strategy)
        self._selection_strategy_combo.add_item(strategy.name())

    def add_crossover_strategy(self, strategy):
        # to do validate strategy
        self._crossover_strategies.append(strategy)
        self._crossover_strategy_combo.add_item(strategy.name())

    def add_mutation_strategy(self, strategy):
        # to do validate strategy
        self._mutation_strategies.append(strategy)
        self._mutation_strategy_combo.add_item(strategy.name())

    def update_from(self, parameter):
        signal_blocker = QtCore.QSignalBlocker(self) # pylint: disable=unused-variable
        self._maximum_epoch_widget.value = parameter.maximum_epoch
        self._population_size_widget.value = parameter.population_size
        self._elitism_rate_widget.set_real_value(parameter.elitism_rate)
        self._selection_rate_widget.set_real_value(parameter.selection_rate)
        self._mutation_rate_widget.set_real_value(parameter.mutation_rate)

        self._selection_strategy_combo.current_text = parameter.selection_strategy.name()
        self._crossover_strategy_combo.current_text = parameter.crossover_strategy.name()
        self._mutation_strategy_combo.current_text = parameter.mutation_strategy.name()

        signal_blocker.unblock()
        self.parameter_changed.emit()

    @Slot()
    def update_from_adapter(self):
        self.update_from(self._ga_adapter.parameters)
    
    @Slot()
    def _update_adapter(self):
        self._ga_adapter.parameters.maximum_epoch = self._maximum_epoch_widget.value
        self._ga_adapter.parameters.population_size = self._population_size_widget.value
        self._ga_adapter.parameters.elitism_rate = self._elitism_rate_widget.get_real_value()
        self._ga_adapter.parameters.selection_rate = self._selection_rate_widget.get_real_value()
        self._ga_adapter.parameters.mutation_rate = self._mutation_rate_widget.get_real_value()

        self._ga_adapter.parameters.selection_strategy = self._selection_strategies[self._selection_strategy_combo.current_index]()
        self._ga_adapter.parameters.crossover_strategy = self._crossover_strategies[self._crossover_strategy_combo.current_index]()
        self._ga_adapter.parameters.mutation_strategy = self._mutation_strategies[self._mutation_strategy_combo.current_index]()

    @property
    def maximum_epoch(self):
        return self._maximum_epoch_widget.value

    @property
    def population_size(self):
        return self._population_size_widget.value

    @property
    def elitism_rate(self):
        return self._elitism_rate_widget.get_real_value()

    @property
    def selection_rate(self):
        return self._selection_rate_widget.get_real_value()

    @property
    def mutation_rate(self):
        return self._mutation_rate_widget.get_real_value()

    @property
    def selection_strategy(self):
        return self._selection_strategies[self._selection_strategy.current_text]()

    @property
    def crossover_strategy(self):
        return self._crossover_strategies[self._crossover_strategy.current_text]()

    @property
    def mutation_strategy(self):
        return self._mutation_strategies[self._mutation_strategy.current_text]()


class QSolutionToSolvePanel(QWidget): # to do : should inherit from ABC : see https://stackoverflow.com/questions/28799089/python-abc-multiple-inheritance
    '''
    Cette classe permet d'ajouter simplement dans l'interface utilisateur un nouveau panneau permettant la résolution d'un problème spécifique.

    Plusieurs fonction abstraites doivent être obligatoirement déterminées :
        - name (propriété)
        - summary (propriété)
        - description (propriété)
        - problem_definition (propriété)
        - default_parameters (propriété)
        - _update_from_simulation (fonction 'protégée')
    '''
    
    def __init__(self, parent=None): 
        super().__init__(parent)

    @property
    @abstractmethod
    def name(self):
        '''
        Retourne un nom court et compact représentant le problème à résoudre.
        Ce nom est affiché dans l'onglet de sélection de problème.
        '''
        raise NotImplementedError()

    @property
    @abstractmethod
    def summary(self):
        '''
        Retourne un court texte décrivant les grandes lignes du problèmes - typiquement 1 à 3 phrases.
        Ce sommaire est affiché en haut de la fenêtre de résolution du problème.
        '''
        raise NotImplementedError()

    @property
    @abstractmethod
    def description(self):
        '''
        Retourne un texte descriptif expliquant les détails du problème.
        Cette description est affichée dans une autre fenêtre lorsqu'on appui sur le bouton en haut à droite.
        '''
        raise NotImplementedError()

    @property
    @abstractmethod
    def problem_definition(self):
        '''
        Retourne un objet complet de définition du problème. L'objet retourné est celui qui sera résoud par l'algorithme génétique.
        '''
        raise NotImplementedError()

    @property
    @abstractmethod
    def default_parameters(self):
        '''
        Retourne un objet de paramètres de l'algorithme génétique. Ces valeurs seront utilisée pour initialiser la liste des paramètres à gauche dans l'interface utilisateur.
        '''
        raise NotImplementedError()

    @abstractmethod
    def _update_from_simulation(self, ga=None):
        '''
        Fonction utilitaire permettant de donner du 'feedback' pour chaque pas de simulation. Il faut gérer le cas où ga est None. Lorsque ga est None, on donne un feedback d'initialisation sans aucune évolution.
        '''
        raise NotImplementedError()

    @Slot()
    def update_solution(self, ga):
        self._update_from_simulation(ga)




class QSolutionPanels(QTabWidget):

    solution_changed = Signal(int)

    class _TabWidget(QWidget):
        def __init__(self, solution_panel):
            super().__init__()

            self._solution_panel = solution_panel

            description_button = QPushButton('Description')
            description_button.size_policy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            label = QLabel(str(solution_panel.summary))
            label.word_wrap = True
            summary_group_box = QGroupBox('Summary')
            summary_group_box.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            summary_group_layout = QHBoxLayout(summary_group_box)
            summary_group_layout.add_widget(label)
            summary_group_layout.add_widget(description_button)

            description_button.clicked.connect(lambda : QMessageBox.information(self, f'{self._solution_panel.name} description', solution_panel.description))

            layout = QGridLayout(self)
            layout.add_widget(summary_group_box)
            layout.add_widget(self._solution_panel)
            solution_layout = self._solution_panel.layout()
            if solution_layout:
                solution_layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)

        self.currentChanged.connect(self.change_solution)
        self.currentChanged.connect(self.solution_changed)

    def add_solution_panel(self, solution_panel):
        # TO DO - THIS IS NOT WORKING WHEN solution_panel is defined in another module
        # if not isinstance(solution_panel, QSolutionToSolvePanel):
        #     raise ValueError('Invalid input parameters in SolutionPanels.add_solution_panel : panel must be a SolutionToSolvePanel object.')

        self.add_tab(QSolutionPanels._TabWidget(solution_panel), str(solution_panel.name))
        self.currentChanged.connect(lambda : solution_panel._update_from_simulation(None))

    @Slot()
    def change_solution(self):
        pass

    @Slot()
    def update(self, ga):
        self.current_widget()._solution_panel.update_solution(ga)

    @property
    def default_parameters(self):
        return self.current_widget()._solution_panel.default_parameters

    @property
    def problem_definition(self):
        return self.current_widget()._solution_panel.problem_definition


class QGAApp(QMainWindow):
    '''
    L'application de résolution de problème par algorithme génétique.

    Cette classe possède 4 fonctions utilitaires pratiques :
        - ajout de panneau de résolution de problème : add_solution_panel
        - ajout de stratégie de sélection : add_selection_strategy
        - ajout de stratégie de croisement : add_crossover_strategy
        - ajout de stratégie de mutation : add_mutation_strategy
    '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.window_title = 'Genetic Algorithm Solver'
        self.window_icon = QIcon('images/gaapp.png')

        self._ga = QGAAdapter()

        self._create_gui()


    def _create_gui(self):
        self.enabled = False

        self._solution_panels = QSolutionPanels()
        self._control_widget = QGAControlWidget(self._ga, self._solution_panels)
        self._parameter_widget = QGAParametersWidget(self._ga)
        self._evolution_info_widget = QEvolutionInfoWidget(self._ga)
        self._history_graph_widget = QHistoryGraph(self._ga)

        self._show_history_widget = QCheckBox()
        self._show_history_widget.checked = True
        show_history_layout = QHBoxLayout()
        show_history_layout.add_stretch()
        show_history_layout.add_widget(QLabel('Show history '))
        show_history_layout.add_widget(self._show_history_widget)

        show_history_group_box = QGroupBox('History')
        show_history_group_layout = QVBoxLayout(show_history_group_box)
        show_history_group_layout.add_widget(self._history_graph_widget)
        show_history_group_layout.add_layout(show_history_layout)

        self._show_history_widget.stateChanged.connect(self._history_graph_widget.updateGraph)

        # self._parameter_widget.update_from_adapter(self._ga)
        
        self._ga.started.connect(lambda : setattr(self._parameter_widget, 'enabled', False))
        self._ga.started.connect(lambda : setattr(self._solution_panels, 'enabled', False))
        self._ga.ended.connect(lambda : setattr(self._parameter_widget, 'enabled', True))
        self._ga.ended.connect(lambda : setattr(self._solution_panels, 'enabled', True))
        self._ga.evolved.connect(self._history_graph_widget.update_history)
        self._ga.evolved.connect(self._evolution_info_widget.update)
        self._ga.evolved.connect(lambda:self._solution_panels.update(self._ga.genetic_algorithm))

        self._ga.reseted.connect(self._history_graph_widget.update_history)
        self._ga.reseted.connect(self._evolution_info_widget.update)
        self._ga.reseted.connect(self._parameter_widget.update_from_adapter)
        

        self._solution_panels.solution_changed.connect(lambda : self._ga.reset(self._solution_panels.default_parameters, self._solution_panels.problem_definition))
        # self._solution_panels.solution_changed.connect(self._evolution_info_widget.clear)
        # self._solution_panels.solution_changed.connect(self._history_graph_widget.update_history)

        left_widget = QWidget()
        left_widget.size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        left_layout = QVBoxLayout(left_widget)
        left_layout.add_widget(self._control_widget)
        left_layout.add_widget(self._parameter_widget)
        # left_layout.add_stretch()
        left_layout.add_widget(self._evolution_info_widget)

        main_splitter = QSplitter()
        main_splitter.orientation = Qt.Vertical
        main_splitter.add_widget(self._solution_panels)
        main_splitter.add_widget(show_history_group_box)

        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        central_layout.add_widget(left_widget)
        central_layout.add_widget(main_splitter)

        self.set_central_widget(central_widget)


    def add_solution_panel(self, solution_panel):
        self._solution_panels.add_solution_panel(solution_panel)
        self.enabled = True

    def add_selection_strategy(self, strategy):
        self._parameter_widget.add_selection_strategy(strategy)

    def add_crossover_strategy(self, strategy):
        self._parameter_widget.add_crossover_strategy(strategy)

    def add_mutation_strategy(self, strategy):
        self._parameter_widget.add_mutation_strategy(strategy)


