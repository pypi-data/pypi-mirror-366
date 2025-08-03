import os
import unittest

from PySide6 import QtCore, QtWidgets

from qtbricks import utils


class TestImagePath(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.join(
            os.path.split(os.path.dirname(__file__))[0], "qtbricks"
        )

    def test_image_path_with_defaults(self):
        image_name = "foo.svg"
        expected = os.path.join(self.basedir, "images", image_name)
        actual = utils.image_path(name=image_name)
        self.assertEqual(expected, actual)

    def test_image_path_with_image_dir(self):
        image_name = "foo.svg"
        image_path = "icons"
        expected = os.path.join(self.basedir, image_path, image_name)
        actual = utils.image_path(name=image_name, image_dir=image_path)
        self.assertEqual(expected, actual)

    def test_image_path_with_base_dir(self):
        image_name = "foo.svg"
        base_dir = os.path.dirname(__file__)
        expected = os.path.join(base_dir, "images", image_name)
        actual = utils.image_path(name=image_name, base_dir=base_dir)
        self.assertEqual(expected, actual)


class TestCreateButton(unittest.TestCase):
    def setUp(self):
        self.app = (
            QtWidgets.QApplication.instance() or QtWidgets.QApplication()
        )
        self.addCleanup(self.release_qt_resources)

    def release_qt_resources(self):
        self.app.sendPostedEvents(event_type=QtCore.QEvent.DeferredDelete)
        self.app.processEvents()

    def test_create_button_returns_button(self):
        button = utils.create_button()
        self.assertIsInstance(button, QtWidgets.QPushButton)


class TestIntValidator(unittest.TestCase):
    def setUp(self):
        self.validator = utils.IntValidator()

    def test_instantiate_class(self):
        pass

    def test_fixup_with_value_exceeding_top_returns_top(self):
        self.validator.setTop(42)
        self.assertEqual(
            self.validator.fixup(str(42 + 5)),
            str(self.validator.top()),
        )

    def test_fixup_with_value_exceeding_bottom_returns_bottom(self):
        self.validator.setBottom(42)
        self.assertEqual(
            self.validator.fixup(str(42 - 5)),
            str(self.validator.bottom()),
        )
