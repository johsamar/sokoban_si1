from mesa import Model
from agent.robotAgent import RobotAgent
from agent.rockAgent import RockAgent
from agent.pathAgent import PathAgent
from agent.boxAgent import BoxAgent
from agent.finishAgent import FinishAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from utils.readfile import read_map
from queue import Queue
from helpers.load_agents import load_agents
from helpers.constants import Constans

class SokobanModel(Model):

    def __init__(self, algorithm=None, heuristic=None, filename=None):
        self.schedule = RandomActivation(self)

        self.queue = Queue()
        self.stack = []
        self.visited = set()

        self.finished = False
        self.found = False

        self.algorithm = algorithm
        self.heuristic = heuristic
        self.filename = filename

        # Carga el mapa
        self.map, self.width, self.height = read_map(filename)

        # Inicializa la cuadrícula con la altura y anchura del mapa
        self.grid = MultiGrid(self.width, self.height, True)

        # Carga los agentes
        load_agents(self.map, self, self.grid, self.schedule, self.width, self.height)

        robot_agent = next(agent for agent in self.schedule.agents if isinstance(agent, RobotAgent))
        goal_agent = next(agent for agent in self.schedule.agents if isinstance(agent, FinishAgent))
        self.goal_position = goal_agent.pos

        # Obtener la posición actual del robot
        start_position = robot_agent.pos
        self.queue.put((start_position, 0))
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
            
    # Calcula la heuristica entre la caja y la meta          
    def calculate_heuristic(self, box_position, finish_position):
        if self.heuristic == 'Manhattan':
            # Cálculo de la distancia de Manhattan entre la caja y la meta
            distance = abs(box_position[0] - finish_position[0]) + abs(box_position[1] - finish_position[1])
            return distance
        elif self.heuristic == 'Euclidiana':
            # Cálculo de la distancia euclidiana entre la caja y la meta
            distance = ((box_position[0] - finish_position[0])**2 + (box_position[1] - finish_position[1])**2)**0.5
            return distance     
            
            
        
            

    def step(self) -> None:        
        # Realizar la búsqueda en anchura
        if self.algorithm == Constans.BFS:
            self.bfs()
        if self.algorithm == Constans.UNIFORM_COST:
            self.costo_uniforme()

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
                neighbors_inv = list(reversed(neighbors))
                print(f"Vecinos: {neighbors_inv} del {current}" )
                for neighbor in neighbors_inv:
                    # Obtener el agente que se encuentra en la posición vecina y verificar que no sea una roca 
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))
                    
                    if neighbor not in self.visited:
                        if(size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent)):
                            print("Vecino: ", neighbor)
                        else:
                            self.queue.put((neighbor, step + 1))
            print(f"Cola: {self.queue.queue}")
        else:
            self.finished = True
    
    def dfs(self):
        if self.stack:
            current, step = self.stack.pop()

            if current == self.goal_position:
                return step

            if current[0] not in self.visited:
                self.visited.add(current[0])
                neighbors = self.grid.get_neighborhood(current, moore=False, include_center=False)
                
                for neighbor in neighbors:
                    size_agents = len(self.grid.get_cell_list_contents([neighbor]))

                    if neighbor not in self.visited:
                        if size_agents > 1 and isinstance(self.grid.get_cell_list_contents([neighbor])[1], RockAgent):
                            print("Vecino: ", neighbor)
                        else:
                            self.stack.append((neighbor, step + 1))
            print(f"Pila: {self.stack}")
            
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

    def calculate_cost(self, position):
        # En este ejemplo, el costo de movimiento es 10 para cualquier dirección
        return 10
