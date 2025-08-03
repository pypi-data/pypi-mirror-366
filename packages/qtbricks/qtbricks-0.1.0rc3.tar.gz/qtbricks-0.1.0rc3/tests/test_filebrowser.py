import unittest

from PySide6 import QtCore, QtWidgets

from qtbricks import filebrowser


class TestFileBrowser(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.widget = filebrowser.FileBrowser()
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.widget.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_instantiate_class(self):
        pass
