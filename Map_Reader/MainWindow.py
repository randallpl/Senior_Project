import sys
import os

from PyQt5.QtWidgets import QAction, QMainWindow, QMessageBox, QMenu
from PyQt5.QtCore import QDateTime, QDate, Qt
import pandas as pd
import json
from functools import partial
import requests

import Tracker
from Windows import *
from CustomQtObjects import Table

class MainWindow(QMainWindow):
    def __init__(self, projectName, controller, reference=None, createdDate=None, openExisting=False, api=None):
        super(MainWindow, self).__init__()
        self.setFixedSize(1080, 768)
        self.controller = controller
        self.projectName = projectName
        self.api = api
        self.scale = None
        self.reference = reference
        self.units = None
        self.points = []
        self.savedPoints = []
        self.createdDate = createdDate

        #Open existing json file containing all data
        if openExisting:
            self.openExistingProject(self.projectName)

        #----------------------Menu Bar-----------------------#
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('File')

        self.menuNew = QAction("&New", self)
        self.menuNew.setShortcut("Ctrl+N")
        self.menuNew.setStatusTip('New Project')
        self.menuNew.triggered.connect(partial(self.controller.newProject, self))

        self.menuSave = QAction("&Save", self)
        self.menuSave.setShortcut("Ctrl+S")
        self.menuSave.setStatusTip('Save File')
        self.menuSave.triggered.connect(self.saveFile)

        self.menuOpen = QAction("&Open", self)
        self.menuOpen.setShortcut("Ctrl+O")
        self.menuOpen.setStatusTip('Open File')
        self.menuOpen.triggered.connect(partial(self.controller.browseProjectsDir, self))

        self.menuClose = QAction("&Close", self)
        self.menuClose.setShortcut("Ctrl+E")
        self.menuClose.setStatusTip('Close File')
        self.menuClose.triggered.connect(self.controller.closeProject)

        self.menuExit = QAction("&Exit", self)
        self.menuExit.setShortcut("Ctrl+Q")
        self.menuExit.setStatusTip('Leave The App')
        self.menuExit.triggered.connect(self.closeApplication)
        
        self.menuExport = QMenu('Export', self)
        self.menuExport.setEnabled(self.points != None)
        
        self.exportCSV = QAction('CSV', self)
        self.menuExport.addAction(self.exportCSV)
        self.exportCSV.triggered.connect(partial(self.export, 'csv'))

        self.exportJSON = QAction('JSON', self)
        self.menuExport.addAction(self.exportJSON)
        self.exportJSON.triggered.connect(partial(self.export, 'json'))

        self.exportExcel = QAction('Excel', self)
        self.menuExport.addAction(self.exportExcel)
        self.exportExcel.triggered.connect(partial(self.export, 'xlsx'))

        self.exportHTML = QAction('HTML', self)
        self.menuExport.addAction(self.exportHTML)
        self.exportHTML.triggered.connect(partial(self.export, 'html'))

        self.fileMenu.addAction(self.menuNew)
        self.fileMenu.addAction(self.menuOpen)
        self.fileMenu.addAction(self.menuSave)
        self.fileMenu.addMenu(self.menuExport)
        self.fileMenu.addAction(self.menuClose)
        self.fileMenu.addAction(self.menuExit)

        self.settingsMenu = menubar.addMenu('Settings')

        self.menuMouseSettings = QAction("Mouse Settings", self)
        self.menuMouseSettings.setShortcut("Ctrl+M")
        self.menuMouseSettings.setStatusTip('Mouse Settings')
        self.menuMouseSettings.triggered.connect(self.launchMouseSettings)

        self.menuProjectSettings = QAction("Edit Project Data", self)
        self.menuProjectSettings.setShortcut("Ctrl+P")
        self.menuProjectSettings.setStatusTip('Project Data')
        self.menuProjectSettings.triggered.connect(self.launchProjectSettings)

        self.menuAPISettings = QAction("Add API Key", self)
        self.menuAPISettings.setShortcut("Ctrl+I")
        self.menuAPISettings.setStatusTip('API Key')
        self.menuAPISettings.triggered.connect(self.launchAPISettings)

        self.viewMenu = menubar.addMenu('View')
        self.menuTheme = QMenu('Theme', self)

        self.themeBlack = QAction('Black', self)
        self.menuTheme.addAction(self.themeBlack)
        self.themeBlack.triggered.connect(partial(self.controller.loadTheme, 'Black'))

        self.themeBlue = QAction('Blue', self)
        self.menuTheme.addAction(self.themeBlue)
        self.themeBlue.triggered.connect(partial(self.controller.loadTheme, 'Blue'))

        self.themeGreen = QAction('Green', self)
        self.menuTheme.addAction(self.themeGreen)
        self.themeGreen.triggered.connect(partial(self.controller.loadTheme, 'Green'))

        self.themeTest = QAction('Test', self)
        self.menuTheme.addAction(self.themeTest)
        self.themeTest.triggered.connect(partial(self.controller.loadTheme, 'Test'))

        self.themeDefault = QAction('Default', self)
        self.menuTheme.addAction(self.themeDefault)
        self.themeDefault.triggered.connect(partial(self.controller.loadTheme))

        self.settingsMenu.addAction(self.menuMouseSettings)
        self.settingsMenu.addAction(self.menuProjectSettings)
        self.settingsMenu.addAction(self.menuAPISettings)

        self.viewMenu.addMenu(self.menuTheme)

        #----------------------Central Widget-----------------------#
        self.cWidget = QWidget()

        mainLayout = QVBoxLayout()

        self.table = Table(
            'Points', 
            self.points, 
            columns=['Latitude', 'Longitude', 'Date', 'Description'],
            index=True)

        #create horizontal window for storing buttons
        hLayout = QHBoxLayout()

        #Add refrence button and connect it to referenceWindow()
        self.addRefButton = Button('Add Reference')
        self.addRefButton.clicked.connect(self.referenceWindow)
        
        #Add scale button and connect it to scaleTracker()
        self.setScaleButton = Button('Set Scale')
        self.setScaleButton.clicked.connect(self.scaleTracker)

        #Add trace button and connect it locationTracker()
        self.traceButton = Button('Trace Point')
        self.traceButton.clicked.connect(self.locationTracker)

        #Add manual input button and connect it locationTracker()
        self.manPointButton = Button('Enter Point')
        self.manPointButton.clicked.connect(self.manualAddWindow)

        #Add Plot button and connect it to plotPoints()
        self.plotButton = Button('Plot')
        self.plotButton.clicked.connect(self.plotPoints)

        #Add all button to horizontal layout
        hLayout.addWidget(self.addRefButton)
        hLayout.addWidget(self.setScaleButton)
        hLayout.addWidget(self.traceButton)
        hLayout.addWidget(self.manPointButton)
        hLayout.addWidget(self.plotButton)

        mainLayout.addWidget(self.table)
        mainLayout.addLayout(hLayout)

        self.cWidget.setLayout(mainLayout)

        self.setCentralWidget(self.cWidget)

        self.setWindowTitle(f'Map Reader - {self.projectName}')
        self.show()
    
    def setProjectName(self, name):
        
        if self.controller.setProjectName(self.projectName, name):
            self.projectName = name
            self.setWindowTitle(f'Map Reader - {self.projectName}')
            self.saveFile()
        else:
            QMessageBox.critical(
                self,
                'Project Error',
                f'Invalid project name: {name}'
            )

    def referenceWindow(self):
        '''
        Displays window to enter lat/lon of reference point
        '''
        self.refWindow = ReferenceWindow(self)
        if self.refWindow.exec_():
            point = self.refWindow.getConfirmedData()
            self.reference.append(point)
            self.saveFile()

    def manualAddWindow(self):
        '''
        Displays window to manually enter data point
        '''
        self.manualAddWindow = AddPointWindow(self)
        if self.manualAddWindow.exec_():
            point = self.manualAddWindow.getConfirmedData()
            self.points.append(point)
            self.saveFile()
            self.table.update(self.points)

    def scaleTracker(self):
        '''
        Launches window to trace scale
        '''
        self.scaleTracker = Tracker.Tracker(self)

    def confirmScale(self, dist_px):
        '''
        Launches window to confirm scale data
        '''
        self.scaleConfirm = ScaleWindow(dist_px, self)
        if self.scaleConfirm.exec_():
            self.scale, self.units = self.scaleConfirm.getConfirmedData()
            self.saveFile()
            self.scaleTracker.close()
        else:
            self.scaleTracker.resetTrace()

    def locationTracker(self):
        '''
        Launches window to locate new point from reference point
        '''
        if self.reference and self.scale and self.units:
            self.referenceTable = ReferenceSelectionWindow(self.reference)
            if self.referenceTable.exec_():
                self.locationTracker = Tracker.TrackerLoc( 
                    self,
                    ref=self.referenceTable.selectedData, 
                    scale=self.scale, 
                    units=self.units
                )

    def confirmLocation(self, lat, lon):
        '''
        Launches window to confirm new point data
        '''
        self.locationConfirm = LocationWindow(lat, lon)

        if self.locationConfirm.exec_():
            self.locationTracker.close()
            data = self.locationConfirm.getConfirmedData()
            self.points.append(data)
            self.table.update(self.points)
            self.menuExport.setEnabled(True)
            self.saveFile()
        else:
            self.locationTracker.resetTrace()

    def launchAPISettings(self):
        '''
        Launch API key window to update API key from settings menu
        '''
        self.apiKeyWindow = APIKeyWindow(self)

        if self.apiKeyWindow.exec_():
            api_key = self.apiKeyWindow.getConfirmedData()

            #api_key was successfully saved in settings file
            if self.controller.setAPI(api_key):
                self.api = api_key
                return True
        
        return False

    def plotPoints(self):
        '''
        Launch instance of MapWindow to plot point on google maps
        '''
        #Test if network is connected before prompting for api key or launching mapwindow
        try:
            requests.get('https://developers.google.com/maps/documentation/javascript/get-api-key', timeout=1)
        except:
            QMessageBox.critical(
                self,
                'Network Error',
                f'No Internet Connection'
            )
            return

        if self.api:
            self.mapWindow = MapWindow(self.api, self.reference, self.points)
        #No API key set, must launch window
        else:
            if self.launchAPISettings():
                self.mapWindow = MapWindow(self.api, self.reference, self.points)

    def launchMouseSettings(self):
        '''
        Launches instance of MouseSettingsWindow from setting menu
        '''
        self.mouseSettingsWindow = MouseSettingsWindow()

    def launchProjectSettings(self):
        '''
        Launches instance of ProjectSettingsWindow from setting menu
        '''
        self.projectSettingsWindow = ProjectSettingsWindow(self)

    def saveFile(self):
        '''
        Stores all project data and passes to project controller to be saved
        '''
        savestate = {
            'ProjectName': self.projectName,
            'Created': self.createdDate,
            'LastAccessed': QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap'),
            'Reference': self.reference,
            'Scale': self.scale,
            'Units': self.units,
            'Points': self.points,
        }
        if self.controller.saveProject(self.projectName, savestate):
            pass
        else:
            QMessageBox.critical(
                self,
                'Save Error',
                f'Project failed to be saved'
            )


    def openExistingProject(self, projectName):
        '''
        Populates table with existing project data from given project
        '''
        data = self.controller.getProjectData(projectName)

        if data:
            self.projectName = data.get('ProjectName')
            self.createdDate = data.get('Created')
            self.reference = data.get('Reference')
            self.scale = data.get('Scale')
            self.units = data.get('Units')
            self.points = data.get('Points')
        else:
            QMessageBox.critical(
                self,
                'File Not Found',
                f'{projectName} is not supported')

    def closeApplication(self):
        '''
        Prompt user when exiting
        '''
        choice = QMessageBox.question(
            self, 
            'Exit Application',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No
        )

        if choice == QMessageBox.Yes:
            sys.exit()

    def export(self, file_type):
        '''
        Export table data to csv file
        '''
        if self.controller.exportProjectData(self.projectName, self.points, file_type):
            QMessageBox.information(
                self,
                'Export File',
                f'{file_type} file was successfully created'
            )
        else:
            QMessageBox.critical(
                self,
                'Export File',
                f'{file_type} file failed to be created'
            )	

    def deleteRowFromTable(self):
        '''
        Delete row from table and self.points list
        '''
        row = self.table.getSelectedRowIndex()
        
        if row is False:
            return
        else:
            choice = QMessageBox.question(
                self, 
                'Confirm Deletion',
                'Are you sure you want to delete?',
                QMessageBox.Yes | QMessageBox.No
            )

            if choice == QMessageBox.Yes:
                del self.points[row]
                self.table.update(self.points)
                self.saveFile()
            
    def keyPressEvent(self, event):
        '''
        Handle key events
        Key_Delete: Delete row from table if highlighted
        '''
        key = event.key()

        if key == Qt.Key_Delete:
            self.deleteRowFromTable()