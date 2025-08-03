"""
File browser widget for selecting (multiple) files from a directory tree.

Sometimes we need a convenient file browser widget displaying a directory as
tree and allowing to both, navigate through the directory hierarchy and to
select (multiple) files. All we are usually interested in is the (full) file
names of the selected files.

There is currently just one public class in this module meant to be included
as a widget into your own GUIs: :class:`FileBrowser`. All other classes are
meant for internal use only, although they are documented.


General characteristics and intended purpose
============================================

The file browser widget is intended to be used as an interface to select one
or multiple individual *files* (not directories) and to return the filenames
with their full path, to further operate on this information.


How to use the FileBrowser in own GUIs?
=======================================

A rather minimal (and not very useful, though educational) example,
including the :class:`FileBrowser` as only widget of a main window:

.. code-block::

    import sys

    from PySide6 import QtWidgets

    from qtbricks import filebrowser


    class MainWindow(QtWidgets.QMainWindow):

        def __init__(self):
            super().__init__()

            widget = filebrowser.FileBrowser()

            # Purely for debugging purposes:
            widget.selection_changed.connect(lambda x: print("Selection:", x))
            self.setCentralWidget(widget)

            self.show()


    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        w = MainWindow()
        app.exec()


While the :class:`FileBrowser` class emits
:attr:`FileBrowser.selection_changed` signals whenever the selection of its
items changed, you can always get the current selection from the
:attr:`FileBrowser.selection` attribute. The :attr:`FileBrowser.selection`
attribute contains the filenames including the full path for each selected
file (item). Similarly, the :attr:`FileBrowser.selection_changed` signal
contains the contents of :attr:`FileBrowser.selection` as payload.


Notes for developers
====================

Wherever possible, the naming follows :pep:`8` conventions. This naturally
leads to some inconsistencies between the PySide6 elements and the own code.

All icons used are from the FontAwesome font (version 6), with a CC BY 4.0
License (https://creativecommons.org/licenses/by/4.0/) for the icons
themselves. To decouple the location of the icons from the actual code,
the :func:`qtbricks.utils.image_path` function gets used.

The entire widget is laid out programmatically, *not* using QtDesigner.
Currently, all widgets are non-public instance attributes, allowing to
define them all together in the class constructor and factoring further
settings into separate methods.

Communication with the outside world beyond the widget primarily takes place
via the Qt signal--slot mechanism.

.. todo::
    Try to reimplement buttons and edit as a Qt toolbar with respective
    actions that can even be added to an external window?

.. todo::
    Try to reimplement toolbar/buttons&edit such that the edit moves in a
    second line if the widget gets too narrow.

.. todo::
    Provide (sensible) minimumSizeHint for FileBrowser widget.

    Depending on the context the widget is used in, this seems not
    necessary... Hence, lower priority.


Module documentation
====================

"""

import os
import sys

from PySide6 import QtWidgets, QtCore, QtGui

from qtbricks import utils


class FileBrowser(QtWidgets.QWidget):
    """
    File browser widget for selecting (multiple) files from a directory tree.

    Sometimes we need a convenient file browser widget displaying a
    directory as tree and allowing to both, navigate through the directory
    hierarchy and to select (multiple) files. All we are usually
    interested in is the (full) file names of the selected files.

    At the core of the widget is a tree view (a :class:`_FileTree` object),
    but for the convenience of the user, a series of additional control
    widgets is added on top:

    * Buttons for home, back, up, and forward
    * A line edit displaying the current directory path

    The back and forward buttons are only active once the user navigated
    within the directory tree. The line edit displaying the current
    directory path can be used as an input as well and will always be in
    sync with the tree view. If the user enters a non-existing directory,
    the edit will simply be reverted to the last (valid) path.

    Multiple selections are allowed, but only files can be selected,
    not directories. You can select multiple files by pressing the "Ctrl"
    key while clicking. In the same way, you can deselect a given file.
    Pressing the "Shift" key when clicking selects a range of files.

    Selecting files using the keyboard follows established conventions as
    well. Moving with the arrow keys moves the selection. Holding the
    "Ctrl" key when navigating with the arrow keys allows to select an
    additional file pressing the "Space" key. Holding the "Shift" key when
    navigating with the arrow keys selects an entire range of files. You can
    even use a sequence of holding "Ctrl" and "Shift" keys for arbitrarily
    complex selection patterns. Just make sure to always keep pressing
    either "Ctrl" or "Shift" when navigating, as otherwise, the selection
    will be cleared and only the current item selected. Deselecting an item
    is possible as well, holding the "Ctrl" key and using the "Space" key to
    toggle selection of the current item.

    Double-clicking on a directory will change the root path to this
    directory.

    Currently, the class has no public methods and only two public
    attributes and a signal documented below.

    Parameters
    ----------
    path : :class:`str`
        Root path to be set for the file browser

    Attributes
    ----------
    root_path : :class:`str`
        Root path set currently for the file browser

    selection : :class:`list`
        Names of the currently selected files

        The names are the actual full paths to the file on the file system.

        Thanks to using a list, the names should always appear in the order
        they have been selected.

    """

    selection_changed = QtCore.Signal(set)
    """
    Signal emitted when the selection of items changed.

    The signal contains the selection as :class:`set` parameter.
    """

    def __init__(self, path=""):
        super().__init__()

        self.root_path = path or os.path.abspath(os.path.curdir)
        self.selection = []

        self._previous_path = ""
        self._next_path = ""
        self._model_settings = {}

        self._home_button = QtWidgets.QPushButton()
        self._back_button = QtWidgets.QPushButton()
        self._up_button = QtWidgets.QPushButton()
        self._forward_button = QtWidgets.QPushButton()
        self._curdir_edit = QtWidgets.QLineEdit()
        self._tree_view = _FileTree(root_path=self.root_path)

        self._setup_ui()
        self._update_ui()

    @property
    def model_settings(self):
        """
        Settings for the underlying QFileSystemModel.

        Often, when browsing the file system, we want to control (and
        restrict) what is displayed how. To this end, settings for the
        underlying model need to be set.

        The settings are contained in a :class:`dict` that supports the
        following fields:

        filters : :class:`list`
            A list of strings to be used for filtering the files.

            Typical use cases would be filters for file extensions, such as
            ``*.py`` or ``*.png``.

            The QFileSystemModel class only supports basic wildcard
            filtering, so you will need to use a ``QSortFilterProxyModel`` to
            get fully customisable filtering. Note however, that the latter
            is currently *not* implemented.

            See https://stackoverflow.com/questions/72587813 for inspiration.

        filter_disables : :class:`bool`
            Whether files filtered with the above filter are displayed.

            The standard handling of the QFileSystemModel is to only
            disable, but not hide the filtered out entries. Set to
            ``False`` in case you want to *hide* the entries entirely.

        Returns
        -------
        model_settings : :class:`dict`
            Settings for the underlying QFileSystemModel


        Note
        ----

        The reason for this attribute to be a property is simple,
        yet deserves a comment for developers: You need to be able to
        set/alter the model settings after you have instantiated the
        class. Therefore, upon changing the settings, an internal method
        is called taking care of applying your settings to the model.

        """
        return self._model_settings

    @model_settings.setter
    def model_settings(self, settings):
        self._model_settings = settings
        self._tree_view.apply_settings(self._model_settings)

    def _setup_ui(self):
        self._set_widget_properties()
        self._set_layout()
        self._connect_signals()

    def _set_widget_properties(self):
        self._home_button.setIcon(QtGui.QIcon(utils.image_path("house.svg")))
        self._home_button.setToolTip(
            "Go to the home directory of the current user"
        )
        self._up_button.setIcon(
            QtGui.QIcon(utils.image_path("circle-up.svg"))
        )
        self._up_button.setToolTip("Go one directory up in the hierarchy")
        self._back_button.setIcon(
            QtGui.QIcon(utils.image_path("circle-left.svg"))
        )
        self._back_button.setToolTip("Go back to the previous directory")
        self._forward_button.setIcon(
            QtGui.QIcon(utils.image_path("circle-right.svg"))
        )
        self._forward_button.setToolTip(
            "Revert going back to the previous directory"
        )
        self._curdir_edit.setText(self.root_path)
        self._curdir_edit.setCursorPosition(len(self._curdir_edit.text()))
        self._curdir_edit.setToolTip(
            "Display/edit the current (root) directory.\n"
            "Only existing directories will be accepted as user input."
        )

    def _set_layout(self):
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(self._home_button)
        controls_layout.addWidget(self._back_button)
        controls_layout.addWidget(self._up_button)
        controls_layout.addWidget(self._forward_button)
        controls_layout.addStretch()
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(controls_layout)
        layout.addWidget(self._curdir_edit)
        layout.addWidget(self._tree_view)
        self.setLayout(layout)

    def _connect_signals(self):
        self._up_button.pressed.connect(self._move_up)
        self._home_button.pressed.connect(self._go_home)
        self._back_button.pressed.connect(self._go_back)
        self._forward_button.pressed.connect(self._go_forward)
        self._curdir_edit.editingFinished.connect(self._change_path)
        self._tree_view.root_path_changed.connect(self._change_root_path)
        self._tree_view.selection_changed.connect(self._change_selection)

    def _change_path(self):
        new_path = self._curdir_edit.text()
        if os.path.exists(new_path):
            self._change_root_path(new_path)
        else:
            self._curdir_edit.setText(self.root_path)

    def _change_selection(self, selection: list):
        self.selection_changed.emit(selection)
        self.selection = selection

    def _change_root_path(self, path=""):
        if path == self.root_path:
            return
        if path.endswith("/") and path != "/":
            path = path[:-1]
        self._previous_path = self.root_path
        self.root_path = path
        self._update_ui()

    def _move_up(self):
        self._change_root_path(path=os.path.split(self.root_path)[:-1][0])

    def _go_home(self):
        self._change_root_path(path=os.path.expanduser("~"))

    def _go_back(self):
        self._next_path = self.root_path
        self._change_root_path(path=self._previous_path)

    def _go_forward(self):
        path = self._next_path
        self._next_path = ""
        self._change_root_path(path=path)

    def _update_ui(self):
        self._curdir_edit.setText(self.root_path)
        self._tree_view.set_root_path(self.root_path)
        self._back_button.setEnabled(bool(self._previous_path))
        self._forward_button.setEnabled(bool(self._next_path))


class _FileTree(QtWidgets.QTreeView):
    """
    Tree view of the file system emitting names of selected files.

    The tree view is based on :class:`PySide6.QtWidgets.QTreeView` and uses
    :class:`PySide6.QtWidgets.QFileSystemModel` as underlying model for the
    file system. Furthermore, multiple selections are allowed, but only
    files can be selected, not directories.

    As a selection mode,
    :attr:`QtWidgets.QAbstractItemView.ExtendedSelection` is used, meaning
    that you can select multiple files by pressing the "Ctrl" key while
    clicking. In the same way, you can deselect a given file. Pressing the
    "Shift" key when clicking selects a range of files.

    Double-clicking on a directory will change the root path to this
    directory.

    The class emits two signals described below.

    Parameters
    ----------
    root_path : :class:`str`
        Root path to be set for the file browser


    .. todo::
        Properly handle hiding of columns, using :meth:`self.hideColumn(#)`.

    .. todo::
        Context menu, allowing to set the columns to be displayed?

    .. todo::
        Allow using the "Return" key to enter directories?

    """

    root_path_changed = QtCore.Signal(str)
    """
    Signal emitted when the root path of the underlying model changed.

    The signal contains the new root path as :class:`str` parameter.
    """

    selection_changed = QtCore.Signal(list)
    """
    Signal emitted when the selection of items changed.

    The signal contains the selection as :class:`list` parameter.
    """

    def __init__(self, root_path=""):
        super().__init__()
        self._root_path = root_path
        self._model = _FileSystemModel()
        self._setup_ui()

    def _setup_ui(self):
        self._model.rootPathChanged.connect(self._root_path_changed)
        self.setModel(self._model)

        self.set_root_path(self._root_path)
        # self.hideColumn(1)

        self.setExpandsOnDoubleClick(False)
        # noinspection PyUnresolvedReferences
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.doubleClicked.connect(self._double_clicked)

        self.setAllColumnsShowFocus(True)

    def set_root_path(self, path=""):
        """
        Set the root path of the directory tree view.

        Parameters
        ----------
        path : :class:`str`
            Path to be set as root path.

        """
        if not path:
            return
        self._model.setRootPath(path)
        self.setRootIndex(self._model.index(self._model.rootPath()))

    def _double_clicked(self, index=QtCore.QModelIndex()):
        """
        Handle double-click events on items.

        In case the user double-clicks on a directory, the root path of the
        tree view is reset to this directory.

        Note that due to the tree view, the user doesn't need to
        double-click on a directory to see its contents, but can unfold it
        as well.

        Parameters
        ----------
        index : :class:`QtCore.QModelIndex`
            Index of the selected item

        """
        if self._model.fileInfo(index).isDir():
            self.set_root_path(self._model.filePath(index))

    def _root_path_changed(self, path=""):
        """
        Handle "rootPathChanged" signal of the underlying model.

        Whenever the root path of the model changed,
        a :attr:`root_path_changed` signal will be emitted sending the new
        path as payload.

        The signal will only be emitted if the path actually changed.

        Parameters
        ----------
        path : :class:`str`
            New root path that has been set.

        """
        if path != self._root_path:
            self._root_path = path
            self.root_path_changed.emit(path)

    def selectionCommand(  # noqa N802
        self, index=QtCore.QModelIndex, event=QtCore.QEvent
    ):
        """
        Handle selection of the underlying tree view.

        In case a directory has been selected, it will automatically be
        deselected, thus making directories not selectable. The idea behind
        this behaviour is to return only files, not directories,
        for settings where you want to operate on one or multiple files,
        but not on entire directories.

        For all items that are not directories, the super method is called
        and the parameters passed to this method.

        Parameters
        ----------
        index : :class:`QtCore.QModelIndex`
            Index of the selected item

        event : :class:`QtCore.Event`
            Event sent during selection.

        """
        if self._model.fileInfo(index).isDir():
            # noinspection PyUnresolvedReferences
            return QtCore.QItemSelectionModel.Deselect
        return super().selectionCommand(index, event)

    def selectionChanged(self, selected, deselected):  # noqa N802
        """
        Handle changes of selection of the underlying tree view.

        A :attr:`selection_changed` signal is emitted, conveying the list of
        filenames (with their full path) corresponding to the currently
        selected items.

        Afterwards, the super method is called and the parameters passed to
        this method.

        Parameters
        ----------
        selected : :class:`QtCore.QItemSelection`
            Selected item

        deselected: :class:`QtCore.QItemSelection`
            Deselected item

        """
        selected_rows = []
        for index in self.selectedIndexes():
            item = self._model.filePath(index)
            if item not in selected_rows:
                selected_rows.append(item)
        self.selection_changed.emit(selected_rows)
        super().selectionChanged(selected, deselected)

    def apply_settings(self, model_settings):
        if "filters" in model_settings:
            self._model.setNameFilters(model_settings["filters"])
        if "filter_disables" in model_settings:
            self._model.setNameFilterDisables(
                model_settings["filter_disables"]
            )


class _FileSystemModel(QtWidgets.QFileSystemModel):
    """
    Model of the file system used in the tree view.

    Basically, the class is identical to its base class, currently just
    adding the relevant code for displaying tooltips.
    """

    # noinspection PyUnresolvedReferences,PyMethodOverriding
    def data(self, index, role):
        """
        Text or else used to display the selected item in the given context.

        Parameters
        ----------
        index : :class:`QtCore.QModelIndex`
            Index of the selected item

        role : :class:`int`
            The Qt role deciding about the context

        Returns
        -------
        data : :class:`Any`
            Data used to display the item

        """
        if role == QtCore.Qt.ToolTipRole:
            role = QtCore.Qt.DisplayRole
        return super().data(index, role)


class _MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        widget = FileBrowser(os.path.dirname(__file__))
        # Purely for debugging purposes:
        widget.selection_changed.connect(lambda x: print("Selection:", x))
        self.setCentralWidget(widget)

        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = _MainWindow()
    app.exec()
