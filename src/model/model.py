from mesa import Model
from agent.robotAgent import RobotAgent
from agent.wallAgent import WallAgent
from agent.boxAgent import BoxAgent
from agent.finishAgent import FinishAgent
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class SokobanModel(Model):
    def __init__(self,width,height):

        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        robot = RobotAgent(1, self)
        wall = WallAgent(2, self)
        box = BoxAgent(3, self)
        finish = FinishAgent(4, self)

        x_robot, y_robot = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
        x_wall, y_wall = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
        x_box, y_box = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
        x_finish, y_finish = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)

        self.grid.place_agent(robot, (x_robot, y_robot))
        self.grid.place_agent(wall, (x_wall, y_wall))
        self.grid.place_agent(box, (x_box, y_box))
        self.grid.place_agent(finish, (x_finish, y_finish))

        self.schedule.add(robot)
        self.schedule.add(wall)
        self.schedule.add(box)
        self.schedule.add(finish)



    def step(self) -> None:
        self.schedule.step()