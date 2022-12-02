import sys
from jaat_components import *
import gaapp



from gaapp import QSolutionToSolvePanel
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from __feature__ import snake_case, true_property

def main():
    
    QApplication.set_attribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    ga_app = gaapp.QGAApp()

    # --------------------------------------------------------
    # ajout de vos stratégies (exemple) :
    # ga_app.add_crossover_strategy(my_awesome_strategy)
    ga_app.add_mutation_strategy(DoubleGeneMutationStrategy())
    # --------------------------------------------------------
    # <Votre code ici>
    
    # --------------------------------------------------------
    # ajout de vos panneaux de résolution de problème (exemple) :
    # ga_app.add_solution_panel(BoxParameters()dans exemple.py)
    # ga_app.add_solution_panel(probleme_2)
    # ga_app.add_solution_panel(probleme_3)
    # --------------------------------------------------------
    # <Votre code ici>
    
    test_panel = BoxProblemSolutionFramePanel()
    ga_app.add_solution_panel(test_panel)

    # open_box_problem = QxOpenBoxPanel()
    # shape_transformation_problem = QxShapeTransformationPanel()
    # image_cloning_problem = QxImageCloningPanel()
    # ga_app.add_solution_panel(open_box_problem)
    # ga_app.add_solution_panel(shape_transformation_problem)
    # ga_app.add_solution_panel(image_cloning_problem)


    ga_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()