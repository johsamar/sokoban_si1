from mesa import Agent

class PathAgent(Agent):
    def __init__(self,unique_id,model):
        super().__init__(unique_id,model)
        self.image = "assets/robot.png"
        self.color = "blue"
        self.layer = 0
        self.heuristic = None
        self.text = ""

    def move(self, new_position):
        pass

    def step(self):
       next_position = self.model.queue.queue[0]
       self.text = next_position[1]