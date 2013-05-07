# -*- coding: utf-8 -*-
# Copyright (c) 2012, Andrey Vasilev
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Graphical user interface classes of the application """

__author__ = 'Andrey Vasilev <vamonster@gmail.com>'

from PySide.QtGui import QMainWindow, QSystemTrayIcon, QWidget, QPushButton, QLabel, \
    QVBoxLayout, QHBoxLayout, QAction, QMenu
from PySide.QtCore import QCoreApplication, Qt
from core import ActivityManager, Settings
import subprocess
from multiprocessing import Process
import resources


class ActivityStatus(QMainWindow):
    """
    Main application window, responsible for application lifecycle
    """

    def __init__(self):
        QMainWindow.__init__(self, None, Qt.FramelessWindowHint)
        self.__settings = Settings()
        self.__activityManager = ActivityManager(self.__settings)
        self.__trayIcon = QSystemTrayIcon(self)
        self.__managerController = ActivityManagerControl(self, self.__activityManager)
        self.__appMenu = QMenu(self)
        self.__closeAction = QAction(self.tr('Close'), self)
        self._configureActions()
        self._configureMenu()
        self._setupTrayIcon()
        self._configureStatusManager()
        self._setupEventHooks()

    def _setupTrayIcon(self):
        """
        Set initial image on tray icon
        """
        self.__trayIcon.setIcon(resources.getIcon('pomidor.png'))
        self.__trayIcon.show()
        self.__trayIcon.activated.connect(self._trayIconClicked)
        self.__trayIcon.setContextMenu(self.__appMenu)

    def _configureStatusManager(self):
        """Setup contents of the main window"""
        self.setCentralWidget(self.__managerController)

    def _setupEventHooks(self):
        """Connect to event hooks provided by the activity manager"""
        self.__activityManager.activityStarted += self._hideMainWindow
        self.__activityManager.workActivityEnded += self._notifyActivityEnding
        self.__activityManager.breakActivityEnded += self._notifyActivityEnding

    def _configureMenu(self):
        """Configure application menu, add all actions and separators"""
        self.__appMenu.addActions(self.__managerController.actionList)
        self.__appMenu.addSeparator()
        self.__appMenu.addAction(self.__closeAction)

    def _configureActions(self):
        """Configure actions of the main controller"""
        self.__closeAction.triggered.connect(_closeApplication)

    def _trayIconClicked(self, reason):
        """
        Process the click on the tray icon
        @param reason: how the icon was clicked
        """
        if reason == QSystemTrayIcon.Trigger:
            self.setVisible(not self.isVisible())

    def closeEvent(self, event):
        """
        Prevent main window from closing by clicking on close button
        @param event: the event, which controls the operation
        @type event: QCloseEvent
        """
        event.ignore()
        self._hideMainWindow()

    def _hideMainWindow(self, _=''):
        """ Hide main window from the screen """
        self.hide()

    def _notifyActivityEnding(self):
        """Invoke activity ending action"""
        process = Process(target=_executeAction, args=(self.__settings.endActivityAction,))
        process.start()


def _closeApplication():
    """
    Close the application. Save all needed information.
    """
    QCoreApplication.quit()


def _executeAction(action):
    """
    Execute an action specified by a string
    @param action: action to be executed
    @type action: str
    """
    subprocess.call(action.format(base=resources.BASEDIR), shell=True)


class ActivityManagerControl(QWidget):
    """
    Timer status display and control widget
    """

    def __init__(self, parent, activityManager):
        """
        @param parent: parent widget to bound with
        @type parent: QWidget
        @param activityManager: the manager of user activities
        @type activityManager: ActivityManager
        """
        QWidget.__init__(self, parent)
        self.__activityManager = activityManager
        self.__startWorkActivity = QAction(self.tr('Start'), self)
        self.__stopActivity = QAction(self.tr('Stop'), self)
        self.__startShortBreakActivity = QAction(self.tr('Short'), self)
        self.__startLongBreakActivity = QAction(self.tr('Long'), self)
        self.actionList = [self.__startWorkActivity, self.__stopActivity,
                           self.__startLongBreakActivity, self.__startShortBreakActivity]
        self.__timeLeft = QLabel()
        self._layoutWidgets()
        self._enableActions([self.__startWorkActivity])
        self._setupEventHandlers()
        self._showStartWorkScreen()

    def _layoutWidgets(self):
        """
        Setup layout of internal widgets
        """
        mainLayout = QVBoxLayout()
        timerLayout = QHBoxLayout()
        timerLayout.addStretch()
        timerLayout.addWidget(self.__timeLeft)
        timerLayout.addStretch()
        mainLayout.addLayout(timerLayout)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(ActionButton(self.__startWorkActivity, self))
        buttonLayout.addWidget(ActionButton(self.__stopActivity, self))
        buttonLayout.addWidget(ActionButton(self.__startShortBreakActivity, self))
        buttonLayout.addWidget(ActionButton(self.__startLongBreakActivity, self))
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def _setupEventHandlers(self):
        """Setup connection between events and corresponding event handlers"""
        self.__startWorkActivity.triggered.connect(self._startWorkActivity)
        self.__stopActivity.triggered.connect(self._stopRunningActivity)
        self.__startShortBreakActivity.triggered.connect(self._startShortBreakActivity)
        self.__startLongBreakActivity.triggered.connect(self._startLongBreakActivity)
        self.__activityManager.activityStarted += self._showActivityRunningScreen
        self.__activityManager.workActivityEnded += self._showStartRestScreen
        self.__activityManager.activityTimeChanged += self._setActivityRemainingTime
        self.__activityManager.breakActivityEnded += self._showStartWorkScreen

    def _startWorkActivity(self):
        """ Start work activity for the user """
        self.__activityManager.startWorkActivity()

    def _stopRunningActivity(self):
        """ Stop the currently running activity """
        self.__activityManager.stopCurrentActivity()

    def _startShortBreakActivity(self):
        """ Start short break activity """
        self.__activityManager.startShortBreakActivity()

    def _startLongBreakActivity(self):
        """ Start long break activity """
        self.__activityManager.startLongBreakActivity()

    def _showActivityRunningScreen(self, _):
        """Show activity running screen"""
        self._enableActions([self.__stopActivity])

    def _showStartWorkScreen(self):
        """Show screen, allowing to start work"""
        self._enableActions([self.__startWorkActivity])
        self.__timeLeft.setText('Start an activity')

    def _showStartRestScreen(self):
        """Show screen calling to make a rest"""
        self._enableActions([self.__startLongBreakActivity, self.__startShortBreakActivity])
        self.__timeLeft.setText('Take a break')

    def _setActivityRemainingTime(self, secondsLeft):
        """
        Show activity remaining time on the label
        @param secondsLeft: how much time is left for the activity
        @type secondsLeft: int
        """
        minutes = int(secondsLeft / 60)
        seconds = secondsLeft % 60
        self.__timeLeft.setText("{0:02d}:{1:02d}".format(minutes, seconds))

    def _enableActions(self, actions):
        """
        Enable only those actions that should be active now and disable all other events
        @param actions: actions to be activated
        @type actions: list
        """
        for action in self.actionList:
            action.setEnabled(False)
        for action in actions:
            action.setEnabled(True)


class ActionButton(QPushButton):
    """Button associated with the action"""

    def __init__(self, action, parent):
        """
        @param action: action to bound button with
        @type action: QAction
        @param parent: parent widget to bound button to
        @type parent: QWidget
        """
        QPushButton.__init__(self, parent)
        self.__action = action
        self.__action.changed.connect(self._synchronizeButtonState)
        self.clicked.connect(self.__action.trigger)
        self._synchronizeButtonState()

    def _synchronizeButtonState(self):
        """
        Synchronize button state with the action state
        """
        self.setText(self.__action.text())
        self.setStatusTip(self.__action.statusTip())
        self.setIcon(self.__action.icon())
        self.setToolTip(self.__action.toolTip())
        self.setVisible(self.__action.isEnabled())
        if self.__action.isEnabled():
            self.setFocus()
