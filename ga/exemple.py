from PySide6.QtWidgets import *
from PySide6.QtCore import *
from __feature__ import snake_case, true_property
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
        self.__value_label.setNum(value * self.__step_value)

    @Slot()
    def set_value(self, value):
        self.__sb.value = value
        
    @property
    def value(self):
        return self.__sb.value()
    
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
