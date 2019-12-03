from Map_Reader.ProjectController import ProjectController
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWizard
import time
import pytest
import os
import shutil

path = os.path.dirname(os.path.realpath(__file__))

def test_1(qtbot):
    '''
    Test normal operation of new project wizard from starter page
    '''
    pc = ProjectController()
    project_name = 'Test_Project'

    def on_timeout():
        #Intro page
        qtbot.mouseClick(pc.npw.button(QWizard.NextButton), QtCore.Qt.LeftButton)

        #Data page
        qtbot.keyClicks(pc.npw.dataPage.nameLineEdit, project_name)
        qtbot.keyClicks(pc.npw.dataPage.latLineEdit, '38.12345')
        qtbot.keyClicks(pc.npw.dataPage.lonLineEdit, '-121.12345')
        qtbot.mouseClick(pc.npw.button(QWizard.NextButton), QtCore.Qt.LeftButton)

        #Conclusion page
        qtbot.mouseClick(pc.npw.button(QWizard.FinishButton), QtCore.Qt.LeftButton)

    QtCore.QTimer.singleShot(0, on_timeout)
    qtbot.mouseClick(pc.sw.newButton, QtCore.Qt.LeftButton)

    assert os.path.exists(f'../Projects/{project_name}')
    assert os.path.exists(f'../Projects/{project_name}/Reports')
    assert os.path.exists(f'../Projects/{project_name}/project_data.json')

    shutil.rmtree(f'../Projects/{project_name}')