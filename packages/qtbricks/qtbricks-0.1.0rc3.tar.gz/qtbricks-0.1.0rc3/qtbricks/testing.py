"""
Testing-related helper functionality of the qtbricks package.

GUIs should be tested, as every code. However, testing GUIs and widgets is
somewhat more complicated and often involves "faking" interaction with the
different widgets.

In case of Qt, even setting up a test in a way that allows for testing any
GUI-related stuff needs a bit of additional knowledge.

This module contains a growing series of helper classes and functions
designed to make your test code simpler and easier to read.
"""

import unittest

from PySide6 import QtCore, QtTest, QtWidgets


def qtest_enter_text(widget=None, text=""):
    """
    Convenience function to enter text in a QLineEdit widget.

    When testing GUI widgets, you sometimes need to enter text into a line
    edit widget. However, entering/replacing text in such a widget is a
    three-step process:

    #. Clear the current text.
    #. Enter the text.
    #. Press the return key to fire the correct signals.

    For convenience, this function takes care of all three steps.

    Parameters
    ----------
    widget : :class:`PySide6.QtWidgets.QLineEdit`
        Widget to enter text into.

    text : :class:`str`
        Text to enter into the widget.

    """
    widget.clear()
    QtTest.QTest.keyClicks(widget, text)
    QtTest.QTest.keyPress(widget, QtCore.Qt.Key.Key_Return)


class SignalReceiver:
    """
    Context manager class detecting whether a QSignal has been emitted.

    Adapted from https://stackoverflow.com/a/48128768
    """

    def __init__(self, test, signal, *args):
        self.test = test
        self.signal = signal
        self.called = False
        self.expected_args = args
        self.actual_args = None

    def slot(self, *args):
        """
        Slot connected to the signal to test for.

        If the signal is emitted, the attribute :attr:`called` is set to True.

        Parameters
        ----------
        args
            Parameters passed by the emitted signal.

        """
        self.actual_args = args
        self.called = True

    def __enter__(self):
        """Entrance of the context manager."""
        self.signal.connect(self.slot)

    def __exit__(self, exception, msg, traceback):
        """
        Exit of the context manager.

        Parameters
        ----------
        exception
            Exception that may have been raised.

        msg : :class:`str`
            Message to pass to the exception

        traceback
            Call trace leading to the exception

        """
        if exception:
            raise exception(msg)
        self.test.assertTrue(self.called, "Signal not called!")
        if self.actual_args:
            self.test.assertEqual(
                self.expected_args,
                self.actual_args,
                f"""Signal arguments don't match!
                actual:   {self.actual_args}
                expected: {self.expected_args}""",
            )


class SignalNotReceiver:
    """
    Context manager class detecting whether a QSignal has not been emitted.

    Adapted from https://stackoverflow.com/a/48128768
    """

    def __init__(self, test, signal):
        self.test = test
        self.signal = signal
        self.called = False

    def slot(self):
        """
        Slot connected to the signal to test for.

        If the signal is emitted, the attribute :attr:`called` is set to True.
        """
        self.called = True

    def __enter__(self):
        """Entrance of the context manager."""
        self.signal.connect(self.slot)

    def __exit__(self, exception, msg, traceback):
        """
        Exit of the context manager.

        Parameters
        ----------
        exception
            Exception that may have been raised.

        msg : :class:`str`
            Message to pass to the exception

        traceback
            Call trace leading to the exception

        """
        if exception:
            raise exception(msg)
        self.test.assertFalse(self.called, "Signal called!")


class TestCaseUsingQSignals(unittest.TestCase):
    """
    Test class for testing whether a QSignal has been emitted.

    Adapted from https://stackoverflow.com/a/48128768
    """

    def setUp(self):
        """Create the QApplication instance"""
        _instance = QtWidgets.QApplication.instance()
        if not _instance:
            _instance = QtWidgets.QApplication([])
        self.app = _instance

    def tearDown(self):
        """Delete the reference owned by self"""
        del self.app

    def assertSignalReceived(self, signal, args):  # noqa N802
        """
        Check whether signal has been received.

        Parameters
        ----------
        signal
            Signal to check for

        args
            Parameters passed by the emitted signal.

        Returns
        -------
        answer : :class:`bool`
            Result of the test

        """
        return SignalReceiver(self, signal, args)

    def assertSignalNotReceived(self, signal):  # noqa N802
        """
        Check whether signal has not been received.

        Parameters
        ----------
        signal
            Signal to check for

        Returns
        -------
        answer : :class:`bool`
            Result of the test

        """
        return SignalNotReceiver(self, signal)
