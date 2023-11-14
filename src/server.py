from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model.model import SokobanModel

def agent_portrayal(agent):
    portrayal={
        "Shape":"circle",
        "Filled":"true",
        "r":0.9,
        "Color": agent.color,
        "Layer":0,
        }
    
    return portrayal

num_row_width = 5
num_row_height = 5

grid = CanvasGrid(agent_portrayal,num_row_width,num_row_height,500,500)
server = ModularServer(SokobanModel,[grid],"Sokoban Model",{"width":num_row_width,"height":num_row_height})
server.port = 8521
server.launch()