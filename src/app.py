from tkinter import *
import automatic_testing, simulate
from tkinterhtml import HtmlFrame


class MainWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        master.title('Evolution Simulator')
        self.make_widgets()

    def create_window(self):
        window = Toplevel(self)
        window.title('Choose a configuration')

    def get_welcome_text(self):
        reader = open("../resources/welcome_text.html", 'r')
        return reader.read()

    def interactive_button_action(self):
        InteractivePopup(self)

    def automatic_testing_button_action(self):
        AutomaticPopup(self)

    def make_widgets(self):
        frame_top = Frame(self.master)
        frame_top.pack()

        frame_bottom = Frame(self.master)
        frame_bottom.pack()

        welcome_text_string = self.get_welcome_text()
        text = HtmlFrame(frame_top)
        text.set_content(welcome_text_string)
        text.pack()

        button_interactive = Button(frame_bottom, text="Start interactive simulation",
                                    command=self.interactive_button_action)
        button_interactive.pack(side=LEFT)

        button_automatic_testing = Button(frame_bottom, text="Start automatic testing",
                                          command=self.automatic_testing_button_action)
        button_automatic_testing.pack(side=RIGHT)


class InteractivePopup(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

        simulate.Simulate('../config.ini')


class AutomaticPopup(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

        automatic_testing.Tester('../auto_testing_config.ini')


def main():
    root = Tk()
    window = MainWindow(root)
    root.mainloop()


if __name__=='__main__':
    main()
