#     ___  _ __        ___     _            _               _   _ _ _ _   _           
#    / _ \| |\ \      / (_) __| | __ _  ___| |_ ___   _   _| |_(_) (_) |_(_) ___  ___ 
#   | | | | __\ \ /\ / /| |/ _` |/ _` |/ _ \ __/ __| | | | | __| | | | __| |/ _ \/ __|
#   | |_| | |_ \ V  V / | | (_| | (_| |  __/ |_\__ \ | |_| | |_| | | | |_| |  __/\__ \
#    \__\_\\__| \_/\_/  |_|\__,_|\__, |\___|\__|___/  \__,_|\__|_|_|_|\__|_|\___||___/
#                                |___/                                                



import math
import umath

from PySide6.QtCore import Qt, Slot, Signal, QSize, QPointF
from PySide6.QtWidgets import (QWidget, QLabel, QScrollBar, QPushButton,
                               QHBoxLayout)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QImage, QPixmap
from __feature__ import snake_case, true_property



def create_scroll_int_value(min_val, init_val, max_val, value_prefix = "", value_suffix = "", sb_min_width=150, value_width = 50, default_width = 25):
    '''to do : description'''

    min_val = min(min_val, max_val)
    max_val = max(min_val, max_val)
    init_val = umath.clamp(min_val, init_val, max_val)

    scroll_bar = QScrollBar()
    scroll_bar.orientation = Qt.Horizontal
    scroll_bar.set_range(min_val, max_val)
    scroll_bar.minimum_width = sb_min_width
    scroll_bar.value = init_val

    value_label = QLabel()
    value_label.set_fixed_width(value_width)
    value_label.alignment = Qt.AlignCenter
    value_label.set_buddy(scroll_bar)

    default_button = QPushButton('!')
    default_button.set_fixed_width(default_width)
    default_button.tool_tip = f'Reset to default value : {init_val}'

    layout = QHBoxLayout()
    layout.add_widget(scroll_bar)
    layout.add_widget(value_label)
    layout.add_widget(default_button)

    update_function = lambda value: setattr(value_label, 'text', f'{value_prefix}{value}{value_suffix}')
    update_function(init_val)
    scroll_bar.valueChanged.connect(update_function)
    default_button.clicked.connect(lambda : setattr(scroll_bar, 'value', init_val))

    return scroll_bar, layout

def create_scroll_real_value(min_val, init_val, max_val, precision, display_multiplier=1., value_prefix = "", value_suffix = "", sb_min_width=150, value_width = 50, default_width = 25):
    '''to do : description'''
    # >>> 2 functions are added to the scroll_bar object :
    #  - scroll_bar.set_real_value
    #  - scroll_bar.get_real_value
    # not entirely tested... to do

    min_val = min(min_val, max_val)
    max_val = max(min_val, max_val)
    init_val = umath.clamp(min_val, init_val, max_val)

    resolution = 10 ** precision
    resolution_format = round(precision - math.log10(display_multiplier))
    format_string = f'.{resolution_format}f' if resolution_format > 0 else 'g'
    scroll_bar = QScrollBar()
    scroll_bar.orientation = Qt.Horizontal
    scroll_bar.set_range(0, round((max_val - min_val) * resolution))
    scroll_bar.minimum_width = sb_min_width

    value_label = QLabel()
    value_label.set_fixed_width(value_width)
    value_label.alignment = Qt.AlignCenter
    value_label.set_buddy(scroll_bar)

    default_button = QPushButton('!')
    default_button.set_fixed_width(default_width)
    default_button.tool_tip = f'Reset to default value : {value_prefix}{init_val:{format_string}}{value_suffix}'

    layout = QHBoxLayout()
    layout.add_widget(scroll_bar)
    layout.add_widget(value_label)
    layout.add_widget(default_button)

    scroll_bar.set_real_value = lambda value : setattr(scroll_bar, 'value', round((value - min_val) * resolution))
    scroll_bar.get_real_value = lambda : scroll_bar.value / resolution + min_val
    update_function = lambda value: setattr(value_label, 'text', f'{value_prefix}{scroll_bar.get_real_value() * display_multiplier:{format_string}}{value_suffix}')
    
    scroll_bar.set_real_value(init_val)
    update_function(init_val)
    scroll_bar.valueChanged.connect(update_function)
    default_button.clicked.connect(lambda : scroll_bar.set_real_value(init_val))

    return scroll_bar, layout




class QImageViewer(QWidget):
    '''Widget utility showing an image. The image is always enabled.'''

    image_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.alignment = Qt.AlignCenter

        self._image = QImage(QSize(250,250), QImage.Format_ARGB32)
        

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self.update()

    @Slot()
    def changeImage(self, image):
        self.image = image
    
    def paint_event(self, event):
        painter = QPainter(self)
        painter.set_background(QBrush(QColor(64, 64, 64)))
        painter.set_pen(Qt.NoPen)
        # painter.set_pen(QPen(QColor(0, 0, 0), 1.))
        painter.set_brush(Qt.NoBrush)
        
        painter.erase_rect(self.rect)
        # painter.translate(self.rect.center())
        image = self._image.scaled(self.size, Qt.KeepAspectRatio, Qt.FastTransformation)
        painter.draw_image(QPointF((self.width - image.width())/2., (self.height - image.height())/2.), image)
        painter.end()




