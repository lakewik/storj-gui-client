# -*- coding: utf-8 -*-

import logging
import threading

import storj.exception as sjexc

from PyQt4 import QtCore, QtGui

from .engine import StorjEngine
from .file_download import SingleFileDownloadUI
from .file_mirror import FileMirrorsListUI
from .file_upload import SingleFileUploadUI
from .qt_interfaces.file_manager_ui import Ui_FileManager
from .utilities.tools import Tools


class FileManagerUI(QtGui.QMainWindow):
    """Files section."""

    __logger = logging.getLogger('%s.FileManagerUI' % __name__)

    def __init__(self, parent=None, bucketid=None):
        QtGui.QWidget.__init__(self, parent)
        self.file_manager_ui = Ui_FileManager()
        self.file_manager_ui.setupUi(self)

        # connect ComboBox change listener
        QtCore.QObject.connect(
            self.file_manager_ui.bucket_select_combo_box,
            QtCore.SIGNAL('currentIndexChanged(const QString&)'),
            self.createNewFileListUpdateThread)
        # create bucket action
        QtCore.QObject.connect(
            self.file_manager_ui.file_mirrors_bt, QtCore.SIGNAL('clicked()'),
            self.open_mirrors_list_window)
        # create bucket action
        QtCore.QObject.connect(
            self.file_manager_ui.quit_bt, QtCore.SIGNAL('clicked()'),
            self.close)
        # create bucket action
        QtCore.QObject.connect(
            self.file_manager_ui.file_download_bt, QtCore.SIGNAL('clicked()'),
            self.open_single_file_download_window)
        # delete selected file
        QtCore.QObject.connect(
            self.file_manager_ui.file_delete_bt, QtCore.SIGNAL('clicked()'),
            self.delete_selected_file)
        # delete selected file
        QtCore.QObject.connect(
            self.file_manager_ui.new_file_upload_bt, QtCore.SIGNAL('clicked()'),
            self.open_single_file_upload_window)

        self.storj_engine = StorjEngine()
        self.createNewBucketResolveThread()

    def open_single_file_upload_window(self):
        self.single_file_upload_window = SingleFileUploadUI(self)
        self.single_file_upload_window.show()

    def delete_selected_file(self):
        self.current_bucket_index = self.file_manager_ui.bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[self.current_bucket_index]

        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.selectedIndexes()))

        selected = False
        for row in rows:
            selected = True
            # get file ID index
            index = tablemodel.index(row, 3)
            # get file name index
            index_filename = tablemodel.index(row, 0)

            # we suppose data are strings
            selected_file_id = str(tablemodel.data(index).toString())
            selected_file_name = str(tablemodel.data(index_filename).toString())
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Question,
                'Question',
                'Are you sure you want to delete this file? File name: %s' % selected_file_name,
                (QtGui.QMessageBox.Yes | QtGui.QMessageBox.No))
            result = msgBox.exec_()
            self.__logger.debug(result)

            if result == QtGui.QMessageBox.Yes:
                try:
                    self.storj_engine.storj_client.file_remove(
                        str(self.current_selected_bucket_id), str(selected_file_id))
                    # update files list
                    self.createNewFileListUpdateThread()
                    QtGui.QMessageBox.about(
                        self,
                        'Success',
                        'File "%s" was deleted successfully' % selected_file_name)
                except sjexc.StorjBridgeApiError as e:
                    self.__logger.error(e)
                    QtGui.QMessageBox.about(
                        self,
                        'Error',
                        'Bridge exception occured while trying to delete file: %s' % e)
                except Exception as e:
                    self.__logger.error(e)
                    QtGui.QMessageBox.about(
                        self,
                        'Error',
                        'Unhandled exception occured while trying to delete file: %s' % e)

        if not selected:
            QtGui.QMessageBox.about(
                self,
                'Information',
                'Please select file which you want to delete')

        return True

    def open_mirrors_list_window(self):
        self.current_bucket_index = self.file_manager_ui.bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[self.current_bucket_index]

        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.selectedIndexes()))
        i = 0
        for row in rows:
            self.__logger.info('Row %d is selected' % row)
            index = tablemodel.index(row, 3)  # get file ID
            # We suppose data are strings
            selected_file_id = str(tablemodel.data(index).toString())
            self.file_mirrors_list_window = FileMirrorsListUI(self, str(self.current_selected_bucket_id),
                                                              selected_file_id)
            self.file_mirrors_list_window.show()
            i += 1

        if i == 0:
            QtGui.QMessageBox.about(
                self,
                'Warning!',
                'Please select file from file list!')

        self.__logger.debug(1)

    def createNewFileListUpdateThread(self):
        download_thread = threading.Thread(target=self.update_files_list, args=())
        download_thread.start()

    def update_files_list(self):

        self.tools = Tools()

        # initialize model for inserting to table
        model = QtGui.QStandardItemModel(1, 1)

        model.setHorizontalHeaderLabels(['File name', 'File size', 'Mimetype', 'File ID'])

        self.current_bucket_index = self.file_manager_ui.bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[self.current_bucket_index]

        i = 0

        try:
            for self.file_details in self.storj_engine.storj_client.bucket_files(str(self.current_selected_bucket_id)):
                item = QtGui.QStandardItem(str(self.file_details['filename'].replace('[DECRYPTED]', "")))
                model.setItem(i, 0, item)  # row, column, item (StandardItem)

                file_size_str = self.tools.human_size(int(self.file_details["size"]))  # get human readable file size

                item = QtGui.QStandardItem(str(file_size_str))
                model.setItem(i, 1, item)  # row, column, item (QQtGui.StandardItem)

                item = QtGui.QStandardItem(str(self.file_details['mimetype']))
                model.setItem(i, 2, item)  # row, column, item (QStandardItem)

                item = QtGui.QStandardItem(str(self.file_details['id']))
                model.setItem(i, 3, item)  # row, column, item (QStandardItem)

                i = i + 1

                self.__logger.info(self.file_details)

        except sjexc.StorjBridgeApiError as e:
            self.__logger.error(e)

        self.file_manager_ui.files_list_tableview.clearFocus()
        self.file_manager_ui.files_list_tableview.setModel(model)
        self.file_manager_ui.files_list_tableview.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def createNewBucketResolveThread(self):
        download_thread = threading.Thread(target=self.initialize_bucket_select_combobox, args=())
        download_thread.start()

    def initialize_bucket_select_combobox(self):
        self.buckets_list = []
        self.bucket_id_list = []
        self.storj_engine = StorjEngine()  # init StorjEngine
        i = 0
        try:
            for bucket in self.storj_engine.storj_client.bucket_list():
                self.buckets_list.append(str(bucket.name))  # append buckets to list
                self.bucket_id_list.append(str(bucket.id))  # append buckets to list
                i = i + 1
        except sjexc.StorjBridgeApiError as e:
            QtGui.QMessageBox.about(
                self,
                'Unhandled bucket resolving exception',
                'Exception: %s' % e)

        self.file_manager_ui.bucket_select_combo_box.addItems(self.buckets_list)

    def open_single_file_download_window(self):
        self.current_bucket_index = self.file_manager_ui.bucket_select_combo_box.currentIndex()
        self.current_selected_bucket_id = self.bucket_id_list[self.current_bucket_index]

        tablemodel = self.file_manager_ui.files_list_tableview.model()
        rows = sorted(set(index.row() for index in
                          self.file_manager_ui.files_list_tableview.selectedIndexes()))
        i = 0
        for row in rows:
            self.__logger.info('Row %d is selected', row)

            # get file ID
            index = tablemodel.index(row, 3)

            # we suppose data are strings
            selected_file_id = str(tablemodel.data(index).toString())
            self.file_mirrors_list_window = SingleFileDownloadUI(
                self, str(self.current_selected_bucket_id), selected_file_id)
            self.file_mirrors_list_window.show()
            i += 1

        if i == 0:
            QtGui.QMessageBox.about(self, 'Warning!', 'Please select file from file list!')

        self.__logger.debug(1)
