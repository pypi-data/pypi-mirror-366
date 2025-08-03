import unittest

from PySide6 import QtCore, QtWidgets, QtTest

from qtbricks import aboutdialog, testing


class TestDatasetDisplayWidget(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.package_name = "qtbricks"
        self.widget = aboutdialog.AboutDialog(package_name=self.package_name)
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.widget.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_window_title(self):
        self.assertEqual(
            f"About {self.package_name}", self.widget.windowTitle()
        )

    def test_has_close_button(self):
        close_button = self.widget._button_box.button(
            QtWidgets.QDialogButtonBox.Close
        )
        self.assertTrue(close_button)


class TestDatasetDisplayWidgetSignals(testing.TestCaseUsingQSignals):
    def setUp(self):
        super().setUp()
        self.package_name = "qtbricks"
        self.widget = aboutdialog.AboutDialog(package_name=self.package_name)

    def test_pressing_close_button_closes_dialog(self):
        close_button = self.widget._button_box.button(
            QtWidgets.QDialogButtonBox.Close
        )
        with self.assertSignalReceived(self.widget.rejected, None):
            QtTest.QTest.mouseClick(
                close_button,
                QtCore.Qt.MouseButton.LeftButton,
            )
