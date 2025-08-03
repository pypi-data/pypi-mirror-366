"""
Main GUI window.

There is usually one main window of a GUI, and this window consists of all
the default parts provided by the Qt framework, namely menu bar and toolbars
at the top, status bar at the bottom, and areas for dockable windows/widgets
on all four sides of the central widget.

While the actual contents of both, the central widget and the dock areas
and the other components are more or less unique for your application,
a main window of a GUI comes with a lot of features and basic
functionality that are rather general. Hence you can greatly reduce the
amount of code to write when inheriting from the :class:`MainWindow` class
implemented here.

.. note::

    Some ideas are borrowed and adapted from Mark Summerfield and his
    excellent book "Rapid GUI Programming with Python and Qt" (Prentice
    Hall, Upper Saddle River, 2008). While written for Python 2 and PyQt4,
    both the concepts and the thorough introduction to GUI programming are
    probably still the best that is available for creating GUIs with
    Python and Qt.


How to call and where to instantiate
====================================

Rather than creating an instance of :class:`MainWindow` yourself, you will
usually call the :func:`app.main` function of the :mod:`app` module,
or simply call the GUI by means of the respective gui_scripts entry point
defined in ``setup.py``.


.. note::

    Of course, you will usually not use the :class:`MainWindow` as
    implemented here, as it lacks all contents, but rather create your own
    ``MainWindow`` class inheriting from :class:`MainWindow` and setting
    the central widgets and everything else as appropriate.


An example of an :mod:`app` module is shown below. Note the fictitious
name ``mypackage`` that you would need to replace with the actual name of
your package:

.. code-block::

    import sys

    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QIcon

    from qtbricks import utils

    from mypackage import mainwindow

    def main():
        app = QApplication(sys.argv)
        app.setOrganizationName("demoapp")
        app.setOrganizationDomain("example.org")
        app.setApplicationName("Demo application")
        app.setWindowIcon(QIcon(utils.image_path("icon.svg")))

        window = mainwindow.MainWindow()
        window.show()
        app.exec()


    if __name__ == "__main__":
        main()


Note that the setting of the organisation name
(``app.setOrganizationName()``) is crucial for storing settings, as this
determines the name of the directory the settings are stored under. The
exact location of the configuration depends on your operating system.
Furthermore, setting the application name (``app.setApplicationName()``)
is relevant for programmatically obtaining the application name, *e.g.*,
for window titles and alike. As you can see from the above code,
Qt is capable of handling SVG files directly, very convenient for icons
and logos of your application.

The corresponding section in the ``setup.py`` file with the gui entrypoint
may look similar to the following:

.. code-block::

    setuptools.setup(
        # ...
        entry_points={
            "gui_scripts": [
                "demoapp = demoapp.gui.app:main"
            ]
        },
        # ...


In this particular case, both, your package and the respective GUI
entrypoint, *i.e.* the callable from the terminal, are named "demoapp". Of
course, you will need to change this to some sensible name for your
package/GUI application.


Some notes for developers
=========================

GUI programming can be quite complex, and the :class:`MainWindow` class
provides only a small set of (sensible) defaults for the most common tasks.
However, to help with creating GUIs and to keep the code as readable as
possible, some general advice and an overview of the functionality
implemented are given below.


First step: creating your own mainwindow module
-----------------------------------------------

The first step is always to create your own ``mainwindow`` module,
presumably in the ``gui`` subpackage of your package. A rather minimal
structure of this module is shown below:


.. code-block::

    from PySide6 import QtWidgets

    import qtbricks.mainwindow

    import mypackage.gui.model as model


    class MainWindow(qtbricks.mainwindow.MainWindow):

        def __init__(self):
            # Customise your main window, setting at least a central widget.
            # Try to keep methods as short and concise as possible.


A few comments, beyond the obvious:

* You will want/need to import further modules containing the definition
  of the widget(s) used as central widget and possibly in dockable areas.

* You should always follow the model-view paradigm for larger
  applications, and come up with a model of your application containing
  the business logic. This is reflected in the import of a model module of
  your fictitious ``mypackage`` package.


Saving and restoring GUI settings
---------------------------------

By default, window geometry and state will be saved on close and restored on
startup. This creates a file, typically in the user's home directory,
and depending on the respective platform. Directory and file name depend on
the settings of organisation and application name on the application level.
For details, see the :func:`app.main` function in the :mod:`app` module.

To this end, a private method :meth:`MainWindow._restore_settings` gets
called from the constructor to restore the settings, and the
:meth.`MainWindow.closeEvent` method is overridden to take care of saving
the current settings on closing the GUI.


Adding menus
------------

Menus (and toolbars) are essential aspects of nearly every GUI, particular
the main window. In its default configuration, three menus are created:
"File", "View", and "Help". The "File" menu is populated with a "Quit"
action and associated keyboard shortcut "Ctrl + Q", the "Help" menu with an
"About" action and associated keyboard shortcut "F1". The "View" menu is a
reminder that in case of dockable windows, you need a way to restore windows
closed by the user.

While the :meth:`MainWindow._create_menus` method gets called from the
:meth:`MainWindow._setup_ui` method on startup, for the sake of code
readability it is best to separate creating each menu into its own (private)
method that gets called in turn from within the
:meth:`MainWindow._create_menus` method.

Each (active) entry in a menu is an action in Qt speak, and to help with
adding those actions, there is a (private) method
:meth:`MainWindow._create_action` taking a series of parameters. Perhaps it
is best explained with an example:


.. code-block::

    file_quit_action = self._create_action(
        "&Quit",
        self.close,
        QtGui.QKeySequence.Quit or "Ctrl+Q",
        "file_quit",
        "Close the application"
    )


Here, we define the action for quitting the main window and hence the entire
GUI application. The first argument is the text appearing in the menu,
including the keyboard accelerator character. The second argument is the
actual method being called, followed by the keyboard shortcut, a name for an
icon file (entirely optional), and finally an explaining text used as
tooltip in case of a toolbar and shown in the status bar in case of a menu.

Qt actions are defined once and can be used in different contexts: You can
add them to a menu, to a context menu, and to a toolbar. Depending on your
way of organising your code, you will need to either make the actions
(private) attributes of the :class:`MainWindow` class or define menus,
context menus and toolbars all within one method.

A further convenience method helping to add actions to menus is
:meth:`MainWindow._add_actions`. Here, you can not only provide a list of
actions, but "None" as well that will be converted to separators.


Adding dockable windows
-----------------------

Generally, dockable windows need to inherit from
:class:`PySide6.QtWidgets.QDockWidget`. A prototypical class for a dockable
window is shown below. Adapt to your own needs. Of course, a dockable window
can (and usually will) contain arbitrarily complex widgets.


.. code-block::

    class GeneralDockWindow(QtWidgets.QDockWidget):

        def __init__(self, title="General Dock Window"):
            super().__init__()
            self.setObjectName("GeneralDockWindow")
            self.setWindowTitle(title)
            self.list_widget = QtWidgets.QListWidget()
            self.setWidget(self.list_widget)


Note that a very similar implementation is provided in the
:class:`GeneralDockWindow` class. See its documentation for further details.

The possible docking areas the window can be attached to can be restricted
as well:


.. code-block::

    self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)


To add such a dockable window to your main window, extend the
:meth:`MainWindow._create_dock_windows` method in a way similar to the
following:


.. code-block::

    def _create_dock_windows(self):
        general_dock_window_1 = GeneralDockWindow("general 1")
        self.addDockWidget(Qt.LeftDockWidgetArea, general_dock_window_1)
        self._view_menu.addAction(general_dock_window_1.toggleViewAction())


Important here is to add the action to the View menu in order to be able to
restore a closed dockable window. To make things easier, the same can be
achieved using the convenience function :meth:`MainWindow._add_dock_window`:


.. code-block::

    dock_window = GeneralDockWindow()
    self._add_dock_window(
        dock_window,
        "general 1",
        Qt.LeftDockWidgetArea
    )


In case you want to layout two or more dock widgets as tabbed windows,
use the same method, but assign the output to a variable of your choosing,
and afterwards programmatically "tabify" the respective docked windows:


.. code-block::

    dock1 = self._add_dock_window(...)
    dock2 = self._add_dock_window(...)
    self.tabifyDockWidget(dock1, dock2)


Just make sure that both windows you want to appear in tabs are set to the
same docking area. Otherwise, the first one will "win" and drag the second
one to the same docking area.


Preventing loss of work on closing the GUI
------------------------------------------

As soon as the user can change contents from within the GUI, it may no
longer be safe to simply close the window and hence quit the entire
application. The same is true for changes that need to be applied or
discarded before switching to some other dataset or else. To detect (and
handle) the situation when changes are present that have not yet been saved,
reimplement the method :meth:`MainWindow._ok_to_continue` according to your
needs. Furthermore, this method allows for convenient and readable code
similar to


.. code-block::

    if self._ok_to_continue():
        ...


For an actual example, you may have a look at the
:meth:`MainWindow.closeEvent` method.


Module documentation
====================

"""

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import SIGNAL, QSettings, QByteArray, QSize, Qt

from qtbricks import utils, aboutdialog


class MainWindow(QtWidgets.QMainWindow):
    """
    Main GUI window of the application.

    There is usually one main window of a GUI, and this window consists of
    all the default parts provided by the Qt framework, namely menu bar and
    toolbars at the top, status bar at the bottom, and areas for dockable
    windows/widgets on all four sides of the central widget.

    While any more complex dialogs and widgets are usually designed using
    the QtDesigner tool, the main window, consisting typically of one
    central widget, is laid out programmatically.

    Rather than creating an instance of :class:`MainWindow` yourself,
    you will usually call the :func:`app.main` function of the :mod:`app`
    module, or simply call the GUI by means of the respective gui_scripts entry
    point defined in ``setup.py``.

    By default, window geometry and state will be saved on close and
    restored on startup. This creates a file, typically in the user's home
    directory, and depending on the respective platform. Directory and file
    name depend on the settings of organisation and application name on the
    application level. For details, see the :func:`app.main` function in the
    :mod:`app` module.

    Attributes
    ----------
    package_name : :class:`str`
        Name of the package the mainwindow belongs to.

        This information is required, *i.a.*, for the "Help About" window.

    logo : :class:`str`
        Path to logo image file

        The logo is used, *i.a.*, for the Help About window.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.package_name = "qtbricks"
        self.logo = utils.image_path("icon.svg")

        self._view_menu = None

        self._setup_ui()
        self._restore_settings()

    def _restore_settings(self):
        settings = QSettings()
        self.restoreGeometry(
            settings.value("MainWindow/Geometry", QByteArray())
        )
        self.restoreState(settings.value("MainWindow/State", QByteArray()))

    def _setup_ui(self):
        """
        Create the elements of the main window.

        The elements created are:

        #. The central widget
        #. The status bar
        #. The menu bar
        #. The dockable windows

        All these tasks are delegated to (non-public) methods. The toolbar
        will usually be created from within the menus, as the actions will
        be defined therein.

        In its default configuration, three menus are created: "File",
        "View", and "Help". The "File" menu is populated with a "Quit"
        action and associated keyboard shortcut "Ctrl + Q", the "Help" menu
        with an "About" action and associated keyboard shortcut "F1". The
        "View" menu is a reminder that in case of dockable windows, you need
        a way to restore windows closed by the user.

        Additionally, the minimum size and title of the main GUI window is
        set. The window title is identical to the application name set in
        the :func:`app.main` function in the :mod:`app` module.

        """
        self._create_central_widget()
        self._create_status_bar()
        self._create_menus()
        self._create_dock_windows()

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle(QtWidgets.QApplication.applicationName())

    def _create_central_widget(self):
        pass

    def _create_status_bar(self):
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

    def _create_menus(self):
        self._create_file_menu()
        self._create_view_menu()
        self._create_help_menu()

    def _create_dock_windows(self):
        pass

    def _create_file_menu(self):
        # noinspection PyUnresolvedReferences
        file_quit_action = self._create_action(
            "&Quit",
            self.close,
            QtGui.QKeySequence.Quit or "Ctrl+Q",
            "file_quit",
            "Close the application",
        )
        file_menu = self.menuBar().addMenu("&File")
        self._add_actions(file_menu, (file_quit_action,))

    def _create_view_menu(self):
        self._view_menu = self.menuBar().addMenu("&View")

    def _create_help_menu(self):
        help_about_action = self._create_action(
            "&About", self.help_about, "F1", "", "About the application"
        )
        help_menu = self.menuBar().addMenu("&Help")
        self._add_actions(help_menu, (help_about_action,))

    # pylint: disable=too-many-arguments
    def _create_action(
        self,
        text,
        slot=None,
        shortcut=None,
        icon=None,
        tip=None,
        checkable=False,
        signal="triggered()",
    ):
        action = QtGui.QAction(text, self)
        if icon:
            action.setIcon(QtGui.QIcon(utils.image_path(f"{icon}.png")))
        if shortcut:
            action.setShortcut(shortcut)
        if tip:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot:
            # noinspection PyTypeChecker
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    @staticmethod
    def _add_actions(target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def _add_dock_window(
        self, dock_window=None, title="", area=Qt.RightDockWidgetArea
    ):
        if title:
            dock_window.setTitle(title)
        self.addDockWidget(area, dock_window)
        self._view_menu.addAction(dock_window.toggleViewAction())
        return dock_window

    def help_about(self):
        """
        Show a dialog with basic information about the application.

        Presenting the user with a concise summary of what the entire
        application is about, perhaps together with the author names,
        a license information, and some very basic system settings,
        is a sensible thing to do. Typically, this can be found in the "Help
        -> About" menu.
        """
        dialog = aboutdialog.AboutDialog(
            parent=self, package_name=self.package_name, logo=self.logo
        )
        dialog.exec()

    def closeEvent(self, event):  # noqa N802
        """
        Actions performed when attempting to close the window.

        By default, both geometry and state of the main window are saved to
        the settings file, to be restored on startup, using the standard Qt
        machinery for this purpose.
        """
        if self._ok_to_continue():
            settings = QSettings()
            settings.setValue("MainWindow/Geometry", self.saveGeometry())
            settings.setValue("MainWindow/State", self.saveState())
        else:
            event.ignore()

    # noinspection PyMethodMayBeStatic
    def _ok_to_continue(self):
        """
        Helper method determining whether it is safe to continue.

        Often, certain actions shall not be performed if the application is in
        an unsaved state (*e.g.*, closing the application). Therefore,
        implement this method according to your needs. In its default
        implementation, it always returns "True".

        Returns
        -------
        status : :class:`bool`
            Whether it is safe to continue

        """
        return True


class GeneralDockWindow(QtWidgets.QDockWidget):
    """
    Convenience class for dockable windows.

    This is a thin wrapper for widgets that should appear as dockable
    windows in a main application window. Note that this dock window is not
    restricted with respect to the dockable areas it can be positioned in.
    You may, however, restrict this afterwards. See the examples section for
    details.

    Parameters
    ----------
    title : :class:`str`
        Window title

        The window title should be comprehensive, as it is used both,
        as window title in the dock and in the view menu of the main window.

    widget : :class:`PySide6.QtWidgets.QWidget`
        Widget to be set as (central) widget of the dockable window


    Examples
    --------
    To add a dockable window to your main application window, you first need
    to create a dockable window containing the (complex) widget of your
    choosing, and afterwards add it to your main application window.

    If you subclass :class:`MainWindow` for your main application window,
    you can make use of a series of convenience methods provided. Dockable
    windows should be defined within the method
    :meth:`MainWindow._create_dock_windows`. You can add the dockable window
    using the method :meth:`MainWindow._add_dock_window`.

    .. code-block::

        def _create_dock_windows(self):
            dock_window = qtbricks.mainwindow.GeneralDockWindow(
                title="My fancy dockable window",
                widget=QtWidgets.QListWidget(),
                object_name="MyDockWindow"
            )
            self._add_dock_window(dock_window=dock_window)

    This will add a dock window to the main application window. Make sure to
    set the object name, as otherwise, Qt will produce warnings if you try
    to save the application state.

    If you would like to restrict the possible docking areas the dock window
    can be added to, you may set the respective property after initialising
    the object:

    .. code-block::

        dock_window = qtbricks.mainwindow.GeneralDockWindow(
            title="My fancy dockable window",
            widget=QtWidgets.QListWidget(),
            object_name="MyDockWindow"
        )
        dock_window.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        )

    Note that you need to import ``PySide6.QtCore.Qt`` for this to work.

    """

    def __init__(
        self, title="General dock window", object_name="", widget=None
    ):
        super().__init__()
        self.setWindowTitle(title)
        self.setObjectName(object_name)
        # noinspection PyTypeChecker
        self.setWidget(widget)


def _main():
    """
    Entry point for the GUI application.

    This function serves as main entry point to the GUI application and gets
    added as "gui_script" entry point. Additionally, the essential
    aspects of the (Qt) application are set that are relevant for saving and
    restoring settings, as well as the window icon.
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("qtbricks")
    app.setOrganizationDomain("example.org")
    app.setApplicationName("Demo application")
    app.setWindowIcon(QtGui.QIcon(utils.image_path("icon.svg")))

    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    import sys

    _main()
