from tkinter import *
from tkinter import messagebox, OptionMenu

import automatic_testing, simulate
from tkinterhtml import HtmlFrame
import os
import configparser
from shutil import copyfile


class MainWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        master.title('Evolution Simulator')
        master.geometry(get_geometry(800, 700))

        self.welcome_text = open("../resources/welcome_text.html", 'r').read()
        self.make_widgets()

    def make_widgets(self):
        # Frames
        frame_top = Frame(self.master)
        frame_top.pack()
        frame_bottom = Frame(self.master)
        frame_bottom.pack(fill=BOTH)

        # Html text box
        text = HtmlFrame(frame_top, vertical_scrollbar=False, horizontal_scrollbar=False, fontscale=1.3)
        text.set_content(self.welcome_text)
        text.pack(padx=20, pady=0)

        # Mode buttons
        button_interactive = Button(frame_bottom, text="Interactive simulation",
                                    command=self.interactive_button_action)
        button_interactive.pack(side=LEFT, padx=100, pady=10)

        button_automatic_testing = Button(frame_bottom, text="Automatic config testing",
                                          command=self.automatic_testing_button_action)
        button_automatic_testing.pack(side=RIGHT, padx=100, pady=10)

    def interactive_button_action(self):
        InteractivePopup(self, interactive_mode=True)

    def automatic_testing_button_action(self):
        InteractivePopup(self, interactive_mode=False)


class InteractivePopup(Toplevel):
    def __init__(self, master, interactive_mode=True):
        Toplevel.__init__(self, master)
        self.interactive_mode = interactive_mode
        self.title('Choose a configuration')
        self.geometry(get_geometry(700, 200))

        # Example configs
        if self.interactive_mode:
            self.example_configs = ['mice_and_owls.ini', 'only_mice.ini']
            self.list_of_configs = os.listdir("../configs/interactive")
        else:
            self.example_configs = ['mice_and_owls.ini', 'only_mice.ini']
            self.list_of_configs = os.listdir("../configs/automatic_testing")

        # menu-selected
        self.tk_var = StringVar(self)
        self.tk_var.set('my_config.ini')

        self.drop_down_menu = None
        self.edit_button = None
        self.make_widgets()

        self.transient(master)  # set to be on top of the main windo
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

    def make_widgets(self):
        # frames
        self.top_frame = Frame(self, highlightbackground='red', highlightthickness=5)
        self.top_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.mid_frame = Frame(self, highlightbackground='yellow', highlightthickness=5)
        self.mid_frame.pack(side=TOP, pady=0, fill=BOTH)
        self.bottom_frame = Frame(self)
        self.bottom_frame.pack()

        # label
        label = Label(self.top_frame, text='Choose one of the pre-defined configuration for the simulation via the '
                                           'drop-down menu below, or add a new one.', pady=10, padx=10)
        label.pack()

        label_menu = Label(self.top_frame, text="Configurations")
        label_menu.pack(side=BOTTOM, anchor=W, padx=30)

        # Drop-down menu
        self.drop_down_menu = OptionMenu(self.mid_frame, self.tk_var, *self.list_of_configs, command=self.dropdown_changed)
        self.drop_down_menu.pack(side=LEFT, padx=30)

        # Buttons
        add_button = Button(self.mid_frame, text='Add new', command=self.add_button_pressed)
        add_button.pack(side=RIGHT, padx=40)

        if self.interactive_mode:
            ok_button = Button(self, text="Start simulation", command=self.ok_button_pressed)
        else:
            ok_button = Button(self, text="Start automatic testing", command=self.ok_button_pressed)

        ok_button.pack(side=BOTTOM, pady=20)

        self.edit_button = Button(self.mid_frame, text='Edit', command=self.edit_button_pressed)
        self.edit_button.pack(side=LEFT, padx=0)

    def dropdown_changed(self, selected=None):
        if self.tk_var.get() in self.example_configs:
            self.edit_button.configure(bg="gray")
        else:
            self.edit_button.config(bg="white")

    def add_button_pressed(self):
        NameInputBox(self)

        menu = self.drop_down_menu["menu"]
        menu.delete(0, "end")
        if self.interactive_mode:
            for name in os.listdir("..\\configs\\interactive"):
                menu.add_command(label=name, command=lambda value=name: self.tk_var.set(value))
        else:
            for name in os.listdir("..\\configs\\automatic_testing"):
                menu.add_command(label=name, command=lambda value=name: self.tk_var.set(value))

    def ok_button_pressed(self):
        self.destroy()
        if self.interactive_mode:
            simulate.Simulate('..\\configs\\interactive\\'+str(self.tk_var.get()))
        else:
            automatic_testing.Tester('..\\configs\\automatic_testing\\'+str(self.tk_var.get()))

    def edit_button_pressed(self):
        if self.tk_var.get() in self.example_configs:
            pass
        elif self.interactive_mode:
            os.startfile("..\\configs\\interactive\\"+str(self.tk_var.get()))
        else:
            os.startfile("..\\configs\\automatic_testing\\"+str(self.tk_var.get()))


class NameInputBox(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title('Name of new config file')
        self.geometry(get_geometry(200, 50))

        #Entry widget
        self.entry_widget = Entry(self)
        self.entry_widget.pack()

        # OK Button
        ok_button = Button(self, text="OK", command=self.ok_button_pressed)
        ok_button.pack()

        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

    def ok_button_pressed(self):
        if self.master.interactive_mode:
            copyfile("..\\configs\\interactive\\mice_and_owls.ini",
                     "..\\configs\\interactive\\"+self.entry_widget.get()+".ini")
        else:
            copyfile("..\\configs\\automatic_testing\\mice_and_owls.ini",
                     "..\\configs\\automatic_testing\\" + self.entry_widget.get() + ".ini")
        self.master.tk_var.set(self.entry_widget.get()+".ini")
        self.destroy()

if __name__=='__main__':
    root = Tk()

    def get_geometry(w, h):
        ws = root.winfo_screenwidth()
        print(ws)
        hs = root.winfo_screenheight()
        print(hs)
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        return f'{w}x{h}+{x}+{y}'

    root.tk_setPalette(background='white', foreground='black',
                       activeBackground='gray', activeForeground='black')
    window = MainWindow(root)

    root.mainloop()



