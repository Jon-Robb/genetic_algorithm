import sys
from jaat_pack import *
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
    ga_app.add_mutation_strategy(DoubleGeneMutationStrategy)
    ga_app.add_mutation_strategy(AllGenesRandomMutationStrategy)
    ga_app.add_mutation_strategy(SingleCloseMutationStrategy)
    ga_app.add_mutation_strategy(AllGenesCloseMutationStrategy)
    ga_app.add_mutation_strategy(AllGenesFarMutationStrategy)
    ga_app.add_mutation_strategy(MutateAllGenesThirdGrowsOnly)
    ga_app.add_mutation_strategy(ShapeTransformationUltimateMutationStrategy)


    # --------------------------------------------------------
    # <Votre code ici>
    
    # --------------------------------------------------------
    # ajout de vos panneaux de résolution de problème (exemple) :
    # ga_app.add_solution_panel(QxOpenBoxPanel())
    # ga_app.add_solution_panel(QxShapeTransformationPanel())
    # ga_app.add_solution_panel(QxImageCloningPanel())
    # --------------------------------------------------------
    # <Votre code ici>
    
    open_box_problem = QxOpenBoxPanel()
    shape_transformation_problem = QxShapeTransformationPanel()
    image_cloning_problem = QxImageCloningPanel()
    
    ga_app.add_solution_panel(open_box_problem)
    ga_app.add_solution_panel(shape_transformation_problem)
    ga_app.add_solution_panel(image_cloning_problem)


    ga_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()