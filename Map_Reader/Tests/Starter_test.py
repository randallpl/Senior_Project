from Map_Reader.Windows import StarterWindow
from Map_Reader.ProjectController import ProjectController
from PyQt5 import QtCore
import pytest
import time

@pytest.fixture
def window():
    window = StarterWindow(ProjectController())
    return window

def test_1(qtbot, window):
    '''
    Test if the about page loads
    '''
    qtbot.mouseClick(window.aboutButton, QtCore.Qt.LeftButton)
    assert window.aboutScreen.isActiveWindow() == True
    window.close()

def test_2(qtbot, window):
    '''
    Test if the about page exits properly
    '''
    qtbot.mouseClick(window.aboutButton, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window.aboutScreen.cancelButton, QtCore.Qt.LeftButton)

    assert window.aboutScreen.isActiveWindow() == False