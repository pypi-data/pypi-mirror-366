"""
Configuration handling of the pymetacode package.

Key to the rather simplistic and user-friendly command-line interface (CLI)
of the pymetacode package is a configuration stored within the
package root directory and read by all the code generators residing in the
:mod:`pymetacode.coding` module.

The :class:`Configuration` class provides the necessary functionality for
creating a default configuration file as well as for reading the
configuration from a file for use with the code generators.

"""

import datetime

import yaml

from pymetacode import utils


LICENSES = (
    "BSD",
    "GPLv3",
)


class Configuration(utils.ToDictMixin):
    """
    Configuration used for generating code.

    A necessary prerequisite for all the code generators is a minimal set of
    configuration values that are persistently stored in a file within the
    project root directory and read from there accordingly.

    The class provides the unique place to structure this configuration.


    Attributes
    ----------
    package : :class:`dict`
        Configuration on the package level

        The following fields are currently available:

        name : :class:`str`
            Name of the package, following :pep:`8` conventions

        author : :class:`str`
            Name of the author(s) of the package

            In case of more than one author, use a comma-separated list

        author_email : :class:`str`
            Email address(es) of the author(s) of the package

            In case of more than one author, use a comma-separated list

        year : :class:`str`
            Year the package has been created

            Can be a span of years, but will typically be a single date
            when a package is created. (Change afterwards if needed.)

        description : :class:`str`
            Short description of the package, typically in one short sentence.

            Gets used as first line in the README and documentation index,
            and is used as package description on PyPI. This is separate
            from the long description (in the ``setup.py`` file, this is
            usually the contents of the README file).

        urls : :class:`dict`
            A series of different URLs, as set in the ``setup.py`` file.

            These URLs are used on PyPI, hence choose with care.
            Typically, you would set ``main`` (the homepage of the package),
            ``documentation``, and ``source`` (GitHub or else).

        keywords : :class:`list`
            List of keywords (strings) describing the package.

            These keywords are used, *i.a.*, on PyPI to find your package.
            Hence, choose with care.

        install_requires : :class:`list`
            List of packages required by your package.

            This should be kept at an absolute minimum. Note that many
            packages often used as dependencies, such as numpy or
            matplotlib, come with many further dependencies.

            Within the ``setup.py`` file, additional requirements for
            documentation (``docs``) and development (``dev``) are set,
            but these are only special requirements for developers.

            If you want to create a GUI (see below), the requirements are
            automatically added for you as well.

        license : :class:`str`
            Abbreviation of the license of your package.

            Currently, only two licenses are supported: "BSD" and "GPLv3".
            The default license, if none is given, is "BSD".

            Note that choosing a license here will copy the corresponding
            license text to the file ``LICENSE`` in your project root
            directory.

            .. versionadded:: 0.5

    documentation : :class:`dict`
        Configuration regarding the documentation of the package

        The following fields are currently available:

        logo : :class:`str`
            Filename of a logo file.

            If no logo is provided, no logo will be added to your
            documentation.

        favicon : :class:`str`
            Filename of the favicon file.

            A favicon is used as icon in your webbrowser and should be
            provided as Windows Icon file.

        language : :class:`str`
            Lower-case abbreviation of the language of your documentation.

            Two-letter abbreviations are used, and default is "en". Note
            that current versions of Sphinx require a language to be set
            in the configuration file.

    options : :class:`dict`
        Configuration regarding the metacode

        .. versionadded:: 0.3

        The following fields are currently available:

        logging : :class:`bool`
            Whether to add logging to your package.

            Default: False

        git : :class:`bool`
            Whether to instantiate a git repository for your package.

            It is *highly recommended* to use git/version control for
            developing any package. If you set this option to true,
            not only will a git repository be initialised for your
            package, but appropriate pre-commit hooks installed that take
            care of automatically incrementing the version number and
            auto-formatting your code on every commit.

            Default: False

        gui : :class:`bool`
            Whether to add a GUI to your package.

            Sometimes, GUIs are a necessary part of a package. If you know
            already when creating the package that you will need a GUI,
            set this option to true. This will not only create the entire
            directory structure for your GUI, but set a few things in
            ``setup.py`` and elsewhere accordingly.

            Default: False

    gui : :class:`dict`
        Configuration regarding the GUI

        .. versionadded:: 0.4

        The following fields are currently available:

        splash : :class:`bool`
            Whether to add a splash screen to your GUI main window.

            Default: True

        organisation : :class:`str`
            Name of the organisation the GUI belongs to.

            This setting is used by Qt to store application settings.
            Hence, it is crucial to set this to a sensible value.

        domain : :class:`str`
            Domain name of the organisation the GUI belongs to.

            This setting is used by Qt in some operating systems to store
            application settings. Hence, it is crucial to set this to a
            sensible value.

    Raises
    ------
    ValueError
        Raised if no dict is provided.


    Examples
    --------
    The following examples demonstrate how to use the CLI from the terminal,
    rather than how to use this class programmatically.

    The first step when creating a new package is to write a config file
    that can be filled with sensible content afterwards:

    .. code-block:: bash

        pymeta write config to mypackage_config.yaml

    This would write the default configuration to "mypackage_config.yaml".
    Change all values in this file according to your needs.


    .. versionchanged:: 0.3
        New property "options", moved key "git" to property "options"

    .. versionchanged:: 0.4
        New property "gui"

    .. versionchanged:: 0.5
        New key "license" in property "package"

    """

    def __init__(self):
        super().__init__()
        self.package = {
            "name": "",
            "author": "",
            "author_email": "",
            "year": datetime.date.strftime(datetime.date.today(), "%Y"),
            "description": "",
            "urls": {
                "main": "",
                "documentation": "",
                "source": "",
            },
            "keywords": [],
            "install_requires": [],
            "license": "BSD",
        }
        self.documentation = {
            "logo": "",
            "favicon": "",
            "language": "en",
        }
        self.options = {
            "logging": False,
            "git": False,
            "gui": False,
        }
        self.gui = {
            "splash": True,
            "organisation": "",
            "domain": "",
        }

    def to_dict(self):
        """
        Create dictionary containing public attributes of an object.

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        self._check_values()
        return super().to_dict()

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.

        Raises
        ------
        ValueError
            Raised if no dict is provided.

        """
        if not dict_:
            raise ValueError
        for key, value in dict_.items():
            if hasattr(self, key) and value:
                if isinstance(getattr(self, key), list):
                    if isinstance(value, list):
                        for element in value:
                            getattr(self, key).append(element)
                    else:
                        getattr(self, key).append(value)
                elif isinstance(getattr(self, key), dict):
                    getattr(self, key).update(value)
                else:
                    setattr(self, key, value)
        self._check_values()

    def to_file(self, name=""):
        """
        Write to YAML file.

        Parameters
        ----------
        name : :class:`str`
            Name of the YAML file to write to.

        """
        with open(name, "w+", encoding="utf8") as file:
            yaml.dump(self.to_dict(), file, sort_keys=False)

    def from_file(self, name=""):
        """
        Read from YAML file.

        Parameters
        ----------
        name : :class:`str`
            Name of the YAML file to read from.

        """
        with open(name, "r", encoding="utf8") as file:
            dict_ = yaml.load(file, Loader=yaml.SafeLoader)
        self.from_dict(dict_)

    def _check_values(self):
        if (
            "license" in self.package
            and self.package["license"] not in LICENSES
        ):
            raise ValueError
