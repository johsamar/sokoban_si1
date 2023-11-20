from agent.robotAgent import RobotAgent
from agent.rockAgent import RockAgent
from agent.boxAgent import BoxAgent
from agent.finishAgent import FinishAgent
from agent.pathAgent import PathAgent
from helpers.constants import Constans
def load_agents(map, model, grid, schedule, width, height):
    agent_id = 0
    for y in range(height - 1, -1, -1):
        for x in range(width):
            grid_content = map[height - 1 - y][x]
            
            path = PathAgent(agent_id, model)
            grid.place_agent(path, (x, y))
            schedule.add(path)
            agent_id += 1

            if 'C-a' in grid_content:
                robot = RobotAgent(agent_id, model)
                grid.place_agent(robot, (x, y))
                schedule.add(robot)
                agent_id += 1
            elif 'C-b' in grid_content:
                box = BoxAgent(agent_id, model)
                grid.place_agent(box, (x, y))
                schedule.add(box)
                agent_id += 1
            elif 'R' in grid_content:
                rock = RockAgent(agent_id, model)
                grid.place_agent(rock, (x, y))
                schedule.add(rock)
                agent_id += 1
            elif 'M' in grid_content:
                finish = FinishAgent(agent_id, model)
                grid.place_agent(finish, (x, y))
                schedule.add(finish)
                agent_id += 1

def calculate_heuristic(heuristic, initial_position, finish_position):
    if heuristic == Constans.MANHATTAN:
        # Cálculo de la distancia de Manhattan entre la caja y la meta
        distance = abs(initial_position[0] - finish_position[0]) + abs(initial_position[1] - finish_position[1])
        return distance
    elif heuristic == Constans.EUCLIDEAN:
        # Cálculo de la distancia euclidiana entre la caja y la meta
        distance = ((initial_position[0] - finish_position[0])**2 + (initial_position[1] - finish_position[1])**2)**0.5
        return distance
    
def calculate_all_heristic(selected_heuristic, schedule, goal_agent):
    for agent in schedule.agents: 
        if isinstance(agent, PathAgent):
            heuristic = calculate_heuristic(selected_heuristic, agent.pos, goal_agent.pos)
            print("Heuristica de", agent.pos, ":", heuristic)
            agent.heuristic = heuristic

        