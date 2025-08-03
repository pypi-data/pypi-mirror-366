"""
General utils of the qtbricks package.

Mostly small functions that are more general and get used in the other
modules. Some of these functions may be useful for packages importing
qtbricks, hence generally the individual functions are designed with
reusability beyond the qtbricks package in mind.
"""

import os

from PySide6 import QtWidgets, QtGui


def image_path(name="", image_dir="images", base_dir=""):
    """
    Return full path to a given image.

    Images, such as icons, are used in several places in GUIs, but are
    usually stored in a separate directory. Hence, a generic function
    returning the full path is both, convenient and modular.

    If the internal organisation of images changes, only this code needs to
    be adapted.

    For use with own packages, you may want to set the parameter
    ``base_dir`` accordingly.

    Parameters
    ----------
    name : :class:`str`
        Name of the icon

    image_dir : :class:`str`
        Directory containing the icons

        Default: "images"

    base_dir : :class:`str`
        Directory used as base for the icons directory

        Useful in cases where the function should be used outside this
        package, *i.e.* with a different base directory for the images.

        Default: ``os.path.dirname(__file__)``

    Returns
    -------
    path : :class:`str`
        Full path to the icon

    """
    base_dir = base_dir or os.path.dirname(__file__)
    path = os.path.join(base_dir, image_dir, name)
    return path


# pylint: disable=too-many-arguments
def create_button(
    text="", slot=None, shortcut="", icon="", checkable=False, tooltip=""
):
    """
    Conveniently create a button.

    Parameters
    ----------
    text : :class:`str`
        The text appearing on the button.

        In case you provide both, icon (see below) and text, both are
        displayed. If you intend to only present an icon, set the text to an
        empty string.

        Default: empty

    slot : :py:obj:`function <types.FunctionType>`
        The slot to connect to the button.

    shortcut : :class:`str`
        The keyboard shortcut used for the action connected to the button.

        Default: empty

    icon : :class:`str`
        The name of the icon file to be used.

        If empty, no icon will be displayed.

        For enhanced modularity, do *not* provide paths, but only icon file
        names, as the full path will get looked up using the
        :func:`icon_path` function.

    checkable : :class:`bool`
        Whether the button is checkable, *i.e.*, displays its current state.

    tooltip : class:`str`
        Tooltip to be displayed for the button.

        Sensible tooltips go a long way towards a user-friendly GUI.

    Returns
    -------
    button : :class:`QtWidgets.QPushButton`

    """
    button = QtWidgets.QPushButton(text)
    if icon:
        button.setIcon(QtGui.QIcon(image_path(icon)))
    if shortcut:
        button.setShortcut(shortcut)
    if tooltip:
        if shortcut:
            tooltip = "\n".join([tooltip, f"Keyboard shortcut: {shortcut}"])
        button.setToolTip(tooltip)
    if slot:
        if checkable:
            button.toggled.connect(slot)
        else:
            button.pressed.connect(slot)
    if checkable:
        button.setCheckable(True)
    return button


def make_buttons_in_group_uncheckable(buttongroup):
    """
    Allow all buttons in exclusive button group to be unchecked.

    By default, an exclusive button group does not allow to uncheck all
    buttons by clicking the selected button, but only to select an
    alternative button, once one button has been clicked.

    Parameters
    ----------
    buttongroup : :class:`QtWidgets.QButtonGroup`
        Button group to operate on

    """
    buttongroup.buttonPressed.connect(
        lambda button: button.group().setExclusive(not button.isChecked())
    )
    buttongroup.buttonClicked.connect(
        lambda button: button.group().setExclusive(True)
    )


class IntValidator(QtGui.QIntValidator):
    """
    Integer validator actually fixing input that is beyond the boundaries.

    The standard Qt integer validator (actually the base class of this class)
    has an empty `fixup` method. Here, the fixup sets text exceeding the set
    boundaries to the respective boundary.

    Examples
    --------
    A typical use case of the :class:`IntValidator` class are
    :class:`PySide6.QtWidgets.QLineEdit` widgets:

    .. code-block::

        line_edit = QtWidgets.QLineEdit()
        validator = IntValidator(0, 42)
        line_edit.setValidator(validator)

    In this case, if the user enters values smaller than 0 or larger than 42,
    the actual value of the line edit will be set to the respective boundary.

    """

    def fixup(self, value):
        """
        Attempt to change input to be valid according to the validator rules.

        In case the value exceeds the lower or upper boundary defined by
        :attr:`bottom` or :attr:`top`, the respective boundary is returned.

        Parameters
        ----------
        value : :class:`str`
            Value to be fixed.

        Returns
        -------
        value : :class:`str`
            Value that has been fixed.

        """
        if int(value) > self.top():
            value = str(self.top())
        if int(value) < self.bottom():
            value = str(self.bottom())
        return value
