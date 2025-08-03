"""
Auxiliary functionality used by other modules of the pymetacode package.

To avoid circular dependencies, this module does *not* depend on any other
modules of the pymetacode package, but it can be imported into every other
module.

As naturally, a utils module tends to be a bit messy, the different tools
available are listed below according to more general categories.


Files and I/O
=============

* :func:`ensure_file_exists`

  Create an (empty) file if it does not exist already.

* :func:`get_data_from_pkg_resources`

  Obtain contents from a non-code file stored within the package.

* :func:`change_working_dir`

  Context manager for temporarily changing the working directory.

* :func:`make_executable`

  Make a file executable, *i.e.*, set its executable flag.


String manipulation
===================

* :func:`camel_case_to_underscore`

  Change string from camel case to using underscores.

* :func:`underscore_to_camel_case`

  Change string from underscores to using camel case.


Manipulating file contents
==========================

Part of metacoding is to manipulate file contents after the files have
been generated using templates. Hence, it is sometimes not easily possible
to parse the entire file into a sensible structure. Therefore, rather
complex search and insert operations need to be performed.

The following functions exist currenty:

* :func:`add_to_toctree`

  Add entries to toctrees in documentation generated via Sphinx


Helper classes
==============

* :class:`ToDictMixin`

  Mixin class for returning all public attributes as dict.

* :class:`Template`

  Wrapper for using the template engine (Jinja2).


Module documentation
====================
"""

import collections
import contextlib
import datetime
import os
import pkgutil
import re

import platformdirs
import jinja2


def ensure_file_exists(name=""):
    """
    Create an (empty) file if it does not exist already.

    This is similar to the "touch" command from unixoid operating systems,
    although it does *not* change the timestamp of the file.

    Parameters
    ----------
    name : :class:`str`
        Name of the file


    Raises
    ------
    ValueError
        Raised if no filename is given.

    """
    if not name:
        raise ValueError("No filename given.")
    with open(name, "a", encoding="utf8"):
        pass


def get_package_data(name="", directory="templates"):
    """
    Obtain contents from a non-code file ("package data").

    There are generally three places where package data can be stored:

    #. Within the package,

    #. In the site-wide data directory (with the package name as subdirectory),

    #. In the user-specific data directory
       (with the package name as subdirectory).

    The location of the latter two is specific to the operating system used.
    Here, the `platformdirs package <https://pypi.org/project/platformdirs/>`_ is
    used, providing paths for all major platforms (Windows, macOS, Linux/Unix).

    The given file is searched for in the user-specific data directory
    first, followed by the site-wide data directory. Only if it cannot be
    found in either place, as a fallback the package itself is queried.
    Thus, files under control of the individual user take precedence over
    site-wide files and files distributed with the package.

    A note to obtaining data from the distributed package: Rather than
    manually playing around with paths relative to the package root
    directory, contents of non-code files need to be obtained in a way that
    works with different kinds of package installation.

    Note that in Python, only files within the package, *i.e.* within the
    directory where all the modules are located, can be accessed, not files
    that reside on the root directory of the package.

    .. note::

        In case you would want to get package data from a package different
        than pymetacode, you can prefix the name of the file to retrieve with
        the package name, using the '@' as a separator.

        Suppose you would want to retrieve the file ``__main__.py`` file
        from the "pip" package (why should you?):

        .. code-block::

            get_package_data('pip@__main__.py', directory='')

        This would return the contents of this file. Of course, the sequence
        of directories as described above is used here as well (user data
        directory, site data directory, package directory).


    Parameters
    ----------
    name : :class:`str`
        Name of the file whose contents should be accessed.

        In case the file should be retrieved from a different package,
        the package name can be prefixed, using '@' as a separator.

    directory : :class:`str`
        Directory within the package where the files are located.

        Default: "templates"

    Returns
    -------
    contents : :class:`str`
        String containing the contents of the non-code file.


    .. versionchanged:: 0.3
        Name can be prefixed with package using '@' as separator

    """
    if not name:
        raise ValueError("No filename given.")
    package = __package__
    if "@" in name:
        package, name = name.split("@")
    path = os.path.join(package, os.path.sep.join(directory.split("/")), name)
    if os.path.exists(os.path.join(platformdirs.user_data_dir(), path)):
        with open(
            os.path.join(platformdirs.user_data_dir(), path), encoding="utf8"
        ) as file:
            contents = file.read()
    elif os.path.exists(os.path.join(platformdirs.site_data_dir(), path)):
        with open(
            os.path.join(platformdirs.site_data_dir(), path), encoding="utf8"
        ) as file:
            contents = file.read()
    else:
        contents = pkgutil.get_data(
            package, "/".join([directory, name])
        ).decode()
    return contents


class ToDictMixin:
    """
    Mixin class for returning all public attributes as dict.

    Sometimes there is the need to either exclude public attributes (in case
    of infinite loops created by trying to apply ``to_dict`` in this case)
    or to add (public) attributes, particularly those used by getters and
    setters that are otherwise not included.

    To do so, there are two non_public attributes of this class each class
    inheriting from it will be able to set as well:

    * :attr:`_exclude_from_to_dict`
    * :attr:`_include_in_to_dict`

    The names should be rather telling. For details, see below.

    Attributes
    ----------
    _exclude_from_to_dict : :class:`list`
        Names of (public) attributes to exclude from dictionary

        Usually, the reason to exclude public attributes from being added to
        the dictionary is to avoid infinite loops, as sometimes an object
        may contain a reference to another object that in turn references back.

    _include_in_to_dict : :class:`list`
        Names of (public) attributes to include into dictionary

        Usual reasons for actively including (public) attributes into the
        dictionary are those attributes accessed by getters and setters and
        hence not automatically included in the list otherwise.


    .. versionchanged:: 0.4
        Return dict rather than collections.OrderedDict, as dicts are
        order-preserving since Python 3.7

    """

    def __init__(self):
        self._exclude_from_to_dict = []
        self._include_in_to_dict = []

    def to_dict(self):
        """
        Create dictionary containing public attributes of an object.

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        result = self._traverse_dict(self.__dict__)
        return result

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            if (
                str(key).startswith("_")
                or str(key) in self._exclude_from_to_dict
            ):
                pass
            else:
                output[key] = self._traverse(key, value)
        for key in self._include_in_to_dict:
            output[key] = self._traverse(key, getattr(self, key))
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            result = value.to_dict()
        elif isinstance(value, (dict, collections.OrderedDict)):
            result = self._traverse_dict(value)
        elif hasattr(value, "__dict__"):
            result = self._traverse_dict(value.__dict__)
        elif isinstance(value, list):
            result = [self._traverse(key, i) for i in value]
        elif isinstance(
            value, (datetime.datetime, datetime.date, datetime.time)
        ):
            result = str(value)
        else:
            result = value
        return result


@contextlib.contextmanager
def change_working_dir(path=""):
    """
    Context manager for temporarily changing the working directory.

    Sometimes it is necessary to temporarily change the working directory,
    but one would like to ensure that the directory is reverted even in case
    an exception is raised.

    Due to its nature as a context manager, this function can be used with a
    ``with`` statement. See below for an example.


    Parameters
    ----------
    path : :class:`str`
        Path the current working directory should be changed to.


    Examples
    --------
    To temporarily change the working directory:

    .. code-block::

        with change_working_dir(os.path.join('some', 'path')):
            # Do something that may raise an exception

    This can come in quite handy in case of tests.

    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def camel_case_to_underscore(name=""):
    """
    Change string from camel case to using underscores.

    According to PEP8, class names should follow camel case convention,
    whereas methods, functions, and variables should use underscores.

    Parameters
    ----------
    name : :class:`str`
        Name to be changed from camel case to using underscores.

    Returns
    -------
    name : :class:`str`
        Name changed from camel case to using underscores.

    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def underscore_to_camel_case(name=""):
    """
    Change string from underscores to using camel case.

    According to PEP8, class names should follow camel case convention,
    whereas methods, functions, and variables should use underscores.

    Parameters
    ----------
    name : :class:`str`
        Name to be changed from underscores to using camel case.

    Returns
    -------
    name : :class:`str`
        Name changed from underscores to using camel case.

    """
    name = "".join(char.capitalize() for char in name.split("_"))
    return name


class Template:
    """
    Wrapper for using the template engine (Jinja2).

    Dealing with templates requires a number of settings to be made, namely
    the source of the template, its name, the context (*i.e.*,
    the dictionary containing the variables to be replaced within the
    template), and the destination the rendered template should be output to.

    .. note::

        Regarding the path of a template, three different places are looked
        up, using the function :func:`get_package_data`: first in the user
        data directory, then in the site data directory, and finally within
        the package (distribution). For details see the description of the
        function :func:`get_package_data`.


    Attributes
    ----------
    path : :class:`str`
        Location where the template resides (see note above).

    template : :class:`str`
        Name of the template to be used.

        Relative to the :attr:`package_path`.

        In case you want to retrieve a template for a package different than
        pymetacode, prefix the template name with the package name,
        using '@' as a separator. See :func:`get_package_data` for details.

    context : :class:`dict`
        Key-value store of variables to be replaced within the template.

    destination : :class:`str`
        Name of the file the rendered template should be output to.


    Examples
    --------
    Probably the best way to use the class is to instantiate an object
    providing all necessary parameters:

    .. code-block::

        template = Template(
            path='some/relative/path/to/the/template',
            template='name_of_the_template',
            context=dict(),
            destination='name_of_the_file_to_output_rendered_template_to',
        )

    Afterwards, the respective command can be issued on the template,
    depending on whether the rendered template should be written or appended
    to the destination:

    .. code-block::

        template.create()
        template.append()

    """

    def __init__(self, path="", template="", context=None, destination=""):
        self.path = path
        self.template = template
        self.context = context
        self.destination = destination

    @property
    def environment(self):
        """
        Environment used by the template engine.

        Read-only property that gets automatically set from the class
        properties.

        Returns
        -------
        env : :class:`jinja2.Environment`
            Environment settings for the template engine.

        """
        env = jinja2.Environment(
            loader=jinja2.FunctionLoader(get_package_data),
            autoescape=True,
            keep_trailing_newline=True,
        )
        return env

    def render(self):
        """
        Render the template.

        Returns
        -------
        content : :class:`str`
            Rendered template.

        """
        self._add_rst_markup_to_context()
        template = self.environment.get_template(
            os.path.join(self.path, self.template)
        )
        return template.render(self.context)

    def create(self):
        """
        Write rendered template to a file.

        Note: If you need to *append* the rendered template to an existing
        file, you should use :meth:`append` instead.

        """
        with open(self.destination, "w+", encoding="utf8") as file:
            file.write(self.render())

    def append(self):
        """
        Append rendered template to a file.

        Note: If you need to *output* the rendered template to a file,
        removing all previous content of this file, you should use
        :meth:`create` instead.

        """
        with open(self.destination, "a", encoding="utf8") as file:
            file.write(self.render())

    def _add_rst_markup_to_context(self):
        if "package" in self.context and "name" in self.context["package"]:
            length = len(self.context["package"]["name"])
            rst_markup = {
                "header_hash": length * "#",
                "header_equal": length * "=",
                "header_minus": length * "-",
                "header_tilde": length * "~",
            }
            self.context["rst_markup"] = rst_markup


def package_version_from_file():
    """
    Obtain version of the given package by reading file "VERSION".

    The function attempts to read the version number from the file "VERSION"
    in the current working directory. Therefore, if this file does not
    exist, a FileNotFoundError will be raised.

    Returns
    -------
    version : :class:`str`
        Version string as contained in file "VERSION" in current directory

    """
    with open("VERSION", encoding="utf8") as file:
        version = file.read()
    return version


def make_executable(path=""):
    """
    Make a file executable, *i.e.*, set its executable flag.

    Only for those allowed to read the file, the executable flag will be set.

    Parameters
    ----------
    path : :class:`str`
        Name of the path/file to make executable

    Taken from http://stackoverflow.com/a/30463972/119527

    .. versionadded:: 0.4

    """
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def add_to_toctree(filename="", entries=None, sort=False, after=""):
    """
    Add entries to toc tree.

    Adding lines to toctrees in documentation generated with Sphinx is a
    frequent task for a metacode package. A toctree in Sphinx typically
    looks similar to the following:

    .. code-block:: rst

        .. toctree::
            :maxdepth: 1

            first_entry

    The ``.. toctree::`` directive is followed by (optional) parameters,
    the actual entries appear after a blank line and are indented.

    This function allows to add arbitrary entries to a given toctree,
    as entries are given as list.

    If you would like to have the toctree entries sorted alphabetically,
    make sure to set the ``sort`` parameter to ``True``.

    In case of several toctrees in one document, you may use the
    ``after`` parameter to provide a string as a marker. This string
    is searched for treating it as substring through all lines of the
    file, and the first matching line used as actual offset.

    In case of the file not containing any toctree directive or the string
    provided by ``after`` not being found, exceptions will be thrown.

    Parameters
    ----------
    filename : :class:`str`
        Name of the file containing the toctree

    entries : :class:`list`
        lines to be added to the toctree

        Note that regardless of the leading whitespace, entries are left
        stripped and indented with four spaces.

    sort : :class:`bool`
        Whether to sort all toctree entries (alphabetically) after insert

        Default: False

    after : :class:`str`
        String used as marker below which we look for a toctree

        Useful particularly in case of several toctree directives in one
        document. Note that the string provided is used as substring: The
        first line containing it will be used as offset.


    .. versionadded:: 0.5

    """
    with open(filename, "r", encoding="utf8") as file:
        contents = file.read()
    contents = contents.split("\n")
    contents = [line.rstrip() for line in contents]

    offset = 0
    if after:
        offset = contents.index(
            [entry for entry in contents if after in entry][0]
        )
    toctree_start = (
        contents.index("", contents.index(".. toctree::", offset)) + 1
    )
    if contents[toctree_start].startswith("  "):
        toctree_end = contents.index("", toctree_start)
    else:
        toctree_end = toctree_start

    entries = [f"    {line.lstrip()}" for line in entries]
    toctree = contents[toctree_start:toctree_end] + entries
    if sort:
        toctree.sort()
    empty_line = [""] if contents[toctree_end] else []

    contents = (
        contents[:toctree_start]
        + toctree
        + empty_line
        + contents[toctree_end:]
    )
    with open(filename, "w+", encoding="utf8") as file:
        for line in contents:
            file.write(f"{line}\n")
