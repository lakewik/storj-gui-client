# -*- coding: utf-8 -*-

import logging

from PyQt4 import QtCore, QtGui

from .qt_interfaces.settings_ui_new import Ui_ClientConfiguration
from .utilities.backend_config import Configuration


class ClientConfigurationUI(QtGui.QMainWindow):
    """Configuration Ui section."""

    __logger = logging.getLogger('%s.ClientConfigurationUI' % __name__)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # register UI
        self.client_configuration_ui = Ui_ClientConfiguration()
        self.client_configuration_ui.setupUi(self)

        self.configuration_manager = Configuration()

        QtCore.QObject.connect(self.client_configuration_ui.apply_bt, QtCore.SIGNAL("clicked()"),
                               self.save_settings)  # save settings action

        QtCore.QObject.connect(self.client_configuration_ui.cancel_bt, QtCore.SIGNAL("clicked()"),
                               self.close)  # close form

    def save_settings(self):
        # validate settings

        self.configuration_manager.save_client_configuration(self.client_configuration_ui)  # save configuration
        QtGui.QMessageBox.about(self, "Success", "Configuration saved successfully!")

    def reset_settings_to_default(self):
        self.__logger.debug(1)
