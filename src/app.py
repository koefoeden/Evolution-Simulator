from tkinter import *
import automatic_testing, simulate
from tkinterhtml import HtmlFrame
import os


class MainWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        master.title('Evolution Simulator')
        self.make_widgets()

    def get_welcome_text(self):
        reader = open("../resources/welcome_text.html", 'r')
        return reader.read()

    def interactive_button_action(self):
        InteractivePopup(self)

    def automatic_testing_button_action(self):
        AutomaticPopup(self)

    def make_widgets(self):
        frame_top = Frame(self.master, bg='white')
        frame_top.pack()

        frame_bottom = Frame(self.master, bg='white')
        frame_bottom.pack(fill=BOTH)

        welcome_text_string = self.get_welcome_text()
        text = HtmlFrame(frame_top, vertical_scrollbar=False, horizontal_scrollbar=False, fontscale=1.3)
        text.set_content(welcome_text_string)
        text.pack(padx=20, pady=0)

        button_interactive = Button(frame_bottom, text="Start interactive simulation",
                                    command=self.interactive_button_action)
        button_interactive.pack(side=LEFT, padx=100, pady=10)

        button_automatic_testing = Button(frame_bottom, text="Start automatic testing",
                                          command=self.automatic_testing_button_action)
        button_automatic_testing.pack(side=RIGHT, padx=100, pady=10)


class InteractivePopup(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.tk_var = StringVar(self)
        self.transient(master)  # set to be on top of the main window
        self.title('Choose a configuration')
        self.make_widgets()

        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

        #simulate.Simulate('../config.ini')
        #self.update_idletasks()

    def make_widgets(self):
        self.top_frame = Frame(self, bg='white')
        self.top_frame.pack(fill=BOTH, expand=TRUE)

        self.mid_frame = Frame(self, bg='white')
        self.mid_frame.pack(pady=20, fill=BOTH)

        self.bottom_frame = Frame(self)
        self.bottom_frame.pack()

        label = Label(self.top_frame, text='Choose one of the pre-defined configuration for the simulation via the '
                                           'drop-down menu below, or add a new one.', pady=10, padx=10, bg='white')
        label.pack()


        list_of_configs = os.listdir("../example_configs")
        list_of_configs.append('config.ini')

        self.tk_var.set('config.ini')
        drop_down_menu = OptionMenu(self.mid_frame, self.tk_var, *list_of_configs)
        drop_down_menu.pack(side=LEFT, padx=10)

        edit_button = Button(self.mid_frame, text='Edit selected')
        edit_button.pack(side=LEFT, padx=10)

        add_button = Button(self.mid_frame, text='Add new')
        add_button.pack(side=RIGHT, padx=40)

        ok_button = Button(self, text="Start simulation", command=self.ok_button_pressed)
        ok_button.pack(side=BOTTOM, pady=20)

    def ok_button_pressed(self):
        print(self.tk_var.get())

    def edit_button_pressed(self):
        print(self.tk_var.get())


class AutomaticPopup(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title('hello')
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

        #automatic_testing.Tester('../auto_testing_config.ini')


def main():
    root = Tk()
    window = MainWindow(root)
    root.mainloop()


if __name__=='__main__':
    main()
