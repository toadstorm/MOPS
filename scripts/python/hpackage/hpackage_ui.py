import os
import sys
import hpackagelib
import settings
from PySide2 import QtWidgets, QtGui, QtCore

# TODO: results dialog
# TODO: error handling

class HPackageUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(HPackageUI, self).__init__(parent)
        self.setWindowTitle(settings.TITLE)

        """ persistent widgets """
        prev_btn = QtWidgets.QPushButton("< Prev")
        next_btn = QtWidgets.QPushButton("Next >")
        prev_btn.setEnabled(False)

        """ intro dialog """
        intro_dialog = QtWidgets.QFrame()
        intro_layout = QtWidgets.QHBoxLayout()
        intro_dialog.setLayout(intro_layout)
        intro_image = QtGui.QImage(settings.IMAGE)
        intro_map = QtGui.QPixmap(intro_image)
        intro_label_image = QtWidgets.QLabel()
        intro_label_image.setPixmap(intro_map)
        intro_layout.addWidget(intro_label_image)
        intro_text_layout = QtWidgets.QVBoxLayout()
        intro_text = QtWidgets.QLabel(settings.INTRO)
        intro_text.setMaximumWidth(settings.LABELWIDTH)
        intro_text.setWordWrap(True)
        intro_text_layout.addWidget(intro_text)
        intro_text_layout.addStretch()
        intro_layout.addLayout(intro_text_layout)

        """ configs dialog """
        configs_dialog = QtWidgets.QFrame()
        configs_layout = QtWidgets.QVBoxLayout()
        configs_dialog.setLayout(configs_layout)
        configs_text = QtWidgets.QLabel(settings.CHOOSER)
        configs_text.setMaximumWidth(settings.LABELWIDTH)
        configs_text.setWordWrap(True)
        configs_layout.addWidget(configs_text)
        # multilist for houdini installations
        configs_list = QtWidgets.QListWidget()
        configs_layout.addWidget(configs_list)

        """ destination dialog """
        dest_dialog = QtWidgets.QFrame()
        dest_layout = QtWidgets.QVBoxLayout()
        dest_dialog.setLayout(dest_layout)
        dest_label = QtWidgets.QLabel(settings.LOCATION)
        dest_label.setMaximumWidth(settings.LABELWIDTH)
        dest_label.setWordWrap(True)
        dest_layout.addWidget(dest_label)
        dest_chooser = QtWidgets.QLineEdit()
        default_path = hpackagelib.find_payload_path()
        dest_chooser.setText(default_path)
        dest_btn = QtWidgets.QPushButton("...")
        dest_ctrl_layout = QtWidgets.QHBoxLayout()
        dest_ctrl_layout.addWidget(dest_chooser)
        dest_ctrl_layout.addWidget(dest_btn)
        dest_layout.addLayout(dest_ctrl_layout)
        dest_layout.addStretch()

        """ confirmation dialog """
        ok_dialog = QtWidgets.QFrame()
        ok_layout = QtWidgets.QVBoxLayout()
        ok_dialog.setLayout(ok_layout)
        confs_label = QtWidgets.QLabel("The package will be installed for the following Houdini configurations:")
        confs_list = QtWidgets.QListWidget()
        confs_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        ok_layout.addWidget(confs_label)
        ok_layout.addWidget(confs_list)
        dest_label = QtWidgets.QLabel("The package files will be installed to this location:")
        dest_path_label = QtWidgets.QLabel()
        ok_layout.addWidget(dest_label)
        ok_layout.addWidget(dest_path_label)

        """ result dialog """
        result_dialog = QtWidgets.QFrame()
        result_layout = QtWidgets.QVBoxLayout()
        result_dialog.setLayout(result_layout)

        """ persistent layouts """
        main_dialog = QtWidgets.QDialog()
        main_layout = QtWidgets.QVBoxLayout()
        main_dialog.setLayout(main_layout)
        btns_layout = QtWidgets.QHBoxLayout()
        btns_layout.addStretch()
        btns_layout.addWidget(prev_btn)
        btns_layout.addWidget(next_btn)

        main_layout.addWidget(intro_dialog)
        main_layout.addWidget(configs_dialog)
        main_layout.addWidget(dest_dialog)
        main_layout.addWidget(ok_dialog)
        main_layout.addWidget(result_dialog)
        main_layout.addLayout(btns_layout)

        self.setCentralWidget(main_dialog)

        dialogs = [intro_dialog, configs_dialog, dest_dialog, ok_dialog, result_dialog]

        # persistent data
        self.data = {
            "state": 0,
            "dialogs": dialogs,
            "default_path": default_path,
            "controls": {
                "prev": prev_btn,
                "next": next_btn,
                "configs": configs_list,
                "destination": dest_chooser,
                "confirmation": confs_list,
                "confirmation_dest": dest_path_label
            }
        }

        # signals/slots
        next_btn.clicked.connect(self.next_state)
        prev_btn.clicked.connect(self.prev_state)
        dest_btn.clicked.connect(self.pick_install_path)

        self.refresh()

    def refresh(self):
        self.state_changed()
        self.get_configs()
        self.show()

    def next_state(self):
        self.data["state"] += 1
        self.state_changed()

    def prev_state(self):
        self.data["state"] -= 1
        self.state_changed()

    def state_changed(self):
        # hide all subdialogs
        for i in self.data["dialogs"]:
            i.setVisible(False)
        # show dialog matching current state
        self.data["dialogs"][self.data["state"]].setVisible(True)
        # enable/disable buttons
        if self.data["state"] == 0:
            self.data["controls"]["prev"].setEnabled(False)
        else:
            self.data["controls"]["prev"].setEnabled(True)
        if self.data["state"] == 3:
            self.load_confs_list()
            self.data["controls"]["confirmation_dest"].setText(self.data["controls"]["destination"].text())
        if self.data["state"] == 4:
            # this should actually run the installation.
            self.do_install()

    def get_configs(self):
        # get all houdini config dirs.
        configs = hpackagelib.get_houdini_prefs_paths()
        # clear existing widget.
        widget = self.data["controls"]["configs"]
        widget.clear()
        for c in configs:
            item = QtWidgets.QListWidgetItem(str(c))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            widget.addItem(item)

    def pick_install_path(self):
        # get the path to install to from the user.
        default_path = self.data["controls"]["destination"].text()
        new_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose installation path...", default_path)
        if new_path:
            self.data["controls"]["destination"].setText(new_path)

    def get_selected_configs(self):
        # get all selected houdini configurations.
        configs = list()
        confs_widget = self.data["controls"]["configs"]
        for x in range(confs_widget.count()):
            if confs_widget.item(x).checkState() == QtCore.Qt.Checked:
                configs.append(confs_widget.item(x).text())
        return configs

    def load_confs_list(self):
        # populate the configurations list for confirmation.
        widget = self.data["controls"]["confirmation"]
        widget.clear()
        configs = self.get_selected_configs()
        for c in configs:
            widget.addItem(c)

    def do_install(self):
        configs = self.get_selected_configs()
        destination = self.data["controls"]["destination"].text()
        if destination == self.data["default_path"]:
            destination = None
        package = hpackagelib.find_package_path()
        hpackagelib.install_package(configs, package, destination, debug=True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = HPackageUI()
    app.exec_()
