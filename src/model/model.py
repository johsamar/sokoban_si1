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
        self.priority_queue_a = PriorityQueue()
        self.visited = set()
        self.vsited_list = []
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
        self.priority_queue.put((0, self.start_position))
        self.priority_queue_a.put((0, self.start_position, 0))
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
        if self.algorithm == Constans.BFS and not self.finished:
            self.bfs()
        if self.algorithm == Constans.UNIFORM_COST and not self.finished:
            self.costo_uniforme()
        elif self.algorithm == Constans.DFS and not self.finished:
            # self.dfs()
            self.dfs2()
        elif self.algorithm == Constans.BEAM_SEARCH and not self.finished:
            self.beam_search(beam_width=4)
        elif self.algorithm == Constans.A_STAR and not self.finished:
            self.a_star()
        if not self.finished:
            self.schedule.step()
        if self.finished:
            if self.found:
                # maximo = self.suma_nodos.max()
                # index = get_index(self.suma_nodos, maximo)
                # print("La columna con mas nodos es: " + str(index) + " con "+ str(maximo))
                print("Se encontró la meta")
                print("orden de visitados: ", self.vsited_list)
                print("Cantidad de nodos visitados: ", len(self.visited))
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
                
                # añadir el orden de visitados
                self.increase_node(current)

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                # print(f"Vecinos: {neighbors_sort} del {current}" )
                for neighbor in neighbors_sort:
                    # Obtener el agente que se encuentra en la posición vecina y verificar que no sea una roca 
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                    
                    if neighbor not in self.visited:
                        if(size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent)):
                            # print("Vecino roca: ", neighbor)
                            pass
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

    def dfs2(self):
        if len(self.stack) > 0:
            current, step = self.stack.pop()
            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True
                
            if current not in self.visited:
                self.visited.add(current)
                # self.suma_nodos[current[0]] += 1
                # print(f"Visitado: {self.visited}")
                # print("suma: " + str(self.suma_nodos))
                
                # añadir el orden de visitados
                self.increase_node(current)

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False )
                #Organiza las prioridades de los vecinos
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}")
                neighbors_inv = list(reversed(neighbors_sort))
                for neighbor in neighbors_inv:
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
            if not self.priority_queue.empty():
                step, current = self.priority_queue.get()
                print(f"Current: {current}")
                # Si el nodo actual es la meta, establece los indicadores y finaliza
                if current == self.goal_position:
                    self.finished = True
                    self.found = True

                # print(f"Paso actual: {current}")
                # print(f"Vecinos: {self.grid.get_neighborhood(current, moore=False, include_center=False)}")
                
                if current not in self.visited:
                    self.visited.add(current)
                    
                    # añadir el orden de visitados
                    self.increase_node(current)

                    # Obtén los vecinos del nodo actual
                    neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                    
                    neighbors_sort = list(neighbors)
                    neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                    neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                    print(f"Vecinos: {neighbors_sort} del {current}")
                    # neighbors_inv = list(reversed(neighbors_sort))
                    # print(f"Vecinos inv: {neighbors_inv} del {current}")

                    for neighbor in neighbors_sort:
                        # Verificar si el vecino es un camino libre
                        contents = self.grid.get_cell_list_contents([neighbor])
                        is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                        is_box = any(isinstance(obj, BoxAgent) for obj in contents)

                        if not is_rock and not is_box and neighbor not in self.visited:
                            # Calcular el costo de moverse al vecino
                            cost = self.calculate_cost(neighbor)
                            print(f"Costo: {cost}")
                            # Actualizar el costo total

                            total_cost = step + cost

                            print(f"Costo total: {total_cost}")
                            self.priority_queue.put((total_cost, neighbor))
                            self.final_path[neighbor] = current
                    print(f"Cola: {self.priority_queue.queue}")
        else:
            self.finished = True

    def calculate_cost(self, position):
        # En este ejemplo, el costo de movimiento es 10 para cualquier dirección
        return 10
        

    def beam_search(self, beam_width):
        if not self.priority_queue.empty():
            step, current = self.priority_queue.get()
            print(f"Current: {current}")
            
            if current == self.goal_position:
                self.finished = True
                self.found = True

            if current not in self.visited:
                self.visited.add(current)
                print(f"Visitado: {self.visited}")
                 # añadir el orden de visitados
                self.increase_node(current)

                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                neighbors_sort = list(neighbors)
                neighbors_sort[1:3] = neighbors_sort[2:0:-1]
                neighbors_sort[-2:] = neighbors_sort[-1], neighbors_sort[-2]
                print(f"Vecinos: {neighbors_sort} del {current}")
                neighbors_inv = list(reversed(neighbors_sort))
                print(f"Vecinos inv: {neighbors_inv} del {current}")
                for neighbor in neighbors_inv:
                    if neighbor not in self.visited:
                        size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                        if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                                print("Vecino roca: ", neighbor)
                        else:           
                            heuristica = self.grid.get_cell_list_contents([neighbor])[0].heuristic
                            self.priority_queue.put((heuristica, neighbor))
                            self.final_path[neighbor] = current
                        
            print(f"Cola: {self.priority_queue.queue}")
        else:
            self.finished = True

    def a_star(self):
        if not self.finished:
            if not self.priority_queue_a.empty():
                g_cost, current, _ = self.priority_queue_a.get()

                if current == self.goal_position:
                    self.finished = True
                    self.found = True

                if current not in self.visited:
                    self.visited.add(current)
                    # añadir el orden de visitados
                    self.increase_node(current)

                    neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                    for neighbor in neighbors:
                        contents = self.grid.get_cell_list_contents([neighbor])
                        is_rock = any(isinstance(obj, RockAgent) for obj in contents)
                        is_box = any(isinstance(obj, BoxAgent) for obj in contents)

                        if not is_rock and not is_box and neighbor not in self.visited:
                            movement_cost = self.calculate_cost(neighbor)
                            heuristic = self.grid.get_cell_list_contents([neighbor])[0].heuristic
                            total_cost = g_cost + movement_cost + heuristic

                            self.priority_queue_a.put((total_cost, neighbor, g_cost + movement_cost))
                            self.final_path[neighbor] = current

            else:
                self.finished = True

    def get_final_path(self, initial, goal):
        finish = True
        path = [goal]
        parent = goal
        while finish:
            parent = self.final_path[parent]
            path.append((parent[0]-1, parent[1]-1))
            if parent == initial:
                finish = False
        return path
    
    def increase_node(self, current):
        self.vsited_list.append((current[0]-1, current[1]-1))
        # print(f"VIsitados: {self.visited}")
        # Obtener agentes en la posición actual
        floorAgent = self.grid.get_cell_list_contents([current])[0]
        #obtener el floorAgent de la posición actual
        floorAgent.set_state(len(self.visited))