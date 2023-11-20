from mesa import Model
from agent.robotAgent import RobotAgent
from agent.rockAgent import RockAgent
from agent.boxAgent import BoxAgent
from agent.finishAgent import FinishAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from utils.readfile import read_map

class SokobanModel(Model):

    def __init__(self, algorithm=None, heuristic=None, filename=None):
        self.schedule = RandomActivation(self)
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.filename = filename

        # Carga el mapa
        self.map, self.width, self.height = read_map(filename)

        # Inicializa la cuadrícula con la altura y anchura del mapa
        self.grid = MultiGrid(self.width, self.height, True)

        agent_id = 0
        for y in reversed(range(self.height)):
            for x in reversed(range(self.width)):
                grid_content = self.map[y][x]
                if 'C-a' in grid_content:
                    robot = RobotAgent(agent_id, self)
                    self.grid.place_agent(robot, (x, y))
                    self.schedule.add(robot)
                    agent_id += 1
                elif 'C-b' in grid_content:
                    box = BoxAgent(agent_id, self)
                    self.grid.place_agent(box, (x, y))
                    self.schedule.add(box)
                    agent_id += 1
                elif 'R' in grid_content:
                    rock = RockAgent(agent_id, self)
                    self.grid.place_agent(rock, (x, y))
                    self.schedule.add(rock)
                    agent_id += 1
                elif 'M' in grid_content:
                    finish = FinishAgent(agent_id, self)
                    self.grid.place_agent(finish, (x, y))
                    self.schedule.add(finish)
                    agent_id += 1



    # Imprime el mapa en la consola con sua agentes y sus posiciones
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
        self.schedule.step()
        self.print_grid()