# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')



import threading

import storj.exception as sjexc

from PyQt4 import QtCore, QtGui

from .engine import StorjEngine
from .qt_interfaces.bucket_editing_ui import Ui_BucketEditing


class BucketEditingUI(QtGui.QMainWindow):

    def __init__(self, parent=None, bucketid=None, action=None, dashboard_instance=None):
        QtGui.QWidget.__init__(self, parent)
        self.bucket_create_ui = Ui_BucketEditing()
        self.bucket_create_ui.setupUi(self)

        self.bucket_id = bucketid

        QtCore.QObject.connect(
            self.bucket_create_ui.cancel_bt, QtCore.SIGNAL('clicked()'),  self.close)


        self.connect(self, QtCore.SIGNAL('printBucketDetails'), self.set_bucket_details)
        self.connect(self, QtCore.SIGNAL('showBucketCreatingException'), self.show_bucket_creating_exception_dialog)
        self.connect(self, QtCore.SIGNAL('showBucketCreatedSuccessfully'), self.show_bucket_created_successfully)
        self.connect(self, QtCore.SIGNAL('showBucketDeletedSuccessfully'), self.show_bucket_deleted_successfully)
        self.connect(self, QtCore.SIGNAL('showBucketUpdatedSuccessfully'), self.show_bucket_updated_successfully)
        self.connect(self, QtCore.SIGNAL('showBucketCreationMissingFields'),
            lambda: QtGui.QMessageBox.about(self, 'Warning', 'Please fill out all fields!'))
        self.dashboard_instance = dashboard_instance
        self.storj_engine = StorjEngine()

        if action == 'add':
            # create bucket action
            QtCore.QObject.connect(
                self.bucket_create_ui.create_edit_bucket_bt,
                QtCore.SIGNAL('clicked()'),
                self.createNewBucketCreateThread)
            self.bucket_create_ui.create_edit_bucket_bt.setText('CREATE')
            self.bucket_create_ui.remove_bucket_bt.setVisible(False)
            self.setWindowTitle('Add bucket - Storj GUI')
        else:
            self.createBucketDetailsLoadThread()

            # edit bucket action
            QtCore.QObject.connect(self.bucket_create_ui.create_edit_bucket_bt, QtCore.SIGNAL('clicked()'),
                                   lambda: self.createNewBucketEditThread())
            # remove bucket action
            QtCore.QObject.connect(self.bucket_create_ui.remove_bucket_bt, QtCore.SIGNAL('clicked()'),
                                   self.createNewBucketRemoveThread)
            self.bucket_create_ui.create_edit_bucket_bt.setText('SAVE')

    def set_bucket_details(self, bucket_name, bucket_transfer, bucket_storage):
        self.bucket_create_ui.bucket_name.setText(str(bucket_name))
        self.bucket_create_ui.bucket_transfer.setText(str(bucket_transfer))
        self.bucket_create_ui.bucket_size.setText(str(bucket_storage))

    def resolve_bucket_details(self):
        # update bucket details
        bucket_details = self.storj_engine.storj_client.bucket_get(str(self.bucket_id))
        self.emit(QtCore.SIGNAL('printBucketDetails'), bucket_details.name,
                  bucket_details.transfer, bucket_details.storage)

    def show_bucket_creating_exception_dialog(self, exception):
        QtGui.QMessageBox.about(
            self,
            'Unhandled exception while creating bucket',
            'Exception: %s' % str(exception))

    def show_bucket_created_successfully(self, bucket_name):
        msgBox = QtGui.QMessageBox(
            QtGui.QMessageBox.Information,
            'Success',
            'Bucket \'%s\' was created successfully!' % bucket_name,
            QtGui.QMessageBox.Ok)
        msgBox.exec_()

    def show_bucket_deleted_successfully(self, bucket_name):
        msgBox = QtGui.QMessageBox(
            QtGui.QMessageBox.Information,
            'Success',
            'Bucket \'%s\' was removed successfully!' % bucket_name,
            QtGui.QMessageBox.Ok)
        msgBox.exec_()


    def show_bucket_updated_successfully(self):
        msgBox = QtGui.QMessageBox(
            QtGui.QMessageBox.Information,
            'Success',
            'Bucket was updated successfully!',
            QtGui.QMessageBox.Ok)
        msgBox.exec_()


    def createNewBucketRemoveThread(self):
        self.bucket_name = self.bucket_create_ui.bucket_name.text()
        msgBox = QtGui.QMessageBox(
            QtGui.QMessageBox.Question,
            'Are you sure?',
            'Are you sure to delete this bucket? Bucket name: \'%s\'' % self.bucket_name,
            (QtGui.QMessageBox.Yes | QtGui.QMessageBox.No))

        result = msgBox.exec_()
        if result == QtGui.QMessageBox.Yes:
            bucket_create_thread = threading.Thread(target=self.remove_bucket, args=())
            bucket_create_thread.start()

    def remove_bucket(self):
        self.bucket_name = self.bucket_create_ui.bucket_name.text()
        success = False
        try:
            self.storj_engine.storj_client.bucket_delete(str(self.bucket_id))
            success = True
        except Exception as e:
            self.__logger.error(e)
            self.__logger.error('Unhandled exception while deleting bucket %s' % e)
            # QtGui.QMessageBox.about(self, "Unhandled exception deleting bucket", "Exception: " + str(e))
            success = False

        if success:
            # show dialog - bucket deleted successfully
            self.dashboard_instance.createNewBucketResolveThread()
            self.emit(QtCore.SIGNAL('showBucketDeletedSuccessfully'), str(self.bucket_name))

    def createNewBucketCreateThread(self):
        bucket_create_thread = threading.Thread(target=self.create_bucket, args=())
        bucket_create_thread.start()

    def createNewBucketEditThread(self):
        bucket_create_thread = threading.Thread(target=self.edit_bucket, args=())
        bucket_create_thread.start()

    def createBucketDetailsLoadThread(self):
        bucket_create_thread = threading.Thread(target=self.resolve_bucket_details, args=())
        bucket_create_thread.start()

    def edit_bucket(self):
        self.emit(QtCore.SIGNAL('showBucketUpdatedSuccessfully'))
        return 1

    def create_bucket(self):
        self.bucket_name = self.bucket_create_ui.bucket_name.text()
        self.bucket_storage = self.bucket_create_ui.bucket_size.text()
        self.bucket_transfer = self.bucket_create_ui.bucket_transfer.text()

        bucket_created = False
        if self.bucket_name and \
                self.bucket_transfer and \
                self.bucket_storage:

            try:
                self.storj_engine.storj_client.bucket_create(
                    str(self.bucket_name),
                    int(self.bucket_storage),
                    int(self.bucket_transfer))
                bucket_created = True
            except sjexc.StorjBridgeApiError as e:
                bucket_created = False
                self.emit(QtCore.SIGNAL('showBucketCreatingException'), str(e))

        else:
            self.emit(QtCore.SIGNAL('showBucketCreationMissingFields'))
            bucket_created = False

        if bucket_created:
            self.dashboard_instance.createNewBucketResolveThread()

            # show dialog - bucket created successfully
            self.emit(QtCore.SIGNAL('showBucketCreatedSuccessfully'), str(self.bucket_name))

        self.logger.debug(1)
