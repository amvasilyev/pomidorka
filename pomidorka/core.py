# -*- coding: utf-8 -*-
# Copyright (c) 2012-13, Andrey Vasilev
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

"""Application core classes"""

__author__ = 'Andrey Vasilev <vamonster@gmail.com>'

from PySide.QtCore import QTimer


class EventHook():
    """
    Special class for implementing effective publish/subscribe mechanism in an application.
    How to use class:

    class MyBroadcaster()
    def __init__():
        self.onChange = EventHook()

    theBroadcaster = MyBroadcaster()

    # add a listener to the event
    theBroadcaster.onChange += myFunction

    # remove listener from the event
    theBroadcaster.onChange -= myFunction

    # fire event
    theBroadcaster.onChange.fire()

    @authors: Michael Foord
    """

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        """
        Add handler to event hook
        """
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        """
        Remove handler from event hook
        @type handler: method
        """
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        """
        Send notification to subscribers, passing all arguments
        """
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        """
        Remove all event handlers coming from specified object
        @param inObject: object to clear handlers
        @type inObject: object
        """
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

    def clearHandlers(self):
        """
        Remove all event handlers from the hook
        """
        self.__handlers = []


class ActivityManager:
    """
    Time management class. Responsible for tracking the status of user activities.
    @authors: Andrey Vasilev
    """

    def __init__(self, settings):
        """
        @param settings: the timer settings
        @type settings: Settings
        """
        self.activityStarted = EventHook()
        self.workActivityEnded = EventHook()
        self.breakActivityEnded = EventHook()
        self.activityTimeChanged = EventHook()
        self.settings = settings
        self.__currentActivity = None

    def _startActivity(self, timePeriod, finishedHook):
        """
        Create new activity object start it and store a link to it
        @param timePeriod: time period in minutes that activity must last
        @type timePeriod: int
        @param finishedHook: hook to be executed on activity end
        @type finishedHook: function
        @return: new work activity
        @rtype: Activity
        """
        self.__currentActivity = Activity(timePeriod)
        self.__currentActivity.finished += finishedHook
        self.__currentActivity.timeChanged += self.activityTimeChanged.fire
        self.__currentActivity.start()
        self.activityStarted.fire(self.__currentActivity)
        return self.__currentActivity

    def _clearCurrentActivity(self):
        """Remove all associations with the current activity"""
        self.__currentActivity.removeHookHandlers()
        self.__currentActivity = None

    def startWorkActivity(self):
        """
        Start working period
        @return: new work activity object
        @rtype: Activity
        """
        return self._startActivity(self.settings.workPeriod, self._workActivityEnded)

    def _workActivityEnded(self):
        """
        Process the end of work activity
        """
        self.workActivityEnded.fire()
        self._clearCurrentActivity()

    def startShortBreakActivity(self):
        """
        Start short break session
        @return: new short break activity
        @rtype: Activity
        """
        return self._startActivity(self.settings.shortRestPeriod, self._restActivityEnded)

    def startLongBreakActivity(self):
        """
        Start long break session
        @return new long break activity
        @rtype: Activity
        """
        return self._startActivity(self.settings.longRestPeriod, self._restActivityEnded)

    def _restActivityEnded(self):
        """
        Process the end of rest activity
        """
        self.breakActivityEnded.fire()
        self._clearCurrentActivity()

    def stopCurrentActivity(self):
        """Try to stop activity if it is running"""
        if self.__currentActivity:
            self.__currentActivity.stop()


class OneSecondTimer:
    """
    Abstract class for a timer, which notifies it listeners about each second passing by.
    Objects, implementing this interface must implement start and stop methods. And notify
    listeners with elapsed message on every second passed.
    """

    def __init__(self):
        self.elapsed = EventHook()

    def start(self):
        """Start timer"""
        pass

    def stop(self):
        """Stop timer"""


class QtOneSecondTimer(OneSecondTimer):
    """
    Concrete implementation of the timer based on Qt classes
    """

    def __init__(self):
        OneSecondTimer.__init__(self)
        self.__timer = QTimer()
        self.__timer.setInterval(1000)
        self.__timer.setSingleShot(False)
        self.__timer.timeout.connect(self._timerElapsed)

    def start(self):
        """Start the timer"""
        self.__timer.start()

    def _timerElapsed(self):
        """Process notification from the timer"""
        self.elapsed.fire()

    def stop(self):
        """Stop the timer"""
        self.__timer.stop()


class Activity:
    """Arbitrary user activity"""

    def __init__(self, timeInterval, timer=QtOneSecondTimer()):
        """
        @param timeInterval: proposed time interval for the activity
        @type timeInterval: int
        """
        self.finished = EventHook()
        self.timeChanged = EventHook()
        self.maxTimeInterval = timeInterval
        self.__timer = timer
        self.__timer.elapsed += self._decreasePeriod
        self.remainingTime = self.maxTimeInterval

    def start(self):
        """Start working on the current activity"""
        self._setRemainingTime(self.maxTimeInterval)
        self.__timer.start()

    def stop(self):
        """Terminate current activity before time period ended"""
        self._setRemainingTime(0)

    def _decreasePeriod(self):
        """Add one second to the """
        self._setRemainingTime(self.remainingTime - 1)

    def _setRemainingTime(self, newTime):
        """
        Set remaining time and notify subscribers. If time is elapsed (e.g. equal to zero,
        then notify about finishing the activity.
        @param newTime: new value of remaining time
        @type newTime: int
        """
        self.remainingTime = newTime
        self.timeChanged.fire(self.remainingTime)
        if self.remainingTime == 0:
            self.__timer.stop()
            self.finished.fire()

    def removeHookHandlers(self):
        """Remove all handlers form all available event hooks"""
        self.finished.clearHandlers()
        self.timeChanged.clearHandlers()


class Settings:
    """Setting of the application"""

    def __init__(self):
        self.workPeriod = 1500
        self.shortRestPeriod = 300
        self.longRestPeriod = 1500
        self.endActivityAction = 'mplayer {base}/assets/alarm.mp3'


