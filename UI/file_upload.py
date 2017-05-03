# -*- coding: utf-8 -*-

from sys import platform
import os

import hashlib
import json
import logging
import mimetypes
import threading
import time

import requests
import storj
import storj.model

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox
from six import print_

from crypto.crypto_tools import CryptoTools
from crypto.file_crypto_tools import FileCrypto
from engine import StorjEngine
from qt_interfaces.file_upload_new import Ui_SingleFileUpload
from utilities.backend_config import Configuration
from utilities.tools import Tools

from resources.html_strings import html_format_begin, html_format_end
from resources.constants import MAX_RETRIES_UPLOAD_TO_SAME_FARMER, \
    MAX_RETRIES_NEGOTIATE_CONTRACT
from resources.internal_backend_config_variables import APPLY_SELECTED_BUCKET_TO_UPLOADER

class SingleFileUploadUI(QtGui.QMainWindow):
    __logger = logging.getLogger('%s.SingleFileUploadUI' % __name__)

    def __init__(self, parent=None, bucketid=None, fileid=None, dashboard_instance=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui_single_file_upload = Ui_SingleFileUpload()
        self.ui_single_file_upload.setupUi(self)
        # open bucket manager
        QtCore.QObject.connect(
            self.ui_single_file_upload.start_upload_bt,
            QtCore.SIGNAL('clicked()'),
            self.createNewUploadThread)
        # open file select dialog
        QtCore.QObject.connect(
            self.ui_single_file_upload.file_path_select_bt,
            QtCore.SIGNAL('clicked()'),
            self.select_file_path)
        # open tmp directory select dialog
        QtCore.QObject.connect(
            self.ui_single_file_upload.tmp_path_select_bt,
            QtCore.SIGNAL('clicked()'),
            self.select_tmp_directory)

        # handle cancel action
        QtCore.QObject.connect(
            self.ui_single_file_upload.cancel_bt,
            QtCore.SIGNAL('clicked()'),
            self.handle_cancel_action)


        self.tools = Tools()

        self.storj_engine = StorjEngine()

        self.initialize_upload_queue_table()
        self.dashboard_instance = dashboard_instance

        self.ui_single_file_upload.uploaded_shards.setText("Waiting...")

        self.is_upload_active = False
        self.current_active_connections = 0

        if platform == 'linux' or platform == 'linux2':
            # linux
            self.temp_dir = '/tmp'
        elif platform == 'darwin':
            # OS X
            self.temp_dir = '/tmp'
        elif platform == 'win32':
            # Windows
            self.temp_dir = 'C:\\Windows\\temp\\'
        self.ui_single_file_upload.tmp_path.setText(self.temp_dir)

        # initialize variables
        self.shards_already_uploaded = 0
        self.uploaded_shards_count = 0
        self.upload_queue_progressbar_list = []

        self.connect(self, QtCore.SIGNAL('addRowToUploadQueueTable'), self.add_row_upload_queue_table)

        self.connect(self, QtCore.SIGNAL('incrementShardsProgressCounters'), self.increment_shards_progress_counters)
        self.connect(self, QtCore.SIGNAL('updateUploadTaskState'), self.update_upload_task_state)
        self.connect(self, QtCore.SIGNAL('updateShardUploadProgress'), self.update_shard_upload_progess)
        self.connect(self, QtCore.SIGNAL('showFileNotSelectedError'), self.show_error_not_selected_file)
        self.connect(self, QtCore.SIGNAL('showInvalidPathError'), self.show_error_invalid_file_path)
        self.connect(self, QtCore.SIGNAL('showInvalidTemporaryPathError'), self.show_error_invalid_temporary_path)
        self.connect(self, QtCore.SIGNAL('refreshOverallProgress'), self.refresh_overall_progress)
        self.connect(self, QtCore.SIGNAL('showFileUploadedSuccessfully'), self.show_upload_finished_message)
        self.connect(self, QtCore.SIGNAL('finishUpload'),
            lambda: self.finish_upload(os.path.split(
                str(self.ui_single_file_upload.file_path.text()))[1],
                str(self.current_selected_bucket_id)))
        self.connect(self, QtCore.SIGNAL('setCurrentUploadState'), self.set_current_status)
        self.connect(self, QtCore.SIGNAL('updateShardUploadCounters'), self.update_shards_counters)
        self.connect(self, QtCore.SIGNAL('setCurrentActiveConnections'), self.set_current_active_connections)
        self.connect(self, QtCore.SIGNAL('setShardSize'), self.set_shard_size)
        #self.connect(self, QtCore.SIGNAL('handleCancelAction'), self.ha)

        # resolve buckets and put to buckets combobox
        self.createBucketResolveThread()

        # file_pointers = self.storj_engine.storj_client.file_pointers(
        #   "6acfcdc62499144929cf9b4a", "dfba26ab34466b1211c60d02")

        # self.emit(QtCore.SIGNAL("addRowToUploadQueueTable"), "important", "information")
        # self.emit(QtCore.SIGNAL("addRowToUploadQueueTable"), "important", "information")
        # self.emit(QtCore.SIGNAL("incrementShardsProgressCounters"))

        self.max_retries_upload_to_same_farmer = MAX_RETRIES_UPLOAD_TO_SAME_FARMER
        self.max_retries_negotiate_contract = MAX_RETRIES_NEGOTIATE_CONTRACT

        # self.initialize_shard_queue_table(file_pointers)

        self.shard_upload_percent_list = []

        self.ui_single_file_upload.overall_progress.setValue(0)

    def set_shard_size(self, shard_size):
        self.ui_single_file_upload.shardsize.setText(str(self.tools.human_size(int(shard_size))))


    def handle_cancel_action(self):
        if self.is_upload_active:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Question, "Question",
                                       "Are you sure that you want cancel upload and close this window?",
                                       (QtGui.QMessageBox.Yes | QtGui.QMessageBox.No))
            result = msgBox.exec_()
            if result == QtGui.QMessageBox.Yes:
                self.close()
        else:
            self.close()


    def show_upload_finished_message(self):
        self.is_upload_active = False
        self.ui_single_file_upload.start_upload_bt.setStyleSheet(("QPushButton:hover{\n"
                                                                  "  background-color: #83bf20;\n"
                                                                  "  border-color: #83bf20;\n"
                                                                  "}\n"
                                                                  "QPushButton:active {\n"
                                                                  "  background-color: #93cc36;\n"
                                                                  "  border-color: #93cc36;\n"
                                                                  "}\n"
                                                                  "QPushButton{\n"
                                                                  "  background-color: #88c425;\n"
                                                                  "    border: 1px solid #88c425;\n"
                                                                  "    color: #fff;\n"
                                                                  "    border-radius: 7px;\n"
                                                                  "}"))
        self.ui_single_file_upload.file_path.setText("")
        QMessageBox.information(self, 'Success!', 'File uploaded successfully!')

    def refresh_overall_progress(self, base_percent):
        """
        """
        total_percent_to_upload = self.all_shards_count * 100
        total_percent_uploaded = sum(self.shard_upload_percent_list) * 100

        actual_percent_uploaded = total_percent_uploaded / total_percent_to_upload

        total_percent = (base_percent * 100) + (0.90 * actual_percent_uploaded)

        self.__logger.info('%s %s total_percent_uploaded' % (actual_percent_uploaded, base_percent))

        # actual_upload_progressbar_value = self.ui_single_file_upload.overall_progress.value()

        self.ui_single_file_upload.overall_progress.setValue(int(total_percent))

    def set_current_active_connections(self):
        self.ui_single_file_upload.current_active_connections.setText(str(self.current_active_connections))

    def update_shards_counters(self):
        self.ui_single_file_upload.uploaded_shards.setText(str(self.shards_already_uploaded) + "/" + str(self.all_shards_count))


    def update_shard_upload_progess(self, row_position_index, value):
        self.upload_queue_progressbar_list[row_position_index].setValue(value)
        return 1

    def update_upload_task_state(self, row_position, state):
        self.ui_single_file_upload.shard_queue_table_widget.setItem(int(row_position), 3,
                                                                    QtGui.QTableWidgetItem(str(state)))

    def show_error_not_selected_file(self):
        QMessageBox.about(self, 'Error', 'Please select file which you want to upload!')

    def show_error_invalid_file_path(self):
        QMessageBox.about(self, 'Error', 'File path seems to be invalid!')

    def show_error_invalid_temporary_path(self):
        QMessageBox.about(self, 'Error', 'Temporary path seems to be invalid!')

    def createBucketResolveThread(self):
        bucket_resolve_thread = threading.Thread(target=self.initialize_buckets_select_list, args=())
        bucket_resolve_thread.start()

    def initialize_buckets_select_list(self):
        """Get all the buckets in which it is possible to store files, and
        show the names in the dropdown list"""
        # self.__logger.warning(str({
        #   "log_event_type": "info",
        #   "title": "Buckets",
        #   "description": "Resolving buckets from Bridge to buckets combobox..."}))
        # self.__logger.warning('"log_event_type": "info"')
        self.__logger.debug('"title": "Buckets"')
        self.__logger.debug('"description": "Resolving buckets from Bridge to buckets combobox..."')

        self.buckets_list = []
        self.bucket_id_list = []
        self.storj_engine = StorjEngine()
        try:
            for bucket in self.storj_engine.storj_client.bucket_list():
                self.__logger.debug('Found bucket: %s', bucket.name)
                # append buckets to list
                self.buckets_list.append(str(bucket.name).decode('utf8'))
                self.bucket_id_list.append(bucket.id)
        except storj.exception.StorjBridgeApiError as e:
            self.__logger.error(e)
            QMessageBox.about(
                self,
                'Unhandled bucket resolving exception',
                'Exception: %s' % e)

        self.ui_single_file_upload.save_to_bucket_select.addItems(self.buckets_list)

        if APPLY_SELECTED_BUCKET_TO_UPLOADER:
            self.ui_single_file_upload.save_to_bucket_select.setCurrentIndex(int(self.dashboard_instance.current_bucket_index))


    def increment_shards_progress_counters(self):
        # self.shards_already_uploaded += 1
        # self.ui_single_file_upload.shards_uploaded.setText(
        #   html_format_begin + str(self.shards_already_uploaded) + html_format_end)
        return 1

    def add_row_upload_queue_table(self, row_data):
        self.upload_queue_progressbar_list.append(QtGui.QProgressBar())

        self.upload_queue_table_row_count = self.ui_single_file_upload.shard_queue_table_widget.rowCount()

        self.ui_single_file_upload.shard_queue_table_widget.setRowCount(
            self.upload_queue_table_row_count + 1)
        self.ui_single_file_upload.shard_queue_table_widget.setCellWidget(
            self.upload_queue_table_row_count, 0, self.upload_queue_progressbar_list[self.upload_queue_table_row_count])
        self.ui_single_file_upload.shard_queue_table_widget.setItem(
            self.upload_queue_table_row_count, 1, QtGui.QTableWidgetItem(row_data['hash']))
        self.ui_single_file_upload.shard_queue_table_widget.setItem(
            self.upload_queue_table_row_count, 2, QtGui.QTableWidgetItem(
                '%s:%d' % (row_data['farmer_address'], row_data['farmer_port'])))
        self.ui_single_file_upload.shard_queue_table_widget.setItem(
            self.upload_queue_table_row_count, 3, QtGui.QTableWidgetItem(
                str(row_data['state'])))
        self.ui_single_file_upload.shard_queue_table_widget.setItem(
            self.upload_queue_table_row_count, 4, QtGui.QTableWidgetItem(
                str(row_data['token'])))
        self.ui_single_file_upload.shard_queue_table_widget.setItem(
            self.upload_queue_table_row_count, 5, QtGui.QTableWidgetItem(
                str(row_data['shard_index'])))

        self.upload_queue_progressbar_list[self.upload_queue_table_row_count].setValue(0)

        self.__logger.info(row_data)

    def select_tmp_directory(self):
        self.selected_tmp_dir = QtGui.QFileDialog.getExistingDirectory(
            None,
            'Select a folder:',
            self.temp_dir,
            QtGui.QFileDialog.ShowDirsOnly)
        self.__logger.debug('Chosen temp dir: %s', self.selected_tmp_dir)
        self.ui_single_file_upload.tmp_path.setText(str(self.selected_tmp_dir).decode('utf-8'))

    def select_file_path(self):
        self.ui_single_file_upload.file_path.setText(str(QtGui.QFileDialog.getOpenFileName()).decode('utf-8'))

    def createNewUploadThread(self):
        # self.download_thread = DownloadTaskQtThread(url, filelocation, options_chain, progress_bars_list)
        # self.download_thread.start()
        # self.download_thread.connect(self.download_thread, QtCore.SIGNAL('setStatus'), self.test1, Qt.QueuedConnection)
        # self.download_thread.tick.connect(progress_bars_list.setValue)

        # Refactor to QtTrhead

        upload_thread = threading.Thread(target=self.file_upload_begin, args=())
        upload_thread.start()

    def initialize_upload_queue_table(self):

        # initialize variables
        self.shards_already_uploaded = 0
        self.uploaded_shards_count = 0
        self.upload_queue_progressbar_list = []

        self.upload_queue_table_header = ['Progress', 'Hash', 'Farmer', 'State', 'Token', 'Shard index']
        self.ui_single_file_upload.shard_queue_table_widget.setColumnCount(6)
        self.ui_single_file_upload.shard_queue_table_widget.setRowCount(0)
        horHeaders = self.upload_queue_table_header
        self.ui_single_file_upload.shard_queue_table_widget.setHorizontalHeaderLabels(horHeaders)
        self.ui_single_file_upload.shard_queue_table_widget.resizeColumnsToContents()
        self.ui_single_file_upload.shard_queue_table_widget.resizeRowsToContents()

        self.ui_single_file_upload.shard_queue_table_widget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def set_current_status(self, current_status):
        self.ui_single_file_upload.current_state.setText(html_format_begin + current_status + html_format_end)

    def createNewShardUploadThread(self, shard, chapters, frame, file_name):
        # another worker thread for single shard uploading and it will retry if download fail
        upload_thread = threading.Thread(
            target=self.upload_shard(
                shard=shard,
                chapters=chapters,
                frame=frame,
                file_name_ready_to_shard_upload=file_name
            ), args=())
        upload_thread.start()

    def _add_shard_to_table(self, frame_content, shard, chapters):
        """
        Add a row to the shard table and return the row number
        """
        # Add items to shard queue table view
        tablerowdata = {}
        tablerowdata['farmer_address'] = frame_content['farmer']['address']
        tablerowdata['farmer_port'] = frame_content['farmer']['port']
        tablerowdata['hash'] = str(shard.hash)
        tablerowdata['state'] = 'Uploading...'
        tablerowdata['token'] = frame_content['token']
        tablerowdata['shard_index'] = str(chapters)

        # self.__logger.warning('"log_event_type": "debug"')
        self.__logger.debug('"title": "Contract negotiated"')
        self.__logger.debug('"description": "Storage contract negotiated \
                     with: "' +
                            str(frame_content["farmer"]["address"]) + ":" +
                            str(frame_content["farmer"]["port"]))
        # self.__logger.warning(str({"log_event_type": "debug", "title": "Contract negotiated",
        #   "description": "Storage contract negotiated with: " +
        #   str(frame_content["farmer"]["address"] + ":" + str(frame_content["farmer"]["port"]))}))

        # add row to table
        self.emit(QtCore.SIGNAL('addRowToUploadQueueTable'), tablerowdata)

        rowcount = self.ui_single_file_upload.shard_queue_table_widget.rowCount()
        return rowcount

    def _read_in_chunks(self, file_object, shard_size, rowposition, blocksize=1024, chunks=-1, shard_index=None):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        # chunk number (first is 0)
        i = 0
        while chunks:
            data = file_object.read(blocksize)
            if not data:
                break
            yield data
            i += 1
            t1 = float(shard_size) / float(blocksize)
            if shard_size <= blocksize:
                t1 = 1

            percent_uploaded = int(round((100.0 * i) / t1))

            self.__logger.debug(i)
            chunks -= 1

            # update progress bar in upload queue table
            self.emit(QtCore.SIGNAL("updateShardUploadProgress"), int(rowposition), percent_uploaded)
            self.shard_upload_percent_list[shard_index] = percent_uploaded
            self.emit(QtCore.SIGNAL("refreshOverallProgress"), 0.1)  # update overall progress bar

    def upload_shard(self, shard, chapters, frame, file_name_ready_to_shard_upload):

        contract_negotiation_tries = 0

        while MAX_RETRIES_NEGOTIATE_CONTRACT > contract_negotiation_tries:
            contract_negotiation_tries += 1
            exchange_report = storj.model.ExchangeReport()

            # emit signal to add row to upload queue table
            # self.emit(QtCore.SIGNAL("addRowToUploadQueueTable"), "important", "information")

            # self.ui_single_file_upload.current_state.setText(
            #   html_format_begin + "Adding shard " + str(chapters) +
            #   " to file frame and getting contract..." + html_format_end)

            # self.__logger.warning('"log_event_type": "debug"')
            self.__logger.debug('"title": "Negotiating contract"')
            self.__logger.debug('"description": "Trying to negotiate storage \
                    contract for shard at index %s"' % chapters)
            if contract_negotiation_tries > 1:
                self.emit(
                    QtCore.SIGNAL('setCurrentUploadState'),
                    'Trying to negotiate storage contract for shard at index %s... Retry %s... ' % (
                        str(chapters), contract_negotiation_tries))
            else:
                self.emit(
                    QtCore.SIGNAL('setCurrentUploadState'),
                    'Trying to negotiate storage contract for shard at index %s...' % str(chapters))
            # self.__logger.warning(str({
            #   "log_event_type": "debug",
            #   "title": "Negotiating contract",
            #   "description": "Trying to negotiate storage contract for shard at index " + str(chapters) + "..."}))

            try:
                frame_content = self.storj_engine.storj_client.frame_add_shard(shard, frame.id)
                # Add a row to the table
                rowposition = self._add_shard_to_table(
                    frame_content,
                    shard,
                    chapters)

                self.__logger.debug('-' * 30)
                # self.__logger.debug("FRAME CONTENT: " + str(frame_content))
                # self.__logger.debug("SHARD: " + str(shard))
                self.__logger.debug(frame_content['farmer']['address'])

                farmerNodeID = frame_content['farmer']['nodeID']

                url = 'http://' + frame_content['farmer']['address'] + ':' + \
                      str(frame_content['farmer']['port']) + '/shards/' + \
                      frame_content['hash'] + '?token=' + \
                      frame_content['token']
                self.__logger.debug('URL: %s', url)

                self.__logger.debug('-' * 30)

                # files = {'file': open(file_path + '.part%s' % chapters)}
                # headers = {'content-type: application/octet-stream', 'x-storj-node-id: ' + str(farmerNodeID)}

                self.emit(
                    QtCore.SIGNAL('setCurrentUploadState'),
                    'Uploading shard %s to farmer...' % str(chapters + 1))

                # begin recording exchange report

                current_timestamp = int(time.time())

                exchange_report.exchangeStart = str(current_timestamp)
                exchange_report.farmerId = str(farmerNodeID)
                exchange_report.dataHash = str(shard.hash)

                shard_size = int(shard.size)

                farmer_tries = 0
                response = None
                success_shard_upload = False
                while MAX_RETRIES_UPLOAD_TO_SAME_FARMER > farmer_tries:
                    farmer_tries += 1
                    try:
                        self.__logger.debug(
                            'Upload shard at index ' +
                            str(shard.index) + ' to ' +
                            str(frame_content['farmer']['address']) +
                            ':' +
                            str(frame_content['farmer']['port']))

                        # self.__logger.warning(str({
                        #   "log_event_type": "debug",
                        #   "title": "Uploading shard",
                        #   "description": "Uploading shard at index " + str(shard.index) + " to " + str(
                        #       frame_content["farmer"]["address"] + ":" + str(frame_content["farmer"][
                        #       "port"]))}))

                        mypath = os.path.join(self.parametrs.tmpPath,
                                              file_name_ready_to_shard_upload +
                                              '-' + str(chapters + 1))

                        # with open(
                        #   self.parametrs.tmpPath + file_name_ready_to_shard_upload + '-' +
                        #   str(chapters + 1), 'rb') as f:
                        self.current_active_connections += 1
                        self.emit(QtCore.SIGNAL('setCurrentActiveConnections'))
                        with open(mypath, 'rb') as f:
                            response = requests.post(
                                url,
                                data=self._read_in_chunks(
                                    f,
                                    shard_size,
                                    rowposition,
                                    shard_index=chapters
                                ),
                                timeout=1)

                        j = json.loads(str(response.content))
                        if j.get('result') == 'The supplied token is not accepted':
                            raise storj.exception.StorjFarmerError(
                                storj.exception.StorjFarmerError.SUPPLIED_TOKEN_NOT_ACCEPTED)
                        success_shard_upload = True

                    except storj.exception.StorjFarmerError as e:
                        self.__logger.error(e)
                        self.current_active_connections -= 1
                        self.emit(QtCore.SIGNAL('setCurrentActiveConnections'))

                        # upload failed due to Farmer Failure
                        if str(e) == str(storj.exception.StorjFarmerError.SUPPLIED_TOKEN_NOT_ACCEPTED):
                            self.__logger.error('The supplied token not accepted')
                        # print_("Exception raised while trying to negitiate contract: " + str(e))
                        continue

                    except Exception as e:
                        self.__logger.error(e)
                        self.current_active_connections -= 1
                        self.emit(QtCore.SIGNAL('setCurrentActiveConnections'))

                        # update shard upload state
                        self.emit(
                            QtCore.SIGNAL('updateUploadTaskState'),
                            rowposition,
                            'First try failed. Retrying... (' + str(farmer_tries) + ')')

                        # self.__logger.warning('"log_event_type": "warning"')
                        self.__logger.warning('"title": "Shard upload error"')
                        self.__logger.warning(
                            '"description": "Error while uploading \
                                       shard to: "' +
                            str(frame_content["farmer"]["address"]) +
                            ":" +
                            str(frame_content["farmer"]["port"]) +
                            " Retrying... (" + str(farmer_tries) +
                            ")")
                        # self.__logger.warning(str({"log_event_type": "warning", "title": "Shard upload error",
                        #   "description": "Error while uploading shard to: " + str(
                        #   frame_content["farmer"]["address"] + ":" + str(frame_content["farmer"][
                        #   "port"])) + " Retrying... (" + str(farmer_tries) + ")"}))
                        continue

                    else:
                        self.current_active_connections -= 1
                        self.emit(QtCore.SIGNAL('setCurrentActiveConnections'))
                        self.emit(
                            # update already uploaded shards count
                            QtCore.SIGNAL('incrementShardsProgressCounters'))
                        self.shards_already_uploaded += 1

                        # update already uploaded shards count
                        self.emit(QtCore.SIGNAL('updateShardUploadCounters'))
                        # logger.warning('"log_event_type": "success"')
                        self.__logger.debug("Shard uploaded successfully to " +
                                     str(frame_content["farmer"]["address"]) +
                                     ":" +
                                     str(frame_content["farmer"]["port"]))
                        # logger.warning(str({"log_event_type": "success", "title": "Uploading shard",
                        #                     "description": "Shard uploaded successfully to " + str(
                        #   frame_content["farmer"]["address"] + ":" + str(frame_content["farmer"][
                        #                             "port"]))}))

                        self.emit(QtCore.SIGNAL("updateUploadTaskState"), rowposition,
                                  "Uploaded!")  # update shard upload state

                        self.__logger.debug(str(self.all_shards_count) + " shards, " +
                                     str(self.shards_already_uploaded) + "sent")

                        if int(self.all_shards_count) <= int(self.shards_already_uploaded):
                            # send signal to save to bucket after all files are uploaded
                            self.emit(
                                QtCore.SIGNAL('finishUpload'))
                        break

                if not success_shard_upload:
                    # update shard upload state
                    self.emit(
                        QtCore.SIGNAL('updateUploadTaskState'),
                        rowposition,
                        'Failed. Trying to upload to another farmer...')

                self.__logger.debug(response.content)

                j = json.loads(str(response.content))
                if j.get('result') == 'The supplied token is not accepted':
                    raise storj.exception.StorjFarmerError(
                        storj.exception.StorjFarmerError.SUPPLIED_TOKEN_NOT_ACCEPTED)

            except storj.exception.StorjBridgeApiError as e:
                self.__logger.error(e)

                # upload failed due to Storj Bridge failure
                self.__logger.error('Exception raised while trying to negitiate contract')
                # self.__logger.warning('"log_event_type": "error"')
                self.__logger.error('"title": "Bridge exception"')
                self.__logger.error('"description": "Exception raised while trying \
                               to negotiate storage contract for shard at index\
                               "' + str(chapters))
                # self.__logger.warning(str({"log_event_type": "error", "title": "Bridge exception",
                #   "description":
                #   "Exception raised while trying to negitiate storage contract for shard at index " + str(
                #   chapters)}))
                continue

            except Exception as e:
                self.__logger.error(e)

                # now send Exchange Report
                # upload failed probably while sending data to farmer
                self.__logger.error('Error occured while trying to upload shard or negotiate contract. Retrying... ')

                # self.__logger.warning('"log_event_type": "error"')
                self.__logger.error('"title": "Unhandled exception"')
                self.__logger.error('"description": "Unhandled exception occured\
                             while trying to upload shard or negotiate \
                             contract for shard at index "' +
                                    str(chapters) +
                                    " . Retrying...")
                # self.__logger.warning(str({"log_event_type": "error", "title": "Unhandled exception",
                #   "description":
                #   "Unhandled exception occured while trying to upload shard or
                #   negotiate contract for shard at index " + str(chapters) + " . Retrying..."}))
                current_timestamp = int(time.time())

                exchange_report.exchangeEnd = str(current_timestamp)
                exchange_report.exchangeResultCode = exchange_report.FAILURE
                exchange_report.exchangeResultMessage = exchange_report.STORJ_REPORT_UPLOAD_ERROR

                self.emit(
                    QtCore.SIGNAL('setCurrentUploadState'),
                    'Sending Exchange Report for shard %s' % str(chapters + 1))
                # self.storj_engine.storj_client.send_exchange_report(exchange_report) # send exchange report
                continue

            # uploaded with success
            current_timestamp = int(time.time())
            # prepare second half of exchange heport
            exchange_report.exchangeEnd = str(current_timestamp)
            exchange_report.exchangeResultCode = exchange_report.SUCCESS
            exchange_report.exchangeResultMessage = exchange_report.STORJ_REPORT_SHARD_UPLOADED
            self.emit(QtCore.SIGNAL("setCurrentUploadState"),
                      "Sending Exchange Report for shard " + str(chapters + 1))
            # self.__logger.warning('"log_event_type": "debug"')
            self.__logger.info("Shard " + str(chapters + 1) +
                               " successfully added and exchange report sent.")
            # self.__logger.warning(str({"log_event_type": "debug", "title": "Shard added",
            #                     "description": "Shard " + str(chapters + 1) + " successfully added and exchange report sent."}))
            # self.storj_engine.storj_client.send_exchange_report(exchange_report) # send exchange report
            break

    def finish_upload(self, bname, bucket_id):
        self.crypto_tools = CryptoTools()
        # self.ui_single_file_upload.current_state.setText(
        #   html_format_begin + "Generating SHA5212 HMAC..." + html_format_end)
        # self.__logger.warning('"log_event_type": "debug"')
        self.__logger.debug('"title": "HMAC"')
        self.__logger.debug('"description": "Generating HMAC..."')
        # self.__logger.warning(str({"log_event_type": "debug", "title": "HMAC",
        #                     "description": "Generating HMAC..."}))
        hash_sha512_hmac_b64 = self.crypto_tools.prepare_bucket_entry_hmac(self.shard_manager_result.shards)
        hash_sha512_hmac = hashlib.sha224(str(hash_sha512_hmac_b64["SHA-512"])).hexdigest()
        self.__logger.debug(hash_sha512_hmac)
        # save

        # import magic
        # mime = magic.Magic(mime=True)
        # mime.from_file(file_path)

        self.__logger.debug(self.frame.id)
        self.__logger.debug("Now upload file")

        data = {
            'x-token': self.push_token.id,
            'x-filesize': str(self.uploaded_file_size),
            'frame': self.frame.id,
            'mimetype': self.file_mime_type,
            'filename': str(bname) + str(self.fileisdecrypted_str),
            'hmac': {
                'type': "sha512",
                # 'value': hash_sha512_hmac["sha512_checksum"]
                'value': hash_sha512_hmac
            },
        }
        # self.ui_single_file_upload.current_state.setText(
        #   html_format_begin + "Adding file to bucket..." + html_format_end)

        # self.__logger.warning('"log_event_type": "debug"')
        self.__logger.debug('"title": "Finishing upload"')
        self.__logger.debug('"description": "Adding file "' +
                            str(bname) + " to bucket...")
        self.emit(QtCore.SIGNAL("setCurrentUploadState"), "Adding file to bucket...")

        # self.__logger.warning(str({"log_event_type": "debug", "title": "Finishing upload",
        #                     "description": "Adding file " + str(bname) + " to bucket..."}))

        success = False
        try:
            response = self.storj_engine.storj_client._request(
                method='POST', path='/buckets/%s/files' % bucket_id,
                # files={'file' : file},
                headers={
                    'x-token': self.push_token.id,
                    'x-filesize': str(self.uploaded_file_size),
                },
                json=data,
            )
            success = True
        except storj.exception.StorjBridgeApiError as e:
            QMessageBox.about(self, "Unhandled bridge exception", "Exception: " + str(e))
        if success:
            # self.ui_single_file_upload.current_state.setText(
            #   html_format_begin + "Upload success! Waiting for user..." + html_format_end)
            # self.__logger.warning('"log_event_type": "success"')
            self.__logger.debug('"title": "File uploaded"')
            self.__logger.debug('"description": "File uploaded successfully!"')
            # self.__logger.warning(str({"log_event_type": "success", "title": "File uploaded",
            #                     "description": "File uploaded successfully!"}))
            self.emit(QtCore.SIGNAL("showFileUploadedSuccessfully"))
            self.emit(QtCore.SIGNAL("setCurrentUploadState"), "File uploaded successfully!")
            self.dashboard_instance.createNewFileListUpdateThread()

    def file_upload_begin(self):
        self.ui_single_file_upload.overall_progress.setValue(0)
        # upload finish function #

        # end upload finishing function #

        file_path = None
        self.validation = {}

        self.initialize_upload_queue_table()

        # item = ProgressWidgetItem()
        # self.ui_single_file_upload.shard_queue_table_widget.setItem(1, 1, item)
        # item.updateValue(1)

        # progress.valueChanged.connect(item.updateValue)

        encryption_enabled = True
        self.parametrs = storj.model.StorjParametrs()

        # get temporary files path
        self.parametrs.tmpPath = str(self.ui_single_file_upload.tmp_path.text())
        self.__logger.debug("Temporary path chosen: " + self.parametrs.tmpPath)

        self.configuration = Configuration()

        # TODO: redundant lines?
        # get temporary files path
        if self.ui_single_file_upload.file_path.text() == "":
            self.parametrs.tmpPath = "/tmp/"
            self.validation["file_path"] = False
            self.emit(QtCore.SIGNAL("showFileNotSelectedError"))  # show error missing file path
            self.__logger.error("temporary path missing")
        else:
            self.parametrs.tmpPath = str(self.ui_single_file_upload.tmp_path.text())
            self.validation["file_path"] = True
            file_path = str(self.ui_single_file_upload.file_path.text()).decode('utf-8')

        if self.validation["file_path"]:

            self.current_bucket_index = self.ui_single_file_upload.save_to_bucket_select.currentIndex()
            self.current_selected_bucket_id = self.bucket_id_list[self.current_bucket_index]
            bucket_id = str(self.current_selected_bucket_id)

            bname = os.path.split(file_path)[1]  # File name

            self.__logger.debug(bname + "npliku")

            # Temporary replace magic with mimetypes python library
            if mimetypes.guess_type(file_path)[0] is not None:
                file_mime_type = mimetypes.guess_type(file_path)[0]
            else:
                file_mime_type = "text/plain"

            file_mime_type = "text/plain"

            # mime = magic.Magic(mime=True)
            # file_mime_type = str(mime.from_file(file_path))

            self.__logger.debug(file_mime_type)
            # file_mime_type = str("A")

            file_existence_in_bucket = False

            # if self.configuration.sameFileNamePrompt or self.configuration.sameFileHashPrompt:
            # file_existence_in_bucket =
            # self.storj_engine.storj_client.check_file_existence_in_bucket(bucket_id=bucket_id,
            # filepath=file_path) # check if exist file with same file name

            if file_existence_in_bucket == 1:
                # QInputDialog.getText(self, 'Warning!', 'File with name ' + str(bname) + " already exist in bucket! Please use different name:", "test" )
                self.__logger.warning("Same file exist!")

            self.fileisdecrypted_str = ""
            if self.ui_single_file_upload.encrypt_files_checkbox.isChecked():
                # encrypt file
                self.emit(QtCore.SIGNAL("setCurrentUploadState"), "Encrypting file...")
                # self.__logger.warning('"log_event_type": "debug"')
                self.__logger.debug('"title": "Encryption"')
                self.__logger.debug('"description": "Encrypting file..."')

                file_crypto_tools = FileCrypto()
                # Path where to save the encrypted file in temp dir
                file_path_ready = os.path.join(self.parametrs.tmpPath,
                                               bname + ".encrypted")
                self.__logger.debug("Call encryption method")
                # begin file encryption")
                file_crypto_tools.encrypt_file(
                    "AES",
                    file_path,
                    file_path_ready,
                    self.storj_engine.account_manager.get_user_password())
                # file_path_ready = self.parametrs.tmpPath + "/" + bname +\
                #     ".encrypted"  # get path to encrypted file in temp dir
                file_name_ready_to_shard_upload = bname + ".encrypted"
                self.fileisdecrypted_str = ""
            else:
                self.fileisdecrypted_str = "[DECRYPTED]"
                file_path_ready = file_path
                file_name_ready_to_shard_upload = bname

            self.__logger.debug("Temp path: " + self.parametrs.tmpPath)
            self.__logger.debug(file_path_ready + "sciezka2")

            def get_size(file_like_object):
                return os.stat(file_like_object.name).st_size

            # file_size = get_size(file)

            file_size = os.stat(file_path).st_size
            self.uploaded_file_size = file_size
            self.file_mime_type = file_mime_type



            self.ui_single_file_upload.file_size.setText(str(self.tools.human_size(int(file_size))))

            # self.ui_single_file_upload.current_state.setText(
            #   html_format_begin + "Resolving PUSH token..." + html_format_end)

            # self.__logger.warning('"log_event_type": "debug"')

            self.is_upload_active = True
            self.ui_single_file_upload.start_upload_bt.setStyleSheet(("QPushButton:hover{\n"
                                                                      "  background-color: #8C8A87;\n"
                                                                      "  border-color: #8C8A87;\n"
                                                                      "}\n"
                                                                      "QPushButton:active {\n"
                                                                      "  background-color: #8C8A87;\n"
                                                                      "  border-color: #8C8A87;\n"
                                                                      "}\n"
                                                                      "QPushButton{\n"
                                                                      "  background-color: #8C8A87;\n"
                                                                      "    border: 1px solid #8C8A87;\n"
                                                                      "    color: #fff;\n"
                                                                      "    border-radius: 7px;\n"
                                                                      "}"))

            self.__logger.debug('"title": "PUSH token"')
            self.__logger.debug('"description": "Resolving PUSH Token for upload..."')
            # self.__logger.warning(str({"log_event_type": "debug", "title": "PUSH token",
            #                     "description": "Resolving PUSH Token for upload..."}))

            push_token = None

            try:
                push_token = self.storj_engine.storj_client.token_create(bucket_id,
                                                                         'PUSH')  # get the PUSH token from Storj Bridge
                self.push_token = push_token
            except storj.exception.StorjBridgeApiError as e:
                self.is_upload_active = False
                QMessageBox.about(self, "Unhandled PUSH token create exception", "Exception: " + str(e))

            self.ui_single_file_upload.push_token.setText(
                str(push_token.id))  # set the PUSH Token

            self.__logger.debug("PUSH Token ID: " + push_token.id)

            # self.ui_single_file_upload.current_state.setText(
            #    html_format_begin + "Resolving frame for file..." + html_format_end)

            # self.__logger.warning('"log_event_type": "debug"')
            self.__logger.debug('"title": "Frame"')
            self.__logger.debug('"description": "Resolving frame for file upload..."')
            # self.__logger.warning(str({"log_event_type": "debug", "title": "Frame",
            #                     "description": "Resolving frame for file upload..."}))

            frame = None  # initialize variable
            try:
                frame = self.storj_engine.storj_client.frame_create()  # Create file frame
                self.frame = frame
            except storj.exception.StorjBridgeApiError as e:
                self.is_upload_active = False
                QMessageBox.about(
                    self,
                    'Unhandled exception while creating file staging frame',
                    'Exception: %s' % e)
                # self.__logger.warning('"log_event_type": "error"')
                self.__logger.debug('"title": "Frame"')
                self.__logger.debug('"description": "Error while resolving frame for\
                    file upload..."')
                # self.__logger.warning(str({"log_event_type": "error", "title": "Frame",
                #                     "description": "Error while resolving frame for file upload..."}))

            self.ui_single_file_upload.file_frame_id.setText(str(frame.id))

            self.__logger.debug('Frame ID: %s', frame.id)
            # Now encrypt file
            self.__logger.debug('%s sciezka', file_path_ready)

            # Now generate shards
            self.emit(QtCore.SIGNAL('setCurrentUploadState'), 'Splitting file to shards...')
            # self.__logger.warning('"log_event_type": "debug"')
            self.__logger.debug('"title": "Sharding"')
            self.__logger.debug('"description": "Splitting file to shards..."')
            # self.__logger.warning(str({"log_event_type": "debug", "title": "Sharding",
            #                     "description": "Splitting file to shards..."}))

            shards_manager = storj.model.ShardManager(filepath=file_path_ready, tmp_path=self.parametrs.tmpPath)
            self.all_shards_count = len(shards_manager.shards)
            self.emit(QtCore.SIGNAL("updateShardUploadCounters"))

            self.shard_manager_result = shards_manager
            # self.ui_single_file_upload.current_state.setText(
            #   html_format_begin + "Generating shards..." + html_format_end)
            # shards_manager._make_shards()
            shards_count = shards_manager.index
            # create file hash
            self.__logger.debug('file_upload() push_token=%s', push_token)

            # upload shards to frame
            self.__logger.debug('Shards count %s' % shards_count)

            # set shards count
            # self.ui_single_file_upload.shards_count.setText(html_format_begin + str(shards_count) + html_format_end)
            self.all_shards_count = shards_count

            chapters = 0


            for shard in shards_manager.shards:
                self.emit(QtCore.SIGNAL("setShardSize"), int(shard.size))

                self.shard_upload_percent_list.append(0)
                self.createNewShardUploadThread(shard, chapters, frame, file_name_ready_to_shard_upload)
                chapters += 1

                # delete encrypted file TODO

                # self.emit(QtCore.SIGNAL("finishUpload")) # send signal to save to bucket after all filea are uploaded

                # finish_upload(self)
