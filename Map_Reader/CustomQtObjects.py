from PyQt5.QtWidgets import *
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
        QTime, QModelIndex, QSize)
from PyQt5.QtGui import QStandardItemModel, QIcon

class Button(QPushButton):
    def __init__(self, name=None):
        super(Button, self).__init__()
        self.setMouseTracking(True)
        self.setText(name)
        
    def enterEvent(self, event):
        if self.isEnabled():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(2)
            shadow.setOffset(3, 3)
            self.setGraphicsEffect(shadow)

    def leaveEvent(self, event):
        self.setGraphicsEffect(None)

class LineEdit(QLineEdit):
    def __init__(self, name=None):
        super(LineEdit, self).__init__()
        self.setText(name)
        
    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(2)
        shadow.setOffset(3, 3)
        self.setGraphicsEffect(shadow)

    def focusOutEvent(self, event):
        QLineEdit.focusOutEvent(self, event)
        self.setGraphicsEffect(None)

class Table(QWidget):
    def __init__(self, name, data, columns=None, index=False, sortCol=None, parent=None):
        super(Table, self).__init__(parent)

        self.name = name
        self.index = index
        
        if not any([data, columns]):
            self.columns = []
        else:
            self.columns = columns if columns else data[0].keys()

        if index:
            self.columns.insert(0, 'ID')

        self.setData(data)

        self.initUI()
        self.sortBy(sortCol)

    def initUI(self):
        '''
        Layout UI elements of table
        '''
        mainLayout = QVBoxLayout()

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)

        self.sourceModel = QStandardItemModel(0, len(self.columns), self)
        for i, column in enumerate(self.columns):
            self.sourceModel.setHeaderData(i, Qt.Horizontal, column)

        self.proxyModel.setSourceModel(self.sourceModel)
        
        self.proxyGroupBox = QGroupBox(self.name)

        self.proxyView = QTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.proxyModel)
        self.proxyView.setSortingEnabled(True)

        self.proxyView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        proxyLayout = QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        self.proxyGroupBox.setLayout(proxyLayout)

        mainLayout.addWidget(self.proxyGroupBox)
        self.setLayout(mainLayout)
        self.update(self.data)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def setData(self, data):
        self.data = [{k: item.get(k, i+1) for k in self.columns} for i, item in enumerate(data)]

    def sortBy(self, colName):
        idx = 0
        try:
            idx = self.columns.index(colName)
        except:
            pass

        self.proxyView.sortByColumn(idx, Qt.AscendingOrder)

    def rowCount(self):
        return self.sourceModel.rowCount()

    def columnCount(self):
        return self.sourceModel.columnCount()

    def setColumns(self, cols):
        if not cols:
            self.columns = self.data[0].keys()

        if self.index:
            self.columns = ['ID'] + cols
        else:
            self.columns = columns
            
        self.update(self.data)

    def addRow(self, row_i, rowData):
        self.sourceModel.insertRow(row_i)

        for col_i, data in enumerate(rowData.values()):
           self.sourceModel.setData(self.sourceModel.index(row_i, col_i), data)
        
    def update(self, data):
        self.setData(data)
        self.sourceModel.removeRows(0, self.sourceModel.rowCount())
        
        for i, data in enumerate(self.data):
            self.addRow(i, data)
    
    def getSelectedRowIndex(self):
        try:
            return self.proxyView.selectedIndexes()[0].row()
        except:
            return False