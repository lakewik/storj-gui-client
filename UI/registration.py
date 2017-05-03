# -*- coding: utf-8 -*-

import logging
import json
import storj

from PyQt4 import QtCore, QtGui

from .login import LoginUI
from .qt_interfaces.register_ui_new import Ui_UI_Register
from .utilities.tools import Tools


# Register section
class RegisterUI(QtGui.QMainWindow):
    __logger = logging.getLogger('%s.RegisterUI' % __name__)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # register UI
        self.register_ui = Ui_UI_Register()
        self.register_ui.setupUi(self)

        self.register_ui.password.setEchoMode(QtGui.QLineEdit.Password)
        self.register_ui.password_2.setEchoMode(QtGui.QLineEdit.Password)

        QtCore.QObject.connect(self.register_ui.register_bt, QtCore.SIGNAL('clicked()'),
                               self.register)  # validate and register user

    def register(self):
        # validate fields
        self.email = self.register_ui.email.text()
        self.password = self.register_ui.password.text()
        self.password_repeat = self.register_ui.password_2.text()
        self.tools = Tools()

        success = False

        if self.email != "" and self.password != "" and self.password_repeat != "":

            if self.password == self.password_repeat:

                if self.tools.check_email(self.email):

                    # take login action
                    try:
                        self.storj_client = \
                            storj.Client(None, '').user_create(
                                str(self.email).strip(),
                                str(self.password).strip())
                        success = True
                    except storj.exception.StorjBridgeApiError as e:
                        j = json.loads(str(e))
                        if j.get('error', None) == 'Email is already registered':
                            QtGui.QMessageBox.about(
                                self,
                                'Warning',
                                'User with this e-mail is \
                                already registered! Please \
                                login or try a different \
                                e-mail!')
                        else:
                            QtGui.QMessageBox.about(self, 'Unhandled exception', 'Exception: %s' % e)
                else:
                    QtGui.QMessageBox.about(
                        self, 'Warning', 'Your e-mail seems to be invalid! Please check e-mail and try again')
            else:
                QtGui.QMessageBox.about(self, 'Warning', 'Given passwords are different! Please check and try again!')
        else:
            QtGui.QMessageBox.about(self, 'Warning', 'Please fill out all fields!')

        if success:
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Information,
                'Success',
                'Successfully registered in Storj Distributed Storage Network! '
                'Now, you must verify your email by'
                'clicking the link that has been sent to you. '
                'Then you can login',
                QtGui.QMessageBox.Ok)
            self.__logger.debug('New user registered')
            self.__logger.debug('Email: %s', self.email)
            self.__logger.debug('Password: %s', self.password)
            result = msgBox.exec_()
            if result == QtGui.QMessageBox.Ok:
                self.login_window = LoginUI(self)
                self.login_window.show()
                self.close()
                # initial_window.hide()
