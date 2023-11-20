from mesa import Agent
from helpers.constants import Constans

class PathAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.color = "white"
        self.layer = 0
        self.heuristic = None
        self.text = ""

    def move(self, new_position):
        pass

    def step(self):
       if self.model.algorithm == Constans.BFS:
           next_position = self.model.queue.queue[0]
           self.text = next_position[1]