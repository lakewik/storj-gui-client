import json
import threading
from PyQt4 import QtCore, QtGui
from .qt_interfaces.file_mirrors_ui_new import Ui_FileMirrorsList
import storj.exception as sjexc

from .engine import StorjEngine
from .node_details import NodeDetailsUI
#from UI.engine import StorjEngine
#from UI.node_details import NodeDetailsUI

from .resources.html_strings import html_format_begin, html_format_end
from .utilities.log_manager import logger


# Mirrors section
class FileMirrorsListUI(QtGui.QMainWindow):

    def __init__(self, parent=None, bucketid=None, fileid=None, filename=None):
        QtGui.QWidget.__init__(self, parent)
        self.file_mirrors_list_ui = Ui_FileMirrorsList()
        self.file_mirrors_list_ui.setupUi(self)
        # model = self.file_mirrors_list_ui.established_mirrors_tree.model()

        self.file_mirrors_list_ui.mirror_details_bt.clicked.connect(
            lambda: self.open_mirror_details_window("established"))
        self.file_mirrors_list_ui.mirror_details_bt_2.clicked.connect(
            lambda: self.open_mirror_details_window("available"))
        self.file_mirrors_list_ui.quit_bt.clicked.connect(self.close)

        self.connect(self, QtCore.SIGNAL("showStorjBridgeException"), self.show_storj_bridge_exception)
        self.connect(self, QtCore.SIGNAL("showUnhandledException"), self.show_unhandled_exception)
        self.connect(self, QtCore.SIGNAL("changeLoadingGif"), self.change_loading_gif)


        # self.connect(self.file_mirrors_list_ui.established_mirrors_tree, QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.open_mirror_details_window)

        # self.connect(self.file_mirrors_list_ui.established_mirrors_tree, QtCore.SIGNAL('selectionChanged()'), self.open_mirror_details_window)

        # QtCore.QObject.connect(self.file_mirrors_list_ui.established_mirrors_tree.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
        # self.open_mirror_details_window)

        # self.file_mirrors_list_ui.established_mirrors_tree.

        self.bucketid = bucketid
        self.fileid = fileid
        self.filename = str(filename).decode('utf-8')

        self.file_mirrors_list_ui.file_id.setText(str(self.fileid))
        self.file_mirrors_list_ui.file_name.setText(str(self.filename).decode('utf-8'))

        logger.info(self.fileid)
        self.storj_engine = StorjEngine()  # init StorjEngine
        self.createNewMirrorListInitializationThread()

    def change_loading_gif(self, is_visible):
        if is_visible:
            movie = QtGui.QMovie(':/resources/loading.gif')
            self.file_mirrors_list_ui.loading_img.setMovie(movie)
            movie.start()
        else:
            self.file_mirrors_list_ui.loading_img.clear()

    def show_unhandled_exception(self, exception_content):
        QtGui.QMessageBox.critical(self, "Unhandled error", str(exception_content))

    def show_storj_bridge_exception(self, exception_content):
        try:
            j = json.loads(str(exception_content))
            QtGui.QMessageBox.critical(self, "Bridge error", str(j["error"]))

        except:
            QtGui.QMessageBox.critical(self, "Bridge error", str(exception_content))

    def open_mirror_details_window(self, mirror_state):
        # self.established_mirrors_tree_view = self.file_mirrors_list_ui.established_mirrors_tree

        # daat = self.file_mirrors_list_ui.established_mirrors_tree.selectedIndexes()
        # model = self.file_mirrors_list_ui.established_mirrors_tree.model()
        # data = []

        # initialize variables
        item = ""
        index = ""
        try:
            if mirror_state == "established":
                index = self.file_mirrors_list_ui.established_mirrors_tree.selectedIndexes()[3]
                item = self.file_mirrors_list_ui.established_mirrors_tree.selectedIndexes()[3]
            elif mirror_state == "available":
                index = self.file_mirrors_list_ui.available_mirrors_tree.selectedIndexes()[3]
                item = self.file_mirrors_list_ui.available_mirrors_tree.selectedIndexes()[3]

            nodeid_to_send = item.model().itemFromIndex(index).text()

            if nodeid_to_send != "":
                self.node_details_window = NodeDetailsUI(self, nodeid_to_send)
                self.node_details_window.show()
            else:
                QtGui.QMessageBox.about(self, "Warning", "Please select farmer node from list")
                logger.warning("Unhandled error")

        except:
            QtGui.QMessageBox.about(self, "Warning", "Please select farmer node from list")
            logger.error("Unhandled error")

    def createNewMirrorListInitializationThread(self):
        mirror_list_initialization_thread = threading.Thread(target=self.initialize_mirrors_tree, args=())
        mirror_list_initialization_thread.start()

    def initialize_mirrors_tree(self):

        self.emit(QtCore.SIGNAL("changeLoadingGif"), True)
        # create model
        # model = QtGui.QFileSystemModel()
        # model.setRootPath(QtCore.QDir.currentPath())

        #self.file_mirrors_list_ui.loading_label_mirrors_established.setStyleSheet('color: red')  # set loading color
        #self.file_mirrors_list_ui.loading_label_mirrors_available.setStyleSheet('color: red')  # set loading color

        self.mirror_tree_view_header = ['Shard Hash / Address', 'User agent', 'Last seed', 'Node ID']

        ######################### set the model for established mirrors ##################################
        self.established_mirrors_model = QtGui.QStandardItemModel()
        self.established_mirrors_model.setHorizontalHeaderLabels(self.mirror_tree_view_header)

        self.established_mirrors_tree_view = self.file_mirrors_list_ui.established_mirrors_tree
        self.established_mirrors_tree_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.established_mirrors_tree_view.setModel(self.established_mirrors_model)
        self.established_mirrors_tree_view.setUniformRowHeights(True)

        self.file_mirrors_list_ui.available_mirrors_tree.setModel(self.established_mirrors_model)

        divider = 0
        group = 1
        self.established_mirrors_count_for_file = 0
        recent_shard_hash = ""
        parent1 = QtGui.QStandardItem('')
        try:
            for file_mirror in self.storj_engine.storj_client.file_mirrors(str(self.bucketid), str(self.fileid)):
                for mirror in file_mirror.established:
                    self.established_mirrors_count_for_file += 1
                    logger.info(file_mirror.established)
                    if mirror["shardHash"] != recent_shard_hash:
                        parent1 = QtGui.QStandardItem('Shard with hash {}'.format(mirror["shardHash"]))
                        divider = divider + 1
                        self.established_mirrors_model.appendRow(parent1)

                    child1 = QtGui.QStandardItem(str(mirror["contact"]["address"] + ":" + str(mirror["contact"]["port"])))
                    child2 = QtGui.QStandardItem(str(mirror["contact"]["userAgent"]))
                    child3 = QtGui.QStandardItem(str(mirror["contact"]["lastSeen"]))
                    child4 = QtGui.QStandardItem(str(mirror["contact"]["nodeID"]))
                    parent1.appendRow([child1, child2, child3, child4])

                    # span container columns
                    # self.established_mirrors_tree_view.setFirstColumnSpanned(1, self.established_mirrors_tree_view.rootIndex(), True)

                    recent_shard_hash = mirror["shardHash"]

            #self.file_mirrors_list_ui.loading_label_mirrors_established.setText("")

            # dbQueryModel.itemData(treeView.selectedIndexes()[0])

            ################################### set the model for available mirrors #########################################
            self.available_mirrors_model = QtGui.QStandardItemModel()
            self.available_mirrors_model.setHorizontalHeaderLabels(self.mirror_tree_view_header)

            self.available_mirrors_tree_view = self.file_mirrors_list_ui.available_mirrors_tree
            self.available_mirrors_tree_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

            self.available_mirrors_tree_view.setModel(self.available_mirrors_model)
            self.available_mirrors_tree_view.setUniformRowHeights(True)

            self.file_mirrors_list_ui.available_mirrors_tree.setModel(self.available_mirrors_model)

            divider = 0
            self.available_mirrors_count_for_file = 0
            recent_shard_hash_2 = ""
            parent2 = QtGui.QStandardItem('')
            for file_mirror in self.storj_engine.storj_client.file_mirrors(str(self.bucketid), str(self.fileid)):
                for mirror_2 in file_mirror.available:
                    self.available_mirrors_count_for_file += 1
                    if mirror_2["shardHash"] != recent_shard_hash_2:
                        parent2 = QtGui.QStandardItem('Shard with hash {}'.format(mirror_2["shardHash"]))
                        divider = divider + 1
                        self.available_mirrors_model.appendRow(parent2)

                    child1 = QtGui.QStandardItem(str(mirror_2["contact"]["address"] + ":" + str(mirror_2["contact"]["port"])))
                    child2 = QtGui.QStandardItem(str(mirror_2["contact"]["userAgent"]))
                    child3 = QtGui.QStandardItem(str(mirror_2["contact"]["lastSeen"]))
                    child4 = QtGui.QStandardItem(str(mirror_2["contact"]["nodeID"]))
                    parent2.appendRow([child1, child2, child3, child4])

                    # span container columns
                    # self.established_mirrors_tree_view.setFirstColumnSpanned(1, self.established_mirrors_tree_view.rootIndex(), True)

                    recent_shard_hash_2 = mirror_2["shardHash"]
            #self.file_mirrors_list_ui.loading_label_mirrors_available.setText("")

            self.file_mirrors_list_ui.established_mirrors_count.setText(
                html_format_begin + "ESTABLISHED (" + str(self.established_mirrors_count_for_file) + ")" + html_format_end)
            self.file_mirrors_list_ui.available_mirrors_count.setText(
                html_format_begin +  "AVAILABLE (" + str(self.available_mirrors_count_for_file) + ")" + html_format_end)

            self.emit(QtCore.SIGNAL("changeLoadingGif"), False)
        except sjexc.StorjBridgeApiError as e:
            self.emit(QtCore.SIGNAL("showStorjBridgeException"), str(e))  # emit Storj Bridge Exception
        except Exception as e:
            self.emit(QtCore.SIGNAL("showUnhandledException"), str(e))  # emit unhandled Exception
            logger.error(e)
