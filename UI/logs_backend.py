# -*- coding: utf-8 -*-
import os

import json
import logging.handlers

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QHBoxLayout, QTableWidgetItem, QWidget
from six import print_

from image_widget import ImageWidget
from qt_interfaces.logs_table_ui import Ui_Logs


class LogsUI(QtGui.QMainWindow):
    """Files section"""

    __logger = logging.getLogger('%s.LogsUI' % __name__)

    def __init__(self, parent=None, bucketid=None):
        QtGui.QWidget.__init__(self, parent)
        self.logs_ui = Ui_Logs()
        self.logs_ui.setupUi(self)

        # TODO hardcoded will need replacement
        fs_watcher = QtCore.QFileSystemWatcher([
            '/home/lakewik/PycharmProjects/storjguibeta/storj-gui-client/upload_log.json'])
        fs_watcher.connect(fs_watcher, QtCore.SIGNAL('fileChanged(QString)'), self.refresh_logs)

        self.initialize_logs_table()

        # self.connect(self, QtCore.SIGNAL("addLogRow"), lambda: self.add_log_row(log_content_array))

    def initialize_logs_table(self):
        self.logs_ui.logs_table.setRowCount(0)
        self.logs_ui.logs_table.setColumnCount(5)
        self.logs_ui.logs_table.setHorizontalHeaderLabels(['', 'Level', 'Title', 'Description', 'Date'])
        # self.logs_ui.logs_table.resizeColumnsToContents()
        # self.logs_ui.logs_table.resizeRowsToContents()
        # self.logs_ui.logs_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.logs_ui.logs_table.setColumnWidth(0, 28)
        self.logs_ui.logs_table.setColumnWidth(1, 110)
        self.logs_ui.logs_table.setColumnWidth(2, 150)
        self.logs_ui.logs_table.setColumnWidth(3, 435)
        self.logs_ui.logs_table.setColumnWidth(4, 140)

        log_content_array = {}
        with open('upload_log.json', 'r') as file_upload_log:
            upload_log = file_upload_log.read()

            upload_log_exploded = upload_log.split('|')
            self.__logger.debug(upload_log_exploded)
            for json_log_upload in upload_log_exploded:
                if json_log_upload:
                    json_log_upload = json_log_upload.replace("'", '"')
                    json_log_upload = json_log_upload.decode('utf-8-sig')
                    print_(json_log_upload)
                    j = json.loads(json_log_upload.encode('utf-8'))
                    log_content_array['log_event_type'] = j['log_event_type']
                    log_content_array['title'] = j['title']
                    log_content_array['description'] = j['description']
                    self.add_log_row(log_content_array)

    def refresh_logs(self):
        self.__logger.debug('Adding row...')
        log_content_array = {}
        with open('upload_log.json', 'r') as file_upload_log:
            upload_log = file_upload_log.read()

            upload_log_exploded = upload_log.split('|')
            self.__logger.debug(upload_log_exploded)

            for json_log_upload in upload_log_exploded:
                if json_log_upload:
                    json_log_upload = json_log_upload.replace("'", '"')
                    json_log_upload = json_log_upload.decode('utf-8-sig')
                    self.__logger.debug(json_log_upload)

                    j = json.loads(json_log_upload.encode('utf-8'))
                    log_content_array['log_event_type'] = j['log_event_type']
                    log_content_array['title'] = j['title']
                    log_content_array['description'] = j['description']
                    self.add_log_row(log_content_array)

        return 1

    def add_log_row(self, log_content_array):
        # add row to the QTableWidget for logs
        row_count = self.logs_ui.logs_table.rowCount()
        self.logs_ui.logs_table.setRowCount(row_count + 1)
        event_sign_image_path = None

        if log_content_array['log_event_type'] == 'info':
            info_png_path = os.path.join(os.path.dirname(__file__), 'resources/img/info.png')
            event_sign_image_path = str(info_png_path)
        elif log_content_array['log_event_type'] == 'warning':
            warning_png_path = os.path.join(os.path.dirname(__file__), 'resources/img/warning.png')
            event_sign_image_path = str(warning_png_path)
        elif log_content_array['log_event_type'] == 'notice':
            notice_png_path = os.path.join(os.path.dirname(__file__), 'resources/img/notice.png')
            event_sign_image_path = str(notice_png_path)
        elif log_content_array['log_event_type'] == 'debug':
            debug_png_path = os.path.join(os.path.dirname(__file__), 'resources/img/debug.png')
            event_sign_image_path = str(debug_png_path)
        elif log_content_array['log_event_type'] == 'success':
            debug_png_path = os.path.join(os.path.dirname(__file__), 'resources/img/success.png')
            event_sign_image_path = str(debug_png_path)
        elif log_content_array['log_event_type'] == 'error':
            error_png_path = os.path.join(os.path.dirname(__file__), 'resources/img/error.png')
            event_sign_image_path = str(error_png_path)

        image = ImageWidget(event_sign_image_path, self)
        widget = QWidget()
        hbl = QHBoxLayout()
        hbl.setMargin(0)
        hbl.setSpacing(0)
        hbl.addWidget(image)
        widget.setLayout(hbl)

        self.logs_ui.logs_table.setCellWidget(row_count, 0, widget)
        self.logs_ui.logs_table.setItem(row_count, 1, QTableWidgetItem(log_content_array['log_event_type']))

        titleitem = QTableWidgetItem(log_content_array['title'])
        titleitem.setTextAlignment(QtCore.Qt.AlignCenter)

        self.logs_ui.logs_table.setItem(row_count, 2, titleitem)
        self.logs_ui.logs_table.setItem(row_count, 3, QTableWidgetItem(log_content_array['description']))

        return 1

    def save_logs(self):
        # TODO save logs to file
        return 1


class LogHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        with open('upload_log.json', 'a') as uploadlogfile:
            uploadlogfile.write('%s|' % (record.msg.encode('utf8')))
