from mesa import Model
from agent.robotAgent import RobotAgent
from agent.wallAgent import WallAgent
from agent.boxAgent import BoxAgent
from agent.finishAgent import FinishAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class SokobanModel(Model):
    def load_map(self, filename):
        with open(filename, 'r') as file:
            map_string = file.read()
        map_list = [line.split(', ') for line in map_string.splitlines()]
        print(map_list) 
        self.width = len(map_list[0]) 
        self.height = len(map_list)
        return map_list

    def __init__(self, algorithm=None, heuristic=None, filename=None):
        self.schedule = RandomActivation(self)
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.filename = filename

        # Carga el mapa
        self.map = self.load_map(filename)

        # Inicializa la cuadrícula con la altura y anchura del mapa
        self.grid = MultiGrid(self.width, self.height, True)

        agent_id = 0
        for y in range(self.height):
            for x in range(self.width):
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
                    wall = WallAgent(agent_id, self)
                    self.grid.place_agent(wall, (x, y))
                    self.schedule.add(wall)
                    agent_id += 1
                elif 'M' in grid_content:
                    finish = FinishAgent(agent_id, self)
                    self.grid.place_agent(finish, (x, y))
                    self.schedule.add(finish)
                    agent_id += 1
        # Resto del código del modelo sin cambios

    # Agregar propiedades 
    
     
    def print_grid(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get_cell_list_contents([(x, y)])
                if len(cell) > 0:
                    print(cell[0].__class__.__name__[0], end='')
                else:
                    print(' ', end='')
            print()

    def step(self) -> None:
        self.schedule.step()
        self.print_grid()