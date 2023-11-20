from mesa import Agent
from helpers.constants import Constans


class RobotAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id,model)
        self.image = "assets/robot.png"
        self.color = "grey"
        self.layer = 1
    
    def step(self):
        if self.model.algorithm == Constans.BFS:
            next_position = self.model.queue.queue[0]
        elif self.model.algorithm == Constans.DFS:
            next_position = self.model.stack[-1]
        self.model.grid.move_agent(self, next_position[0])
       
        