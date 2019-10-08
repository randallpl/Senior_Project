import os

from PyQt5.QtCore import Qt, QDateTime, QStringListModel
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from StarterTable import StarterTable
import json

from MainWindow import MainWindow
from NewProjectWizard import NewProjectWizard
from CustomQtObjects import Button

'''
About Window Class Containing Info About Project
'''
class AboutWindow(QDialog):
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.setFixedSize(240,180)
        self.setWindowTitle('About This Project')
        self.initUI()
    
    def initUI(self):
        self.aboutlayout = QVBoxLayout()
        self.textbox = QLabel()
        self.textbox.setAlignment(Qt.AlignLeft)
        self.textbox.setWordWrap(True)
        self.textbox.setText('This project is was made by Evan Brittain, Gabriel Aguirre, Ryan Swearingen, Randall Plant, and Blake Carlisle.  More to follow...')
        self.aboutlayout.addWidget(self.textbox)
        self.setLayout(self.aboutlayout)
        self.show()

'''
Main Window
'''
class StarterWindow(QDialog):
    def __init__(self):
        super(StarterWindow, self).__init__()
        
        qApp.setWindowIcon(QtGui.QIcon('./Resources/icons/app_icon.png'))

        self.setFixedSize(300, 400)
        self.setWindowTitle('Welcome')
        self.mw = None
        self.newProjectWizard = None
        self.aboutWindow = None
        self.settings = None

        #Create main projects directory
        if not os.path.exists('./Projects'):
            os.mkdir('./Projects')

        self.loadSettings()
        
        self.initUI()

    def initUI(self):
        '''
        Setup GUI elements of scale window
        '''
        mainLayout = QVBoxLayout()

        #horizontal layout containing new and open buttons
        hLayout = QHBoxLayout()
        self.projectTable = StarterTable(self)
        

        self.newButton = Button('New')
        self.newButton.clicked.connect(self.newProject)

        self.openButton = Button('Open')
        self.openButton.clicked.connect(self.openProject)

        self.aboutButton = Button('About')
        self.aboutButton.clicked.connect(self.aboutProject)
        
        mainLayout.addWidget(self.projectTable)
        hLayout.addWidget(self.newButton)
        hLayout.addWidget(self.openButton)
        hLayout.addWidget(self.aboutButton)

        mainLayout.addLayout(hLayout)
    
        self.setLayout(mainLayout)

        self.show()

    def loadSettings(self):
        '''
        Load default user settings
        '''
        path = './Settings/settings.json'

        try:
            with open('./Settings/settings.json', 'rt') as f:
                self.settings = json.loads(f.read())
        #No settings file found, create defaults and save to settings.json
        except FileNotFoundError:
            os.mkdir('./Settings')
            self.settings = {
                'Theme': None
            }
            self.saveSettings()

        self.loadTheme(theme=self.settings.get('Theme'))

    def saveSettings(self):
        '''
        Save updated settings data 
        '''
        with open('./Settings/settings.json', 'w+') as f:
            f.write(json.dumps(self.settings))

    def loadTheme(self, theme=None, save=False):
        '''
        Load given theme and save to settings file if flag is set
        '''
        if save:
            self.settings['Theme'] = theme
            self.saveSettings()
        if theme:
            with open(f'./Resources/stylesheet_{theme}.css', 'rt') as f:
                qApp.setStyleSheet(f.read())
        else:
            qApp.setStyleSheet(None)

    def newProject(self):
        '''
        Send reference point back to main window to be stored
        '''
        self.newProjectWizard = NewProjectWizard(self)
        

    def createProject(self, projectName, refPoint):
        '''
        Creates a new project and launch main window
        '''
        self.hide()
        self.newProjectWizard.close()

        if self.mw:
            self.mw.close()

        createdDate = QDateTime().currentDateTime().toString('MM-dd-yyyy hh:mm:ss ap')

        #Creates project name directory and Reports subdirectory
        try:
            os.makedirs(f'./Projects/{projectName}/Reports')

        except FileExistsError:
            msg = f'{projectName} already exists'
            QMessageBox.critical(
                    self,
                    'Error Creating Project',
                    msg)

            self.show()
        
        #Create project_data.json file with new data and start main window
        else:
            defaultData = {
                'ProjectName': projectName,
                'Created': createdDate,
                'LastAccessed': createdDate,
                'Reference': refPoint,
                'Scale': 0,
                'Units': '',
                'Points': []
            }

            with open(f'./Projects/{projectName}/project_data.json', 'w+') as f:
                f.write(json.dumps(defaultData, indent=2))

            self.mw = MainWindow(
                projectName, 
                reference=refPoint, 
                createdDate=createdDate, 
                parent=self)
        
    def openProject(self):
        '''
        Open an existing project and launch main window
        '''
        fileDialog = QFileDialog(self, 'Projects', './Projects')
        fileDialog.setFileMode(QFileDialog.DirectoryOnly)
        fileDialog.setAttribute(Qt.WA_QuitOnClose, False)       
        
        #If a valid path is returned from file dialog screen
        if fileDialog.exec_():
            filename = fileDialog.selectedFiles()[0]
            #Check if json data file is in selected folder
            if os.path.exists(f'{filename}/project_data.json'):
                self.hide()
                projectName = filename.split('/')[-1]
                if self.mw:
                    if self.mw.projectName == projectName:
                        return
                    else:
                        self.mw.close()

                self.mw = MainWindow(projectName, self, openExisting=True)

            #alert for invalid project and return to main window or starter screen
            else:
                QMessageBox.critical(
                    self,
                    'Invalid Project',
                    f'{filename} is an invalid project')
        

    def starterScreen(self, closeMW=False):
        '''
        Display starter page if hidden
        '''
        if closeMW:
            self.mw.close()
            self.mw = None

        if self.newProjectWizard:
            self.newProjectWizard.close()

        self.show()

    def aboutProject(self):
        '''
        Show About Screen
        '''
        self.aboutScreen = AboutWindow()

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = StarterWindow()
    sys.exit(app.exec_())