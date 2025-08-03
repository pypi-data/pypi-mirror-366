"""pymetacode

A Python package helping to write and maintain Python packages.


Design principles
-----------------

The pymetacode package uses a YAML file ``.package_config.yaml`` in the
project root directory of a Python package created and/or handled by
pymetacode as storage for all relevant configuration. This configuration
is internally represented by the
:class:`pymetacode.configuration.Configuration` class and stored as an
attribute in all the relevant objects of the coding classes defined in the
:mod:`pymetacode.coding` module. Therefore, all except of the initial
configuration and package creation tasks are performed from **within the
package root directory**. This is an important fact to have in mind when
further developing the package, as this determines the relative paths used.

The basic user interface is a command-line interface (CLI) designed for
convenience and easy to memorise commands and command structure. All the
details are implemented in the :mod:`pymetacode.cli` module.

Trying to add a module, class, function, GUI window (or even the GUI
itself) that already exists should always result in a warning issued and
no further action taken, such as to not overwrite any existing code. The
same care should be taken when modifying files such as ``setup.py`` or
``MANIFEST.in``, as the developers may have modified those files and they
are not under exclusive control of the pymetacode package.

The pymetacode package tries to depend on as few additional packages as
possible. After all, it is a helper tool for the convenience of the user,
not a full-fledged framework.

While there are some ways to configure the behaviour of the pymetacode
package, it is clearly *opinionated* in many ways. The templates can be
greatly adapted to your own needs, but the overall package structure or
the way how GUIs are designed and the corresponding directory structure
laid out is rather fixed. This is intentional and not meant to be changed
soon.


Available modules
-----------------

The following list provides a high-level overview of the package. More
details can be found in the documentation of the individual modules.

:mod:`pymetacode.configuration`
    Configuration handling of the pymetacode package.

:mod:`pymetacode.coding`
    The actual code generators of the pymetacode package.

:mod:`pymetacode.cli`
    Command-line interface (CLI) module of the pymetacode package.

:mod:`pymetacode.utils`
    Auxiliary functionality used by other modules of the pymetacode package.

"""
