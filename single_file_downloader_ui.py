# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'single_file_downloader.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SingleFileDownload(object):
    def setupUi(self, SingleFileDownload):
        SingleFileDownload.setObjectName(_fromUtf8("SingleFileDownload"))
        SingleFileDownload.resize(1149, 474)
        self.line_3 = QtGui.QFrame(SingleFileDownload)
        self.line_3.setGeometry(QtCore.QRect(5, 40, 1141, 20))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.label = QtGui.QLabel(SingleFileDownload)
        self.label.setGeometry(QtCore.QRect(20, 10, 1121, 31))
        self.label.setObjectName(_fromUtf8("label"))
        self.shard_queue_table = QtGui.QTableView(SingleFileDownload)
        self.shard_queue_table.setGeometry(QtCore.QRect(405, 130, 731, 221))
        self.shard_queue_table.setObjectName(_fromUtf8("shard_queue_table"))
        self.label_6 = QtGui.QLabel(SingleFileDownload)
        self.label_6.setGeometry(QtCore.QRect(410, 90, 721, 41))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.line = QtGui.QFrame(SingleFileDownload)
        self.line.setGeometry(QtCore.QRect(390, 50, 21, 311))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.line_2 = QtGui.QFrame(SingleFileDownload)
        self.line_2.setGeometry(QtCore.QRect(400, 350, 741, 31))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.label_2 = QtGui.QLabel(SingleFileDownload)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 71, 31))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(SingleFileDownload)
        self.label_3.setGeometry(QtCore.QRect(10, 120, 111, 31))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.file_save_path = QtGui.QLineEdit(SingleFileDownload)
        self.file_save_path.setGeometry(QtCore.QRect(130, 120, 191, 31))
        self.file_save_path.setObjectName(_fromUtf8("file_save_path"))
        self.file_save_path_bt = QtGui.QPushButton(SingleFileDownload)
        self.file_save_path_bt.setGeometry(QtCore.QRect(330, 120, 61, 31))
        self.file_save_path_bt.setObjectName(_fromUtf8("file_save_path_bt"))
        self.start_download_bt = QtGui.QPushButton(SingleFileDownload)
        self.start_download_bt.setGeometry(QtCore.QRect(10, 270, 381, 51))
        self.start_download_bt.setObjectName(_fromUtf8("start_download_bt"))
        self.file_id = QtGui.QLabel(SingleFileDownload)
        self.file_id.setGeometry(QtCore.QRect(80, 70, 311, 31))
        self.file_id.setObjectName(_fromUtf8("file_id"))
        self.label_5 = QtGui.QLabel(SingleFileDownload)
        self.label_5.setGeometry(QtCore.QRect(10, 170, 311, 31))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.connections_onetime = QtGui.QSpinBox(SingleFileDownload)
        self.connections_onetime.setGeometry(QtCore.QRect(330, 170, 61, 32))
        self.connections_onetime.setObjectName(_fromUtf8("connections_onetime"))
        self.label_7 = QtGui.QLabel(SingleFileDownload)
        self.label_7.setGeometry(QtCore.QRect(10, 220, 151, 31))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.tmp_dir_bt = QtGui.QPushButton(SingleFileDownload)
        self.tmp_dir_bt.setGeometry(QtCore.QRect(330, 220, 61, 31))
        self.tmp_dir_bt.setObjectName(_fromUtf8("tmp_dir_bt"))
        self.tmp_dir = QtGui.QLineEdit(SingleFileDownload)
        self.tmp_dir.setGeometry(QtCore.QRect(170, 220, 151, 31))
        self.tmp_dir.setObjectName(_fromUtf8("tmp_dir"))
        self.overall_progress = QtGui.QProgressBar(SingleFileDownload)
        self.overall_progress.setGeometry(QtCore.QRect(10, 370, 1131, 31))
        self.overall_progress.setProperty("value", 24)
        self.overall_progress.setObjectName(_fromUtf8("overall_progress"))
        self.cancel_bt = QtGui.QPushButton(SingleFileDownload)
        self.cancel_bt.setGeometry(QtCore.QRect(210, 330, 181, 31))
        self.cancel_bt.setObjectName(_fromUtf8("cancel_bt"))
        self.line_4 = QtGui.QFrame(SingleFileDownload)
        self.line_4.setGeometry(QtCore.QRect(10, 430, 1131, 16))
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.label_8 = QtGui.QLabel(SingleFileDownload)
        self.label_8.setGeometry(QtCore.QRect(10, 440, 171, 31))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.downloaded_shards = QtGui.QLabel(SingleFileDownload)
        self.downloaded_shards.setGeometry(QtCore.QRect(180, 440, 141, 31))
        self.downloaded_shards.setObjectName(_fromUtf8("downloaded_shards"))
        self.label_10 = QtGui.QLabel(SingleFileDownload)
        self.label_10.setGeometry(QtCore.QRect(330, 440, 161, 31))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.remeianing_shards = QtGui.QLabel(SingleFileDownload)
        self.remeianing_shards.setGeometry(QtCore.QRect(500, 440, 141, 31))
        self.remeianing_shards.setObjectName(_fromUtf8("remeianing_shards"))
        self.label_12 = QtGui.QLabel(SingleFileDownload)
        self.label_12.setGeometry(QtCore.QRect(650, 440, 71, 31))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.file_size = QtGui.QLabel(SingleFileDownload)
        self.file_size.setGeometry(QtCore.QRect(730, 440, 151, 31))
        self.file_size.setObjectName(_fromUtf8("file_size"))
        self.open_log_bt = QtGui.QPushButton(SingleFileDownload)
        self.open_log_bt.setGeometry(QtCore.QRect(10, 330, 191, 31))
        self.open_log_bt.setObjectName(_fromUtf8("open_log_bt"))
        self.line_5 = QtGui.QFrame(SingleFileDownload)
        self.line_5.setGeometry(QtCore.QRect(400, 80, 741, 20))
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName(_fromUtf8("line_5"))
        self.label_14 = QtGui.QLabel(SingleFileDownload)
        self.label_14.setGeometry(QtCore.QRect(410, 50, 101, 41))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.file_name = QtGui.QLabel(SingleFileDownload)
        self.file_name.setGeometry(QtCore.QRect(520, 50, 621, 41))
        self.file_name.setObjectName(_fromUtf8("file_name"))
        self.label_16 = QtGui.QLabel(SingleFileDownload)
        self.label_16.setGeometry(QtCore.QRect(10, 400, 131, 41))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.current_state = QtGui.QLabel(SingleFileDownload)
        self.current_state.setGeometry(QtCore.QRect(140, 400, 1001, 41))
        self.current_state.setObjectName(_fromUtf8("current_state"))
        self.label_13 = QtGui.QLabel(SingleFileDownload)
        self.label_13.setGeometry(QtCore.QRect(900, 440, 101, 31))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.total_shards = QtGui.QLabel(SingleFileDownload)
        self.total_shards.setGeometry(QtCore.QRect(1010, 440, 121, 31))
        self.total_shards.setObjectName(_fromUtf8("total_shards"))

        self.retranslateUi(SingleFileDownload)
        QtCore.QMetaObject.connectSlotsByName(SingleFileDownload)

    def retranslateUi(self, SingleFileDownload):
        SingleFileDownload.setWindowTitle(_translate("SingleFileDownload", "Single file download - Storj GUI Client", None))
        self.label.setText(_translate("SingleFileDownload", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Single file downloading - Storj GUI Client</span></p></body></html>", None))
        self.label_6.setText(_translate("SingleFileDownload", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Shard download queue progress</span></p></body></html>", None))
        self.label_2.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">File ID:</span></p></body></html>", None))
        self.label_3.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Save file to:</span></p></body></html>", None))
        self.file_save_path_bt.setText(_translate("SingleFileDownload", "Select...", None))
        self.start_download_bt.setText(_translate("SingleFileDownload", "Start downloading process", None))
        self.file_id.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Initializing...</span></p></body></html>", None))
        self.label_5.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Number of transfers at the same time:</span></p></body></html>", None))
        self.label_7.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Temp directory:</span></p></body></html>", None))
        self.tmp_dir_bt.setText(_translate("SingleFileDownload", "Select...", None))
        self.cancel_bt.setText(_translate("SingleFileDownload", "Cancel", None))
        self.label_8.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Downloaded shards:</span></p></body></html>", None))
        self.downloaded_shards.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Initializing...</span></p></body></html>", None))
        self.label_10.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Remaianing shards:</span></p></body></html>", None))
        self.remeianing_shards.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Initializing...</span></p></body></html>", None))
        self.label_12.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">File size:</span></p></body></html>", None))
        self.file_size.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Initializing...</span></p></body></html>", None))
        self.open_log_bt.setText(_translate("SingleFileDownload", "Open download log", None))
        self.label_14.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">File name:</span></p></body></html>", None))
        self.file_name.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Initializing...</span></p></body></html>", None))
        self.label_16.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Current status:</span></p></body></html>", None))
        self.current_state.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Waiting</span></p></body></html>", None))
        self.label_13.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Total shards:</span></p></body></html>", None))
        self.total_shards.setText(_translate("SingleFileDownload", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Initializing...</span></p></body></html>", None))

