from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
        QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import *
import random

#Define constants for table columns
PID, LAT, LON, DATE, DESC = range(5)

#Class to layout the table and buttons on the main window
class Table(QWidget):
    def __init__(self, parent):
        super(Table, self).__init__(parent)

        self.model = QSortFilterProxyModel()
        self.model.setDynamicSortFilter(True)
        
        #Create and define columns in table
        model = QStandardItemModel(0, 5, self)
        model.setHeaderData(PID, Qt.Horizontal, "Point")
        model.setHeaderData(LAT, Qt.Horizontal, "Latitude")
        model.setHeaderData(LON, Qt.Horizontal, "Longitude")
        model.setHeaderData(DATE, Qt.Horizontal, "Date")
        model.setHeaderData(DESC, Qt.Horizontal, "Description")

        self.model.setSourceModel(model)

        self.proxyGroupBox = QGroupBox("Points")

        self.proxyView = QTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.model)
        self.proxyView.setSortingEnabled(True)

        proxyLayout = QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        self.proxyGroupBox.setLayout(proxyLayout)

        #create horizontal window for storing buttons
        hLayout = QHBoxLayout()

        #Add refrence button and connect it to referenceWindow() in MainWindow to launch window
        self.addRefButton = QPushButton('Add Reference')
        self.addRefButton.clicked.connect(self.parent().referenceWindow)
        
        #Add scale button and connect it to scaleTracker() in MainWindow to launch window
        self.setScaleButton = QPushButton('Set Scale')
        self.setScaleButton.clicked.connect(self.parent().scaleTracker)

        #Add locate button and connect it locationTracker() in MainWindow to launch window
        self.locateButton = QPushButton('Locate Point')
        self.locateButton.clicked.connect(self.parent().locationTracker)

        #Add Plot button and connect it to plotPoints() in MainWindow to launch window
        self.plotButton = QPushButton('Plot')
        self.plotButton.clicked.connect(self.parent().plotPoints)

        #Add all button to horizontal layout
        hLayout.addWidget(self.addRefButton)
        hLayout.addWidget(self.setScaleButton)
        hLayout.addWidget(self.locateButton)
        hLayout.addWidget(self.plotButton)

        #Create main layout and add all table and button sublayouts
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.proxyGroupBox)
        mainLayout.addLayout(hLayout)
        self.setLayout(mainLayout)

        #Sort able by point ID
        self.proxyView.sortByColumn(PID, Qt.AscendingOrder)

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)

    def update(self, points):
        '''
        Update table with points list passed from main window
        Iterate over list and add all data from each dictionary
        '''
        self.model.removeRows(0, self.model.rowCount())
        for i, data in enumerate(points):
            self.model.insertRow(i)
            self.model.setData(self.model.index(i, PID), i+1)
            self.model.setData(self.model.index(i, LAT), data['Latitude'])
            self.model.setData(self.model.index(i, LON), data['Longitude'])
            self.model.setData(self.model.index(i, DATE), data['Date'])
            self.model.setData(self.model.index(i, DESC), data['Description'])