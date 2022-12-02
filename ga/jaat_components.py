from gacvm import Domains, Parameters, ProblemDefinition
from gaapp import QSolutionToSolvePanel
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import numpy as np
from exemple import *
class QxVerticalControlPanel(QGroupBox):
    def __init__(self, layout=QVBoxLayout(), menus:list[QWidget]=None, width:int=None, parent=None):
        super().__init__(parent)

        self.__q_widgets = []
        self.__layout = layout
        self.set_layout(layout)
       
        if menus is not None:
            for i, q_widget in enumerate(menus):
                self.__q_widgets.append(q_widget)
                #q_widget.setFixedWidth(width)
                self.__layout.add_widget(self.__q_widgets[i])
class QxVisualizationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        #set title
        self.title = "Visualization"

        self.__layout = QVBoxLayout(self)
       
        
        self.__canvas = QPixmap(600, 500)
       

        self.__canvas.fill(Qt.black)
        self.__canvas_box = QLabel(pixmap=self.__canvas)
        self.__layout.add_widget(self.__canvas_box)
class QxSolutionPanelFrame(QSolutionToSolvePanel):

    def fitness_method():
        return "A fitness method"

    def __init__(   self,
                    name : str="A name",
                    summary : str="A summary",
                    description : str="A description",
                    problem_definition : ProblemDefinition=ProblemDefinition(   domains=Domains(ranges=np.zeros((3,2)),
                                                                                names=("x", "y", "z")),
                                                                                fitness=fitness_method),
                    default_parameters : Parameters=Parameters(),
                    vertical_control_panel : QxVerticalControlPanel=None,
                    visualisation_panel : QxVisualizationPanel=None,
                    parent : QWidget=None):

        super().__init__(parent)

        self.__name = name
        self.__summary = summary
        self.__description = description
        self.__problem_definition = problem_definition
        self.__parameters = default_parameters

        self.__layout = QHBoxLayout(self)

        self.__qx_vertical_control_panel = vertical_control_panel
        self.__qx_visualization_panel = visualisation_panel

        self.__layout.add_widget(self.__qx_vertical_control_panel)
        self.__layout.add_widget(self.__qx_visualization_panel)

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

class QxImageCloningPanel(QxSolutionPanelFrame):
    pass

class QxOpenBoxPanel(QxSolutionPanelFrame):
    pass

class QxShapeTransformationPanel(QxSolutionPanelFrame):
    pass


class BoxProblemSolutionFramePanel(QxSolutionPanelFrame):
    def fitness_method():
        return "A fitness method"
    def __init__(self, name: str = "Box Problem", summary: str = "A summary", description: str = "A description", problem_definition: ProblemDefinition = ProblemDefinition(domains=Domains(ranges=np.zeros((3, 2)), names=("x", "y", "z")), fitness=fitness_method), default_parameters: Parameters = Parameters(), parent: QWidget = None):
        self.__menu = []
        self.__widthscrollbar = ScrollValue("Width", (0, 100),50, 50)
        self.__heightscrollbar = ScrollValue("Height", (0, 100),50, 50)
        self.__menu.append(self.__widthscrollbar)
        self.__menu.append(self.__heightscrollbar)
        self.__qx_vertical_control_panel = QxVerticalControlPanel(menus=self.__menu)

        self.__qx_visualization_panel  = QxVisualizationPanel()



        super().__init__(name, summary, description, problem_definition, default_parameters, self.__qx_vertical_control_panel,self.__qx_visualization_panel, parent)
    
        
        
        
        
        
        
       



        



