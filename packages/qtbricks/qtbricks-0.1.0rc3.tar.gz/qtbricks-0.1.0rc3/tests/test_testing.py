import unittest

from PySide6 import QtCore, QtWidgets

from qtbricks import testing


class TestQtestEnterText(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.widget = QtWidgets.QLineEdit()
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.widget.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_qtest_enter_text_enters_text(self):
        text = "Lorem ipsum"
        testing.qtest_enter_text(widget=self.widget, text=text)
        self.assertEqual(text, self.widget.text())

    def test_qtest_enter_text_clears_text_before(self):
        text = "Lorem ipsum"
        self.widget.setText("Bla")
        testing.qtest_enter_text(widget=self.widget, text=text)
        self.assertEqual(text, self.widget.text())

    def test_qtest_enter_text_sends_signals(self):
        def mock_slot():
            self.has_been_called = True

        self.has_been_called = False
        text = "Lorem ipsum"
        self.widget.editingFinished.connect(mock_slot)
        testing.qtest_enter_text(widget=self.widget, text=text)
        self.assertTrue(self.has_been_called)
