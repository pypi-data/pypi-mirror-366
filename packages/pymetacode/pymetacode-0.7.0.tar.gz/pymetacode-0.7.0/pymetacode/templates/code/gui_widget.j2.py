"""
Widget for ...

**Purpose:** ...

**Design principles:** The dialog should be as self-contained and
self-consistent as possible...

**Limitations:** ...

"""

from PySide6 import QtWidgets


class {{ class.name }}(QtWidgets.QWidget):
    """
    One sentence (on one line) describing the class.

    More description comes here...


    Attributes
    ----------
    attr : :class:`None`
        Short description

    """

    def __init__(self):
        super().__init__()

        # Define all UI elements (widgets) here as non-public attributes

        self._setup_ui()
        self._update_ui()

    def _setup_ui(self):
        """
        Set up the widget.

        This method takes care of setting up all the elements of the widget.
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

    def _update_ui(self):
        """
        Update all the elements of the widget.

        This is the once central place taking care of updating all the
        user-facing elements of your widget.
        """
        pass

    def _set_widget_properties(self):
        """
        Set the widgets of all the UI components.

        Usually, a widget will contain a number of other widgets whose
        properties need to be set initially. This is the one central place
        to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        pass

    def _set_layout(self):
        """
        Lay out the elements of the widget.

        Usually, a widget will contain a number of other widgets that need
        to be laid out in some way. This is the central place to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        pass

    def _connect_signals(self):
        """
        Connect all signals and slots of the widget.

        To have a widget perform its tasks interactively, it will usually
        define signals and slots that need to be connected. This is the
        central place to do this.

        A requirement is to define all widgets as non-public attributes in
        the class constructor.
        """
        pass
