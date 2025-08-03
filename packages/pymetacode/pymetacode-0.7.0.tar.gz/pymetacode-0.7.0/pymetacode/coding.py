"""
The actual code generators of the pymetacode package.

Currently, there are the following types of code generators:

* :class:`pymetacode.coding.PackageCreator`

  Generate the basic package structure.

* :class:`pymetacode.coding.ModuleCreator`

  Add a module to an existing package.

* :class:`pymetacode.coding.ClassCreator`

  Add a class to an existing module, including a test class.

* :class:`pymetacode.coding.FunctionCreator`

  Add a function to an existing module, including a test class.

* :class:`pymetacode.coding.GuiCreator`

  Add PySide6-based (Qt6) GUI subpackage to an existing package.

* :class:`pymetacode.coding.GuiWindowCreator`

  Add a PySide6-based (Qt6) GUI window to an existing GUI subpackage.

* :class:`pymetacode.coding.GuiWidgetCreator`

  Add a PySide6-based (Qt6) GUI widget to an existing GUI subpackage.

* :class:`pymetacode.coding.GuiDialogCreator`

  Add a PySide6-based (Qt6) GUI dialog to an existing GUI subpackage.

* :class:`pymetacode.coding.SubpackageCreator`

  Add a subpackage to an existing package.

Each of these generators uses templates in the ``templates`` subdirectory of
the pymetacode package.

"""

import os
import stat
import subprocess  # noqa: bandit B404
import warnings

from pymetacode import configuration, utils

LICENSES = {
    "BSD": "bsd-2clause.j2.txt",
    "GPLv3": "gpl-v3-boilerplate.j2.txt",
}


class PackageCreator:
    """
    Generate the basic package structure.

    The :doc:`basic package structure <../directory-structure>` follows Python
    best practices and has been used in a number of packages by the author
    of this package. In short, the modules reside in a subdirectory with the
    same name as the package, and parallel to that are directories for tests
    and documentation ("tests", "docs").

    Furthermore, a "setup.py" file is created to have the package
    installable using pip, and a license ("LICENSE") and readme ("README.rst")
    file are present.

    The package version is stored in the file "VERSION", a ".gitignore" file
    exists as well in the package root, and depending on the configuration,
    a git repository is initialised within the package root directory. In
    this case, a pre-commit hook is installed as well incrementing the
    version number for each commit, using the file "incrementVersion.sh"
    from the "bin" directory, and auto-formatting Python code using Black on
    each commit.

    In case of the ``gui`` option in the :attr:`configuration` being set,
    a scaffold for a complete GUI (based on Qt6, PySide6) is added. See the
    :class:`GuiCreator` class for further details.


    Attributes
    ----------
    name : :class:`str`
        Name of the package to be created.

        Will usually be read from the configuration.

    subdirectories : :class:`list`
        Directories and subdirectories created within the package root.

    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    documentation : :class:`dict`
        Settings for creating the documentation.


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

    """

    def __init__(self):
        self.name = ""
        self.subdirectories = [
            "tests",
            os.path.join("docs", "api"),
            "bin",
        ]
        self.configuration = configuration.Configuration()
        self.documentation = {
            "pages": [
                "audience",
                "changelog",
                "developers",
                "installing",
                "people",
                "roadmap",
                "usecases",
            ]
        }

    def create(self, name=""):
        """
        Generate the basic package structure.

        Parameters
        ----------
        name : :class:`str`
            Name of the package to create.

            If provided, this will set the :attr:`name` attribute of the
            class.

        """
        if name:
            self.name = name
        elif not self.name:
            raise ValueError
        self._create_subdirectories()
        self._create_init_files()
        self._create_gitignore()
        self._create_prospector_profile()
        self._create_version_file()
        self._create_license_file()
        self._create_manifest_file()
        self._create_setup_py_file()
        self._create_pyproject_toml_file()
        self._create_readme_file()
        self._create_makefile()
        self._create_citation_cff_file()
        self._create_version_updater_file()
        self._create_python_formatter_file()
        self._create_documentation_stub()
        self._git_init()
        self._create_gui()

    def _create_subdirectories(self):
        self.subdirectories.append(self.name)
        for directory in self.subdirectories:
            self._create_directory(name=os.path.join(self.name, directory))

    @staticmethod
    def _create_directory(name=""):
        if os.path.exists(name):
            warnings.warn("Directory '" + name + "' exists already.")
        else:
            os.makedirs(name)

    def _create_init_files(self):
        for directory in [self.name, "tests"]:
            init_filename = os.path.join(self.name, directory, "__init__.py")
            utils.ensure_file_exists(init_filename)

    def _create_gitignore(self):
        contents = utils.get_package_data("gitignore")
        with open(
            os.path.join(self.name, ".gitignore"), "w+", encoding="utf8"
        ) as file:
            file.write(contents)

    def _create_prospector_profile(self):
        template = utils.Template(
            path="",
            template="prospector.j2.yaml",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, ".prospector.yaml"),
        )
        template.create()

    def _create_manifest_file(self):
        template = utils.Template(
            path="",
            template="MANIFEST.j2.in",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "MANIFEST.in"),
        )
        template.create()

    def _create_version_file(self):
        with open(
            os.path.join(self.name, "VERSION"), "w+", encoding="utf8"
        ) as file:
            file.write("0.1.0.dev0\n")

    def _create_license_file(self):
        template = utils.Template(
            path="licenses",
            template=LICENSES[self.configuration.package["license"]],
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "LICENSE"),
        )
        template.create()
        if self.configuration.package["license"] == "GPLv3":
            template = utils.Template(
                path="licenses",
                template="gpl-v3.txt",
                context=self.configuration.to_dict(),
                destination=os.path.join(self.name, "COPYING"),
            )
            template.create()

    def _create_setup_py_file(self):
        license_classifiers = {
            "BSD": "BSD License",
            "GPLv3": "GNU General Public License v3 (GPLv3)",
        }
        context = self.configuration.to_dict()
        context["package"]["license_classifier"] = license_classifiers[
            context["package"]["license"]
        ]
        template = utils.Template(
            path="",
            template="setup.j2.py",
            context=context,
            destination=os.path.join(self.name, "setup.py"),
        )
        template.create()

    def _create_pyproject_toml_file(self):
        template = utils.Template(
            path="",
            template="pyproject.j2.toml",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "pyproject.toml"),
        )
        template.create()

    def _create_readme_file(self):
        template = utils.Template(
            path="",
            template="README.j2.rst",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "README.rst"),
        )
        template.create()

    def _create_makefile(self):
        contents = utils.get_package_data("Makefile")
        destination = os.path.join(self.name, "Makefile")
        with open(destination, "w+", encoding="utf8") as file:
            file.write(contents)

    def _create_citation_cff_file(self):
        license_classifiers = {
            "BSD": "BSD-2-Clause",
            "GPLv3": "GPL-3.0",
        }
        context = self.configuration.to_dict()
        context["package"]["license_classifier"] = license_classifiers[
            context["package"]["license"]
        ]
        author_entries = self.configuration.package["author"].split(",")
        context["authors"] = [
            {
                "family_names": name.rsplit(maxsplit=1)[1],
                "given_names": name.rsplit(maxsplit=1)[0],
            }
            for name in author_entries
            if name
        ]
        template = utils.Template(
            path="",
            template="CITATION.j2.cff",
            context=context,
            destination=os.path.join(self.name, "CITATION.cff"),
        )
        template.create()

    def _create_version_updater_file(self):
        contents = utils.get_package_data("incrementVersion.sh")
        destination = os.path.join(self.name, "bin", "incrementVersion.sh")
        with open(destination, "w+", encoding="utf8") as file:
            file.write(contents)
        os.chmod(destination, os.stat(destination).st_mode | stat.S_IXUSR)

    def _create_python_formatter_file(self):
        contents = utils.get_package_data("formatPythonCode.sh")
        destination = os.path.join(self.name, "bin", "formatPythonCode.sh")
        with open(destination, "w+", encoding="utf8") as file:
            file.write(contents)
        os.chmod(destination, os.stat(destination).st_mode | stat.S_IXUSR)

    def _create_documentation_stub(self):
        self._create_documentation_generator_files()
        self._create_documentation_config()
        self._create_documentation_index()
        self._create_documentation_api_index()
        self._create_documentation_contents()
        self._create_documentation_multiversion_templates()

    def _create_documentation_generator_files(self):
        make_files = ["make.bat", "Makefile"]
        for file in make_files:
            contents = utils.get_package_data("/".join(["docs", file]))
            destination = os.path.join(self.name, "docs", file)
            with open(destination, "w+", encoding="utf8") as doc_file:
                doc_file.write(contents)

    def _create_documentation_index(self):
        template = utils.Template(
            path="docs",
            template="index.j2.rst",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "docs", "index.rst"),
        )
        template.create()
        template = utils.Template(
            path="docs",
            template="main-toctree.j2.rst",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "docs", "index.rst"),
        )
        template.append()

    def _create_documentation_config(self):
        template = utils.Template(
            path="docs",
            template="conf.j2.py",
            context=self.configuration.to_dict(),
            destination=os.path.join(self.name, "docs", "conf.py"),
        )
        template.create()

    def _create_documentation_api_index(self):
        context = self.configuration.to_dict()
        context["package"] = {"name": self.name}
        template = utils.Template(
            path="docs",
            template="api_index.j2.rst",
            context=context,
            destination=os.path.join(self.name, "docs", "api", "index.rst"),
        )
        template.create()

    def _create_documentation_contents(self):
        for name in self.documentation["pages"]:
            template = utils.Template(
                path="docs",
                template=f"{name}.j2.rst",
                context=self.configuration.to_dict(),
                destination=os.path.join(self.name, "docs", f"{name}.rst"),
            )
            template.create()

    def _create_documentation_multiversion_templates(self):
        os.mkdir(os.path.join(self.name, "docs", "_templates"))
        make_files = ["page.html", "versions.html"]
        for file in make_files:
            contents = utils.get_package_data(
                "/".join(["docs", "_templates", file])
            )
            destination = os.path.join(self.name, "docs", "_templates", file)
            with open(destination, "w+", encoding="utf8") as doc_file:
                doc_file.write(contents)

    def _git_init(self):
        if self.configuration.options["git"]:
            subprocess.run(
                ["git", "init"], cwd=self.name, check=False
            )  # nosec
            with utils.change_working_dir(
                os.path.join(self.name, ".git", "hooks")
            ):
                with open("pre-commit", "w+", encoding="utf8") as file:
                    file.write("#!/bin/sh\n")
                    file.write("./bin/incrementVersion.sh\n")
                    file.write("./bin/formatPythonCode.sh\n")
                utils.make_executable("pre-commit")

    def _create_gui(self):
        if self.configuration.options["gui"]:
            with utils.change_working_dir(self.name):
                gui = GuiCreator()
                gui.configuration = self.configuration
                gui.create()


class ModuleCreator:
    """
    Add a module to an existing package.

    Actually, adding a module consists of creating three files: the module
    itself, an accompanying test module, and the API documentation file. The
    latter gets added to the API toctree directive as well.

    If you try to add an already existing module, a warning is raised and no
    further action taken, in order *not* to overwrite existing code.

    If the module name contains a dot, the first part will be interpreted
    as subpackage and the second as module name. In this case, the module
    is added to the subpackage, and the API documentation handled
    accordingly.

    If you try to add a module to a nonexisting subpackage, a warning is
    raised and no further action taken. In such case, first create the
    subpackage. See the :class:`SubpackageCreator` class for further details.

    Attributes
    ----------
    name : :class:`str`
        Name of the module to be created.

    subpackage : :class:`str`
        Name of the subpackage (if any).

        If the name of a module contains a dot, the part before the dot is
        interpreted as subpackage.

        If the subpackage does not exist, a warning is issued and no
        module created.

        .. versionadded:: 0.5

    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no name is provided


    Examples
    --------
    The following examples demonstrate how to use the CLI from the terminal,
    rather than how to use this class programmatically.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add module mymodule

    This will add a module "mymodule" to your package, together with a
    "test_mymodule" module in the "tests" subdirectory. And even better,
    the API documentation will be updated as well for you.

    Suppose you would have a subpackage "mysubpackage" and would want to add
    a module to this subpackage. In this case, simply use the familiar dot
    notation for separating subpackage and module:

    .. code-block:: bash

        pymeta add module mysubpackage.mymodule

    This will add a module "mymodule" to the subpackage "mysubpackage" of
    your package, together with a "test_mymodule" module in the
    "mysubpackage" subdirectory of the "tests" directory. And even better,
    the API documentation will be updated for you as well.

    This can even be cascaded and used for nested subpackages:

    .. code-block:: bash

        pymeta add module mysubpackage.mysubsubpackage.mymodule

    This will add a module "mymodule" to the subpackage "mysubsubpackage" of
    the subpackage "mysubpackage" of your package, together with a
    "test_mymodule" module in the "mysubpackage/mysubsubpackage" subdirectory
    of the "tests" directory. And even better, the API documentation will be
    updated for you as well.

    .. versionchanged:: 0.6
        Support for nested subpackages

    """

    def __init__(self):
        self.name = ""
        self.subpackage = ""
        self.configuration = configuration.Configuration()

    def create(self, name=""):
        """
        Add a module to an existing package.

        Parameters
        ----------
        name : :class:`str`
            Name of the module to add.

            If provided, this will set the :attr:`name` attribute of the
            class.

        """
        if name:
            self.name = name
        elif not self.name:
            raise ValueError
        self._assign_subpackage()
        if not self._subpackage_exists():
            warnings.warn(
                f"Subpackage '{self.subpackage}' does not exist. "
                f"Module not created."
            )
            return
        self._create_module()
        self._create_test_module()
        self._create_api_documentation()
        self._add_api_documentation_to_toctree()

    def _assign_subpackage(self):
        if "." in self.name:
            self.subpackage, self.name = self.name.rsplit(".", maxsplit=1)

    def _subpackage_exists(self):
        subpackage_path = os.path.join(
            self.configuration.package["name"], *self.subpackage.split(".")
        )
        return os.path.exists(subpackage_path)

    def _create_module(self):
        filename = os.path.join(
            self.configuration.package["name"],
            *self.subpackage.split("."),
            self.name + ".py",
        )
        if os.path.exists(filename):
            warnings.warn(f"Module '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        template = utils.Template(
            path="code",
            template="module.j2.py",
            context=context,
            destination=filename,
        )
        template.create()

    def _create_test_module(self):
        filename = os.path.join(
            "tests", *self.subpackage.split("."), f"test_{self.name}.py"
        )
        if os.path.exists(filename):
            warnings.warn(f"Module '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        if self.subpackage:
            context["package"]["name"] = ".".join(
                [context["package"]["name"], self.subpackage]
            )
        template = utils.Template(
            path="code",
            template="test_module.j2.py",
            context=context,
            destination=filename,
        )
        template.create()

    def _create_api_documentation(self):
        package = self.configuration.package["name"]
        filename = os.path.join(
            "docs",
            "api",
            *self.subpackage.split("."),
            ".".join(
                [
                    item
                    for item in [package, self.subpackage, f"{self.name}.rst"]
                    if item
                ]
            ),
        )
        if os.path.exists(filename):
            warnings.warn(f"File '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        if self.subpackage:
            module_name = ".".join([self.subpackage, self.name])
        else:
            module_name = self.name
        context["module"] = {"name": module_name}
        context["header_extension"] = (
            len(package) + len(module_name) + 1
        ) * "="
        template = utils.Template(
            path="docs",
            template="api_module.j2.rst",
            context=context,
            destination=filename,
        )
        template.create()

    def _add_api_documentation_to_toctree(self):
        index_filename = os.path.join(
            "docs", "api", *self.subpackage.split("."), "index.rst"
        )
        if not os.path.exists(index_filename):
            return
        package = self.configuration.package["name"]
        utils.add_to_toctree(
            filename=index_filename,
            entries=[
                ".".join(
                    [
                        item
                        for item in [package, self.subpackage, self.name]
                        if item
                    ]
                )
            ],
            sort=True,
        )


class ClassCreator:
    """
    Add a class to an existing module, including a test class.

    When a class is added to a module, it will always be added to the bottom
    of the module file, and at the same time a test class with a very basic
    setup and a first test will be added to the corresponding test module.

    If you try to add an already existing class to the given module,
    a warning is raised and no further action taken, in order *not* to
    overwrite existing code.


    Attributes
    ----------
    name : :class:`str`
        Name of the class to be added to the module

    module : :class:`str`
        Name of the module the class should be added to

    subpackage : :class:`str`
        Name of the subpackage (if any).

        If the name of a module contains a dot, the part before the dot is
        interpreted as subpackage.

        If the subpackage does not exist, an exception is raised.

        .. versionadded:: 0.5

    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no class or module name is provided


    Examples
    --------
    The following examples demonstrate how to use the CLI from the terminal,
    rather than how to use this class programmatically.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add class MyClass to mymodule

    This will add the class "MyClass" to the module "mymodule", together
    with a test class in the "test_mymodule" module. The class will come
    with a basic docstring, and the test class with a minimalistic setup
    and first test (for implementation of the class) that gets you started
    with writing further tests.

    Suppose you have a subpackage "mysubpackage" and would want to add
    a class to a module of this subpackage. In this case, simply use the
    familiar dot notation for separating subpackage and module:

    .. code-block:: bash

        pymeta add class MyClass to mysubpackage.mymodule

    This will add the class "MyClass" to the module "mymodule" in the
    subpackage "mysubpackage", together with a test class in the
    "test_mymodule" module in the respective "mysubpackage" directory. The
    class will come with a basic docstring, and the test class with a
    minimalistic setup and first test (for implementation of the class)
    that gets you started with writing further tests.

    This can even be cascaded and used for nested subpackages:

    .. code-block:: bash

        pymeta add class MyClass to mysubpackage.mysubsubpackage.mymodule

    This will add the class "MyClass" to the module "mymodule" in the
    subpackage "mysubsubpackage" in the subpackage "mysubpackage", together
    with a test class in the "test_mymodule" module in the respective
    "mysubpackage/mysubsubpackage" directory. The class will come with a
    basic docstring, and the test class with a minimalistic setup and first
    test (for implementation of the class) that gets you started with
    writing further tests.

    .. versionchanged:: 0.6
        Support for nested subpackages

    """

    def __init__(self):
        self.name = ""
        self.module = ""
        self.subpackage = ""
        self.configuration = configuration.Configuration()
        self._module_filename = ""
        self._package_version = ""

    def create(self, name="", module=""):
        """
        Create actual code stub for the class.

        Parameters
        ----------
        name : :class:`str`
            Name of the function to be created

        module : :class:`str`
            Name of the module the function should be added to

        Raises
        ------
        ValueError
            Raised if function or module name is missing

        """
        self._check_prerequisites(module, name)
        if self._class_exists_in_module():
            msg = f"Class {self.name} exists already in {self.module}."
            warnings.warn(msg)
            return
        self._create_class()
        self._create_test_class()

    def _check_prerequisites(self, module, name):
        if name:
            self.name = name
        elif not self.name:
            raise ValueError("Class name missing")
        if module:
            self.module = module
        elif not self.module:
            raise ValueError("Module name missing")
        package = self.configuration.package["name"]
        if "." in self.module:
            self.subpackage, self.module = self.module.rsplit(".", maxsplit=1)
        self._module_filename = os.path.join(
            package, *self.subpackage.split("."), f"{self.module}.py"
        )
        if not os.path.exists(self._module_filename):
            raise ValueError(f"Module {self.module} does not exist")
        if not self._package_version:
            version = utils.package_version_from_file()
            self._package_version = ".".join(version.split(".")[0:2])

    def _class_exists_in_module(self):
        with open(self._module_filename, encoding="utf8") as file:
            contents = file.read()
        return any(
            name in contents
            for name in [f"class {self.name}:", f"class {self.name}("]
        )

    def _create_class(self):
        context = self.configuration.to_dict()
        context["class"] = {"name": self.name}
        context["package"]["version"] = self._package_version
        template = utils.Template(
            path="code",
            template="class.j2.py",
            context=context,
            destination=self._module_filename,
        )
        template.append()

    def _create_test_class(self):
        context = self.configuration.to_dict()
        context["class"] = {
            "name": self.name,
            "instance": utils.camel_case_to_underscore(self.name),
        }
        context["module"] = {"name": self.module}
        filename = os.path.join(
            "tests", *self.subpackage.split("."), f"test_{self.module}.py"
        )
        template = utils.Template(
            path="code",
            template="test_class.j2.py",
            context=context,
            destination=filename,
        )
        template.append()


class FunctionCreator:
    """
    Add a function to an existing module, including a test class.

    When a function is added to a module, it will always be added to the
    bottom of the module file, and at the same time a test class with a
    first test will be added to the corresponding test module.

    If you try to add an already existing function to the respective module,
    a warning is raised and no further action taken, in order *not* to
    overwrite existing code.


    Attributes
    ----------
    name : :class:`str`
        Name of the function to be added to the module

    module : :class:`str`
        Name of the module the function should be added to

    subpackage : :class:`str`
        Name of the subpackage (if any).

        If the name of a module contains a dot, the part before the dot is
        interpreted as subpackage.

        If the subpackage does not exist, an exception is raised.

        .. versionadded:: 0.5

    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no function or module name is provided


    Examples
    --------
    The following examples demonstrate how to use the CLI from the terminal,
    rather than how to use this class programmatically.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add function my_function to mymodule

    This will add the function "my_function" to the module "mymodule",
    together with a test class in the "test_mymodule" module. The function
    will come with a basic docstring, and the test class with a
    minimalistic first test that gets you started with writing further tests.

    Suppose you have a subpackage "mysubpackage" and would want to add
    a function to a module of this subpackage. In this case, simply use the
    familiar dot notation for separating subpackage and module:

    .. code-block:: bash

        pymeta add function my_function to mysubpackage.mymodule

    This will add the function "my_function" to the module "mymodule" in the
    subpackage "mysubpackage", together with a test class in the
    "test_mymodule" module in the respective "mysubpackage" directory. The
    function will come with a basic docstring, and the test class with a
    minimalistic setup and first test that gets you started with writing
    further tests.

    This can even be cascaded and used for nested subpackages:

    .. code-block:: bash

        pymeta add function my_function to mysubpackage.mysubsubpackage.mymodule

    This will add the function "my_function" to the module "mymodule" in the
    subpackage "mysubsubpackage" in the subpackage "mysubpackage", together
    with a test class in the "test_mymodule" module in the respective
    "mysubpackage/mysubsubpackage" directory. The function will come with a
    basic docstring, and the test class with a minimalistic setup and first
    test that gets you started with writing further tests.

    .. versionchanged:: 0.6
        Support for nested subpackages

    """

    def __init__(self):
        self.name = ""
        self.module = ""
        self.subpackage = ""
        self.configuration = configuration.Configuration()
        self._module_filename = ""
        self._package_version = ""

    def create(self, name="", module=""):
        """
        Create actual code stub for the function.

        Parameters
        ----------
        name : :class:`str`
            Name of the function to be created

        module : :class:`str`
            Name of the module the function should be added to

        Raises
        ------
        ValueError
            Raised if function or module name is missing

        """
        self._check_prerequisites(module, name)
        if self._function_exists_in_module():
            msg = f"Function {self.name} exists already in {self.module}."
            warnings.warn(msg)
            return
        self._create_function()
        self._create_test_class()

    def _check_prerequisites(self, module, name):
        if name:
            self.name = name
        elif not self.name:
            raise ValueError("Function name missing")
        if module:
            self.module = module
        elif not self.module:
            raise ValueError("Module name missing")
        if "." in self.module:
            self.subpackage, self.module = self.module.rsplit(".", maxsplit=1)
        package = self.configuration.package["name"]
        self._module_filename = os.path.join(
            package, *self.subpackage.split("."), f"{self.module}.py"
        )
        if not os.path.exists(self._module_filename):
            raise ValueError(f"Module {self.module} does not exist")
        if not self._package_version:
            version = utils.package_version_from_file()
            self._package_version = ".".join(version.split(".")[0:2])

    def _function_exists_in_module(self):
        with open(self._module_filename, encoding="utf8") as file:
            contents = file.read()
        return any(
            name in contents
            for name in [f"def {self.name}:", f"def {self.name}("]
        )

    def _create_function(self):
        context = self.configuration.to_dict()
        context["function"] = {"name": self.name}
        context["package"]["version"] = self._package_version
        template = utils.Template(
            path="code",
            template="function.j2.py",
            context=context,
            destination=self._module_filename,
        )
        template.append()

    def _create_test_class(self):
        context = self.configuration.to_dict()
        context["function"] = {
            "name": self.name,
            "name_camelcase": utils.underscore_to_camel_case(self.name),
        }
        context["module"] = {"name": self.module}
        filename = os.path.join(
            "tests", *self.subpackage.split("."), f"test_{self.module}.py"
        )
        template = utils.Template(
            path="code",
            template="test_function.j2.py",
            context=context,
            destination=filename,
        )
        template.append()


class GuiCreator:
    r"""
    Add PySide6-based (Qt6) GUI subpackage to an existing package.

    If you want to add a GUI to your package, this involves extending the
    overall package structure with a GUI submodule (as well in the tests).
    For now, the pymetacode package only supports creating GUIs using Qt6
    and the PySide6 bindings. The package structure of the added
    subpackages follows best practices. An example of the additional
    package structure is shown below.

    In case a GUI already exists (or at least the ``gui`` subpackage),
    a warning is raised and no further action taken, in order *not* to
    overwrite existing code.


    .. code-block::

        mypackage
        ├── docs
        │   ├── api
        │   │   ├── gui
        │   │   │   ├── mypackage.gui.app.rst
        │   │   │   ├── mypackage.gui.mainwindow.rst
        │   │   │   └── index.rst
        │   │   └── ...
        │   └── ...
        ├── mypackage
        │   ├── gui
        │   │   ├── app.py
        │   │   ├── data
        │   │   │   ├── icon.svg
        │   │   │   └── splash.svg
        │   │   ├── __init__.py
        │   │   ├── mainwindow.py
        │   │   ├── Makefile
        │   │   └── ui
        │   │       └── __init__.py
        │   └── ...
        └── tests
            ├── gui
            │   ├── __init__.py
            │   └── test_mainwindow.py
            └── ...


    To summarise, what is added in terms of subdirectories:

    #. A ``gui`` directory within the package source directory
    #. A ``gui`` directory within the package tests directory
    #. A ``gui`` directory within the package API docs directory

    The ``gui`` directories in source and tests as well as the ``gui.ui``
    directory behave like subpackages, as they all contain an
    ``__init__.py`` file.

    The ``gui`` directory in the package source directory deserves a few
    more comments:

    * The user interface (\*.ui) files containing the XML
      description of the Qt windows created by/modified with the Qt Designer
      reside in the ``ui`` subdirectory, together with the auto-generated
      Python files used for import. To help with auto-generating the Python
      files from the ui files, use the ``Makefile`` in the ``gui``
      subdirectory.

    * Additional data files, such as icons or images for a splash screen,
      reside in the ``data`` subdirectory.

    * The ``app.py`` module contains the main entrance point to the GUI that
      is added to the gui_scripts entrypoint in the ``setup.py`` file.

    * The ``mainwindow.py`` module contains all relevant code for the main GUI
      window.

      pymetacode uses the `qtbricks <https://qtbricks.docs.till-biskup.de/>`_
      package, hence the definition of the main window is rather minimal to
      start with and does *not* use ui files/the Qt Designer. Have a look at
      :mod:`qtbricks.mainwindow` for details.

    * The ``Makefile`` is used for convenience to generate the Python files
      from the ui files used by the Qt Designer. Simply type ``make`` in the
      ``gui`` subdirectory to have them built.

    If you would like to add additional windows to your existing GUI, have a
    look at the :class:`GuiWindowCreator` class.


    Attributes
    ----------
    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    subdirectories : :class:`list`
        Subdirectories created within the package source directory.


    Examples
    --------
    The following example demonstrates how to use the CLI from the terminal,
    rather than how to use this class programmatically, as this is the
    preferred and intended use case.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following CLI commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add gui

    This will add the basic structure for a GUI to your package, including
    tests and documentation.

    However, in case you want or need to access pymetacode programmatically,
    this is the series of steps you would need to perform to create a GUI.
    At the same time, this is a minimum scenario for manually testing the
    functionality:

    .. code-block::

        from pymetacode import coding, configuration, utils

        cfg = configuration.Configuration()
        cfg.package['name'] = 'pkgname'

        pkg = coding.PackageCreator()
        pkg.configuration = cfg
        pkg.create(name=cfg.package['name'])

        with utils.change_working_dir(cfg.package['name']):
            gui = coding.GuiCreator()
            gui.configuration = cfg
            gui.create()

    As you see here, this assumes no package to preexist. The crucial step
    is to create a configuration first and as a bare minimum set the package
    name. Next comes creating the package, and only afterwards the GUI. The
    configuration is reused in both cases.

    .. versionadded:: 0.4


    """

    def __init__(self):
        self.configuration = configuration.Configuration()
        self.subdirectories = [
            os.path.join("gui", "images"),
            os.path.join("gui", "ui"),
        ]
        self._src_dir = ""

    def create(self):
        """
        Create actual code stub for the GUI subpackage.

        This will create a number of files and (sub)directories,
        as mentioned in the :class:`GuiCreator` class documentation.

        """
        self._src_dir = self.configuration.package["name"]
        if os.path.exists(os.path.join(self._src_dir, "gui")):
            warnings.warn("GUI directory exists already... nothing done.")
            return
        self._create_subdirectories()
        self._create_init_files()
        self._create_makefile()
        self._create_modules()
        self._create_test_modules()
        self._add_tests()
        self._create_splash_file()
        self._copy_images()
        self._create_documentation()
        self._update_manifest()
        self._update_setup()

    def _create_subdirectories(self):
        for directory in self.subdirectories:
            self._create_directory(
                name=os.path.join(self._src_dir, directory)
            )
        self._create_directory(os.path.join("tests", "gui"))
        self._create_directory(os.path.join("docs", "api", "gui"))

    @staticmethod
    def _create_directory(name=""):
        if os.path.exists(name):
            warnings.warn("Directory '" + name + "' exists already.")
        else:
            os.makedirs(name)

    def _create_init_files(self):
        directories = [
            os.path.join(self._src_dir, "gui"),
            os.path.join(self._src_dir, "gui", "ui"),
            os.path.join("tests", "gui"),
        ]
        for directory in directories:
            init_filename = os.path.join(directory, "__init__.py")
            utils.ensure_file_exists(init_filename)

    def _create_makefile(self):
        contents = utils.get_package_data("Makefile_gui")
        filepath = os.path.join(self._src_dir, "gui", "Makefile")
        with open(filepath, "w+", encoding="utf8") as file:
            file.write(contents)

    def _create_modules(self):
        modules = ["app", "mainwindow"]
        for module in modules:
            template = utils.Template(
                path="code",
                template=f"gui_{module}.j2.py",
                context=self.configuration.to_dict(),
                destination=os.path.join(
                    self._src_dir, "gui", f"{module}.py"
                ),
            )
            template.create()

    def _create_test_modules(self):
        modules = ["app", "mainwindow"]
        for module in modules:
            context = self.configuration.to_dict()
            context["module"] = {"name": module}
            template = utils.Template(
                path="code",
                template="test_guimodule.j2.py",
                context=context,
                destination=os.path.join("tests", "gui", f"test_{module}.py"),
            )
            template.create()

    def _add_tests(self):
        classname = "MainWindow"
        modulename = "mainwindow"
        context = self.configuration.to_dict()
        context["class"] = {"name": classname}
        context["module"] = {"name": modulename}
        filename = os.path.join("tests", "gui", f"test_{modulename}.py")
        template = utils.Template(
            path="code",
            template="test_guiclass.j2.py",
            context=context,
            destination=filename,
        )
        template.append()

    def _create_splash_file(self):
        if not self.configuration.gui["splash"]:
            return
        template = utils.Template(
            path="",
            template="splash.j2.svg",
            context=self.configuration.to_dict(),
            destination=os.path.join(
                self._src_dir, "gui", "images", "splash.svg"
            ),
        )
        template.create()

    def _copy_images(self):
        images = ["icon.svg"]
        for image in images:
            contents = utils.get_package_data(image)
            filepath = os.path.join(self._src_dir, "gui", "images", image)
            with open(filepath, "w+", encoding="utf8") as file:
                file.write(contents)

    def _create_documentation(self):
        self._create_documentation_index()
        self._add_subpackage_documentation()
        modules = ["app", "mainwindow"]
        for module in modules:
            self._create_api_documentation(module)
        self._add_api_documentation_to_toctree()

    def _create_documentation_index(self):
        package_name = self.configuration.package["name"]
        context = self.configuration.to_dict()
        context["subpackage"] = {"name": f"{package_name}.gui"}
        context["header_extension"] = (len(package_name) + 4) * "="
        template = utils.Template(
            path="docs",
            template="api_subpackage_index.j2.rst",
            context=context,
            destination=os.path.join("docs", "api", "gui", "index.rst"),
        )
        template.create()

    def _add_subpackage_documentation(self):
        package_name = self.configuration.package["name"]
        context = self.configuration.to_dict()
        context["package"] = {"name": package_name}
        template = utils.Template(
            path="docs",
            template="api_index_subpackages_block.j2.rst",
            context=context,
            destination=os.path.join("docs", "api", "index.rst"),
        )
        template.append()

    def _create_api_documentation(self, module):
        package = self.configuration.package["name"] + ".gui"
        filename = os.path.join(
            "docs", "api", "gui", f"{package}.{module}.rst"
        )
        if os.path.exists(filename):
            warnings.warn(f"File '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        context["package"] = {"name": package}
        context["module"] = {"name": module}
        context["header_extension"] = (len(package) + len(module) + 1) * "="
        template = utils.Template(
            path="docs",
            template="api_gui_module.j2.rst",
            context=context,
            destination=filename,
        )
        template.create()

    def _add_api_documentation_to_toctree(self):
        index_filename = os.path.join("docs", "api", "index.rst")
        if not os.path.exists(index_filename):
            return
        utils.add_to_toctree(
            filename=index_filename,
            entries=["gui/index"],
            sort=True,
            after="Subpackages",
        )
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        if not os.path.exists(index_filename):
            return
        modules = ["app", "mainwindow"]
        package = self.configuration.package["name"] + ".gui"
        utils.add_to_toctree(
            filename=index_filename,
            entries=[f"{package}.{module}" for module in modules],
            sort=True,
        )

    def _update_manifest(self):
        package_name = self.configuration.package["name"]
        context = self.configuration.to_dict()
        context["package"] = {"name": package_name}
        template = utils.Template(
            template="MANIFEST-gui.j2.in",
            context=context,
            destination="MANIFEST.in",
        )
        template.append()

    def _update_setup(self):
        filename = os.path.join("setup.py")
        if not os.path.exists(filename):
            return
        with open(filename, encoding="utf8") as file:
            contents = file.read()
        lines = contents.split("\n")
        lines = self._insert_packages_to_install_requires(lines)
        lines = self._add_gui_script_entry_point(lines)
        with open(filename, "w+", encoding="utf8") as file:
            file.write("\n".join(lines))

    @staticmethod
    def _insert_packages_to_install_requires(lines):
        gui_requirements = ["PySide6", "qtbricks"]
        start_of_install_requires = lines.index("    install_requires=[")
        end_of_install_requires = lines[start_of_install_requires:].index(
            "    ],"
        )
        install_requires = lines[
            start_of_install_requires : start_of_install_requires
            + end_of_install_requires
        ]
        add_requirements = []
        for requirement in gui_requirements:
            if requirement not in "".join(install_requires):
                add_requirements.append(requirement)
        for offset, requirement in enumerate(add_requirements):
            lines.insert(
                start_of_install_requires + end_of_install_requires + offset,
                f'        "{requirement}",',
            )
        return lines

    def _add_gui_script_entry_point(self, lines):
        if '"gui_scripts": [' not in "".join(lines):
            package_name = self.configuration.package["name"]
            context = self.configuration.to_dict()
            context["package"] = {"name": package_name}
            template = utils.Template(
                template="setup-gui-scripts.j2.py",
                context=context,
            )
            entry_points = template.render()
            start_of_install_requires = lines.index("    install_requires=[")
            lines.insert(start_of_install_requires, entry_points)
        return lines


class GuiWindowCreator:
    """
    Add a PySide6-based (Qt6) GUI window to an existing GUI subpackage.

    Actually, adding a GUI window consists of creating a number of files:

    #. the module used to call the GUI window
    #. the corresponding ui file defining the Qt layout of the window
    #. an accompanying test module
    #. the API documentation file

    The latter gets added to the API toctree directive as well.

    If you try to add an already existing GUI window, a warning is raised
    and no further action taken, in order *not* to overwrite existing code.


    Attributes
    ----------
    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no name is provided


    Examples
    --------
    The following example demonstrates how to use the CLI from the terminal,
    rather than how to use this class programmatically, as this is the
    preferred and intended use case.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following CLI commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add window mywindow

    This will add the GUI window ``mywindow`` to the ``gui`` subpackage of
    your package, together with the ``test_mywindow`` module in the
    ``tests.gui`` directory. Furthermore, the corresponding UI file (to be
    used with the Qt Designer) gets added to the ``gui/ui`` subpackage.
    And even better, the API documentation will be updated as well for you.


    .. versionadded:: 0.4

    """

    def __init__(self):
        self.configuration = configuration.Configuration()
        self._name = ""
        self._class_name = ""

    @property
    def name(self):
        """
        Name of the GUI window to be created.

        A suffix "window" gets added if not present, and the name is
        ensured to be in lowercase letters.

        Returns
        -------
        name : :class:`str`
            Name of the GUI window to be created.

        """
        return self._name

    @name.setter
    def name(self, name=""):
        if not name:
            self._name = ""
            self._class_name = ""
        elif name.lower().endswith("window"):
            self._name = name.lower()
            self._class_name = f"{self.name[:-6].capitalize()}Window"
        else:
            self._name = f"{name}window".lower()
            self._class_name = f"{name.capitalize()}Window"

    @property
    def class_name(self):
        """
        The name of the class containing the GUI window.

        Similar to :attr:`name`, but in CamelCase with the first letter
        capitalised and the suffix "Window".

        Returns
        -------
        class_name : :class:`str`
            The name of the class containing the GUI window.

        """
        return self._class_name

    def create(self, name=""):
        """
        Create actual code stub for the GUI window.

        This will create a number of files:

        #. the module used to call the GUI window
        #. the corresponding ui file defining the Qt layout of the window
        #. an accompanying test module
        #. the API documentation file

        The latter gets added to the API toctree directive as well.

        """
        if name:
            self.name = name
        elif not self.name:
            raise ValueError("No window name given")
        if self._window_exists():
            warnings.warn(f"Window {self.name} exists already. Nothing done.")
            return
        self._create_window()
        self._add_tests()
        self._create_api_documentation()
        self._add_api_documentation_to_toctree()

    def _window_exists(self):
        window_module = os.path.join(
            self.configuration.package["name"], "gui", f"{self.name}.py"
        )
        return os.path.exists(window_module)

    def _create_window(self):
        gui_dir = os.path.join(self.configuration.package["name"], "gui")
        test_dir = os.path.join("tests", "gui")
        files = [
            {
                "template": "gui_window.j2.py",
                "path": os.path.join(gui_dir, f"{self.name}.py"),
            },
            {
                "template": "gui_window.j2.ui",
                "path": os.path.join(gui_dir, "ui", f"{self.name}.ui"),
            },
            {
                "template": "test_guimodule.j2.py",
                "path": os.path.join(test_dir, f"test_{self.name}.py"),
            },
        ]
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        context["class"] = {"name": self.class_name}
        for file in files:
            template = utils.Template(
                path="code",
                template=file["template"],
                context=context,
                destination=file["path"],
            )
            template.create()
        # Decide whether to auto-generate these files or whether to postpone
        # subprocess.run(
        #     ['pyside6-uic',
        #      os.path.join(self._src_dir, 'gui', 'ui', f'{self.name}.ui'),
        #      '-o',
        #      os.path.join(self._src_dir, 'gui', 'ui', f'{self.name}.py')]
        # )

    def _add_tests(self):
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        context["class"] = {"name": self.class_name}
        filename = os.path.join("tests", "gui", f"test_{self.name}.py")
        template = utils.Template(
            path="code",
            template="test_guiclass.j2.py",
            context=context,
            destination=filename,
        )
        template.append()

    def _create_api_documentation(self):
        package = self.configuration.package["name"] + ".gui"
        filename = os.path.join(
            "docs", "api", "gui", f"{package}.{self.name}.rst"
        )
        if os.path.exists(filename):
            warnings.warn(f"File '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        context["package"] = {"name": package}
        context["module"] = {"name": self.name}
        context["header_extension"] = (
            len(package) + len(self.name) + 1
        ) * "="
        template = utils.Template(
            path="docs",
            template="api_module.j2.rst",
            context=context,
            destination=filename,
        )
        template.create()

    def _add_api_documentation_to_toctree(self):
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        if not os.path.exists(index_filename):
            return

        package = self.configuration.package["name"]
        utils.add_to_toctree(
            filename=index_filename,
            entries=[f"{package}.gui.{self.name}"],
            sort=True,
        )


class SubpackageCreator:
    """
    Add a subpackage to an existing package.

    Actually, adding a subpackage consists of creating three directories and
    three files: the subpackage itself, an accompanying test subpackage,
    and the API documentation subdirectory. The latter gets added to the API
    toctree directive as well. Furthermore, in the subpackage and test
    subpackage directories ``__init__.py`` files are created, and an index
    file for the subpackage API documentation.

    If you try to add an already existing subpackage, a warning is raised
    and no further action taken, in order *not* to overwrite existing code.

    Attributes
    ----------
    name : :class:`str`
        Name of the subpackage to be created.

    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no name is provided


    Examples
    --------
    The following examples demonstrate how to use the CLI from the terminal,
    rather than how to use this class programmatically.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add subpackage mysubpackage

    This will add a subpackage "mysubpackage" to your package, together with a
    "mysubpackage" subpackage in the "tests" subdirectory. And even better,
    the API documentation will be updated for you as well.

    This can even be cascaded and used for nested subpackages. In this case,
    simply use the familiar dot notation for separating subpackages:

    .. code-block:: bash

        pymeta add subpackage mysubpackage.mysubsubpackage

    This will add a subpackage "mysubsubpackage" to the subpackage
    "mysubpackage" in your package, together with a
    "mysubpackage/mysubsubpackage" subpackage in the "tests" subdirectory.
    And even better, the API documentation will be updated for you as well.

    .. note::
        If you like to create nested subpackages as described above,
        make sure to sequentially create all intermediate subpackages.
        Otherwise, you subpackage will *not* be created and a warning issued.

    .. versionadded:: 0.5

    .. versionchanged:: 0.6
        Support for nested subpackages

    """

    def __init__(self):
        self.name = ""
        self.configuration = configuration.Configuration()

    def create(self, name=""):
        """
        Add a subpackage to an existing package.

        Parameters
        ----------
        name : :class:`str`
            Name of the subpackage to add.

            If provided, this will set the :attr:`name` attribute of the
            class.

        """
        if name:
            self.name = name
        if not self.name:
            raise ValueError
        if self._subpackage_exists():
            warnings.warn(f"Subpackage '{self.name}' exists already")
            return
        try:
            self._create_directories()
        except FileNotFoundError:
            warnings.warn(
                f"Subpackage '{self.name}' cannot be created - "
                f"missing intermediate directory?"
            )
            return
        self._create_documentation()

    def _subpackage_exists(self):
        directory = os.path.join(
            self.configuration.package["name"], *self.name.split(".")
        )
        return os.path.exists(directory) and os.path.isdir(directory)

    def _create_directories(self):
        directories = [self.configuration.package["name"], "tests"]
        for directory in directories:
            directory = os.path.join(directory, *self.name.split("."))
            os.mkdir(directory)
            init_filename = os.path.join(directory, "__init__.py")
            utils.ensure_file_exists(init_filename)

    def _create_documentation(self):
        os.makedirs(os.path.join("docs", "api", *self.name.split(".")))
        self._create_documentation_index()
        self._add_subpackage_block_to_documentation_index()
        self._add_api_documentation_to_toctree()

    def _create_documentation_index(self):
        package_name = self.configuration.package["name"]
        context = self.configuration.to_dict()
        context["subpackage"] = {"name": f"{package_name}.{self.name}"}
        context["header_extension"] = (
            len(package_name) + len(self.name) + 1
        ) * "="
        template = utils.Template(
            path="docs",
            template="api_subpackage_index.j2.rst",
            context=context,
            destination=os.path.join(
                "docs", "api", *self.name.split("."), "index.rst"
            ),
        )
        template.create()

    def _add_subpackage_block_to_documentation_index(self):
        destination = os.path.join("docs", "api", "index.rst")
        if os.path.exists(destination):
            with open(destination, encoding="utf8") as file:
                contents = file.read()
            if "Subpackages" in contents:
                return
        context = self.configuration.to_dict()
        template = utils.Template(
            path="docs",
            template="api_index_subpackages_block.j2.rst",
            context=context,
            destination=destination,
        )
        template.append()

    def _add_api_documentation_to_toctree(self):
        index_filename = os.path.join(
            "docs", "api", ".".join(self.name.split(".")[:-1]), "index.rst"
        )
        if not os.path.exists(index_filename):
            return
        if "." in self.name:
            path_to_docs = ".".join(self.name.split(".")[1:]).replace(
                ".", "/"
            )
            after = ""
        else:
            path_to_docs = self.name.replace(".", "/")
            after = "Subpackage"
        utils.add_to_toctree(
            filename=index_filename,
            entries=[f"{path_to_docs}/index"],
            sort=True,
            after=after,
        )


class GuiWidgetCreator:
    """
    Add a PySide6-based (Qt6) GUI widget to an existing GUI subpackage.

    Actually, adding a GUI window consists of creating a number of files:

    #. the module used to call the GUI window
    #. an accompanying test module
    #. the API documentation file

    The latter gets added to the API toctree directive as well.

    If you try to add an already existing GUI widget, a warning is raised
    and no further action taken, in order *not* to overwrite existing code.


    Attributes
    ----------
    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no name is provided


    Examples
    --------
    The following example demonstrates how to use the CLI from the terminal,
    rather than how to use this class programmatically, as this is the
    preferred and intended use case.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following CLI commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add widget mywidget

    This will add the GUI widget ``mywidget`` to the ``gui`` subpackage of
    your package, together with the ``test_mywidget`` module in the
    ``tests.gui`` directory. Furthermore, the API documentation will be
    updated as well for you.


    .. versionadded:: 0.5

    """

    def __init__(self):
        self._name = ""
        self._class_name = ""
        self.configuration = configuration.Configuration()

    @property
    def name(self):
        """
        Name of the GUI widget to be created.

        A suffix "widget" gets added if not present, and the name is
        ensured to be in lowercase letters.

        Returns
        -------
        name : :class:`str`
            Name of the GUI widget to be created.

        """
        return self._name

    @name.setter
    def name(self, name=""):
        if not name:
            self._name = ""
            self._class_name = ""
        elif name.lower().endswith("widget"):
            self._name = name.lower()
            self._class_name = utils.underscore_to_camel_case(self.name)
        else:
            self._name = f"{name}_widget".lower()
            self._class_name = utils.underscore_to_camel_case(self.name)

    @property
    def class_name(self):
        """
        The name of the class containing the GUI widget.

        Similar to :attr:`name`, but in CamelCase with the first letter
        capitalised and the suffix "Widget".

        Returns
        -------
        class_name : :class:`str`
            The name of the class containing the GUI widget.

        """
        return self._class_name

    def create(self, name=""):
        """
        Add a widget to an existing GUI.

        Parameters
        ----------
        name : :class:`str`
            Name of the widget to add.

            If provided, this will set the :attr:`name` attribute of the
            class.

        """
        if name:
            self.name = name
        if not self.name:
            raise ValueError
        if self._widget_exists():
            warnings.warn(f"Widget {self.name} exists already. Nothing done.")
            return
        self._create_widget()
        self._add_tests()
        self._create_api_documentation()
        self._add_api_documentation_to_toctree()

    def _widget_exists(self):
        window_module = os.path.join(
            self.configuration.package["name"], "gui", f"{self.name}.py"
        )
        return os.path.exists(window_module)

    def _create_widget(self):
        gui_dir = os.path.join(self.configuration.package["name"], "gui")
        test_dir = os.path.join("tests", "gui")
        files = [
            {
                "template": "gui_widget.j2.py",
                "path": os.path.join(gui_dir, f"{self.name}.py"),
            },
            {
                "template": "test_guimodule.j2.py",
                "path": os.path.join(test_dir, f"test_{self.name}.py"),
            },
        ]
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        context["class"] = {"name": self.class_name}
        for file in files:
            template = utils.Template(
                path="code",
                template=file["template"],
                context=context,
                destination=file["path"],
            )
            template.create()

    def _add_tests(self):
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        context["class"] = {"name": self.class_name}
        filename = os.path.join("tests", "gui", f"test_{self.name}.py")
        template = utils.Template(
            path="code",
            template="test_guiclass.j2.py",
            context=context,
            destination=filename,
        )
        template.append()

    def _create_api_documentation(self):
        package = self.configuration.package["name"] + ".gui"
        filename = os.path.join(
            "docs", "api", "gui", f"{package}.{self.name}.rst"
        )
        if os.path.exists(filename):
            warnings.warn(f"File '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        context["package"] = {"name": package}
        context["module"] = {"name": self.name}
        context["header_extension"] = (
            len(package) + len(self.name) + 1
        ) * "="
        template = utils.Template(
            path="docs",
            template="api_gui_module.j2.rst",
            context=context,
            destination=filename,
        )
        template.create()

    def _add_api_documentation_to_toctree(self):
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        if not os.path.exists(index_filename):
            return

        package = self.configuration.package["name"]
        utils.add_to_toctree(
            filename=index_filename,
            entries=[f"{package}.gui.{self.name}"],
            sort=True,
        )


class GuiDialogCreator:
    """
    Add a PySide6-based (Qt6) GUI widget to an existing GUI subpackage.

    Actually, adding a GUI window consists of creating a number of files:

    #. the module used to call the GUI window
    #. an accompanying test module
    #. the API documentation file

    The latter gets added to the API toctree directive as well.

    If you try to add an already existing GUI widget, a warning is raised
    and no further action taken, in order *not* to overwrite existing code.


    Attributes
    ----------
    configuration : :class:`pymetacode.configuration.Configuration`
        Configuration as usually read from the configuration file.

    Raises
    ------
    ValueError
        Raised if no name is provided


    Examples
    --------
    The following example demonstrates how to use the CLI from the terminal,
    rather than how to use this class programmatically, as this is the
    preferred and intended use case.

    Prerequisite for using the CLI is to have the package configuration
    stored within the package root directory in the file
    ".project_configuration.yaml". This will be the case if the package has
    been created by the CLI as well. Furthermore, all following CLI commands
    need to be issued from *within* the root directory of your package.

    .. code-block:: bash

        pymeta add dialog mydialog

    This will add the GUI widget ``mydialog`` to the ``gui`` subpackage of
    your package, together with the ``test_mydialog`` module in the
    ``tests.gui`` directory. Furthermore, the API documentation will be
    updated as well for you.


    .. versionadded:: 0.5

    """

    def __init__(self):
        self._name = ""
        self._class_name = ""
        self.configuration = configuration.Configuration()

    @property
    def name(self):
        """
        Name of the GUI dialog to be created.

        A suffix "dialog" gets added if not present, and the name is
        ensured to be in lowercase letters.

        Returns
        -------
        name : :class:`str`
            Name of the GUI dialog to be created.

        """
        return self._name

    @name.setter
    def name(self, name=""):
        if not name:
            self._name = ""
            self._class_name = ""
        elif name.lower().endswith("dialog"):
            self._name = name.lower()
            self._class_name = utils.underscore_to_camel_case(self.name)
        else:
            self._name = f"{name}_dialog".lower()
            self._class_name = utils.underscore_to_camel_case(self.name)

    @property
    def class_name(self):
        """
        The name of the class containing the GUI dialog.

        Similar to :attr:`name`, but in CamelCase with the first letter
        capitalised and the suffix "Dialog".

        Returns
        -------
        class_name : :class:`str`
            The name of the class containing the GUI dialog.

        """
        return self._class_name

    def create(self, name=""):
        """
        Add a dialog to an existing GUI.

        Parameters
        ----------
        name : :class:`str`
            Name of the dialog to add.

            If provided, this will set the :attr:`name` attribute of the
            class.

        """
        if name:
            self.name = name
        if not self.name:
            raise ValueError
        if self._dialog_exists():
            warnings.warn(f"Dialog {self.name} exists already. Nothing done.")
            return
        self._create_widget()
        self._add_tests()
        self._create_api_documentation()
        self._add_api_documentation_to_toctree()

    def _dialog_exists(self):
        window_module = os.path.join(
            self.configuration.package["name"], "gui", f"{self.name}.py"
        )
        return os.path.exists(window_module)

    def _create_widget(self):
        gui_dir = os.path.join(self.configuration.package["name"], "gui")
        test_dir = os.path.join("tests", "gui")
        files = [
            {
                "template": "gui_dialog.j2.py",
                "path": os.path.join(gui_dir, f"{self.name}.py"),
            },
            {
                "template": "test_guimodule.j2.py",
                "path": os.path.join(test_dir, f"test_{self.name}.py"),
            },
        ]
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        context["class"] = {"name": self.class_name}
        for file in files:
            template = utils.Template(
                path="code",
                template=file["template"],
                context=context,
                destination=file["path"],
            )
            template.create()

    def _add_tests(self):
        context = self.configuration.to_dict()
        context["module"] = {"name": self.name}
        context["class"] = {"name": self.class_name}
        filename = os.path.join("tests", "gui", f"test_{self.name}.py")
        template = utils.Template(
            path="code",
            template="test_guiclass.j2.py",
            context=context,
            destination=filename,
        )
        template.append()

    def _create_api_documentation(self):
        package = self.configuration.package["name"] + ".gui"
        filename = os.path.join(
            "docs", "api", "gui", f"{package}.{self.name}.rst"
        )
        if os.path.exists(filename):
            warnings.warn(f"File '{filename}' exists already")
            return
        context = self.configuration.to_dict()
        context["package"] = {"name": package}
        context["module"] = {"name": self.name}
        context["header_extension"] = (
            len(package) + len(self.name) + 1
        ) * "="
        template = utils.Template(
            path="docs",
            template="api_gui_module.j2.rst",
            context=context,
            destination=filename,
        )
        template.create()

    def _add_api_documentation_to_toctree(self):
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        if not os.path.exists(index_filename):
            return

        package = self.configuration.package["name"]
        utils.add_to_toctree(
            filename=index_filename,
            entries=[f"{package}.gui.{self.name}"],
            sort=True,
        )
