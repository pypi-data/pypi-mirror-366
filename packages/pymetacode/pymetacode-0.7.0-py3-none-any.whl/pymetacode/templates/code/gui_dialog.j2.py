"""
Dialog for ...

**Purpose:** ...

**Design principles:** The dialog should be as self-contained and
self-consistent as possible...

**Limitations:** ...


Some notes for developers
=========================

There are two general types of dialogs: modal and modeless. While a modal
dialog stays in front of the parent window and does not allow the user to
interact with the parent until the dialog is closed, a modeless dialog is
more independent and allows for interacting with the parent window. For
further details, see the documentation for the
:class:`PySide6.QtWidgets.QDialog` class.

Message boxes are typical examples of modal dialogs, whereas the
search&replace dialog of a text editor is a prime example of a modeless
dialog.

For simple messages, there is usually no need to create a separate dialog
class, as Qt comes equipped with a series of standard dialogs. Have a look
at :class:`PySide6.QtWidgets.QMessageBox` for details.
"""

from PySide6 import QtWidgets


class {{ class.name }}(QtWidgets.QDialog):
    """
    One sentence (on one line) describing the class.

    More description comes here...


    Parameters
    ----------
    parent : :class:`PySide6.QtWidgets.QWidget`
        Parent of the dialog

        The dialog will usually be centered upon the parent.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Define all UI elements (widgets) here as non-public attributes
        self._dialog_buttons = QtWidgets.QDialogButtonBox.Close
        self._button_box = QtWidgets.QDialogButtonBox(self._dialog_buttons)

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
        self._set_widget_properties()
        self._set_layout()
        self._connect_signals()

    def _set_widget_properties(self):
        """
        Set the widgets of all the UI components.

        Usually, a widget will contain a number of other widgets whose
        properties need to be set initially. This is the one central place
        to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        self.setWindowTitle("Dialog")

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
