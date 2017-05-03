# -*- coding: utf-8 -*-

import json
import logging

import storj

from PyQt4 import QtCore, QtGui

from .mainUI import MainUI
from .qt_interfaces.login_ui_new import Ui_Login
from .utilities.account_manager import AccountManager


class LoginUI(QtGui.QMainWindow):
    """Login section."""

    __logger = logging.getLogger('%s.LoginUI' % __name__)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # login UI
        self.login_ui = Ui_Login()
        self.login_ui.setupUi(self)

        # Account manager
        self.login_ui.password.setEchoMode(QtGui.QLineEdit.Password)

        QtCore.QObject.connect(self.login_ui.login_bt, QtCore.SIGNAL("clicked()"), self.login)  # take login action

    def login(self):
        # take login action
        self.email = str(self.login_ui.email.text()).strip()  # get mail
        self.password = str(self.login_ui.password.text()).strip()  # get password

        self.storj_client = storj.Client(email=self.email,
                                         password=self.password)
        success = False
        # take login action - check credentials by listing keys :D
        try:
            self.storj_client.key_list()
            success = True
        except storj.exception.StorjBridgeApiError as e:
            j = json.loads(str(e))
            if j.get("error") == "Invalid email or password":
                QtGui.QMessageBox.about(self, "Warning",
                                        "Invalid email or password - access denied. "
                                        "Please check your credentials and try again!")
            else:
                QtGui.QMessageBox.about(self, "Unhandled exception", "Exception: " + str(e))

        if success:
            self.account_manager = AccountManager(self.email, self.password)  # init account manager
            self.account_manager.save_account_credentials()  # save login credentials and state
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Success", "Successfully loged in!",
                                       QtGui.QMessageBox.Ok)
            result = msgBox.exec_()
            if result == QtGui.QMessageBox.Ok:
                self.__logger.info("User {} succesfully logged in".format(self.email))
                self.main_ui_window = MainUI(self)
                self.main_ui_window.show()
                self.close()
                # initial_window.hide()
