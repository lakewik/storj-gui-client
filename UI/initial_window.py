# -*- coding: utf-8 -*-

import logging

from PyQt4 import QtCore, QtGui

from .engine import StorjEngine
from .login import LoginUI
from .qt_interfaces.initial_window_ui_new import Ui_InitialWindow
from .registration import RegisterUI


class InitialWindowUI(QtGui.QMainWindow):
    """Initial window section."""

    __logger = logging.getLogger('%s.InitialWindowUI' % __name__)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui_initial_window = Ui_InitialWindow()
        self.ui_initial_window.setupUi(self)

        # open bucket manager
        # QtCore.QObject.connect(
        #   self.ui.pushButton_3,
        #   QtCore.SIGNAL("clicked()"),
        #   self.save_config)

        self.storj_engine = StorjEngine()

        # open login window
        QtCore.QObject.connect(
            self.ui_initial_window.login_bt,
            QtCore.SIGNAL('clicked()'),
            self.open_login_window)

        # open registration window
        QtCore.QObject.connect(
            self.ui_initial_window.register_bt,
            QtCore.SIGNAL('clicked()'),
            self.open_register_window)

        # open about window
        # QtCore.QObject.connect(
        #   self.ui_initial_window.about_bt,
        #   QtCore.SIGNAL("clicked()"),
        #   self.open_about_window)

    def open_login_window(self):
        self.login_window = LoginUI(self)
        self.login_window.show()
        # initial_window.hide()

    def open_register_window(self):
        self.register_window = RegisterUI(self)
        self.register_window.show()
