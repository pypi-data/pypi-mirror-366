"""
{{ package.name }} app.

This module provides the high-level interface to the app and a function that
gets wired up as "gui_script" entry point in the ``setup.py``.
"""

import os
import sys

from PySide6 import QtWidgets, QtGui
{%- if gui.splash %}
from PySide6.QtCore import Qt
{%- endif %}

import qtbricks.utils

from {{ package.name }}.gui import mainwindow


{% if gui.splash -%}
def splash_screen():
    """
    Create a splash screen normally used during GUI startup.

    Depending on the complexity of a GUI main window, startup may take some
    time. Hence, it is good practice to present the user with a splash
    screen as immediate feedback that something is happening in the background.

    Usually, a splash screen will present an image and perhaps a message.

    Returns
    -------
    splash : :class:`PySide6.QtWidgets.QSplashScreen`
        Splash screen object

        Necessary to interact with the splash screen, *e.g.*, set messages
        and finally remove it from the screen.

    """
    splash = QtWidgets.QSplashScreen(
        QtGui.QPixmap(
            qtbricks.utils.image_path(
                "splash.svg", base_dir=os.path.dirname(__file__)
            )
        )
    )
    splash.show()
    return splash


{% endif -%}
def main():
    """
    Entry point for the GUI application.

    This function serves as main entry point to the GUI application and gets
    added as "gui_script" entry point. Additionally, the essential
    aspects of the (Qt) application are set that are relevant for saving and
    restoring settings, as well as the window icon.
    """
    app = QtWidgets.QApplication(sys.argv)
    {% if gui.splash -%}
    splash = splash_screen()

    {% endif -%}
    app.setOrganizationName("{{ gui.organisation }}")
    app.setOrganizationDomain("{{ gui.domain }}")
    app.setApplicationName("{{ package.name }}")
    app.setWindowIcon(
        QtGui.QIcon(
            qtbricks.utils.image_path(
                "icon.svg", base_dir=os.path.dirname(__file__)
            )
        )
    )
    window = mainwindow.MainWindow()
    window.show()
    {% if gui.splash -%}

    alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
    splash.showMessage("Loaded main window", alignment=alignment)
    splash.finish(window)

    {% endif -%}
    app.exec()


if __name__ == "__main__":
    main()
