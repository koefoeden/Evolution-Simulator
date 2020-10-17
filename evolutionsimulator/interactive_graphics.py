import tkinter as tk
import animals
#from PIL import Image

class View:
    def __init__(self, env):
        self.env = env
        self.root = tk.Tk()
        self.owl_image = tk.PhotoImage(file="images/owl_image_50.GIF")
        self.mouse_image = tk.PhotoImage(file="images/mouse_resized.pgm")
        self.root.geometry("1280x720")
        self.root["bg"] = "black"

    def update_view(self):
        for r in range(self.env.dimensions):
            for c in range(self.env.dimensions):
                if isinstance(self.env.fields[r][c].animal, animals.Owl):
                    tk.Label(self.root, text="This is a label", image=self.owl_image).grid(row=r, column=c)
                else:
                    tk.Label(self.root, text="mouse here", image=self.mouse_image).grid(row=r, column=c)
        #self.root.mainloop()