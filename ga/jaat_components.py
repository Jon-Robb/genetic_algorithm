from abc import abstractmethod
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
    

#    _____           _     _                    
#   |  __ \         | |   | |                   
#   | |__) | __ ___ | |__ | | ___ _ __ ___  ___ 
#   |  ___/ '__/ _ \| '_ \| |/ _ \ '_ ` _ \/ __|
#   | |   | | | (_) | |_) | |  __/ | | | | \__ \
#   |_|   |_|  \___/|_.__/|_|\___|_| |_| |_|___/                                                                                 
class Problem():

    def fitness(self):
        return "A fitness method"

    def __call__(self):
        return self.fitness()

class OpenBoxProblem(Problem):
    def __init__(self, width, length):
        self.__width = width
        self.__length = length
        self.__height = 0

    def fitness(self, cut_length:float = 0) -> float:
        self.__width -= 2 * cut_length
        self.__length -= 2 * cut_length
        self.__height = cut_length
        return self.__width * self.__length * self.__height

    def __call__(self, cut_length):
        return self.fitness(cut_length)
    
    @property
    def width(self):
        return self.__width
    
    @property
    def length(self):
        return self.__length
    
    @width.setter
    def width(self, width):
        self.__width = width
        

        self.__canvas.fill(Qt.black)
        self.__canvas_box = QLabel(pixmap=self.__canvas)
        self.__layout.add_widget(self.__canvas_box)
    @length.setter
    def length(self, length):
        self.__length = length


class ShapeTransformationProblem(Problem):
    pass

class ImageCloningProblem(Problem):
    pass

#      _____                                             _       
#     / ____|                                           | |      
#    | |     ___  _ __ ___  _ __   ___  _ __   ___ _ __ | |_ ___ 
#    | |    / _ \| '_ ` _ \| '_ \ / _ \| '_ \ / _ \ '_ \| __/ __|
#    | |___| (_) | | | | | | |_) | (_) | | | |  __/ | | | |_\__ \
#     \_____\___/|_| |_| |_| .__/ \___/|_| |_|\___|_| |_|\__|___/
#                          | |                                   
#                          |_|                                   
class QxSolutionPanelFrame(QSolutionToSolvePanel):

    def __init__(   self,
                    name : str="A name",
                    summary : str="A summary",
                    description : str="A description",
                    problem_definition : ProblemDefinition=ProblemDefinition(   domains=Domains(ranges=np.zeros((3,2)),
                                                                                                names=("x", "y", "z")),
                                                                                fitness=Problem()),
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
    
        
        
        

class QxVisualizationPanel(QGroupBox):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__layout = QVBoxLayout(self)
        self.__size = (self.screen().size().width(), self.screen().size().height())
        pass
        self.__canvas = QPixmap(self.__size)
        pass
        self.__canvas.fill(Qt.black)
        self.__canvas_box = QLabel(pixmap=self.__canvas)
        self.__layout.add_widget(self.__canvas_box)

if __name__ == "__main__":

    p = Problem()
    print(p())

    obp = OpenBoxProblem(10, 10)
    print(obp(5))