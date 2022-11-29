from abc import ABC, abstractmethod
from enum import Enum
import numpy as np

import umath



#    ____                        _           
#   |  _ \  ___  _ __ ___   __ _(_)_ __  ___ 
#   | | | |/ _ \| '_ ` _ \ / _` | | '_ \/ __|
#   | |_| | (_) | | | | | | (_| | | | | \__ \
#   |____/ \___/|_| |_| |_|\__,_|_|_| |_|___/
#                                            
class Domains:
    '''
        Le domaine détermine, pour chaque dimension du problème, un interval donnant la plage de résolution du problème :
            - il est important de savoir que cet interval n'est pas forcé pendant la résolution du problème mais plutôt utilisé pour générer des valeurs aélatoires plausibles lorsque requis (initialisation et mutation principalement)
        Par exemple, pour un problème à 4 dimensions, il y aura 4 intervals

        En plus de donner les plages, un nom pour chaque dimension doit être donné.

        Indirectement, cette classe donne aussi la dimension du problème.

        Les types attendus sont : 
            - ranges : numpy.ndarray de float64
                - r lignes (où r est le nombre de dimension)
                - 2 colonnes donnant : le min et le max de l'interval pour cette dimension
            - names : un tuple Python de chaîne de caractères (doit toujours être un tuple - attention au problème à 1D => ('x',) <= la virgule est essentielle)
    '''

    def __init__(self, ranges, names):
        if not isinstance(ranges, np.ndarray):
            raise ValueError('Invalid input parameters in Domains : ranges must be an numpy.ndarray object.')
        if ranges.dtype not in (float, np.float16, np.float32, np.float64):#, np.float128):
            raise ValueError('Invalid input parameters in Domains : ranges must be a 2D numpy ndarray class of any float.')
        if ranges.ndim != 2:
            raise ValueError('Invalid input parameters in Domains : ranges must be a 2D numpy ndarray class.')
        if ranges.shape[0] <= 0 or ranges.shape[1] != 2:
            raise ValueError('Invalid input parameters in Domains : ranges must be a 2D numpy ndarray class with n x 2 describing n x 1D intervals.')
        if np.any(ranges[:,0] > ranges[:,1]):
            raise ValueError('Invalid input parameters in Domains : all range must describe a 1D interval with [min, max] such as min <= max.')
        if len(names) != ranges.shape[0]:
            raise ValueError('Invalid input parameters in Domains : one name must be available for each dimension.')
        self._ranges = ranges
        self._names = names
        self._rng = np.random.default_rng()

    def _scale_normalized(self, values):
        return values * (self._ranges[:,1] - self._ranges[:,0]) + self._ranges[:,0]

    def random_value(self, index):
        return self._rng.random() * (self._ranges[index,1] - self._ranges[index,0]) + self._ranges[index,0]

    def random_values(self):
        return self._scale_normalized(self._rng.random(self._ranges.shape[0]))

    def random_population(self, size):
        return self._scale_normalized(self._rng.random((size, self._ranges.shape[0])))

    @property
    def ranges_span(self):
        return self._ranges[:,1] - self._ranges[:,0]

    @property
    def ranges(self):
        return self._ranges

    @property
    def names(self):
        return self._names

    @property
    def dimension(self):
        return self._ranges.shape[0]


#    ____            _     _                ____        __ _       _ _   _             
#   |  _ \ _ __ ___ | |__ | | ___ _ __ ___ |  _ \  ___ / _(_)_ __ (_) |_(_) ___  _ __  
#   | |_) | '__/ _ \| '_ \| |/ _ \ '_ ` _ \| | | |/ _ \ |_| | '_ \| | __| |/ _ \| '_ \ 
#   |  __/| | | (_) | |_) | |  __/ | | | | | |_| |  __/  _| | | | | | |_| | (_) | | | |
#   |_|   |_|  \___/|_.__/|_|\___|_| |_| |_|____/ \___|_| |_|_| |_|_|\__|_|\___/|_| |_|
#                                                                                      
class ProblemDefinition:
    '''
    Cette classe encapsule les 2 données fondamentales qui définissent un problème à résoudre :
        - le domaine : voir la définition de la classe pour plus de détail
        - la 'fitness' : une fonction faisant l'évaluation de la performance relative d'une solution
    '''

    def __init__(self, domains, fitness):
        if not isinstance(domains, Domains):
            raise ValueError('Invalid input parameters in ProblemDefinition : domains must be an Domains object.')
        if not callable(fitness): # to do : validate function signature detection?!
            raise ValueError('Invalid input parameters in ProblemDefinition : fitness must be callable.')

        self._domains = domains
        self._fitness = fitness

    @property
    def domains(self):
        return self._domains

    @property
    def fitness(self):
        return self._fitness

    @property
    def dimension(self):
        return self._domains.dimension



#       _    _         _                  _         _             _             _           
#      / \  | |__  ___| |_ _ __ __ _  ___| |_   ___| |_ _ __ __ _| |_ ___  __ _(_) ___  ___ 
#     / _ \ | '_ \/ __| __| '__/ _` |/ __| __| / __| __| '__/ _` | __/ _ \/ _` | |/ _ \/ __|
#    / ___ \| |_) \__ \ |_| | | (_| | (__| |_  \__ \ |_| | | (_| | ||  __/ (_| | |  __/\__ \
#   /_/   \_\_.__/|___/\__|_|  \__,_|\___|\__| |___/\__|_|  \__,_|\__\___|\__, |_|\___||___/
#                                                                         |___/             

class Strategy(ABC):
    def __init__(self):
        self._rng = np.random.default_rng()

    @staticmethod
    @abstractmethod
    def name():
        raise NotImplementedError()
    
class SelectionStrategy(Strategy):
    '''
    Représente l'algorithme à utiliser pour la sélection de géniteurs.
    '''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def select(self, genitor, fitness_data, selection_rate, selection_size):
        '''
        Doit produire une liste de géniteurs sélectionnés :
            - genitor : la liste des géniteurs disponibles
            - fitness_data : les informations de performance triées

            - selection_rate : taux de sélection
            - taille de sélection

        genitor a la structures : ndarray
            - r lignes représentants tous les géniteurs
            - c colonnes représentants les gènes du chromosome (une valeur pour chaque dimension du problème)
        fitness_data a la structure : ndarray de structure composée ainsi :
            - index : l'index du géniteur
            - value : l'indice de performance relative
            - cumul : la somme cumulative des performances relatives
        ATTENTION, l'ordre de genitor est indéterminé alors que fitness_data est trié en ordre de performance (du plus perf au moins perf)

        La fonction doit retourner une liste de selection_size géniteurs qui auront été sélectionnés en fonction de leur performance.
        '''                
        raise NotImplementedError()

class CrossoverStrategy(Strategy):
    '''
    Représente l'algorithme à utiliser pour le croisement entre des pairs de géniteurs permettant de produire des progénitures.
    '''    
    def __init__(self):
        super().__init__()

    @abstractmethod
    def breed(self, genitors_1, genitors_2, offsprings):
        '''
        Doit produire plusieurs progénitures à partir des 2 listes de géniteurs données :
            - genitors_1 : la liste des 1er géniteurs à utiliser
            - genitors_2 : la liste des 2e géniteurs à utiliser
            - genitors_1 : la liste des nouvelles progénitures à produire
        Les trois variables ont la même structures : ndarray
            - r lignes représentants le parent 1, le parent 2 et la nouvelle progéniture à produire
            - c colonnes représentants les gènes du chromosome (une valeur pour chaque dimension du problème)
        La création des progénitures doit se faire en place. Autrement dit, il faut modifier la variable passée pour chacune des n progénitures données.
        '''        
        raise NotImplementedError()

class MutationStrategy(Strategy):
    '''
    Représente l'algorithme à utiliser pour la mutation des progénitures.
    '''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def mutate(self, offsprings, mutation_rate, domains):
        '''
        Doit modifier les progénitures reçues en fonctions des paramètres reçus.
            - offspring : la liste de toutes les nouvelles progénitures
            - mutation_rate : pour chaque progénitures on évalue si une mutation a bien lieu (valeur aléatoire en deça de ce taux) 
            - domains : le domaine du problème (pour chaque dimension, la plage de valeurs possibles)
        offsprings a la structure suivante : ndarray
            - r lignes représentants les progénitures à considérer
            - c colonnes représentants les gènes du chromosome (une valeur pour chaque dimension du problème)
        '''
        raise NotImplementedError()



#    ____        __             _ _         _             _             _           
#   |  _ \  ___ / _| __ _ _   _| | |_   ___| |_ _ __ __ _| |_ ___  __ _(_) ___  ___ 
#   | | | |/ _ \ |_ / _` | | | | | __| / __| __| '__/ _` | __/ _ \/ _` | |/ _ \/ __|
#   | |_| |  __/  _| (_| | |_| | | |_  \__ \ |_| | | (_| | ||  __/ (_| | |  __/\__ \
#   |____/ \___|_|  \__,_|\__,_|_|\__| |___/\__|_|  \__,_|\__\___|\__, |_|\___||___/
#                                                                 |___/             

class RouletteWheelSelectionStrategy(SelectionStrategy):
    '''
    Sélectionne aléatoirement les parents selon la probabilité relative de leur performance par rapport aux autres.
    '''
    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Roulette Wheel'

    def select(self, genitor, fitness_data, selection_rate, selection_size):
        def select_each(rnd_val, fitness_data):
            return fitness_data[np.argmax(fitness_data[fitness_data['cumul'] <= max(fitness_data[0]['cumul'], rnd_val)]['cumul'])]['index']

        random_select = self._rng.random(selection_size) * selection_rate
        indices = np.apply_along_axis(select_each, 1, random_select[:,np.newaxis], fitness_data)
        return genitor[indices]

class WeightedAverageCrossoverStrategy(CrossoverStrategy):
    '''
    Produit une progéniture à partir d'une moyenne pondérée selon 2 géniteurs. La pondération est variable pour chaque dimension. 
    '''
    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Weighted Average'

    def breed(self, genitors_1, genitors_2, offsprings):
        weight = self._rng.random((genitors_2.shape[0],1))
        offsprings[:] = weight * genitors_1 + (1. - weight) * genitors_2

class GeneMutationStrategy(MutationStrategy):
    '''
    Lorsqu'une mutation a lieu, un seul gène est généré aléatoirement selon le domaine. Le gène modifié est déterminé aléatoirement parmi tous les gènes.
    '''

    def __init__(self):
        super().__init__()

    @staticmethod
    def name():
        return 'Mutate Single Gene'

    def mutate(self, offsprings, mutation_rate, domains):
        def do_mutation(offspring, mutation_rate, domains):
            if self._rng.random() <= mutation_rate:
                index = self._rng.integers(0, offsprings.shape[1])
                offspring[index] = domains.random_value(index)
        
        np.apply_along_axis(do_mutation, 1, offsprings, mutation_rate, domains)




#    ____                                _                
#   |  _ \ __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___ 
#   | |_) / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
#   |  __/ (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
#   |_|   \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
#                                                         
class Parameters:
    '''
    La classe Parameters représente tous les paramètres standards de l'algorithme génétique :
        - maximum_epoch : le nombre d'évolution maximum
        - population_size : la taille de la population
        - elitism_rate : le taux d'élitisme (% de la population)
        - selection_rate : le taux de sélection (% de la population - effectue la sélection parmi les x% meilleurs de la population)
        - mutation_rate : le taux de mutation (probabilité d'appliquer une mutation pour chaque descendant)
        
        - selection_strategy : stratégie de sélection (algorithme ou méthode de sélection)
        - crossover_strategy : stratégie de croisement (algorithme ou méthode de croisement)
        - mutation_strategy : stratégie de mutation (algorithme ou méthode de mutation)

    Il est donc possible de définir tous ces paramètres avant de lancer une résolution de problème avec l'algorithme génétique.
    '''
    def __init__(self, selection_strategy=RouletteWheelSelectionStrategy(), crossover_strategy=WeightedAverageCrossoverStrategy(), mutation_strategy=GeneMutationStrategy()):
        if not isinstance(selection_strategy, SelectionStrategy):
            raise ValueError('Invalid input parameters in Parameters : selection_strategy must be an SelectionStrategy object.')
        if not isinstance(crossover_strategy, CrossoverStrategy):
            raise ValueError('Invalid input parameters in Parameters : crossover_strategy must be an CrossoverStrategy object.')
        if not isinstance(mutation_strategy, MutationStrategy):
            raise ValueError('Invalid input parameters in Parameters : mutation_strategy must be an MutationStrategy object.')

        self._maximum_epoch = 1000

        self._population_size = 50
        self._elitism_rate = 0.05
        self._selection_rate = 0.6
        self._mutation_rate = 0.2
        
        self._selection_strategy = selection_strategy
        self._crossover_strategy = crossover_strategy
        self._mutation_strategy = mutation_strategy

        self._epsilon_min_fitness = 1.e-12

        self._engine_to_update = []
        
    @property
    def maximum_epoch(self) -> int:
        return self._maximum_epoch

    @maximum_epoch.setter
    def maximum_epoch(self, value: int):
        self._maximum_epoch = max(1, value)

    @property
    def population_size(self) -> int:
        return self._population_size

    @population_size.setter
    def population_size(self, value: int):
        self._population_size = max(5, value)
        for engine in self._engine_to_update:
            engine._setup()

    @property
    def elitism_rate(self) -> float:
        return self._elitism_rate

    @elitism_rate.setter
    def elitism_rate(self, value: float):
        self._elitism_rate = umath.clamp(0., value, 1.)

    @property
    def elitism_size(self) -> int:
        return int(np.round(self._elitism_rate * self._population_size))

    @property
    def selection_rate(self) -> float:
        return self._selection_rate

    @selection_rate.setter
    def selection_rate(self, value: float):
        self._selection_rate = umath.clamp(0., value, 1.)

    @property
    def mutation_rate(self) -> float:
        return self._mutation_rate

    @mutation_rate.setter
    def mutation_rate(self, value: float):
        self._mutation_rate = umath.clamp(0., value, 1.)

    @property
    def selection_strategy(self):
        return self._selection_strategy

    @selection_strategy.setter
    def selection_strategy(self, value):
        if not isinstance(value, SelectionStrategy):
            raise ValueError('Invalid input parameters in Parameters : selection_strategy must be an SelectionStrategy object.')
        self._selection_strategy = value

    @property
    def crossover_strategy(self):
        return self._crossover_strategy

    @crossover_strategy.setter
    def crossover_strategy(self, value):
        if not isinstance(value, CrossoverStrategy):
            raise ValueError('Invalid input parameters in Parameters : crossover_strategy must be an CrossoverStrategy object.')
        self._crossover_strategy = value

    @property
    def mutation_strategy(self):
        return self._mutation_strategy

    @mutation_strategy.setter
    def mutation_strategy(self, value):
        if not isinstance(value, MutationStrategy):
            raise ValueError('Invalid input parameters in Parameters : mutation_strategy must be an MutationStrategy object.')
        self._mutation_strategy = value



class Observer(ABC):
    @abstractmethod
    def update(self, engine):
        raise NotImplementedError()


#    _   _ _     _                   
#   | | | (_)___| |_ ___  _ __ _   _ 
#   | |_| | / __| __/ _ \| '__| | | |
#   |  _  | \__ \ || (_) | |  | |_| |
#   |_| |_|_|___/\__\___/|_|   \__, |
#                              |___/ 
class History:
    def __init__(self):
        self._last_epoch = -1

    def _setup(self, maximum_epoch, problem_dimension):
        self._last_epoch = -1
        self._best_solution_history = np.zeros((maximum_epoch, problem_dimension), dtype=np.float64)
        self._fitness_history = np.zeros((maximum_epoch, 5), dtype=np.float64) # best, worst, average, std dev, median
        self._epoch_ref = np.arange(maximum_epoch)

    def _log_history(self, best_solution, best_fitness, worst_fitness, average_fitness, std_dev_fitness, median_fitness):
        self._last_epoch += 1
        self._best_solution_history[self._last_epoch] = best_solution
        self._fitness_history[self._last_epoch, 0] = best_fitness
        self._fitness_history[self._last_epoch, 1] = worst_fitness
        self._fitness_history[self._last_epoch, 2] = average_fitness
        self._fitness_history[self._last_epoch, 3] = std_dev_fitness
        self._fitness_history[self._last_epoch, 4] = median_fitness

    @property
    def count(self):
        return self._last_epoch + 1

    @property
    def best_solution(self):
        return self._best_solution_history[self._last_epoch]

    @property
    def best_fitness(self):
        return self._fitness_history[self._last_epoch, 0]

    @property
    def worst_fitness(self):
        return self._fitness_history[self._last_epoch, 1]

    @property
    def average_fitness(self):
        return self._fitness_history[self._last_epoch, 2]

    @property
    def standard_deviation_fitness(self):
        return self._fitness_history[self._last_epoch, 3]

    @property
    def median_fitness(self):
        return self._fitness_history[self._last_epoch, 4]        

    @property
    def history(self):
        return self._fitness_history[:self._last_epoch,:]

    @property
    def epoch(self):
        return self._epoch_ref[:self._last_epoch]

    @property
    def gradient(self, average_size = 5):
        if self._last_epoch < average_size + 1:
            return None
        return np.average(self._fitness_history[self._last_epoch - average_size:self._last_epoch, 0] - self._fitness_history[self._last_epoch - average_size - 1:self._last_epoch - 1, 0])




#     ____                 _   _         _    _                  _ _   _               
#    / ___| ___ _ __   ___| |_(_) ___   / \  | | __ _  ___  _ __(_) |_| |__  _ __ ___  
#   | |  _ / _ \ '_ \ / _ \ __| |/ __| / _ \ | |/ _` |/ _ \| '__| | __| '_ \| '_ ` _ \ 
#   | |_| |  __/ | | |  __/ |_| | (__ / ___ \| | (_| | (_) | |  | | |_| | | | | | | | |
#    \____|\___|_| |_|\___|\__|_|\___/_/   \_\_|\__, |\___/|_|  |_|\__|_| |_|_| |_| |_|
#                                               |___/                                  

class GeneticAlgorithm:

    class State(Enum):
        IDLE    = 0 # (0, True, False, 'Start', 'Pause', 'RUNNING', 'IDLE', 'Idle')
        RUNNING = 1 # (1, True, True, 'Stop', 'Pause', 'IDLE', 'PAUSED', 'Running')
        PAUSED  = 2 # (2, True, True, 'Stop', 'Resume', 'IDLE', 'RUNNING', 'Paused')

    def __init__(self, problem_definition=None, parameters=Parameters()):
        if not isinstance(problem_definition, ProblemDefinition) and problem_definition is not None:
            raise ValueError('Invalid input value in GeneticAlgorithm.problem_definition property : value must be a ProblemDefinition object.')
        if not isinstance(parameters, Parameters):
            raise ValueError('Invalid input value in GeneticAlgorithm.parameters property : value must be a Parameters object.')

        self._fit_type = np.dtype([('index', np.int32), ('value', np.float64), ('cumul', np.float64)])
        self._rng = np.random.default_rng()
        self._observers = []
        
        self._state = GeneticAlgorithm.State.IDLE
        self._current_epoch = 0
        self._history = History()
        
        self._problem_definition = problem_definition
        self._parameters = parameters
        self._parameters._engine_to_update.append(self)

        if self._problem_definition is not None:
            self._setup()

    @property
    def is_ready(self):
        return self._problem_definition is not None

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        if not isinstance(value, Parameters):
            raise ValueError('Invalid input value in GeneticAlgorithm.parameters property : value must be a Parameters object.')
        if self in self._parameters._engine_to_update:
            self._parameters._engine_to_update.remove(self)
        self._parameters = value
        self._parameters._engine_to_update.append(self)
        self._setup()

    @property
    def problem_definition(self):
        return self._problem_definition

    @problem_definition.setter
    def problem_definition(self, value):
        if not isinstance(value, ProblemDefinition):
            raise ValueError('Invalid input value in GeneticAlgorithm.problem_definition property : value must be a ProblemDefinition object.')
        self._problem_definition = value
        self._setup()

    @property
    def history(self):
        return self._history

    @property
    def population(self):
        return self._genitors[self._genitors_fit['index']]

    @property
    def population_fitness(self):
        return self._genitors_fit['value']

    def add_observer(self, observer):
        if not isinstance(observer, Observer):
            raise ValueError('Observer must inherit from GAObserver.')
        self._observers.append(observer)

    def clear_observer(self):
        self._observers = []

    def _setup(self):
        if self._problem_definition is None:
            return
        
        self._current_epoch = 0
        self._population_1 = np.empty((self._parameters.population_size, self._problem_definition.dimension), dtype=np.float64)
        self._population_2 = np.empty((self._parameters.population_size, self._problem_definition.dimension), dtype=np.float64)
        self._genitors_fit = np.empty((self._parameters.population_size), dtype=self._fit_type)
        self._genitors_fit_index = np.arange(self._parameters.population_size) 
        self._genitors = self._population_1
        self._offsprings = self._population_2

    def _log_history(self):
        self._history._log_history( self._genitors[self._genitors_fit[0]['index']], # best solution
                                    self._genitors_fit[0]['value'], # best fitness
                                    self._genitors_fit[-1]['value'], # worst fitness
                                    np.average(self._genitors_fit['value']), # average fitness
                                    np.std(self._genitors_fit['value']), # standard deviation fitness
                                    np.median(self._genitors_fit['value'])) # median fitness

    def _initialize(self):
        self._state = GeneticAlgorithm.State.RUNNING
        self._current_epoch = 0
        self._history._setup(self._parameters.maximum_epoch, self._problem_definition.dimension)

        self._randomize(self._genitors)
        self._process_fitness()

        self._log_history()

    def _randomized_population(self):
        return self._problem_definition.domains.random_population(self._parameters.population_size)
    
    def _randomize(self, population):
        population[:] = self._randomized_population()

    def _process_fitness(self):
        self._genitors_fit['index'] = self._genitors_fit_index
        self._genitors_fit['value'] = np.apply_along_axis(self._problem_definition.fitness, 1, self._genitors)

        if np.any(self._genitors_fit['value'] < 0.):
            raise ValueError('Invalid fitness. Negative value generated by fitness function. All fitness value must be positive. Suggestion : adjust the fitness function such as all return values are greather or equal than zero for the specified domain.')
        if np.sum(self._genitors_fit['value']) <= self._parameters._epsilon_min_fitness:
            raise ValueError('Invalid fitness. All values are too close to zero. Suggestion : adjust the fitness function such as it returns some values greather than zero for the specified domain.')

        self._genitors_fit[::-1].sort(order='value')
        self._genitors_fit['cumul'] = np.cumsum(self._genitors_fit['value']) / np.sum(self._genitors_fit['value'])


    def _process_elitism(self):
        if self._parameters.elitism_size:
            self._offsprings[0:self._parameters.elitism_size] = self._genitors[self._genitors_fit[0:self._parameters.elitism_size]['index']]

    def _breed(self):
        g1 = self._parameters.selection_strategy.select(self._genitors, self._genitors_fit, self._parameters.selection_rate, self._parameters.population_size - self._parameters.elitism_size)
        g2 = self._parameters.selection_strategy.select(self._genitors, self._genitors_fit, self._parameters.selection_rate, self._parameters.population_size - self._parameters.elitism_size)
        self._parameters.crossover_strategy.breed(g1, g2, self._offsprings[self._parameters.elitism_size:])

    def _mutate(self):
        self._parameters.mutation_strategy.mutate(self._offsprings[self._parameters.elitism_size:], self._parameters.mutation_rate, self._problem_definition.domains)

    def _evolve_one(self):
        self._process_elitism()
        if self._parameters.elitism_size != self._parameters.population_size:
            self._breed()
            self._mutate()

        self._genitors, self._offsprings = self._offsprings, self._genitors
        self._process_fitness()

        self._current_epoch += 1
        self._log_history()

    def evolve(self):
        if self.is_ready:
            self._initialize()

            for _ in range(self._parameters.maximum_epoch - 1): # -1 because initialization is first epoch
                self._evolve_one()

                for obs in self._observers:
                    obs.update(self)

                while self._state == GeneticAlgorithm.State.PAUSED: # monothread simplification -> should be multithreaded or, at least, managed with Qt's signal --- this approach require resuming from an observer 
                    for obs in self._observers:
                        obs.update(self)

                if self._state == GeneticAlgorithm.State.IDLE:
                    return

    # def prepare_evolution_by_step(self):
    #     if self.is_ready:
    #         self._initialize()

    # def evolve_by_step(self):
    #     self._evolve_one()

    #     for obs in self._observers:
    #         obs.update(self)

    def stop(self):
        self._state = GeneticAlgorithm.State.IDLE

    def pause(self):
        self._state = GeneticAlgorithm.State.PAUSED

    def resume(self):
        self._state = GeneticAlgorithm.State.RUNNING

    def reset(self):
        self._history._setup(self._parameters.maximum_epoch, self._problem_definition.dimension)

    @property
    def state(self):
        return self._state

    @property
    def current_epoch(self):
        return self._current_epoch






