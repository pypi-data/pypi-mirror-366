"""
Command-line interface (CLI) module of the pymetacode package.

While the actual code creating code is contained in the
:mod:`pymetacode.coding` module, for most day-to-day business, programmers
need a simple interface they can use without need to write code that writes
code. Therefore, a key concept of the pymetacode package is an intuitive
command-line interface (CLI) that gets used from within a terminal - the
natural habitat of most programmers.


General usage
=============

The package provides a command ``pymeta`` (by means of a console-script
entry point) available from the command line given the pymetacode package is
installed. This command comes with built-in help and follows a rather simple
scheme:

.. code-block:: bash

    pymeta <command> <option1> ...

The number of options available and required depends on the type of command
used. The design goal is an intuitive and robust user interface with
feedback and help built-in and a "grammar" that feels natural. For more
details, see the "Examples" section of the :class:`pymetacode.cli.Cli` class
documentation.


A bit of background
===================

The first (and necessary) step for using the CLI is to create a
configuration file, typically by issuing the following command on the terminal:

.. code-block:: bash

    pymeta write config to mypackage_config.yaml

After having changed all values within this configuration file according to
the specific needs, one can continue to create a package, or alternatively,
if the package should exist already, move the configuration file to the root
directory of this existing package and rename it to ``.package_config.yaml``
(note the leading "."). This is the (only) way the CLI has access to
necessary information, such as the package name, and this is as well the
reason why each of the commands for adding modules, classes, and functions
need to be issued from the *root directory* of your package.


Module documentation
====================

"""

import logging
import os.path
import shutil
import sys

from pymetacode import coding, configuration


logger = logging.getLogger(__name__)


class Cli:
    """
    The actual command-line interface (CLI) of the pymetacode package.

    More description comes here...


    Attributes
    ----------
    command : :class:`str`
        The actual command to be executed.

        In case of using the CLI from the terminal, the first argument.

    options : :class:`list`
        A list of options for the command.

        In case of using the CLI from the terminal, all arguments from the
        second argument on.

    conf_file : :class:`str`
        The name the config file gets written to using the ``write`` command.

        Default: "package_config.yaml"


    Examples
    --------
    The following examples demonstrate how to use the CLI from the terminal,
    rather than how to use this class programmatically.

    The first step when creating a new package is to write a config file
    that can be filled with sensible content afterwards:

    .. code-block:: bash

        pymeta write config to mypackage_config.yaml

    This would write the default configuration to "mypackage_config.yaml".
    Change all values in this file according to your needs. Afterwards,
    you can create the basic structure of your new project:

    .. code-block:: bash

        pymeta create package from mypackage_config.yaml

    Now, you have a complete package that is installable and deployable.
    Next is to add some modules to your newly created package. All following
    commands need to be issued from *within* the root directory of your new
    package.

    .. code-block:: bash

        pymeta add module mymodule

    will add a module "mymodule" to your package, together with a
    "test_mymodule" module in the "tests" subdirectory. And even better,
    the API documentation will be updated as well for you.

    Time to add a class to your new module:

    .. code-block:: bash

        pymeta add class MyClass to mymodule

    Here, again, the class will be added to "mymodule" and a test class
    added to "test_mymodule". Similarly, you can add a function:

    .. code-block:: bash

        pymeta add function my_function to mymodule

    Again, function and test class will be added to your package.

    And if you are in doubt how to use the ``pymeta`` command, we've got you
    covered:

    .. code-block:: bash

        pymeta
        pymeta help

    are two equivalent commands that display some general help. Furthermore,
    you can get help for particular commands, too:

    .. code-block:: bash

        pymeta help create

    would provide you with help specifically for the "create" command.
    Furthermore, if you make a mistake, usually, the context-specific help
    will be displayed for you as well.

    """

    def __init__(self):
        self.command = ""
        self.options = []
        self.conf_file = "package_config.yaml"
        self._command_name = "pymeta"

    def call(self, command="", options=None):
        """
        Execute a given command with the given options (if any).

        Parameters
        ----------
        command : :class:`str`
            The actual command to be executed.

            In case of using the CLI from the terminal, the first argument.

        options : :class:`list`
            A list of options for the command.

            In case of using the CLI from the terminal, all arguments from the
            second argument on.

        """
        self.command = command
        self.options = options
        if not self.command:
            self._print_help()
        else:
            method = f"_command_{self.command}"
            if hasattr(self, method):
                getattr(self, method)()
            else:
                self._print_help()

    def _command_write(self):
        if (
            not self.options
            or not self.options[0] == "config"
            or (len(self.options) > 2 and not self.options[1] == "to")
        ):
            self._print_write_help()
            return
        conf = configuration.Configuration()
        if len(self.options) == 3:
            self.conf_file = self.options[2]
        conf.to_file(self.conf_file)
        logger.info('Wrote configuration to file "%s"', self.conf_file)

    def _command_create(self):
        if (
            not self.options
            or not self.options[0] == "package"
            or not self.options[1] == "from"
        ):
            self._print_create_help()
            return
        conf_file = self.options[2]
        conf = configuration.Configuration()
        conf.from_file(conf_file)
        creator = coding.PackageCreator()
        creator.configuration = conf
        creator.name = conf.package["name"]
        creator.create()
        shutil.copyfile(
            conf_file,
            os.path.join(conf.package["name"], ".package_config.yaml"),
        )
        logger.info(
            'Created package "%s" in directory "%s"',
            conf.package["name"],
            conf.package["name"],
        )

    def _command_add(self):
        if not self.options:
            self._print_add_help()
            return
        method = f"_command_add_{self.options[0]}"
        if hasattr(self, method):
            conf_file = ".package_config.yaml"
            conf = configuration.Configuration()
            conf.from_file(conf_file)
            getattr(self, method)(conf)
        else:
            self._print_add_help()

    def _command_add_module(self, conf):
        creator = coding.ModuleCreator()
        creator.configuration = conf
        creator.name = self.options[1]
        creator.create()
        logger.info('Added module "%s"', creator.name)

    def _command_add_class(self, conf):
        creator = coding.ClassCreator()
        creator.configuration = conf
        creator.name = self.options[1]
        creator.module = self.options[3]
        creator.create()
        logger.info(
            'Added class "%s" to module "%s"', creator.name, creator.module
        )

    def _command_add_function(self, conf):
        creator = coding.FunctionCreator()
        creator.configuration = conf
        creator.name = self.options[1]
        creator.module = self.options[3]
        creator.create()
        logger.info(
            'Added function "%s" to module "%s"', creator.name, creator.module
        )

    def _command_add_gui(self, conf):
        creator = coding.GuiCreator()
        creator.configuration = conf
        creator.create()
        logger.info("Added GUI")

    def _command_add_window(self, conf):
        creator = coding.GuiWindowCreator()
        creator.name = self.options[1]
        creator.configuration = conf
        creator.create()
        logger.info("Added %s to GUI", creator.name)

    def _command_add_subpackage(self, conf):
        creator = coding.SubpackageCreator()
        creator.name = self.options[1]
        creator.configuration = conf
        creator.create()
        logger.info('Added subpackage "%s"', creator.name)

    def _command_add_widget(self, conf):
        creator = coding.GuiWidgetCreator()
        creator.name = self.options[1]
        creator.configuration = conf
        creator.create()
        logger.info("Added %s to GUI", creator.name)

    def _command_add_dialog(self, conf):
        creator = coding.GuiDialogCreator()
        creator.name = self.options[1]
        creator.configuration = conf
        creator.create()
        logger.info("Added %s to GUI", creator.name)

    def _command_help(self):
        if not self.options:
            self._print_help()
        else:
            help_method = f"_print_{self.options[0]}_help"
            getattr(self, help_method)()

    def _print_help(self):
        help_text = """
        General usage:
            command_name <command> <option1> ...

        Possible commands are:
            write
            add
            create
            help

        To get more details for a command, type: 
            command_name help <command> 
        """
        self._output_help_text(help_text)

    def _print_write_help(self):
        help_text = """
        Usage for write command:
            command_name write <item> to <destination>
            command_name write <item>

        Possible items are:
            config

        Examples:
            command_name write config to package_config.yaml

            Writes a configuration file with empty values to 
            "package_config.yaml"

        Note: The default filename for the configuration file if not 
        provided is "package_config.yaml".          
        """
        self._output_help_text(help_text)

    def _print_create_help(self):
        help_text = """
        Usage for create command:
            command_name create package from <config>

        Prerequisite for this command is an existing configuration stored in 
        the file given as <config> (a YAML file). Use

            command_name write config to <filename>

        to create a config file in YAML format and populate the values 
        according to your needs. 
        """
        self._output_help_text(help_text)

    def _print_add_help(self):
        help_text = """
        Usage for add command:
            command_name add <item>
            command_name add <item> <name>
            command_name add <item> <name> to <module>
            command_name add window <window>
            command_name add widget <widget>

        Possible items are:
            subpackage
            module
            class
            function
            gui
            window
            widget

        For "class" and "function", you need to provide the name of an 
        existing module these items should be added to.

        For "window" and "widget", you need to provide a name for the 
        GUI window or widget, respectively.
        """
        self._output_help_text(help_text)

    def _output_help_text(self, help_text=""):
        print(
            help_text.replace("        ", "").replace(
                "command_name", self._command_name
            )
        )


def cli():
    """
    Console entry point for the command-line interface.

    The actual handling of the commands is entirely done within the
    :class:`pymetacode.cli.Cli` class, but this function serves as entry
    point for the console script, providing the ``pymeta`` command on the
    command line.

    """
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    cli_object = Cli()
    if len(sys.argv) == 1:
        cli_object.call()
    elif len(sys.argv) == 2:
        cli_object.call(command=sys.argv[1])
    else:
        cli_object.call(command=sys.argv[1], options=sys.argv[2:])
