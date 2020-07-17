import sys
from collections import deque

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase

from ui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView, qApp
from PyQt5 import QtSql
from PyQt5 import QtCore


def createConnection():
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('task')
    if not db.open():
        QMessageBox.critical(None, qApp.tr("Cannot open database"),
                             qApp.tr("Unable to establish a database connection."),
                             QMessageBox.Cancel)
        return False
    return True


class MyTree(QtWidgets.QWidget):
    def __init__(self, data):
        super(MyTree, self).__init__()
        self.tree = QtWidgets.QTreeView(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'id_parent'])
        self.tree.header().setDefaultSectionSize(180)
        self.tree.setModel(self.model)
        self.importData(data)
        self.tree.expandAll()

    def importData(self, data, root=None):
        self.model.setRowCount(0)
        if root is None:
            root = self.model.invisibleRootItem()
        seen = {}
        values = deque(data)
        while values:
            value = values.popleft()
            if value['level'] == 0:
                parent = root
            else:
                pid = value['parent_ID']
                if pid not in seen:
                    values.append(value)
                    continue
                parent = seen[pid]
            dbid = value['dbID']
            parent.appendRow([
                QtGui.QStandardItem(value['short_name']),
                QtGui.QStandardItem(str(dbid)),
            ])
            seen[dbid] = parent.child(parent.rowCount() - 1)


class CustomSqlModel(QSqlQueryModel):
    def __init__(self):
        QSqlQueryModel.__init__(self)
        self.setQuery("Select * from hierarhy")
        self.setHeaderData(0, Qt.Horizontal, "id")
        self.setHeaderData(1, Qt.Horizontal, "id_parent")
        self.setHeaderData(2, Qt.Horizontal, "Name")
        self.setHeaderData(3, Qt.Horizontal, "Image")
        self.setHeaderData(4, Qt.Horizontal, "state")

    def data(self, item, role):
        if role == Qt.BackgroundRole:
            if QSqlQueryModel.data(self, self.index(item.row(), 4), Qt.DisplayRole) == 0:
                return QBrush(Qt.red)
            elif QSqlQueryModel.data(self, self.index(item.row(), 4), Qt.DisplayRole) == 1:
                return QBrush(Qt.yellow)
            elif QSqlQueryModel.data(self, self.index(item.row(), 4), Qt.DisplayRole) == 2:
                return QBrush(Qt.green)
        return QSqlQueryModel.data(self, item, role)


class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('task')
        self.model = QtSql.QSqlTableModel()
        self.model.setTable('hierarhy')
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.select()
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, "id")
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, "id_parent")
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, "name")
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, "image")
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, "state")
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.hideColumn(0)
        self.ui.tableView.hideColumn(1)
        self.ui.tableView.hideColumn(4)
        self.ui.tableView.setColumnWidth(2, 170)
        self.ui.tableView.setColumnWidth(3, 220)

        self.ui.pushButton.clicked.connect(self.addToDb)
        self.show()
        self.ui.pushButton_2.clicked.connect(self.updaterow)
        self.ui.pushButton_3.clicked.connect(self.delrow)
        self.i = self.model.rowCount()
        self.ui.pushButton_5.clicked.connect(self.getFileName)

    def addToDb(self):
        self.model.insertRows(self.i, 1)
        self.model.setData(self.model.index(self.i, 3), self.ui.lineEdit_2.text())
        self.model.setData(self.model.index(self.i, 2), self.ui.lineEdit.text())
        self.model.setData(self.model.index(self.i, 4), self.ui.tableView.currentIndex())
        self.model.sub.submitAll()
        self.i += 1

    def delrow(self):
        if self.ui.tableView.currentIndex().row() > -1:
            self.model.removeRow(self.ui.tableView.currentIndex().row())
            self.i -= 1
            self.model.select()
        else:
            QMessageBox.question(self, 'Message', "Пожалуйста, выберите строку, которую вы хотите удалить",
                                 QMessageBox.Ok)
            self.show()

    def updaterow(self):
        if self.ui.tableView.currentIndex().row() > -1:
            record = self.model.record(self.ui.tableView.currentIndex().row())
            record.setValue("Name", self.ui.lineEdit.text())
            record.setValue("Image", self.ui.lineEdit_2.text())
            self.model.setRecord(self.ui.tableView.currentIndex().row(), record)
        else:
            QMessageBox.question(self, 'Message', "Please select a row would you like to update", QMessageBox.Ok)
            self.show()

    def data(self, item, role):
        if role == Qt.BackgroundRole:
            if QSqlQueryModel.data(self, self.index(item.row(), 4), Qt.DisplayRole) == 0:
                return QBrush(Qt.red)
            elif QSqlQueryModel.data(self, self.index(item.row(), 4), Qt.DisplayRole) == 1:
                return QBrush(Qt.yellow)
            elif QSqlQueryModel.data(self, self.index(item.row(), 4), Qt.DisplayRole) == 2:
                return QBrush(Qt.green)
        return QSqlQueryModel.data(self, item, role)

    def getFileName(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open File',
                                                            './',
                                                            'PNG Files(*.png);;All Files(*)')

        if fileName:
            self.ui.scrollAreaWidgetContents.setStyleSheet(
                "border-image: url(" + fileName + ");"
                                                  "min-width: 100%;"
                                                  "min-height: 100%;")
            self.result = self.ui.lineEdit_2
            self.result.setText(fileName)


if __name__ == '__main__':
    data = [
        {'level': 0, 'dbID': 1, 'parent_ID': 1, 'short_name': 'Армия 1', 'order': 1, 'pos': 0},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 1', 'order': 2, 'pos': 1},
        {'level': 2, 'dbID': 3, 'parent_ID': 2, 'short_name': 'Полк 1', 'order': 3, 'pos': 2},
        {'level': 4, 'dbID': 4, 'parent_ID': 3, 'short_name': 'Дивизион 1', 'order': 4, 'pos': 3},
        {'level': 4, 'dbID': 4, 'parent_ID': 3, 'short_name': 'Дивизион 2', 'order': 4, 'pos': 4},
        {'level': 4, 'dbID': 4, 'parent_ID': 3, 'short_name': 'Дивизион 3', 'order': 4, 'pos': 5},
        {'level': 5, 'dbID': 5, 'parent_ID': 4, 'short_name': 'Взвод 1', 'order': 4, 'pos': 6},
        {'level': 5, 'dbID': 5, 'parent_ID': 4, 'short_name': 'Взвод 2', 'order': 4, 'pos': 7},
        {'level': 5, 'dbID': 5, 'parent_ID': 4, 'short_name': 'Взвод 3', 'order': 4, 'pos': 8},
        {'level': 2, 'dbID': 3, 'parent_ID': 2, 'short_name': 'Полк 2', 'order': 3, 'pos': 9},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 2', 'order': 2, 'pos': 10},
        {'level': 0, 'dbID': 1, 'parent_ID': 2, 'short_name': 'Армия 2', 'order': 1, 'pos': 11},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 3', 'order': 2, 'pos': 12},
        {'level': 2, 'dbID': 3, 'parent_ID': 2, 'short_name': 'Полк 3', 'order': 3, 'pos': 13},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 4', 'order': 2, 'pos': 14},
        {'level': 0, 'dbID': 1, 'parent_ID': 2, 'short_name': 'Армия 3', 'order': 1, 'pos': 15},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 5', 'order': 2, 'pos': 16},
        {'level': 2, 'dbID': 3, 'parent_ID': 2, 'short_name': 'Полк 4', 'order': 3, 'pos': 17},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 6', 'order': 2, 'pos': 18},
        {'level': 2, 'dbID': 3, 'parent_ID': 2, 'short_name': 'Полк 5', 'order': 3, 'pos': 19},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 7', 'order': 2, 'pos': 20},
        {'level': 2, 'dbID': 3, 'parent_ID': 2, 'short_name': 'Полк 6', 'order': 3, 'pos': 21},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 8', 'order': 2, 'pos': 22},
        {'level': 1, 'dbID': 2, 'parent_ID': 1, 'short_name': 'Дивизия 9', 'order': 2, 'pos': 23}
    ]

    app = QApplication(sys.argv)

    frm = Form()

    window = MyTree(data)
    window.setGeometry(600, 50, 400, 470)
    window.setWindowTitle("Hierarhy")
    window.show()

    model = CustomSqlModel()
    view = QTableView()
    view.resizeColumnsToContents()
    view.setModel(model)
    view.setWindowTitle("Hierarhy")
    view.hideColumn(0)
    view.hideColumn(1)
    view.hideColumn(3)
    view.hideColumn(4)
    view.setColumnWidth(2, 300)
    view.resize(300, 470)
    view.show()

    sys.exit(app.exec_())
