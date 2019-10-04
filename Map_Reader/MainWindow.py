import sys
import os

from PyQt5.QtWidgets import QAction, QMainWindow, QMessageBox, QMenu
from PyQt5.QtCore import QDateTime, QDate, Qt
import pandas as pd
import json
from functools import partial
import requests

import Tracker
from Table import Table
from Windows import *

class MainWindow(QMainWindow):
    def __init__(self, projectName, parent, reference=None, createdDate=None, openExisting=False):
        super(MainWindow, self).__init__(parent)
        self.setFixedSize(1080, 768)
        self.projectName = projectName
        self.table = Table(self)
        self.scale = None
        self.reference = reference
        self.units = None
        self.points = []
        self.savedPoints = []
        self.createdDate = createdDate
        self.api = None
        
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('File')

        self.menuNew = QAction("&New", self)
        self.menuNew.setShortcut("Ctrl+N")
        self.menuNew.setStatusTip('New Project')
        self.menuNew.triggered.connect(self.parent().newProject)

        self.menuSave = QAction("&Save", self)
        self.menuSave.setShortcut("Ctrl+S")
        self.menuSave.setStatusTip('Save File')
        self.menuSave.triggered.connect(self.saveFile)

        self.menuOpen = QAction("&Open", self)
        self.menuOpen.setShortcut("Ctrl+O")
        self.menuOpen.setStatusTip('Open File')
        self.menuOpen.triggered.connect(self.parent().openProject)

        self.menuClose = QAction("&Close", self)
        self.menuClose.setShortcut("Ctrl+E")
        self.menuClose.setStatusTip('Close File')
        self.menuClose.triggered.connect(partial(self.parent().starterScreen, closeMW=True))

        self.menuExit = QAction("&Exit", self)
        self.menuExit.setShortcut("Ctrl+Q")
        self.menuExit.setStatusTip('Leave The App')
        self.menuExit.triggered.connect(self.closeApplication)
        
        self.menuExport = QMenu('Export', self)
        self.menuExport.setEnabled(False)
        
        self.exportCSV = QAction('CSV', self)
        self.menuExport.addAction(self.exportCSV)
        self.exportCSV.triggered.connect(self.exportToCSV)

        self.exportJSON = QAction('JSON', self)
        self.menuExport.addAction(self.exportJSON)
        self.exportJSON.triggered.connect(self.exportToJSON)

        self.exportExcel = QAction('Excel', self)
        self.menuExport.addAction(self.exportExcel)
        self.exportExcel.triggered.connect(self.exportToExcel)

        self.exportHTML = QAction('HTML', self)
        self.menuExport.addAction(self.exportHTML)
        self.exportHTML.triggered.connect(self.exportToHTML)

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

        self.fileMenu.addAction(self.menuNew)
        self.fileMenu.addAction(self.menuOpen)
        self.fileMenu.addAction(self.menuSave)
        self.fileMenu.addMenu(self.menuExport)
        self.fileMenu.addAction(self.menuClose)
        self.fileMenu.addAction(self.menuExit)

        self.settingsMenu.addAction(self.menuMouseSettings)
        self.settingsMenu.addAction(self.menuProjectSettings)
        self.settingsMenu.addAction(self.menuAPISettings)

        self.setCentralWidget(self.table)

        #Open existing json file containing all data
        if openExisting:
            self.openExistingProject(self.projectName)

        self.setWindowTitle(f'Map Reader - {self.projectName}')
        self.show()
    
    def setProjectName(self, name):
        try:
            os.rename(f'./Projects/{self.projectName}', f'./Projects/{name}')
        except:
            QMessageBox.critical(
                self,
                'Project Error',
                f'Invalid project name: {name}'
            )
            return

        self.projectName = name
        self.setWindowTitle(f'Map Reader - {self.projectName}')
        self.saveFile()

    def referenceWindow(self):
        '''
        Displays window to enter lat/lon of reference point
        '''
        self.refWindow = ReferenceWindow(self)

    def setReference(self, point):
        '''
        Sets the local reference variable with point data passed from reference window
        '''
        self.reference = point
        self.saveFile()

    def scaleTracker(self):
        '''
        Launches window to trace scale
        '''
        self.scaleTracker = Tracker.Tracker('scale', self)

    def confirmScale(self, dist_px):
        '''
        Launches window to confirm scale data
        '''
        self.scaleConfirm = ScaleWindow(dist_px, self)

    def setScale(self, scale, units):
        '''
        Sets Scale and unit input passed from scale window
        '''
        self.scale = scale
        self.units = units
        self.saveFile()
        self.scaleTracker.close()

    def locationTracker(self):
        '''
        Launches window to locate new point from reference point
        '''
        if self.reference and self.scale and self.units:
            self.locationTracker = Tracker.Tracker( 
                'location', 
                self,
                ref=self.reference, 
                scale=self.scale, 
                units=self.units)

    def confirmLocation(self, lat, lon, dist, bearing, units):
        '''
        Launches window to confirm new point data
        '''
        self.locationConfirm = LocationWindow(lat, lon, dist, bearing, units, self)

    def setLocation(self, lat, lon, desc, dist, bearing, units):
        '''
        Adds location to points list and passes list to Table class to update table data
        '''
        self.locationTracker.close()
        data = {
            'Latitude': lat,
            'Longitude': lon,
            'Date': QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap'),
            'Description': desc,
            'Distance': dist,
            'Bearing': bearing,
            'Units': units,
            'ReferencePoint': self.reference,
            'Scale': self.scale
        }
        self.points.append(data)
        self.table.update(self.points)
        self.menuExport.setEnabled(True)
        self.saveFile()

    def setAPI(self, api_key, plot):
        '''
        Set api key with key provided from APIKeyWindow
        '''
        self.api = api_key
        self.saveFile()

        if plot:
            self.mapWindow = MapWindow(self.api, self.reference, self.points)

    def launchAPISettings(self):
        '''
        Launch API key window to update API key from settings menu
        '''
        self.apiKeyWindow = APIKeyWindow(parent=self)

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
            self.apiKeyWindow = APIKeyWindow(plot=True, parent=self)

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
        Saves the project data in json format and writes to a file
        '''
        savestate = {
            'ProjectName': self.projectName,
            'Created': self.createdDate,
            'LastAccessed': QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap'),
            'Reference': self.reference,
            'Scale': self.scale,
            'Units': self.units,
            'Points': self.points,
            'APIKey': self.api
        }

        with open(f'./Projects/{self.projectName}/project_data.json', 'w+') as f:
            f.write(json.dumps(savestate, indent=2))

    def openExistingProject(self, projectName):
        '''
        Populates table with existing project data from given project
        '''
        try:
            with open(f'./Projects/{projectName}/project_data.json', 'r') as f:
                data = json.loads(f.read())
        except:
            QMessageBox.critical(
                self,
                'File Not Found',
                f'{projectName} is not supported')
        else:
            self.projectName = data.get('ProjectName')
            self.createdDate = data.get('Created')
            self.reference = data.get('Reference')
            self.scale = data.get('Scale')
            self.units = data.get('Units')
            self.points = data.get('Points')
            self.api = data.get('APIKey')

        if self.points:
            self.menuExport.setEnabled(True)
            self.table.update(self.points)

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

    def exportToCSV(self):
        '''
        Export table data to csv file
        '''
        df = pd.DataFrame(self.points)
        
        try:
            df.to_csv(f'./Projects/{self.projectName}/Reports/{QDate.currentDate().toString("MM-dd-yy")}_Report.csv', index=False)   
        except:
            self.fileCreatedAlert('CSV', True)	
        else:
            self.fileCreatedAlert('CSV')

    def exportToJSON(self):
        '''
        Export table data to json file
        '''
        json_data = json.dumps(self.points, indent=2)
        
        try:
            with open(f'./Projects/{self.projectName}/Reports/{QDate.currentDate().toString("MM-dd-yy")}_Report.json', 'w+') as f:
                f.write(json_data)
        except:
            self.fileCreatedAlert('JSON', True)	
        else:
            self.fileCreatedAlert('JSON')

    def exportToExcel(self):
        '''
        Export table data to excel file
        '''
        df = pd.DataFrame(self.points)
        
        try:
            df.to_excel(f'./Projects/{self.projectName}/Reports/{QDate.currentDate().toString("MM-dd-yy")}_Report.xlsx', index=False)
        except:
            self.fileCreatedAlert('Excel', True)
        else:
            self.fileCreatedAlert('Excel')

    def exportToHTML(self):
        '''
        Export table data to html file
        '''
        df = pd.DataFrame(self.points)
        
        try:
            df.to_html(f'./Projects/{self.projectName}/Reports/{QDate.currentDate().toString("MM-dd-yy")}_Report.html', index=False)	
        except:
            self.fileCreatedAlert('HTML', True)
        else:
            self.fileCreatedAlert('HTML')
		
    def fileCreatedAlert(self, filetype, error=False):
        '''
        Display alert box to inform user export file was created
        '''
        if error:
            QMessageBox.critical(
                self,
                'Export File',
                f'{filetype} file failed to be created'
            )	
        else:
            QMessageBox.information(
                self,
                'Export File',
                f'{filetype} file was successfully created'
            )

    def deleteRowFromTable(self):
        '''
        Delete row from table and self.points list
        '''
        row = self.table.getRowIndex()
        
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