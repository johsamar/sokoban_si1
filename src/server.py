from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model.model import SokobanModel
from mesa.visualization.UserParam import UserParam
import tkinter as tk
from mesa.visualization.modules import TextElement

class ViewElement(TextElement):
    def __init__(self):
        pass

    def algoritmo_render(self, model):
        return "Algoritmo seleccionado: " + model.algorithm
    
    def heuristic_render(self, model):
        return "Heuristica seleccionada: " + model.heuristic


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.9,
        "Color": agent.color,
        "Layer": 0,
    }
    return portrayal


def seleccionar_algoritmo():

    global variable, variable_heuristica
    seleccion = variable.get()
    #print("Algoritmo seleccionado:", seleccion)
    heuristica= variable_heuristica.get() 
    return seleccion, heuristica
    
num_row_width = 5
num_row_height = 5

# Crear la ventana Tkinter
root = tk.Tk()
root.title("Selección de Algoritmo")

# Lista de opciones de algoritmos
opciones = ["Algoritmo No informado", "Algoritmo Informado"]
variable = tk.StringVar(root)
variable.set(opciones[0]) 


# Lista de opciones de heurísticas
opciones_heuristica = ["Manhattan ", "Euclidiana"]
variable_heuristica = tk.StringVar(root)
variable_heuristica.set(opciones_heuristica[0])

# Crear menú desplegable algoritmos
menu = tk.OptionMenu(root, variable, *opciones)
menu.pack()

# Crear menú desplegable heurísticas
menu_heuristica = tk.OptionMenu(root, variable_heuristica, *opciones_heuristica)
menu_heuristica.pack()

# Botón para confirmar selección
boton = tk.Button(root, text="Seleccionar", command=seleccionar_algoritmo)
boton.pack()


    
root.mainloop()


# Crear la cuadrícula para la visualización
grid = CanvasGrid(agent_portrayal, num_row_width, num_row_height, 500, 500)

# Crear el servidor con el modelo Sokoban y la cuadrícula
#server = ModularServer(SokobanModel, [grid], "Sokoban Model", {"width": num_row_width, "height": num_row_height, "algorithm": seleccionar_algoritmo()})
#server.port = 8521

algoritmo_seleccionado, heuristica_seleccionada = seleccionar_algoritmo()
algoritmo_element = ViewElement().algoritmo_render
heuristic_element = ViewElement().heuristic_render


server = ModularServer(SokobanModel, [grid,algoritmo_element,heuristic_element], "Sokoban Model", {"width": num_row_width, "height": num_row_height, "algorithm": algoritmo_seleccionado, "heuristic": heuristica_seleccionada})
server.port = 8521
print("Algoritmo en el modelo:", server.model.algorithm)
print("Heuristica en el modelo:", server.model.heuristic)

server.launch()
#root.update()
#root.mainloop()
#print("Algoritmo en el modelo:", server.model.algorithm)
#server.launch()

