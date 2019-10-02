from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
        QTime)
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import *
import random
import os
PName = range(1)
class StarterTable(QWidget):
    def __init__(self, parent):
        super(StarterTable, self).__init__(parent)

        self.model = QSortFilterProxyModel()
        self.model.setDynamicSortFilter(True)
        
        #Create and define columns in table
        model = QStandardItemModel(0, 1, self)
        model.setHeaderData(0, Qt.Horizontal, "Project Name")

        subfolders = [f.name for f in os.scandir('./Projects') if f.is_dir() ]
        #subfolders = ['a', 'b', 'c']
        #lengthS = len(subfolders)
        for i in range(len(subfolders)):
            model.insertRow(i)
            model.setData(model.index(i,0), subfolders[i])

        self.model.setSourceModel(model)

        self.proxyGroupBox = QGroupBox("Projects")

        self.proxyView = QTreeView()
        self.proxyView.setRootIsDecorated(False)
        self.proxyView.setAlternatingRowColors(True)
        self.proxyView.setModel(self.model)
        self.proxyView.setSortingEnabled(True)

        proxyLayout = QGridLayout()
        proxyLayout.addWidget(self.proxyView, 0, 0, 1, 3)
        self.proxyGroupBox.setLayout(proxyLayout)

        #create horizontal window for storing buttons
       

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.proxyGroupBox)
        #mainLayout.addLayout(hLayout)
        self.setLayout(mainLayout)
        #Sort able by point ID
        self.proxyView.sortByColumn(0, Qt.AscendingOrder)

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