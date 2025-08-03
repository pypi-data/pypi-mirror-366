"""
Help-About dialog for main GUI windows.

**Purpose:** Typically, every GUI has a "Help About" dialog displaying some
information regarding the application, such as its name and version number,
website, license, authors, and debug information.

**Design principles:** The dialog should be as self-contained and
self-consistent as possible. The only crucial information that needs to be
set from the outside is the package name.

**Limitations:** Handling of author/contributor names and email addresses
is limited by how this information is stored in the ``setup.py`` file and
read by the ``importlib.metadata`` module.


Some notes for developers
=========================

If you base the main window of your GUI application on the
:class:`qtbricks.mainwindow.MainWindow` class and set the
:attr:`qtbricks.mainwindow.MainWindow.package_name` attribute accordingly,
you are basically set up.

If, however, you want to change or extend the texts displayed in the three
tabs, the easiest way is to change each of the respective methods returning
the text to be displayed, namely:

* :meth:`AboutDialog._create_about_text`
* :meth:`AboutDialog._create_authors_text`
* :meth:`AboutDialog._create_debug_info_text`

Each of these non-public methods returns a text that is set as text of the
underlying display widget. Hence, you can use a reduced set of HTML tags to
properly format the text.

Furthermore, if you need more control, you may think of using `Jinja
<https://jinja.palletsprojects.com/>`_ as template engine.


Module documentation
====================

"""
from importlib import metadata
import platform
import string
import subprocess  # noqa
import sys

from PySide6 import QtWidgets, QtGui

import qtbricks.utils

ABOUT_STRING = """
<p>
${package_name} - Version ${package_version}
</p>

<p>
<em>${description}</em>
</p>

<p>
Website: <a href="${website}" title="Open ${website} in your preferred 
browser (if configured).">${website}</a>
</p>

<p>
License: ${package_name} is free software: you can redistribute it and/or 
modify it under the terms of the <strong>${license} license</strong>.
</p>
"""

AUTHOR_STRING = """
<p>
The following people contributed to ${package_name}:
</p>

${authors}

You may contact the authors or maintainer(s) using the following email 
address: <a href="mailto:${email}" title="Send email to ${email} 
using your preferred email client (if configured).">${email}</a>.

<hr />

<p>
License: ${package_name} is free software: you can redistribute it and/or 
modify it under the terms of the <strong>${license} license</strong>.
</p>
"""

DEBUG_INFO_STRING = """
<p>
${package_name} - Version ${package_version}
</p>

<p>
OS: ${os}<br />
CPU architecture: ${architecture}<br />
Kernel: ${kernel}
</p>

<p>
Python version: ${python_version}<br />
PySide6 version: ${pyside6_version}
</p>

<hr />

<p>
All installed Python packages:
</p>

<p>
${all_packages}
</p>
"""


class AboutDialog(QtWidgets.QDialog):
    """
    Typical "Help About" Dialog of the main window of a GUI application.

    Most GUI main windows have a "Help About" dialog displaying some
    information regarding the application, such as its name and version
    number, website, license, authors, and debug information.

    Attributes
    ----------
    package_name : :class:`str`
        Name of the package

        This information is crucial for displaying the relevant
        package metadata, such as version, short description, authors,
        and licence.

    logo : :class:`str`
        Path to logo image file


    Parameters
    ----------
    parent : :class:`PySide6.QtWidgets.QWidget`
        Parent of the dialog

        The dialog will usually be centered upon the parent.

    package_name : :class:`str`
        Name of the package

        This information is crucial for displaying the relevant
        package metadata, such as version, short description, authors,
        and licence.

    logo : :class:`str`
        Path to logo image file

    """

    def __init__(self, parent=None, package_name="", logo=""):
        super().__init__(parent)

        self.package_name = package_name
        if logo:
            self.logo = QtGui.QPixmap(logo)
        else:
            self.logo = QtGui.QPixmap(qtbricks.utils.image_path("icon.svg"))

        self._application_name = QtWidgets.QApplication.applicationName()
        self._dialog_buttons = QtWidgets.QDialogButtonBox.Close
        self._button_box = QtWidgets.QDialogButtonBox(self._dialog_buttons)

        self._top_layout = QtWidgets.QHBoxLayout()
        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_about = QtWidgets.QTextBrowser()
        self._tab_authors = QtWidgets.QTextBrowser()
        self._tab_debug_info = QtWidgets.QTextEdit()

        self._setup_ui()

    def _setup_ui(self):
        """
        Setup the dialog window.

        This method takes care of setting up all the elements of the dialog.
        This is a three-step process, each carried out calling the
        corresponding non-public method:

        #. Set the widget properties
        #. Set the layout
        #. Connect the signals and slots

        A requirement is to define all widgets as non-public attributes in
        the class constructor. This comes with the advantage to separate
        the different tasks into methods.
        """
        self._create_top_layout()
        self._add_tab_widgets()
        self._set_widget_properties()
        self._set_layout()
        self._connect_signals()

    def _create_top_layout(self):
        package_metadata = metadata.metadata(self.package_name)
        version = package_metadata["Version"]
        icon = QtWidgets.QLabel()
        icon.setPixmap(self.logo.scaledToHeight(60))
        text = QtWidgets.QLabel(
            f"<h1>{self.package_name}</h1>Version {version}"
        )
        self._top_layout.addWidget(icon)
        self._top_layout.addWidget(text)
        self._top_layout.addStretch(1)

    def _add_tab_widgets(self):
        self._tab_widget.addTab(self._tab_about, "About")
        self._tab_widget.addTab(self._tab_authors, "Authors")
        self._tab_widget.addTab(self._tab_debug_info, "Debug info")

    def _set_widget_properties(self):
        """
        Set the widgets of all the UI components.

        Usually, a widget will contain a number of other widgets whose
        properties need to be set initially. This is the one central place
        to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        self.setWindowTitle(f"About {self.package_name}")
        self._tab_about.setOpenExternalLinks(True)
        self._tab_about.setReadOnly(True)
        self._tab_about.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._tab_about.setText(self._create_about_text())
        self._tab_authors.setOpenExternalLinks(True)
        self._tab_authors.setReadOnly(True)
        self._tab_authors.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._tab_authors.setText(self._create_authors_text())
        self._tab_debug_info.setReadOnly(True)
        self._tab_debug_info.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._tab_debug_info.setText(self._create_debug_info_text())

    def _set_layout(self):
        """
        Lay out the elements of the dialog.

        Usually, a dialog will contain a number of other widgets that need
        to be laid out in some way. This is the central place to do this.

        Furthermore, typically a dialog has a series of buttons contained
        in a button box that need to be placed somewhere as well.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self._top_layout)
        layout.addWidget(self._tab_widget)
        layout.addWidget(self._button_box)
        self.setLayout(layout)

    def _connect_signals(self):
        """
        Connect all signals and slots of the dialog.

        As a bare minimum, the signals of the individual buttons need to be
        connected to some slot. In case of a single "Close" button,
        there is a special (not necessarily intuitive) signal to be connected:

        .. code-block::

            self._button_box.rejected.connect(self.reject)

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        self._button_box.rejected.connect(self.reject)

    def _create_about_text(self):
        package_metadata = metadata.metadata(self.package_name)
        text = string.Template(ABOUT_STRING)
        substitutions = {
            "package_name": self.package_name,
            "package_version": package_metadata["Version"],
            "description": package_metadata["Summary"] or "Lorem ipsum...",
            "website": package_metadata["Home-page"] or "http://example.org/",
            "license": package_metadata["License"],
        }
        return text.substitute(substitutions)

    def _create_authors_text(self):
        package_metadata = metadata.metadata(self.package_name)
        text = string.Template(AUTHOR_STRING)
        author_names = "<li>John Doe</li>\n"
        if "Author" in package_metadata:
            author_names = [
                f"<li>{name}</li>\n"
                for name in package_metadata["Author"].split(",")
            ]
        authors = f"<ul>\n{author_names[0]}</ul>\n"
        if "Author-email" in package_metadata:
            email = package_metadata["Author-email"]
        else:
            email = "doe@example.net"
        substitutions = {
            "package_name": self.package_name,
            "authors": authors,
            "email": email,
            "license": package_metadata["License"],
        }
        return text.substitute(substitutions)

    def _create_debug_info_text(self):
        package_metadata = metadata.metadata(self.package_name)
        text = string.Template(DEBUG_INFO_STRING)
        substitutions = {
            "package_name": self.package_name,
            "package_version": package_metadata["Version"],
            "os": platform.system(),
            "architecture": platform.machine(),
            "kernel": platform.release(),
            "python_version": platform.python_version(),
            "pyside6_version": metadata.metadata("PySide6")["Version"],
            "all_packages": self._package_list(),
        }
        return text.substitute(substitutions)

    @staticmethod
    def _package_list():
        """
        Return list of all packages currently installed with version number.

        There are several ways to get the result of "pip list"
        programmatically from within Python. However, getting the version
        numbers as well seems to require using the deprecated
        ``pkg_resources``, as ``pkg_resources.working_set`` seems to have
        no replacement in other modules. Hence, we rely here on calling
        "pip list" directly from the command line and catching the output.

        The output is reformatted for use in an HTML context. Hence,
        the method in its present form is not a general-purpose function.

        Returns
        -------
        package_list : :class:`str`
            List of all packages currently installed

        """
        args = [sys.executable, "-m", "pip", "list"]
        process = subprocess.run(  # noqa
            args,
            check=True,
            capture_output=True,
        )
        output = process.stdout.decode().split("\n")[2:]
        package_list = "<br />\n".join(
            [": ".join(package.split()[0:2]) for package in output if output]
        )
        return package_list


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    app.setOrganizationName("qtbricks")
    app.setOrganizationDomain("example.org")
    app.setApplicationName("Demo application")
    app.setWindowIcon(QtGui.QIcon(qtbricks.utils.image_path("icon.svg")))

    dialog = AboutDialog(package_name="qtbricks")
    dialog.exec()
    del app
