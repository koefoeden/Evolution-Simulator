import tkinter as tk
import environment
import animals
from PIL import Image



class View:
    def __init__(self, env):
        root = tk.Tk()
        owl_image = tk.PhotoImage(file="Images/owl_image_50.GIF")
        mouse_image = tk.PhotoImage(file="Images/mouse_resized.pgm")
        root.geometry("1280x720")
        root["bg"] = "black"

        for r in range(env.dimensions):
            for c in range(env.dimensions):
                if isinstance(env.fields[r][c].animal, animals.Owl):
                    tk.Label(root, text="This is a label", image=owl_image).grid(row=r, column=c)
                else:
                    tk.Label(root, text="mouse here", image=mouse_image).grid(row=r, column=c)
        root.mainloop()