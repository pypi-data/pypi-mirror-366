"""
Small Qt widgets for general use with Qt GUIs.

There is a number of small widgets that can be created with a few lines of code
from existing Qt widgets. However, it is often convenient to have these widgets
as separate classes.

Typical examples include horizontal and vertical lines that are basically
one-dimensional instances of QFrame.


Widgets
=======

Currently, the following widgets are contained in this module:

* :class:`QHLine`

    Horizontal line for Qt GUIs

* :class:`QVLine`

    Vertical line for Qt GUIs


Module documentation
====================

"""

from PySide6 import QtWidgets


class QHLine(QtWidgets.QFrame):
    """
    Horizontal line for Qt GUIs.

    Sometimes there is the need to add a horizontal line to a Qt layout.
    As a horizontal line is nothing else than a QFrame object, this class
    provides a convenient shortcut.

    Inspiration taken from Michael Leonard via StackOverflow:
    https://stackoverflow.com/a/41068447

    Examples
    --------
    Suppose you want to add a horizontal line to your grid layout

    .. code-block::

        from PySide6 import QtWidgets
        import qtbricks


        layout = QtWidgets.QGridLayout()
        layout.addWidget(qtbricks.widgets.QHLine(), 4, 0, 1, 2)


    Here, the horizontal line will span two columns of your grid layout.


    See Also
    --------
    :class:`QVLine`
        Vertical line for Qt GUIs

    """

    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLine(QtWidgets.QFrame):
    """
    Vertical line for Qt GUIs.

    Sometimes there is the need to add a vertical line to a Qt layout.
    As a horizontal line is nothing else than a QFrame object, this class
    provides a convenient shortcut.

    Inspiration taken from Michael Leonard via StackOverflow:
    https://stackoverflow.com/a/41068447


    Examples
    --------
    Suppose you want to add a vertical line to your grid layout

    .. code-block::

        from PySide6 import QtWidgets
        import qtbricks


        layout = QtWidgets.QGridLayout()
        layout.addWidget(qtbricks.widgets.QVLine(), 4, 0, 2, 1)


    Here, the vertical line will span two rows of your grid layout.


    See Also
    --------
    :class:`QHLine`
        Horizontal line for Qt GUIs

    """

    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
