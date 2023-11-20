from mesa import Model
from agent.robotAgent import RobotAgent
from agent.rockAgent import RockAgent
from agent.pathAgent import PathAgent
from agent.boxAgent import BoxAgent
from agent.finishAgent import FinishAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from utils.readfile import read_map
from queue import Queue, PriorityQueue
from helpers.load_agents import load_agents, calculate_all_heristic
from helpers.constants import Constans

class SokobanModel(Model):

    def __init__(self, algorithm=None, heuristic=None, filename=None):
        self.schedule = RandomActivation(self)

        # Estructuras de datos para la búsqueda
        self.queue = Queue()        
        self.stack = []
        self.priority_queue = PriorityQueue()
        self.visited = set()

        # Los flags de finalización y éxito
        self.finished = False
        self.found = False

        # Inicializa los parámetros del modelo
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.filename = filename

        # Carga el mapa
        self.map, self.width, self.height = read_map(filename)

        # Inicializa la cuadrícula con la altura y anchura del mapa
        self.grid = MultiGrid(self.width, self.height, True)

        # Carga los agentes
        load_agents(self.map, self, self.grid, self.schedule, self.width, self.height)

        # Obtener la posición de la meta, y el robot
        robot_agent = next(agent for agent in self.schedule.agents if isinstance(agent, RobotAgent))
        goal_agent = next(agent for agent in self.schedule.agents if isinstance(agent, FinishAgent))

        #Define la posición de la meta
        self.goal_position = goal_agent.pos

        calculate_all_heristic(self.heuristic, self.schedule, goal_agent)

        # Obtener la posición actual del robot
        start_position = robot_agent.pos

        # Agregar la posición inicial del robot a las estructuras de datos
        self.queue.put((start_position, 0))
        self.priority_queue.put((start_position, 0))
        self.stack.append((start_position, 0))
     
    def print_grid(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get_cell_list_contents([(x, y)])
                if len(cell) > 0:
                    for item in cell:
                        print(f'{item.__class__.__name__} en ({x}, {y})', end='')
                else:
                    print(f'Camino en ({x}, {y})', end='')
            print()

    def step(self) -> None:        
        # Realizar la búsqueda en anchura
        if self.algorithm == Constans.BFS:
            self.bfs()
        elif self.algorithm == Constans.DFS:
            self.dfs()
        elif self.algorithm == Constans.BEAM_SEARCH:
            self.beam_search(beam_width=2)

        if not self.finished:
            self.schedule.step()
        if self.finished:
            if self.found:
                print("Se encontró la meta")
            else:
                print("No se encontró la meta")

    def bfs(self):        
        if not self.queue.empty():
            current, step = self.queue.get()
            print(f"Current: {current}")
            if current == self.goal_position:
                self.finished = True
                self.found = True
            if current not in self.visited:
                self.visited.add(current)
                print(f"VIsitado: {self.visited}")

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}" )
                for neighbor in neighbors_sort:
                    # Obtener el agente que se encuentra en la posición vecina y verificar que no sea una roca 
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                    
                    if neighbor not in self.visited:
                        if(size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent)):
                            print("Vecino roca: ", neighbor)
                        else:
                            self.queue.put((neighbor, step + 1))
            print(f"Cola: {self.queue.queue}")
        else:
            self.finished = True
    
    def dfs(self):
        if len(self.stack) > 0:
            current, step = self.stack.pop()
            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True
                
            if current not in self.visited:
                self.visited.add(current)
                print(f"Visitado: {self.visited}")

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False )
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}")

                for neighbor in neighbors_sort:
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))

                    if neighbor not in self.visited:
                        if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                            print("Vecino roca: ", neighbor)
                        else:
                            self.stack.append((neighbor, step + 1))
            print(f"Pila: {self.stack}")
        else:
            self.finished = True

    def beam_search(self, beam_width):
        if not self.priority_queue.empty():
            current, step = self.priority_queue.get()
            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True

            if current not in self.visited:
                self.visited.add(current)
                print(f"Visitado: {self.visited}")

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                neighbors_with_heuristics = []

                for neighbor in neighbors:
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                    if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                            print("Vecino roca: ", neighbor)
                    else:                    
                        heuristica = self.grid.get_cell_list_contents([neighbor])[0].heuristic
                        neighbors_with_heuristics.append((neighbor, heuristica))

                # Ordenar vecinos por heurística y tomar los primeros "beam_width"
                neighbors_sorted = [neighbor for neighbor, _ in sorted(neighbors_with_heuristics, key=lambda x: x[1])[:beam_width]]

                print(f"Vecinos: {neighbors_sorted} del {current}")

                for neighbor in neighbors_sorted:
                    if neighbor not in self.visited:
                        self.priority_queue.put((neighbor, step + 1))
            print(f"Cola: {self.priority_queue.queue}")
        else:
            self.finished = True