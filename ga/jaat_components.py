from gacvm import Domains, Parameters, ProblemDefinition
from gaapp import QSolutionToSolvePanel
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import numpy as np

class QxSolutionPanelFrame(QSolutionToSolvePanel):

    def fitness_method():
        pass

    def __init__(   self,
                    name="A name",
                    summary="A summary",
                    description="A description",
                    problem_definition=ProblemDefinition(domains=Domains(ranges=np.zeros((3,2)), names=("x", "y", "z")), fitness=fitness_method()),
                    default_parameters=Parameters(), parent=None):

        super().__init__(parent)

        self.__name = name
        self.__summary = summary
        self.__description = description
        self.__problem_definition = problem_definition
        self.__default_parameters = default_parameters

        @property
        def name(self):
            return self.__name

        @property
        def summary(self):
            return self.__summary
    
        @property
        def description(self):
            return self.__description

        @property
        def problem_definition(self):
            return self.__problem_definition

        @property
        def default_parameters(self):
            return self.__parameters

        def _update_from_simulation(self, ga=None):
            pass

        self.__layout = QHBoxLayout()

        self.__qx_vertical_control_panel = QxVerticalControlPanel()
        self.__qx_visualization_panel = QxVisualizationPanel()

        self.__layout.add_widget(self.__qx_vertical_control_panel)
        self.__layout.add_widget(self.__qx_visualization_panel)

class QxImageCloningPanel(QxSolutionPanelFrame):
    pass

class QxOpenBoxPanel(QxSolutionPanelFrame):
    pass

class QxShapeTransformationPanel(QxSolutionPanelFrame):
    pass

class QxVerticalControlPanel(QGroupBox):
    def __init__(self, menus:list[QWidget]=None, width:int=None, parent=None):
        super().__init__(parent, layout=QVBoxLayout())

        self.__q_widgets = []

        if menus is not None:
            for i, q_widget in enumerate(menus):
                self.__q_widgets.append(q_widget)
                q_widget.setFixedWidth(width)
                self.addWidget(self.__q_widgets[i])

class QxVisualizationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__layout = QVBoxLayout()

        self.__canvas = QPixmap(500, 500)
        self.__canvas.fill(Qt.black)
        self.__canvas_box = QLabel(pixmap=self.__canvas)
        self.__layout.add_widget(self.__canvas_box)