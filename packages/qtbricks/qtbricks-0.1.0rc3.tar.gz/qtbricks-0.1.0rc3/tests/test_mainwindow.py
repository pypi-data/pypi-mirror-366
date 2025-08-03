import unittest

from PySide6 import QtCore, QtWidgets

from qtbricks import mainwindow


class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.window = mainwindow.MainWindow()
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.window.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_instantiate_class(self):
        pass


class TestGeneralDockWindow(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.window = mainwindow.GeneralDockWindow()
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.window.deleteLater()
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_instantiate_class(self):
        pass

    def test_initialisation_sets_window_title(self):
        window_title = "Lorem ipsum"
        window = mainwindow.GeneralDockWindow(title="Lorem ipsum")
        self.assertEqual(window.windowTitle(), window_title)

    def test_initialisation_sets_widget(self):
        widget = QtWidgets.QListWidget()
        window = mainwindow.GeneralDockWindow(widget=widget)
        self.assertEqual(window.widget(), widget)

    def test_initialisation_sets_object_name(self):
        object_name = "Foo"
        window = mainwindow.GeneralDockWindow(object_name=object_name)
        self.assertEqual(window.objectName(), object_name)
