from PyQt5.QtCore import Qt, QDateTime, QRegExp
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

#Class to display new project wizard
class NewProjectWizard(QWizard):
    def __init__(self, parent=None):
        super(NewProjectWizard, self).__init__(parent)
        
        self.addPage(self.createIntroPage())
        self.dataPage = WizardDataPage(self)
        self.addPage(self.dataPage)
        self.addPage(self.createConclusionPage())

        self.setWindowTitle('New Project Wizard')
        self.button(QWizard.FinishButton).clicked.connect(self.startNewProject)
        self.button(QWizard.CancelButton).clicked.connect(self.cancel)
        self.setModal(True)
        self.show()

    def createIntroPage(self):
        '''
        Create first page of wizard
        '''
        page = QWizardPage()
        page.setTitle("Welcome")

        label = QLabel(
                "Follow instructions to create new Map Reader project.")
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)

        return page

    def createConclusionPage(self):
        '''
        Create last page of wizard
        '''
        page = QWizardPage()
        page.setTitle("Conclusion")

        label = QLabel("Your project has been created")
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        page.setLayout(layout)

        return page

    def startNewProject(self):
        '''
        Launch main window of application when wizard completes and all data is validated
        '''
        name = self.dataPage.getProjectName()
        refPoint = self.dataPage.getReferencePoint()

        if self.parent():
            self.parent().createProject(name, refPoint)

    def cancel(self):
        '''
        Return to starter screen when cancel is pressed
        '''
        if self.parent():
            self.parent().starterScreen()
        else:
            self.close()
        


#Class to setup wizard page for project name and reference point entry
class WizardDataPage(QWizardPage):
    def __init__(self, parent):
        super(WizardDataPage, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
        self.setTitle("Project Data")
        self.setSubTitle("Please fill all fields.")

        self.nameLabel = QLabel("Project Name:")
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setValidator(QtGui.QRegExpValidator(QRegExp('[^\\\*<>:"/\|?*]+')))
        self.registerField('projectName*', self.nameLineEdit)

        self.refLabel = QLabel("Reference Point:")
        self.latLineEdit = QLineEdit()
        self.latLineEdit.setPlaceholderText('Latitude')
        self.latLineEdit.setValidator(QtGui.QDoubleValidator(-90.00000, 90.00000, 5))
        self.registerField('latitude*', self.latLineEdit)

        self.lonLineEdit = QLineEdit()
        self.lonLineEdit.setPlaceholderText('Longitude')
        self.lonLineEdit.setValidator(QtGui.QDoubleValidator(-180.00000, 180.00000, 5))
        self.registerField('longitude*', self.lonLineEdit)

        self.layout = QGridLayout()
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.nameLineEdit, 0, 1, 1, 3)
        self.layout.addWidget(self.refLabel, 1, 0)
        self.layout.addWidget(self.latLineEdit, 1, 1)
        self.layout.addWidget(self.lonLineEdit, 1, 2)

        self.setLayout(self.layout)

    def getProjectName(self):
        '''
        Returns project name entered in nameLineEdit field
        '''
        return self.nameLineEdit.text()

    def getReferencePoint(self):
        '''
        Returns reference lat/lon as tuple from latLineEdit and lonLineEdit fields
        '''
        lat = eval(self.latLineEdit.text())
        lon = eval(self.lonLineEdit.text())

        return lat, lon