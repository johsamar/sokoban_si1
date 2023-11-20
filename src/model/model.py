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
import numpy as np
from utils.config import get_index

class SokobanModel(Model):

    def __init__(self, algorithm=None, heuristic=None, filename=None):
        self.schedule = RandomActivation(self)

        # Estructuras de datos para la búsqueda
        self.queue = Queue()        
        self.stack = []
        self.priority_queue = PriorityQueue()
        self.visited = set()
        self.final_path = {}

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
        self.start_position = robot_agent.pos

        # Lista para la sumar los nodos en la columna
        self.suma_nodos = np.zeros(self.width)

        # Agregar la posición inicial del robot a las estructuras de datos
        self.queue.put((self.start_position, 0))
        self.priority_queue.put((self.start_position, 0))
        self.stack.append((self.start_position, 0))
     
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
        if self.algorithm == Constans.UNIFORM_COST:
            self.costo_uniforme()
        elif self.algorithm == Constans.DFS:
            self.dfs()
        elif self.algorithm == Constans.BEAM_SEARCH:
            self.beam_search(beam_width=4)
        elif self.algorithm == Constans.A_STAR:
            self.a_star()
        if not self.finished:
            self.schedule.step()
        if self.finished:
            if self.found:
                maximo = self.suma_nodos.max()
                index = get_index(self.suma_nodos, maximo)
                print("La columna con mas nodos es: " + str(index) + " con "+ str(maximo))
                print("Caminos: ", self.final_path)
                print("Se encontró la meta")
                path = list(reversed(self.get_final_path(self.start_position, self.goal_position)))
                print("path", path )
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
                            self.final_path[neighbor] = current
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
                self.suma_nodos[current[0]] += 1
                print(f"Visitado: {self.visited}")
                print("suma: " + str(self.suma_nodos))
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
                            self.final_path[neighbor] = current

            print(f"Pila: {self.stack}")
        else:
            self.finished = True
            
    def costo_uniforme(self):
        if not self.finished:
            if not self.queue.empty():
                current, step = self.queue.get()

                # Si el nodo actual es la meta, establece los indicadores y finaliza
                if current == self.goal_position:
                    self.finished = True
                    self.found = True

                print(f"Paso actual: {current}")
                print(f"Vecinos: {self.grid.get_neighborhood(current, moore=False, include_center=False)}")
                
                if current not in self.visited:
                    self.visited.add(current)

                    # Obtén los vecinos del nodo actual
                    neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                    for neighbor in neighbors:
                        # Verificar si el vecino es un camino libre
                        contents = self.grid.get_cell_list_contents([neighbor])
                        is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                        is_box = any(isinstance(obj, BoxAgent) for obj in contents)

                        if not is_rock and not is_box and neighbor not in self.visited:
                            # Calcular el costo de moverse al vecino
                            cost = self.calculate_cost(neighbor)

                            # Actualizar el costo total
                            total_cost = step + cost

                            self.queue.put((neighbor, total_cost))
                            self.final_path[neighbor] = current
        else:
            self.finished = True

    def calculate_cost(self, position):
        # En este ejemplo, el costo de movimiento es 10 para cualquier dirección
        return 10
        

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
                        self.final_path[neighbor] = current


                # Ordenar vecinos por heurística y tomar los primeros "beam_width"
                neighbors_sorted = [neighbor for neighbor, _ in sorted(neighbors_with_heuristics, key=lambda x: x[1])[:beam_width]]

                print(f"Vecinos: {neighbors_sorted} del {current}")

                for neighbor in neighbors_sorted:
                    if neighbor not in self.visited:
                        self.priority_queue.put((neighbor, step + 1))
                        
            print(f"Cola: {self.priority_queue.queue}")
        else:
            self.finished = True

    def a_star(self):
        if not self.finished:
            if not self.priority_queue.empty():
                current, g_cost = self.priority_queue.get()

                if current == self.goal_position:
                    self.finished = True
                    self.found = True

                print(f"Current: {current}")

                if current not in self.visited:
                    self.visited.add(current)

                    neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                    for neighbor in neighbors:
                        contents = self.grid.get_cell_list_contents([neighbor])
                        is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                        is_box = any(isinstance(obj, BoxAgent) for obj in contents)

                        if not is_rock and not is_box and neighbor not in self.visited:
                            # Calcular el costo de movimiento
                            movement_cost = self.calculate_cost(neighbor)
                            # Calcular la heurística
                            heuristic = self.grid.get_cell_list_contents([neighbor])[0].heuristic
                            # Calcular el costo total: f(n) = g(n) + h(n)
                            total_cost = g_cost + movement_cost + heuristic

                            self.priority_queue.put((neighbor, g_cost + movement_cost))
                            self.final_path[neighbor] = current
            else:
                self.finished = True

    def get_final_path(self, initial, goal):
        finish = True
        path = [goal]
        parent = goal
        while finish:
            parent = self.final_path[parent]
            path.append(parent)
            if parent == initial:
                finish = False
        return path