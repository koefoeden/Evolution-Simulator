import pkg_resources
from tkinter import *
from tkinter import OptionMenu
from tk_html_widgets import *
import subprocess
import os
from shutil import copyfile
import platform

RESORUCES = pkg_resources.resource_filename('evolutionsimulator', 'resources/')
CONFIGS = pkg_resources.resource_filename('evolutionsimulator', 'configs/')
IMAGES = pkg_resources.resource_filename('evolutionsimulator', 'images/')

print(pkg_resources.resource_filename('evolutionsimulator', 'interac,tive.py', ))


class MainWindow(Frame):
    """The main window when running the tool."""

    def __init__(self, master):
        """Sets standard options."""
        Frame.__init__(self, master)
        master.title('Evolution Simulator')
        master.geometry(get_geometry(700, 500))
        self.welcome_text = open(os.path.join(RESORUCES, 'welcome_text.html'), 'r').read()
        self.make_widgets()

    def make_widgets(self):
        """Make all widgets for the main windows"""
        # Frames
        frame_top = Frame(self.master)
        frame_top.pack()
        frame_bottom = Frame(self.master)
        frame_bottom.pack(fill=BOTH, side=BOTTOM)

        html_text = HTMLLabel(frame_top, html=self.welcome_text, background='white', height=200,
                              highlightbackground="red", highlightthickness=0,
                              pady=20)
        html_text.pack(fill="both", expand=True, padx=0)
        html_text.fit_height()

        # Mode buttons
        button_interactive = Button(frame_bottom, text="Interactive simulation",
                                    command=self.interactive_button_action,
                                    font=10)
        button_interactive.pack(side=LEFT, padx=100, pady=10, anchor=S)

        button_automatic_testing = Button(frame_bottom, text="Automatic config testing",
                                          command=self.automatic_testing_button_action,
                                          font=10)
        button_automatic_testing.pack(side=RIGHT, padx=100, pady=10)

    def interactive_button_action(self):
        ConfigurationWindow(self, interactive_mode=True)

    def automatic_testing_button_action(self):
        ConfigurationWindow(self, interactive_mode=False)


class ConfigurationWindow(Toplevel):
    """The window to choose the configuration for either interactive or automatic mode"""

    def __init__(self, master, interactive_mode=True):
        """Initialize window."""
        Toplevel.__init__(self, master)
        self.interactive_mode = interactive_mode
        self.title('Choose a configuration')
        self.width = 500
        self.geometry(get_geometry(self.width, 180))

        # Get list of configs and set example configs:
        if self.interactive_mode:
            self.example_configs = ['mice_and_owls.ini', 'only_mice.ini']
            self.list_of_configs = os.listdir(os.path.join(CONFIGS, "interactive"))
        else:
            self.example_configs = ['mice_and_owls.ini', 'only_mice.ini']
            self.list_of_configs = os.listdir(os.path.join(CONFIGS, "automatic_testing"))

        # menu-selected
        self.selected_config = StringVar(self)
        self.selected_config.set('Select a config...')

        self.drop_down_menu = None
        self.edit_button = None
        self.make_widgets()

        self.transient(master)  # set to be on top of the main windo
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

    def make_widgets(self):
        """Make widgets"""

        # frames
        self.top_frame = Frame(self)
        self.top_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.mid_frame = Frame(self)
        self.mid_frame.pack(side=TOP, pady=0, fill=BOTH)
        self.bottom_frame = Frame(self)
        self.bottom_frame.pack()

        # label
        label = Message(self.top_frame, text='Choose one of the pre-defined configuration for the simulation via the '
                                             'drop-down menu below, or add a new one.', pady=5, padx=10,
                        width=self.width)
        label.pack()

        label_menu = Label(self.top_frame, text="Configurations")
        label_menu.pack(side=BOTTOM, anchor=W, padx=20)

        # Drop-down menu
        self.drop_down_menu = OptionMenu(self.mid_frame, self.selected_config, *self.list_of_configs,
                                         command=self.dropdown_changed)
        self.drop_down_menu.pack(side=LEFT, padx=20)

        # Buttons
        add_button = Button(self.mid_frame, text='Add new', command=self.add_button_pressed)
        add_button.pack(side=RIGHT, padx=(40, 15))

        if self.interactive_mode:
            ok_button = Button(self, text="Start simulation", command=self.ok_button_pressed)
        else:
            ok_button = Button(self, text="Start automatic testing", command=self.ok_button_pressed)

        ok_button.pack(side=BOTTOM, pady=20)

        self.delete_button = Button(self.mid_frame, text='Delete', command=self.delete_button_pressed)
        self.delete_button.pack(side=RIGHT, padx=0)

        self.edit_button = Button(self.mid_frame, text='Edit', command=self.edit_button_pressed)
        self.edit_button.pack(side=RIGHT, padx=10, anchor=CENTER)

    def delete_button_pressed(self):
        """Delete config button action"""
        if self.interactive_mode:
            os.remove(os.path.join(CONFIGS, "interactive\\" + self.selected_config.get()))
        else:
            os.remove(os.path.join(CONFIGS, "automatic_testing\\" + self.selected_config.get()))

        self.update_dropdown_list()
        self.selected_config.set('Select a config...')

    def dropdown_changed(self, selected=None):
        """Drop down menu behavior"""
        if self.selected_config.get() in self.example_configs:
            self.edit_button.configure(bg="gray")
        else:
            self.edit_button.config(bg="white")

    def add_button_pressed(self):
        """Add new config behavior"""
        NameInputBox(self)
        self.update_dropdown_list()

    def update_dropdown_list(self):
        menu = self.drop_down_menu["menu"]
        menu.delete(0, "end")
        if self.interactive_mode:
            for name in os.listdir(os.path.join(CONFIGS, "interactive")):
                menu.add_command(label=name, command=lambda value=name: self.selected_config.set(value))
                # self.drop_down_menu.configure(command=self.dropdown_changed)
        else:
            for name in os.listdir(os.path.join(CONFIGS, "automatic_testing")):
                menu.add_command(label=name, command=lambda value=name: self.selected_config.set(value))

    def ok_button_pressed(self):
        """Ok button action"""
        if self.selected_config.get() in os.listdir(os.path.join(CONFIGS, "automatic_testing")) or \
                self.selected_config.get() in os.listdir(os.path.join(CONFIGS, "interactive")):
            if self.interactive_mode:
                if platform.system() == 'Linux':
                    subprocess.Popen(
                        f"python {pkg_resources.resource_filename('evolutionsimulator', 'interactive.py')} {os.path.join(CONFIGS, 'interactive', self.selected_config.get())}",
                        shell=True)
                else:
                    subprocess.Popen(
                        f"python {pkg_resources.resource_filename('evolutionsimulator', 'interactive.py')} {os.path.join(CONFIGS, 'interactive', self.selected_config.get())}",
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
                print(os.path.join(CONFIGS, 'interactive', self.selected_config.get()))
            else:
                if platform.system() == 'Linux':
                    subprocess.Popen(
                        f"python {pkg_resources.resource_filename('evolutionsimulator', 'automatic_testing.py')} {os.path.join(CONFIGS, 'automatic_testing', self.selected_config.get())}",
                        shell=True)
                else:
                    subprocess.Popen(
                        f"python {pkg_resources.resource_filename('evolutionsimulator', 'interactive.py')} {os.path.join(CONFIGS, 'interactive', self.selected_config.get())}",
                        creationflags=subprocess.CREATE_NEW_CONSOLE)

    def edit_button_pressed(self):
        """Edit button action"""
        if self.selected_config.get() in self.example_configs:
            pass
        elif self.interactive_mode:
            os.startfile(os.path.join(CONFIGS, 'interactive', self.selected_config.get()))
        else:
            os.startfile(os.path.join(CONFIGS, 'automatic_testing', self.selected_config.get()))


class NameInputBox(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title('Name of new config file')
        self.geometry(get_geometry(200, 50))

        # Entry widget
        self.entry_widget = Entry(self)
        self.entry_widget.pack(side=LEFT, padx=10)
        self.entry_widget.bind('<Return>', self.ok_button_pressed)

        # OK Button
        ok_button = Button(self, text="Add", command=self.ok_button_pressed)
        ok_button.pack(side=LEFT)

        self.transient(master)  # set to be on top of the main window
        self.grab_set()  # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self)  # pause anything on the main window until this one closes (optional)

    def ok_button_pressed(self, event=None):
        if self.master.interactive_mode:
            copyfile(os.path.join(CONFIGS, 'interactive', "mice_and_owls.ini"),
                     os.path.join(CONFIGS, 'interactive', self.entry_widget.get(), ".ini"))
        else:
            copyfile(os.path.join(CONFIGS, 'automatic_testing', "mice_and_owls.ini"),
                     os.path.join(CONFIGS, 'automatic_testing', self.entry_widget.get(), ".ini"))
        self.master.selected_config.set(self.entry_widget.get() + ".ini")
        self.destroy()


def main():
    global get_geometry

    def get_geometry(w, h):
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))
        return f'{w}x{h}+{x}+{y}'

    root = Tk()
    root.tk_setPalette(background='white', foreground='black',
                       activeBackground='gray', activeForeground='black')

    window = MainWindow(root)

    root.mainloop()


if __name__ == '__main__':
    main()
