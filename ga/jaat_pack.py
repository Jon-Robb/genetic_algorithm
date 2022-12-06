from abc import abstractmethod
from gacvm import Domains, Parameters, ProblemDefinition, MutationStrategy
from gaapp import QSolutionToSolvePanel
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import numpy as np
from typing import Optional
from uqtwidgets import QImageViewer


#  .----------------. 
# | .--------------. |
# | | ____    ____ | |
# | ||_   \  /   _|| |
# | |  |   \/   |  | |
# | |  | |\  /| |  | |
# | | _| |_\/_| |_ | |
# | ||_____||_____|| |
# | |              | |
# | '--------------' |
#  '----------------' 
# ------------------------------------------------------------------------------------------ 
#  ______ _ _                         ______          _             _   _             
# |  ____(_) |                       |  ____|        | |           | | (_)            
# | |__   _| |_ _ __   ___  ___ ___  | |____   ____ _| |_   _  __ _| |_ _  ___  _ __  
# |  __| | | __| '_ \ / _ \/ __/ __| |  __\ \ / / _` | | | | |/ _` | __| |/ _ \| '_ \ 
# | |    | | |_| | | |  __/\__ \__ \ | |___\ V / (_| | | |_| | (_| | |_| | (_) | | | |
# |_|    |_|\__|_| |_|\___||___/___/ |______\_/ \__,_|_|\__,_|\__,_|\__|_|\___/|_| |_| 
# ------------------------------------------------------------------------------------------                                                                 
class FE():
    
    def __init_(self, parent_panel:type["QxSolutionPanelFrame"]):
        self._parent_panel = parent_panel

    def fitness_evaluation(self):
        return "A fitness method"

    def __call__(self):
        return self.fitness_evaluation()

class OpenBoxFE(FE):

    def __init__(self, width=50, length=100):
        self.__width = width
        self.__length = length

    def __call__(self, cut_length):
        return self.fitness_evaluation(cut_length)

    def fitness_evaluation(self, cut_length):
        width = self.__width
        length = self.__length
        cut_length = cut_length[0]
        width -= 2 * cut_length
        length -= 2 * cut_length
        height = cut_length
        volume = float(width * length * height)
        return volume

    @property
    def width(self):
        return self.__width
    
    @property
    def length(self):
        return self.__length
    
    @width.setter
    def width(self, width):
        self.__width = width
        
    @length.setter
    def length(self, length):
        self.__length = length

class ShapeTransformationFE(FE):
    def __init__(self):
        pass

class ImageCloningFE(FE):
    pass
# ------------------------------------------------------------------------------------------ 
#   _____ _             _             _           
#  / ____| |           | |           (_)          
# | (___ | |_ _ __ __ _| |_ ___  __ _ _  ___  ___ 
#  \___ \| __| '__/ _` | __/ _ \/ _` | |/ _ \/ __|
#  ____) | |_| | | (_| | ||  __/ (_| | |  __/\__ \
# |_____/ \__|_|  \__,_|\__\___|\__, |_|\___||___/
#                                __/ |            
#                               |___/             
# ------------------------------------------------------------------------------------------ 
# <-. (`-')  
#    \(OO )_ 
# ,--./  ,-.)      _        _   _             
# |   `.'   |     | |      | | (_)            
# |  |'.'|  |_   _| |_ __ _| |_ _  ___  _ __  
# |  |   |  | | | | __/ _` | __| |/ _ \| '_ \ 
# |  |   |  | |_| | || (_| | |_| | (_) | | | |
# `--'   `--'\__,_|\__\__,_|\__|_|\___/|_| |_|
# ------------------------------------------------------------------------------------------
class DoubleGeneMutationStrategy(MutationStrategy):
    '''
    Lorsqu'une mutation a lieu, deux gènes sont générés aléatoirement selon le domaine. Les gènes modifiés sont déterminés aléatoirement parmi tous les gènes.
    '''

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Mutate Two Genes'

    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                index1 = self._rng.integers(0, offsprings.shape[1])
                index2 = self._rng.integers(0, offsprings.shape[1])
                while index1 == index2:
                    index2 = self._rng.integers(0, offsprings.shape[1])
                offspring[index1] = domains.random_value(index1)
                offspring[index2] = domains.random_value(index2)

        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)
# ------------------------------------------------------------------------------------------ 
#  .----------------.  .----------------. 
# | .--------------. || .--------------. |
# | | ____   ____  | || |     ______   | |
# | ||_  _| |_  _| | || |   .' ___  |  | |
# | |  \ \   / /   | || |  / .'   \_|  | |
# | |   \ \ / /    | || |  | |         | |
# | |    \ ' /     | || |  \ `.___.'\  | |
# | |     \_/      | || |   `._____.'  | |
# | |              | || |              | |
# | '--------------' || '--------------' |
#  '----------------'  '----------------' 
# ------------------------------------------------------------------------------------------ 
#   _____       _            _____                                             _       
#  / ____|     | |          / ____|                                           | |      
# | (___  _   _| |__ ______| |     ___  _ __ ___  _ __   ___  _ __   ___ _ __ | |_ ___ 
#  \___ \| | | | '_ \______| |    / _ \| '_ ` _ \| '_ \ / _ \| '_ \ / _ \ '_ \| __/ __|
#  ____) | |_| | |_) |     | |___| (_) | | | | | | |_) | (_) | | | |  __/ | | | |_\__ \
# |_____/ \__,_|_.__/       \_____\___/|_| |_| |_| .__/ \___/|_| |_|\___|_| |_|\__|___/
#                                                | |                                   
#                                                |_|     
# ------------------------------------------------------------------------------------------ 
class ScrollValue(QWidget):
    
    valueChanged = Signal(int)
    
    def __init__(self, title:str, range:tuple, fixed_widget_length:int = 50,init:int=None, parent=None, step_value:int=1):
        super().__init__(parent)

        
        self.tool_tip = 'Valeur KNN'
        
        if init is None:
            init = round(sum(range) / 2)
        else:
            init = max(range[0], min(init, range[1]))
            
        title_label = QLabel()
        self.__sb = QScrollBar()
        self.__value_label = QLabel()

        title_label.set_text(title)
        title_label.set_fixed_width(fixed_widget_length)

        self.__sb.minimumWidth = 2 * fixed_widget_length
        self.__sb.set_orientation(Qt.Horizontal)
        self.__sb.set_range(range[0], range[1])
        self.__sb.set_value(init)

        self.__step_value = step_value
        
        self.__value_label.set_fixed_width(fixed_widget_length)
        self.__value_label.alignment = Qt.AlignCenter
        self.__value_label.set_num(init*step_value)
        
        self.__sb.valueChanged.connect(self.update)
        self.__sb.valueChanged.connect(self.valueChanged)


        layout = QHBoxLayout()
        layout.add_widget(title_label)
        layout.add_widget(self.__sb)
        layout.add_widget(self.__value_label)
        
        self.set_layout(layout)
        
        self.set_contents_margins(0, 0, 0, 0)
    

    def update(self, value:int):
        self.__value_label.set_num(value * self.__step_value)

    @Slot()
    def set_value(self, value):
        self.__sb.value = value
        
    @property
    def value(self):
        return self.__sb.value
    
    @value.setter
    def value(self, val):
        self.set_value(val)

    @property
    def step_value(self):
        return self.__step_value
    
    @step_value.setter
    def step_value(self, val):
        self.__step_value = val

    @property
    def range(self):
        return self.__range
    
    @range.setter
    def range(self, val):
        self.__range = val

    @property
    def sb(self):
        return self.__sb
    
    @sb.setter
    def sb(self, val):
        self.__sb = val
        
class ScrollValueButton(ScrollValue):
    def __init__(self, title: str, range: tuple, fixed_widget_length: int = 50, init: int = 50, parent=None, step_value: int = 1):
        super().__init__(title, range, fixed_widget_length, init, parent, step_value)
        self.__init = init
        self.__button = QPushButton("!");
        self.__button.set_fixed_width(fixed_widget_length/2)
        # self.__button.tool_tip = f'Reset to default value : {value_prefix}{init_val:{format_string}}{value_suffix}'
        self.__button.tool_tip = f'Reset to default value : {init}'
        # self.__button.connect(self.set_value)
        self.__button.clicked.connect(lambda : self.set_value(self.__init))
        self.layout().add_widget(self.__button)

class QxVerticalControlPanel(QGroupBox):
    def __init__(self, layout:Optional[QVBoxLayout]= None,title="Paramètres", menus:list[QWidget]=None, width:int=None, parent=None):
        super().__init__(parent)

        self.title = title
        self.__q_widgets = []
        self.__layout = layout if layout else QVBoxLayout()
        self.set_layout(self.__layout)
       
        if menus is not None:
            for i, q_widget in enumerate(menus):
                self.__q_widgets.append(q_widget)
                self.__layout.add_widget(self.__q_widgets[i])
        self.__layout.add_stretch(1)
        
class QxVisualizationPanel(QGroupBox):
    
    def __init__(self, parent=None):
        super().__init__(parent=parent, title='Visualisation')

        self.__layout = QVBoxLayout(self)
        self.__layout.content_margins = (0, 0, 0, 0)
        
       
        
        self.__image_viewer = QImageViewer()
        self.__layout.add_widget(self.__image_viewer)
        
   
    @property
    def image(self):
        return self.__image_viewer.image
    
    
    @image.setter
    def image(self, img):
        self.__image_viewer.image = img
    

   

class QxForm(QWidget):
    def __init__(self, title_widget:list[(str,QWidget)]=None, parent=None):
        super().__init__(parent)
        
        self.__form_layout = QFormLayout(self)
        
        if title_widget is not None:
            for title, widget in title_widget:
                self.__form_layout.add_row(title, widget)
        
# ------------------------------------------------------------------------------------------ 
#   _____                                             _       
#  / ____|                                           | |      
# | |     ___  _ __ ___  _ __   ___  _ __   ___ _ __ | |_ ___ 
# | |    / _ \| '_ ` _ \| '_ \ / _ \| '_ \ / _ \ '_ \| __/ __|
# | |___| (_) | | | | | | |_) | (_) | | | |  __/ | | | |_\__ \
#  \_____\___/|_| |_| |_| .__/ \___/|_| |_|\___|_| |_|\__|___/
#                       | |                                   
#                       |_|                                   
# ------------------------------------------------------------------------------------------ 
class QxSolutionPanelFrame(QSolutionToSolvePanel):

    def __init__(   self,
                    name : str="A name",
                    summary : str="A summary",
                    description : str="A description",
                    default_parameters : Optional[Parameters]=None,
                    tmp_ranges : Optional[np.ndarray]=None,
                    vertical_control_panel : QxVerticalControlPanel=None,
                    visualisation_panel : QxVisualizationPanel=None,
                    parent : QWidget=None):

        super().__init__(parent)
        
        self.__name = name
        self.__summary = summary
        self.__description = description
        
        self.__tmp_ranges = np.zeros((3,2)) if tmp_ranges is None else tmp_ranges
        
        self.__parameters = Parameters() if default_parameters is None else default_parameters

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
        return ProblemDefinition(domains=Domains(ranges=self.__tmp_ranges, names=("x", "y", "z")), fitness=FE())

    @property
    def default_parameters(self):
        return self.__parameters

    def _update_from_simulation(self, ga=None):
        if ga is None:
            return 
        pass
    
    @abstractmethod
    def draw_on_canvas(self, data):
        pass

class QxImageCloningPanel(QxSolutionPanelFrame):
    pass

class QxOpenBoxPanel(QxSolutionPanelFrame):
    
    def __init__(   self,
                    name: str = "Box Problem",
                    summary: str = "Box problem summary",
                    description: str = "Box problem description",
                    default_parameters: Optional[Parameters] = None,
                    parent: QWidget = None):

        self.__menu = []
        self.__widthscrollbar = ScrollValueButton("Width", (1, 100), 50, 50)
        self.__heightscrollbar = ScrollValueButton("Height", (1, 100), 50, 50)
        
        self.__default_parameters = Parameters() if default_parameters is None else default_parameters
        
        self.__menu.append(self.__widthscrollbar)
        self.__menu.append(self.__heightscrollbar)
        
        self.__qx_vertical_control_panel = QxVerticalControlPanel(menus=self.__menu)
        self.__qx_visualization_panel  = QxVisualizationPanel()
        
        self.draw_on_canvas(100)
        
        super().__init__(name, summary, description, self.__default_parameters, np.asarray([[0, min(self.__widthscrollbar.value, self.__heightscrollbar.value) / 2]], np.uint16), self.__qx_vertical_control_panel, self.__qx_visualization_panel, parent)
        # self.problem_definition.domains.ranges = np.asarray([0, int(min(self.__widthscrollbar.value, self.__heightscrollbar.value)) / 2], np.uint16)

    @property
    def problem_definition(self):
        return ProblemDefinition(domains=Domains(ranges=np.asarray([[0, min(self.__widthscrollbar.value, self.__heightscrollbar.value) / 2]], np.float16), names=("Coupe", )), fitness=OpenBoxFE(self.__widthscrollbar.value, self.__heightscrollbar.value))

    def draw_on_canvas(self, data):
        img = QImage(400, 400, QImage.Format_ARGB32)
        img.fill(QColor(0,0,0))
        painter = QPainter(img)
        painter.fill_rect(0, 0, data, data, "red")
        painter.fill_rect(400-data,0,data,data,"red")
        painter.fill_rect(0,400-data,data,data,"red")
        painter.fill_rect(400-data,400-data,data,data,"red")
        self.__qx_visualization_panel.image = img 
        painter.end()

        
class QxShapeTransformationPanel(QxSolutionPanelFrame):
    
     def __init__(self, name: str = "Shape shift problem", summary: str = "Shape shift summary", description: str = "Shape shift description", problem_definition: ProblemDefinition = ProblemDefinition(domains=Domains(ranges=np.zeros((3, 2)), names=("x", "y", "z")), fitness=OpenBoxFE()), default_parameters: Parameters = Parameters(), parent: QWidget = None):
        
        
        self.__width_label = QLabel("650")
        self.__height_label = QLabel("500")
        
        self.__form_list = [("Width : ",self.__width_label),("Height : ",self.__height_label)]     
        self.__width_height_form_layout = QxForm(self.__form_list)
        
        self.__obstacle_count_sb = ScrollValueButton("Obstacle Count : ", (0, 100),100, 50)
        self.__generate_obtacle_btn = QPushButton("Generate Obstacle")
        
        self.__shape_combobox = QComboBox()
        self.__shape_combobox.add_items(["Circle","Rectangle","Triangle"])
        self.__shape_combobox.set_fixed_width(250)
        self.__shape_form_layout = QxForm([("Shape : ", self.__shape_combobox)])
        
        
        self.__menu = [self.__width_height_form_layout,self.__obstacle_count_sb,self.__generate_obtacle_btn,self.__shape_form_layout]
        
        self.__qx_vertical_control_panel = QxVerticalControlPanel(menus=self.__menu)
        self.__qx_visualization_panel  = QxVisualizationPanel()

        super().__init__(name, summary, description, problem_definition, default_parameters, self.__qx_vertical_control_panel ,self.__qx_visualization_panel, parent)
        

class QxImageCloningPanel(QxSolutionPanelFrame):
    def __init__(self, name: str = "Image cloning problem", summary: str = "Image cloning summary", description: str = "Shape shift description", problem_definition: ProblemDefinition = ProblemDefinition(domains=Domains(ranges=np.zeros((3, 2)), names=("x", "y", "z")), fitness=FE()), default_parameters: Parameters = Parameters(), vertical_control_panel: QxVerticalControlPanel = None, visualisation_panel: QxVisualizationPanel = None, parent: QWidget = None):
        
        self.__width_label = QLabel("650")
        self.__height_label = QLabel("500")
        self.__form_list = [("Width : ",self.__width_label),("Height : ",self.__height_label)]
        self.__width_height_form_layout = QxForm(self.__form_list)        
        
        self.__pixels_count_sb = ScrollValueButton("Pixels Count : ", (0, 1000),100, 500)
        
        self.__image_combobox = QComboBox()
        self.__image_combobox.add_items(["Dali", "Picasso", "Van Gogh"])
        self.__image_form_layout = QxForm([("Image : ", self.__image_combobox)])
        
        self.__generate_img_btn = QPushButton("Generate Image")

        self.__menu = [self.__width_height_form_layout,self.__pixels_count_sb,self.__image_form_layout,self.__generate_img_btn]
        
        self.__qx_vertical_control_panel = QxVerticalControlPanel(menus=self.__menu)
        
        self.__qx_visualization_panel  = QxVisualizationPanel()
        
        super().__init__(name, summary, description, problem_definition, default_parameters, self.__qx_vertical_control_panel, self.__qx_visualization_panel, parent)
    

# ------------------------------------------------------------------------------------------ 
#  _______        _   _             
# |__   __|      | | (_)            
#    | | ___  ___| |_ _ _ __   __ _ 
#    | |/ _ \/ __| __| | '_ \ / _` |
#    | |  __/\__ \ |_| | | | | (_| |
#    |_|\___||___/\__|_|_| |_|\__, |
#                              __/ |
#                             |___/ 
# ------------------------------------------------------------------------------------------ 
if __name__ == "__main__":

    p = FE()
    print(p())

    obp = OpenBoxFE(50, 100)
    print(obp((14.25634434,0)))
# ------------------------------------------------------------------------------------------ 
