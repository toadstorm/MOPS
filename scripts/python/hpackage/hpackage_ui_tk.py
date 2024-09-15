import os
import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import hpackagelib
import settings


class WrapLabel(tk.Label):
    def __init__(self, parent=None, **kwargs):
        tk.Label.__init__(self, parent, **kwargs)
        self.bind("<Configure>", lambda x: self.config(wraplength=self.winfo_width()))


class HPackageUI():
    # main dialog wrapper

    # ui functions
    def next_dialog(self):
        self.state += 1
        self.dialog_changed()

    def prev_dialog(self):
        self.state -= 1
        self.dialog_changed()

    def hide_dialogs(self):
        self.intro_dialog.grid_remove()
        self.location_dialog.grid_remove()
        self.chooser_dialog.grid_remove()
        self.confirm_dialog.grid_remove()

    def choose_directory(self):
        test_dir = filedialog.askdirectory()
        if test_dir is None:
            return
        self.directory.set(test_dir)

    def dialog_changed(self):
        # print(self.state)
        self.hide_dialogs()
        if self.state == 0:
            self.intro_dialog.grid()
            self.back_btn.configure(state=tk.DISABLED)

        elif self.state == 1:
            self.chooser_dialog.grid()
            self.back_btn.configure(state=tk.ACTIVE)

        elif self.state == 2:
            self.location_dialog.grid()

        elif self.state == 3:
            self.populate_installs_frame()
            self.confirm_dialog.grid()

    def populate_installs_frame(self):
        # used in the confirm dialog to show all selected installations.
        for i in self.installs_frame.winfo_children():
            i.destroy()
        for i in range(len(self.install_vars)):
            do_install = self.install_vars[i].get()
            path = self.installs[i]
            if do_install:
                ttk.Label(self.installs_frame, text=path, justify=tk.LEFT, width=80).grid(column=0, row=i, sticky="W")

    def __init__(self):

        root = tk.Tk()
        root.title(settings.TITLE)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.state = 0

        # back/next buttons
        btns = ttk.Frame(root)
        btns.grid(column=0, row=1, ipadx=15, ipady=15, sticky='SE')
        self.back_btn = ttk.Button(btns, text="< Back", state=tk.DISABLED)
        self.back_btn.grid(column=0, row=0, sticky='SE')
        self.next_btn = ttk.Button(btns, text="Next >")
        self.next_btn.grid(column=1, row=0, sticky='SE')

        # window 1 dialog
        self.intro_dialog = ttk.Frame(root, padding="15 15 15 15")
        self.intro_dialog.grid(column=0, row=0, ipadx=15, ipady=15, sticky="NSWE")
        self.intro_dialog.columnconfigure(1, weight=1)
        self.intro_dialog.rowconfigure(1, weight=1)
        image = ImageTk.PhotoImage(Image.open(settings.IMAGE))
        image_label = tk.Label(self.intro_dialog, image=image)
        image_label.grid(column=0, row=0, sticky='NW')
        WrapLabel(self.intro_dialog, text=settings.INTRO, width=60, justify=tk.LEFT).grid(column=1, row=0, columnspan=2, sticky='WE')

        # window 2 dialog
        self.chooser_dialog = ttk.Frame(root, padding="15 15 15 15")
        self.chooser_dialog.grid(column=0, row=0, ipadx=15, ipady=15, columnspan=2, sticky="NSWE")
        self.chooser_dialog.columnconfigure(0, weight=1)
        self.chooser_dialog.rowconfigure(0, weight=1)
        label = WrapLabel(self.chooser_dialog, text=settings.CHOOSER, width=60, justify=tk.LEFT)
        label.grid(column=0, row=0, columnspan=2, sticky="NW")
        # get potential install folders
        self.installs = hpackagelib.get_houdini_prefs_paths()
        # create container for list
        self.list_container = ttk.Frame(self.chooser_dialog)
        self.list_container.grid(column=0, row=1, sticky="NSWE", columnspan=2)
        self.install_vars = list()
        for x in range(len(self.installs)):
            self.install_vars.append(tk.IntVar(root, value=1))
        for x in range(len(self.installs)):
            cb = ttk.Checkbutton(self.list_container, text=self.installs[x], variable=self.install_vars[x])
            cb.grid(row=x, column=0, sticky="W")

        # window 3 dialog
        self.location_dialog = ttk.Frame(root, padding="15 15 15 15")
        self.location_dialog.grid(column=0, row=0, ipadx=15, ipady=15, columnspan=2, sticky="NSWE")
        self.location_dialog.columnconfigure(0, weight=1)
        label = WrapLabel(self.location_dialog, text=settings.LOCATION, width=60, justify=tk.LEFT)
        label.grid(column=0, row=0, sticky="NW", pady=10)
        default_dir = os.path.join(os.path.expanduser("~"), "MOPS")
        self.directory = tk.StringVar()
        self.directory.set(default_dir)
        directory_ctrl = ttk.Entry(self.location_dialog, width=80, textvariable=self.directory)
        directory_ctrl.grid(column=0, row=1, sticky="NWE")
        btn = ttk.Button(self.location_dialog, text="...", width=4, command=self.choose_directory)
        btn.grid(column=1, row=1, sticky="W", padx=5)

        # window 4 dialog
        self.confirm_dialog = ttk.Frame(root, padding="15 15 15 15")
        self.confirm_dialog.grid(column=0, row=0, ipadx=15, ipady=15, columnspan=2, sticky="NSWE")
        self.confirm_dialog.columnconfigure(0, weight=1)
        label = WrapLabel(self.confirm_dialog,
                          text="The Houdini package file will be installed to the following locations:",
                          justify=tk.LEFT)
        label.grid(column=0, row=0, sticky="NW", pady=10)
        self.installs_frame = ttk.Frame(self.confirm_dialog)
        self.installs_frame.grid(column=0, row=1, sticky="NW")
        self.populate_installs_frame()
        label2 = WrapLabel(self.confirm_dialog, text="The package contents will be installed to:", justify=tk.LEFT)
        label2.grid(column=0, row=2, sticky="NW", pady=10)
        self.dir_label = WrapLabel(self.confirm_dialog, textvariable=self.directory, justify=tk.LEFT)
        self.dir_label.grid(column=0, row=3, sticky="NW")


        # bind to controls
        self.next_btn.configure(command=self.next_dialog)
        self.back_btn.configure(command=self.prev_dialog)

        # init
        self.dialog_changed()
        root.mainloop()


if __name__ == "__main__":
    UI = HPackageUI()