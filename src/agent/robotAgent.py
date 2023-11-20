from mesa import Agent
from queue import Queue


class RobotAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id,model)
        self.image = "assets/robot.png"
        self.color = "grey"
        self.layer = 1
    
    def step(self):
        next_position = self.model.queue.queue[0]

        self.model.grid.move_agent(self, next_position[0])
       
        