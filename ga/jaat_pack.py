from abc import abstractmethod
from gacvm import Domains, Parameters, ProblemDefinition, MutationStrategy, GeneMutationStrategy
from gaapp import QSolutionToSolvePanel
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import numpy as np
from typing import Optional
from uqtwidgets import QImageViewer
from uqtgui import *
import random
from PIL import Image
from PIL.ImageQt import ImageQt
from os import listdir, path
from pathlib import Path

from __feature__ import snake_case, true_property
#  __    __  .___________. __   __       __  .___________. __   _______     _______.
# |  |  |  | |           ||  | |  |     |  | |           ||  | |   ____|   /       |
# |  |  |  | `---|  |----`|  | |  |     |  | `---|  |----`|  | |  |__     |   (----`
# |  |  |  |     |  |     |  | |  |     |  |     |  |     |  | |   __|     \   \    
# |  `--'  |     |  |     |  | |  `----.|  |     |  |     |  | |  |____.----)   |   
#  \______/      |__|     |__| |_______||__|     |__|     |__| |_______|_______/                                                                                                                                           
class Utils():
    """
    This class contains a method used to clamp a value between a min and max value.
    """          
    def clamp(value, min, max):
        return max(min(value, max), min)

    def clamp_max(value, max):
        return min(value, max)
    
    def clamp_min(value, min):
        return max(value, min)
    
    def readfile(filename:str)->list:
        data = []
        with open(filename, 'r') as file:
            for line in file:
                data.append(line)
        return data
    
    def transform_shape(shape:QPolygonF, translation_x, translation_y, rotation, scaling):
        transformation = QTransform()
        transformation.translate(translation_x, translation_y)
        transformation.rotate(rotation)
        transformation.scale(scaling, scaling)
        return transformation.map(shape)
        

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

    def __call__(self, data):
        return self.fitness_evaluation(data)

    def fitness_evaluation(self, data):
        width = self.__width
        length = self.__length
        cut_length = data[0]
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
    def __init__(self, polygone:QPolygon=None, obstacles:list[QPoint]=None, container:QRect=None):
        
        self.__polygone = polygone
        self.__obstacles = obstacles
        self.__container = container
        
    def __call__(self, data):
        return self.fitness_evaluation(data)    
    
    def fitness_evaluation(self, data):
      
        polygone = Utils.transform_shape(self.__polygone, data[0], data[1], data[2], data[3])
                       
        for obstacle in self.__obstacles:
            if polygone.contains_point(obstacle, Qt.OddEvenFill):
                return 0
        if not self.__container.contains(polygone.bounding_rect()):
            return 0
        
        return area_from_QPolygonF(polygone)
    
        
class ImageCloningFE(FE):
    def __init__(self, image_array:np.ndarray=None):
        
        self.__image_array = image_array
            
    def __call__(self, data):
        return self.fitness_evaluation(data)
    
    def fitness_evaluation(self, data):
        
        max_distance = np.sum(np.maximum(abs(self.__image_array - 255), 255 - self.__image_array))
        distance = np.sum(abs(self.__image_array - data))
        
        return abs(distance - max_distance)
        
               
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
class AllGenesCloseMutationStrategy(MutationStrategy):
    '''
    Lorsqu'une mutation a lieu, tous les gènes sont modifiés près de leur valeur actuelle selon le domaine.
    '''
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Mutate All Genes (Close)'

    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                for i in range(0, offsprings.shape[1]):
                    offspring[i] += self._rng.choice([domains.random_value(i) * 0.01, domains.random_value(i) * -0.01])
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)
        

class AllGenesFarMutationStrategy(MutationStrategy):
    '''
    Lorsqu'une mutation a lieu, tous les gènes sont modifiés loin de leur valeur actuelle selon le domaine.
    '''

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Mutate All Genes (Far)'

    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                for i in range(0, offsprings.shape[1]):
                    offspring[i] += self._rng.choice([domains.random_value(i) * 0.9, domains.random_value(i) * -0.9])
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)


class SingleCloseMutationStrategy(MutationStrategy):
    '''
    Lorsqu'une mutation a lieu, un seul gène est généré près de sa valeur actuelle selon le domaine. Le gène modifié est déterminé aléatoirement parmi tous les gènes.
    '''

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Mutate Single Gene (Close)'

    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                index = self._rng.integers(0, offsprings.shape[1])
                offspring[index] += self._rng.choice([domains.random_value(index) * 0.1, domains.random_value(index) * -0.1])
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)


class MutateAllGenesThirdGrowsOnly(MutationStrategy):
    def __init__(self):
        super().__init__()
        
    @staticmethod
    def name():
        return 'Mutate All Genes (Third Grows Only)'
        
    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                for i in range(0, offsprings.shape[1]):
                    if i == 3:
                        offspring[i] += domains.random_value(i) 	             
                    else:
                        offspring[i] = domains.random_value(i)
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)
        
        
class ShapeTransformationUltimateMutationStrategy(MutationStrategy):
    def __init__(self):     
        super().__init__()
        
        self.__third_grows_only = MutateAllGenesThirdGrowsOnly()
        self.__all_genes_close = AllGenesCloseMutationStrategy()
        
    @staticmethod
    def name():
        return 'Shape Transformation Ultimate Mutation Strategy'
   
    def mutate(self, offsprings, mutation_rate, domains):
        if self._rng.random() <= 0.5:
            self.__third_grows_only.mutate(offsprings, mutation_rate, domains)        
        else:
            self.__all_genes_close.mutate(offsprings, mutation_rate, domains)
                       
            
class ImageCloningUltimateMutationStrategy(MutationStrategy):
    def __init__(self):
        super().__init__()
              
    @staticmethod
    def name():
        return 'Image Cloning Ultimate Mutation Strategy'
        
    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                mutating_genes = np.random.choice([True, False], offspring.shape[0], p=[1, 0])
                offspring = np.where(mutating_genes == True, domains.random_values(), offspring)                
          
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)
        

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
                index1, index2 = self._rng.integers(0, offsprings.shape[1], 2)
                offspring[index1] = domains.random_value(index1)
                offspring[index2] = domains.random_value(index2)
       
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)
        
        
class AllGenesRandomMutationStrategy(MutationStrategy):
    '''
    Lorsqu'une mutation a lieu,  tous les gènes sont générés aléatoirement selon le domaine. Les gènes modifiés sont déterminés aléatoirement parmi tous les gènes.
    '''

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Mutate All Genes'

    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                for i in range(0, offsprings.shape[1]):
                    offspring[i] = domains.random_value(i)

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
    
    def __init__(self, title:str, range:tuple, fixed_widget_length:int = 50,init:int=None, parent=None, step_value:int=1, prefix:str='', suffix:str=''):
        super().__init__(parent)
        self.__prefix = prefix
        self.__suffix = suffix
        
        self.tool_tip = 'Valeur de ' + title
        
        if init is None:
            init = round(sum(range) / 2)
        else:
            init = max(range[0], min(init, range[1]))
            
        title_label = QLabel()
        self.__sb = QScrollBar()
        self.__value_label = QLabel()

        title_label.text = title
        title_label.set_fixed_width(fixed_widget_length)

        self.__sb.minimumWidth = 2 * fixed_widget_length
        self.__sb.set_orientation(Qt.Horizontal)
        self.__sb.set_range(range[0], range[1])
        self.__sb.set_value(init)

        self.__step_value = step_value
        
        self.__value_label.set_fixed_width(fixed_widget_length)
        self.__value_label.alignment = Qt.AlignCenter
        self.update(init)
        
        self.__sb.valueChanged.connect(self.update)
        self.__sb.valueChanged.connect(self.valueChanged)

        layout = QHBoxLayout()
        layout.add_widget(title_label)
        layout.add_widget(self.__sb)
        layout.add_widget(self.__value_label)
        
        self.set_layout(layout)
        
        self.set_contents_margins(0, 0, 0, 0)
    
    def update(self, value:int):
        self.__value_label.text = self.__prefix + str(value*self.__step_value) + " " + self.__suffix

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
    def __init__(self, title: str, range: tuple, fixed_widget_length: int = 50, init: int = 50, parent=None, step_value: int = 1, prefix: str = '', suffix: str = ''):
        super().__init__(title, range, fixed_widget_length, init, parent, step_value, prefix, suffix)
        
        self.__init = init
        self.__button = QPushButton("!");
        self.__button.set_fixed_width(fixed_widget_length/2)
        self.__button.tool_tip = f'Reset to default value : {init}'
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
    
    @property
    def image_viewer(self):
        return self.__image_viewer
   

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
            self.draw_on_canvas() 
        else:
            self.draw_on_canvas(ga)
                   
    @abstractmethod
    def draw_on_canvas(self, data=None):
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
        
        self.draw_on_canvas()
        
        super().__init__(name, summary, description, self.__default_parameters, np.asarray([[0, min(self.__widthscrollbar.value, self.__heightscrollbar.value) / 2]], np.float16), self.__qx_vertical_control_panel, self.__qx_visualization_panel, parent)

    @property
    def problem_definition(self):
        return ProblemDefinition(domains=Domains(ranges=np.asarray([[0, min(self.__widthscrollbar.value, self.__heightscrollbar.value) / 2]], np.float16), names=("Coupe", )), fitness=OpenBoxFE(self.__widthscrollbar.value, self.__heightscrollbar.value))

    def draw_on_canvas(self, ga=None):
       
        canvas_width = self.__widthscrollbar.value
        canvas_height = self.__heightscrollbar.value
        
        box_offset_x = canvas_width * 0.05
        box_offset_y = canvas_height * 0.1
        box_width = canvas_width * 0.9
        box_height = canvas_height * 0.8
        img = QImage(canvas_width, canvas_height, QImage.Format_ARGB32)
        img.fill(QColor(0,0,0,0))
        painter = QPainter(img)
        painter.fill_rect(box_offset_x, box_offset_y,box_width,box_height,"blue")
      
        if ga is not None:
            for unit in ga.population:
                cut_lenght = unit[0]
                pen = QPen(QColor(68,72,242,255))
                pen.set_width(0.5)
                painter.set_pen(pen)
                painter.draw_rect(box_offset_x, box_offset_y, cut_lenght, cut_lenght)
                painter.draw_rect(box_width-cut_lenght+box_offset_x,box_offset_y,cut_lenght,cut_lenght)
                painter.draw_rect(box_offset_x,box_height + box_offset_y-cut_lenght,cut_lenght,cut_lenght)
                painter.draw_rect(box_width-cut_lenght+box_offset_x,box_height + box_offset_y- cut_lenght, cut_lenght,cut_lenght)
                    
            painter.fill_rect(box_offset_x, box_offset_y, ga.history.best_solution[0], ga.history.best_solution[0], "black")
            painter.fill_rect(box_width-ga.history.best_solution[0]+box_offset_x,box_offset_y,ga.history.best_solution[0],ga.history.best_solution[0],"black")
            painter.fill_rect(box_offset_x,box_height + box_offset_y-ga.history.best_solution[0],ga.history.best_solution[0],ga.history.best_solution[0],"black")
            painter.fill_rect(box_width-ga.history.best_solution[0]+box_offset_x,box_height + box_offset_y- ga.history.best_solution[0], ga.history.best_solution[0],ga.history.best_solution[0],"black")          
                    
        self.__qx_visualization_panel.image = img 
        painter.end()
        
        
class QxShapeTransformationPanel(QxSolutionPanelFrame):   
    def __init__(self, name: str = "Shape shift problem", summary: str = "Shape shift summary", description: str = "Shape shift description", default_parameters: Parameters = Parameters(), parent: QWidget = None):
               
        self.__width_label = QLabel("640")
        self.__height_label = QLabel("400")
        
        self.__form_list = [("Width : ",self.__width_label),("Height : ",self.__height_label)]     
        self.__width_height_form_layout = QxForm(self.__form_list)
        
        self.__obstacle_count_sb = ScrollValueButton("Obstacle Count : ", (0, 100),100, 50, suffix="obstacles")
        self.__generate_obstacle_btn = QPushButton("Generate Obstacle")

        self.__conteneur = QRectF(0,0,640,400)
        self.__rectangle = QPolygonF(QRectF(0,0, self.__conteneur.width(), self.__conteneur.height()))
        rectangle_bb = self.__rectangle.bounding_rect()
        rectangle_center = rectangle_bb.center()
        self.__rectangle.translate(-rectangle_center.x(), -rectangle_center.y())
        
        self.__triangle = QPolygonF([QPointF(0,0), QPointF(self.__conteneur.width(), 0), QPointF(self.__conteneur.width() / 2, self.__conteneur.height())])
        triangle_bb = self.__triangle.bounding_rect()
        triangle_center = triangle_bb.center()
        self.__triangle.translate(-triangle_center.x(), -triangle_center.y())
        
        self.__porygon = QPolygonF([QPointF(0,85), QPointF(15,80), QPointF(190,215), QPointF(310,140), QPointF(230,125), QPointF(200,60), QPointF(245,10), QPointF(370,5), QPointF(480,35), QPointF(640,125), QPointF(640,140), QPointF(580,145), QPointF(425,150), QPointF(530, 235), QPointF(495,280), QPointF(570, 325), QPointF(600, 385), QPointF(580, 395), QPointF(380,365), QPointF(370, 345), QPointF(275, 360), QPointF(260,345), QPointF(185,365), QPointF(55,375), QPointF(25, 365), QPointF(70,300), QPointF(115,260), QPointF(0,95)])
        porygon_bb = self.__porygon.bounding_rect()
        porygon_center = porygon_bb.center()
        self.__porygon.translate(-porygon_center.x(), -porygon_center.y())
        
        self.__current_shape = self.__rectangle
        
        self.__shape_combobox = QComboBox()
        self.__shape_combobox.add_items(["Rectangle","Triangle","Porygon"])
        self.__shape_combobox.set_fixed_width(250)
        self.__shape_form_layout = QxForm([("Shape : ", self.__shape_combobox)])
        self.__panel_thumbnail = QImageViewer()
        self.__panel_thumbnail.minimum_height = 200
        
        self.__temp_ranges = np.asarray([[0, 650], 
                                  [0, 500],
                                  [0, 360],
                                  [0, 1]], np.float32)
        
        
        self.__menu = [self.__width_height_form_layout,self.__obstacle_count_sb,self.__generate_obstacle_btn,self.__shape_form_layout, self.__panel_thumbnail]
        
        self.__qx_vertical_control_panel = QxVerticalControlPanel(menus=self.__menu)
        self.__qx_visualization_panel  = QxVisualizationPanel()
        self.__qx_visualization_panel.image_viewer.image = QImage(int(self.__conteneur.width()), int(self.__conteneur.height()), QImage.Format_ARGB32)

        self.__thumbnail_img = QImage(int(self.__conteneur.width()), int(self.__conteneur.height()), QImage.Format_ARGB32)
        self.__thumbnail_img.fill(QColor(0,0,0,255))

        self.__visualization_img = QImage(int(self.__conteneur.width()), int(self.__conteneur.height()), QImage.Format_ARGB32)
        self.__visualization_img.fill(QColor(0,0,0,255))
        
        self.__obstacles = []
        self.update_obstacles(self.__obstacle_count_sb.value * self.__obstacle_count_sb.step_value)
        self.draw_obstacles()
        self.draw_thumbnail(self.__panel_thumbnail)

        # connections
        self.__obstacle_count_sb.valueChanged.connect(self.generate_obstacles)
        self.__generate_obstacle_btn.clicked.connect(self.generate_obstacles) 
        self.__shape_combobox.currentTextChanged.connect(self.update_shape)

        super().__init__(name, summary, description, default_parameters, self.__temp_ranges,  self.__qx_vertical_control_panel ,self.__qx_visualization_panel, parent)

    @Slot()    
    def update_shape(self, value):
        self.change_shape(value)
        self.draw_thumbnail(self.__panel_thumbnail)

    def change_shape(self, value):

        if value == "Rectangle":
            self.__current_shape = self.__rectangle
        elif value == "Triangle":
            self.__current_shape = self.__triangle
        elif value == "Porygon":
            self.__current_shape = self.__porygon
        else:
            raise ValueError("Unknown shape")

    @Slot()
    def generate_obstacles(self):
        self.update_obstacles(self.__obstacle_count_sb.value * self.__obstacle_count_sb.step_value)
        self.draw_obstacles()
    
    def update_obstacles(self, value):
        self.__obstacles.clear()
        for _ in range(self.__obstacle_count_sb.step_value * value):
            self.__obstacles.append(QPointF(random.randrange(0,self.__conteneur.width() + 1),random.randrange(0,self.__conteneur.height() + 1)))

    def draw_obstacles(self, fill: bool = True):
        if fill:
            self.__visualization_img.fill(QColor(0,0,0,255))
        painter = QPainter(self.__visualization_img)
        pen = QPen(QColor(255,255,255,255))
        painter.set_pen(pen)
        for obstacle in self.__obstacles:
            painter.draw_rect(obstacle.x(),obstacle.y(),1 ,1)
        self.__qx_visualization_panel.image_viewer.image = self.__visualization_img
        painter.end()
      
    @property
    def problem_definition(self):
        return ProblemDefinition(domains=Domains(ranges=self.__temp_ranges, names=("translation_x", "translation_y", "rotation", "scaling")), fitness=ShapeTransformationFE(self.__current_shape, self.__obstacles, self.__conteneur))

    def draw_thumbnail(self, canevas:QImageViewer):
     
        img = QImage(161, 100, QImage.Format_ARGB32)
        temp_shape = self.__current_shape
        transform = QTransform()
        transform.scale(0.2,0.2)
        temp_shape = transform.map(temp_shape)
        self.__thumbnail_img = img
            

        img.fill(QColor(0,0,0,255))
        painter = QPainter(img)
        pen = QPen(QColor(128,0,128,255))
        painter.set_pen(pen)
        painter.draw_polygon(temp_shape)
        canevas.image = img
        painter.end()
    
    def draw_on_canvas(self, ga=None):

        self.__visualization_img.fill(QColor(0,0,0,255))

        if ga:
            painter = QPainter(self.__visualization_img)
            pen = QPen(QColor(128,0,128,255))
            pen.set_width(2)
            painter.set_pen(pen)
            for unit in ga.population:
                shape = Utils.transform_shape(self.__current_shape, unit[0], unit[1], unit[2], unit[3])
                painter.draw_polygon(shape)

            shape = Utils.transform_shape(self.__current_shape, ga.history.best_solution[0], ga.history.best_solution[1], ga.history.best_solution[2], ga.history.best_solution[3])
            shape = shape.to_polygon()
            pen = QPen(QColor(0,255,0,255))
            brush = QBrush(QColor(0,127,0,255))
            pen.set_width(2)
            painter.set_brush(brush)
            painter.set_pen(pen)
            painter.draw_polygon(shape)
            self.__qx_visualization_panel.image_viewer.image = self.__visualization_img

            painter.end()
            
        self.draw_obstacles(fill=False)


class QxImageCloningPanel(QxSolutionPanelFrame):
    def __init__(self, name: str = "Image cloning problem", summary: str = "Image cloning summary", description: str = "Image cloning description",  default_parameters: Parameters = Parameters(), parent: QWidget = None):
        self.__width_label = QLabel("-")
        self.__height_label = QLabel("-")
        
        self.__form_list = [("Width : ",self.__width_label),("Height : ",self.__height_label)]
        self.__width_height_form_layout = QxForm(self.__form_list)        
        
        self.__pixels_count_sb = ScrollValueButton("Image scale : ", (0, 200), 100, 100, suffix="%")
        
        self.__image_combobox = QComboBox() 
        self.__image_directory = "ga/images/"
        self.__arr_of_image_files = listdir(self.__image_directory)
        self.__arr_of_image = []
        
        for i in self.__arr_of_image_files:
            if i.endswith(".webp") or i.endswith(".png") or i.endswith(".jpg") or i.endswith(".jpeg"):   
                self.__arr_of_image.append(i)
                
        self.__image = self.__arr_of_image[0]
                
        self.__image_combobox.add_items(self.__arr_of_image)
        self.__image_form_layout = QxForm([("Image : ", self.__image_combobox)])
        self.__image_label = QLabel()
        self.__image_label.set_fixed_width(100)
        self.__image_label.set_fixed_height(100)
        
        # add image to label
        self.__image_combobox.currentTextChanged.connect(self.text_changed)     
        self.__load_image(self.__arr_of_image_files[0])
        
        self.__menu = [self.__width_height_form_layout,self.__pixels_count_sb,self.__image_form_layout,self.__image_label]
        
        self.__qx_vertical_control_panel = QxVerticalControlPanel(menus=self.__menu)       
        self.__qx_visualization_panel  = QxVisualizationPanel()
        
        super().__init__(name, summary, description, default_parameters, self.__temp_ranges, self.__qx_vertical_control_panel, self.__qx_visualization_panel, parent)

    def draw_on_canvas(self, ga=None):
        if ga:
            img = ga.history.best_solution.reshape(self.__img_arr.shape)
            # Array to Pillow Image
            img = Image.fromarray(img.astype('uint8'), 'RGB') 
            # Pillow Image to QImage
            self.__imgQt = QImage(ImageQt(img))

        else:
           #img = QImage()
            self.__imgQt = ImageQt(self.__image)   
            
        self.__qx_visualization_panel.image = self.__imgQt

    def __load_image(self, image_name):
        # On va chercher notre image
        self.__image = Image.open(self.__image_directory + image_name)
        
        # On transforme notre image en array numpy, puis on le flatten
        self.__img_arr = np.asarray(self.__image)
        arr_flat = self.__img_arr.flatten()
        
        # Set image with and height in the label
        self.__width_label.text = str(self.__img_arr.shape[1]) + " pixels"
        self.__height_label.text = str(self.__img_arr.shape[0]) + " pixels"
        
        # On crée un tableau de 2 colonnes range [0,255] et autant de lignes que de pixels
        self.__temp_ranges = np.full((arr_flat.shape[0], 2), [0, 255], np.float16)
        
        self.__domain_names = []
        for i in range(1, int(arr_flat.shape[0] / 3) + 1):
            for j in range(3):
                if j % 3 == 0:
                    self.__domain_names.append("R of pixel " + str(i))
                elif j % 3 == 1:
                    self.__domain_names.append("G of pixel " + str(i))
                else:
                    self.__domain_names.append("B of pixel " + str(i))
      
    def setting_image(self, text):
        newPixmap = QPixmap(self.__image_directory + text)
        self.__image_label.pixmap = newPixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation)
        
    @property
    def problem_definition(self):
        return ProblemDefinition(domains=Domains(ranges=self.__temp_ranges, names=self.__domain_names), fitness=ImageCloningFE(np.array(self.__image).flatten()))

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, image):
        self.__image = image

    @Slot()
    def text_changed(self, text):
        self.__load_image(text)
        self.setting_image(text)
        self.draw_on_canvas()


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
    
    print("Did you mean to run main.py?")
    
# ------------------------------------------------------------------------------------------ 
