import datetime
import os
import shutil
import unittest
import warnings

from pymetacode import coding, utils
import pymetacode.configuration


class TestPackageCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.PackageCreator()
        self.name = "foo"

    def tearDown(self):
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_with_name_property_set(self):
        self.creator.name = self.name
        self.creator.create()

    def test_create_with_name_sets_name_property(self):
        self.creator.create(name=self.name)
        self.assertEqual(self.name, self.creator.name)

    def test_create_creates_package_directory(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(self.name))
        self.assertTrue(os.path.isdir(self.name))

    def test_create_with_existing_directory_issues_warning(self):
        os.makedirs(os.path.join(self.name, self.name))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)
        self.assertTrue(os.path.exists(self.name))
        self.assertTrue(os.path.isdir(self.name))

    def test_create_creates_subdirectories(self):
        directories = [
            os.path.join(self.name, self.name),
            os.path.join(self.name, "tests"),
            os.path.join(self.name, "docs", "api"),
            os.path.join(self.name, "bin"),
        ]
        self.creator.create(name=self.name)
        for directory in directories:
            with self.subTest(directory=directory):
                self.assertTrue(os.path.exists(directory))
                self.assertTrue(os.path.isdir(directory))

    def test_create_creates_init_files(self):
        directories = [
            os.path.join(self.name, self.name),
            os.path.join(self.name, "tests"),
        ]
        self.creator.create(name=self.name)
        for directory in directories:
            with self.subTest(directory=directory):
                filename = os.path.join(directory, "__init__.py")
                self.assertTrue(os.path.exists(filename))

    def test_create_copies_gitignore_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, ".gitignore")))

    def test_create_copies_prospector_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(
            os.path.exists(os.path.join(self.name, ".prospector.yaml"))
        )

    def test_create_creates_version_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, "VERSION")))

    def test_create_sets_version_in_version_file(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "VERSION")) as file:
            contents = file.read().strip()
        self.assertEqual("0.1.0.dev0", contents)

    def test_create_creates_license_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, "LICENSE")))

    def test_create_fills_license_file(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "LICENSE")) as file:
            contents = file.read()
        self.assertIn("THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT", contents)

    def test_create_replaces_placeholders_in_license_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["author"] = "John Doe"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "LICENSE")) as file:
            contents = file.read()
        current_year = datetime.date.strftime(datetime.date.today(), "%Y")
        copyright_line = "Copyright (c) {} {}".format(
            current_year, configuration.package["author"]
        )
        self.assertIn(copyright_line, contents)

    def test_create_creates_correct_license_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["license"] = "GPLv3"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "LICENSE")) as file:
            contents = file.read()
        self.assertIn("GNU General Public License", contents)

    def test_gplv3_license_creates_copying_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["license"] = "GPLv3"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, "COPYING")))
        with open(os.path.join(self.name, "COPYING")) as file:
            contents = file.read()
        self.assertIn("GNU General Public License", contents)

    def test_create_creates_setup_py_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, "setup.py")))

    def test_create_fills_setup_py_file(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "setup.py")) as file:
            contents = file.read()
        self.assertIn("setuptools.setup(", contents)

    def test_create_replaces_placeholders_in_setup_py_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["author"] = "John Doe"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "setup.py")) as file:
            contents = file.read()
        content_line = 'author="{}"'.format(configuration.package["author"])
        self.assertIn(content_line, contents)

    def test_set_correct_license_in_setup_py_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["license"] = "GPLv3"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "setup.py")) as file:
            contents = file.read()
        content_line = f'license="{configuration.package["license"]}"'
        self.assertIn(content_line, contents)
        self.assertNotIn("BSD License", contents)

    def test_create_creates_readme_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, "README.rst")))

    def test_create_fills_readme_file(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "README.rst")) as file:
            contents = file.read()
        self.assertIn("documentation", contents)

    def test_create_replaces_placeholders_in_readme_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "README.rst")) as file:
            contents = file.read()
        content_line = "{}".format(self.name)
        self.assertIn(content_line, contents)

    def test_create_readme_file_adjusts_rst_header_length(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "README.rst")) as file:
            contents = file.read().split("\n")
        self.assertEqual(len(contents[0]), len(contents[1]))

    def test_create_readme_sets_correct_license(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        configuration.package["license"] = "GPLv3"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "README.rst")) as file:
            contents = file.read().split("\n")
        self.assertIn(configuration.package["license"], "".join(contents))

    def test_create_creates_manifest_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(
            os.path.exists(os.path.join(self.name, "MANIFEST.in"))
        )

    def test_create_fills_manifest_file(self):
        self.creator.create(name=self.name)
        file_path = os.path.join(self.name, "MANIFEST.in")
        with open(file_path) as file:
            contents = file.read()
        self.assertIn("include VERSION", contents)

    def test_create_replaces_placeholders_in_manifest_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        file_path = os.path.join(self.name, "MANIFEST.in")
        with open(file_path) as file:
            contents = file.read()
        self.assertIn(self.name, contents)

    def test_create_creates_makefile(self):
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, "Makefile")))

    def test_create_creates_citation_cff_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(
            os.path.exists(os.path.join(self.name, "CITATION.cff"))
        )

    def test_create_fills_citation_cff_file(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "CITATION.cff")) as file:
            contents = file.read()
        self.assertIn("cff-version:", contents)

    def test_create_replaces_placeholders_in_citation_cff_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        configuration.package["author"] = "John Doe"
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "CITATION.cff")) as file:
            contents = file.read()
        author_family_names_line = "family-names: Doe"
        author_given_names_line = "given-names: John"
        self.assertIn(author_family_names_line, contents)
        self.assertIn(author_given_names_line, contents)

    def test_create_creates_version_updater_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(
            os.path.exists(
                os.path.join(self.name, "bin", "incrementVersion.sh")
            )
        )

    def test_create_fills_version_updater_file(self):
        self.creator.create(name=self.name)
        file_path = os.path.join(self.name, "bin", "incrementVersion.sh")
        with open(file_path) as file:
            contents = file.read()
        self.assertIn("Increment version number", contents)

    def test_version_updater_is_executable(self):
        self.creator.create(name=self.name)
        file_path = os.path.join(self.name, "bin", "incrementVersion.sh")
        self.assertTrue(os.access(file_path, os.X_OK))

    def test_create_creates_python_formatter_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(
            os.path.exists(
                os.path.join(self.name, "bin", "formatPythonCode.sh")
            )
        )

    def test_create_fills_python_formatter_file(self):
        self.creator.create(name=self.name)
        file_path = os.path.join(self.name, "bin", "formatPythonCode.sh")
        with open(file_path) as file:
            contents = file.read()
        self.assertIn("Autoformat Python files", contents)

    def test_python_formatter_is_executable(self):
        self.creator.create(name=self.name)
        file_path = os.path.join(self.name, "bin", "formatPythonCode.sh")
        self.assertTrue(os.access(file_path, os.X_OK))

    def test_create_populates_docs_subdirectory(self):
        self.creator.create(name=self.name)
        files = ["make.bat", "Makefile", "index.rst", "conf.py"]
        for file in files:
            with self.subTest(file=file):
                filename = os.path.join(self.name, "docs", file)
                self.assertTrue(os.path.exists(filename))

    def test_create_adds_toctree_to_documentation_index(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "docs", "index.rst")) as file:
            contents = file.read()
        self.assertIn(".. toctree::", contents)

    def test_create_populates_docs_api_subdirectory(self):
        self.creator.create(name=self.name)
        files = ["index.rst"]
        for file in files:
            with self.subTest(file=file):
                filename = os.path.join(self.name, "docs", "api", file)
                self.assertTrue(os.path.exists(filename))

    def test_create_replaces_variables_in_docs_api_index(self):
        self.creator.create(name=self.name)
        filename = os.path.join(self.name, "docs", "api", "index.rst")
        with open(filename, encoding="utf8") as file:
            contents = file.read()
        self.assertIn(f"modules available within the {self.name}", contents)

    def test_create_populates_docs_directory(self):
        self.creator.create(name=self.name)
        files = self.creator.documentation["pages"]
        for file in files:
            with self.subTest(file=file):
                filename = os.path.join(
                    self.name, "docs", "{}.rst".format(file)
                )
                self.assertTrue(os.path.exists(filename))

    def test_create_replaces_placeholders_in_docs_conf_file(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "docs", "conf.py")) as file:
            contents = file.read()
        self.assertIn(self.name, contents)

    def test_create_sets_language_in_docs_conf_file(self):
        language = "de"
        configuration = pymetacode.configuration.Configuration()
        configuration.documentation["language"] = language
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "docs", "conf.py")) as file:
            contents = file.read()
        self.assertIn(language, contents)

    def test_create_adds_templates_for_multiversion(self):
        self.creator.create(name=self.name)
        files = ["page.html", "versions.html"]
        for file in files:
            with self.subTest(file=file):
                filename = os.path.join(self.name, "docs", "_templates", file)
                self.assertTrue(os.path.exists(filename))

    def test_create_with_git_true_creates_git_directory(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        configuration.options["git"] = True
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(os.path.join(self.name, ".git")))

    def test_create_with_git_true_creates_pre_commit_hook(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        configuration.options["git"] = True
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(
            os.path.join(self.name, ".git", "hooks", "pre-commit")
        ) as file:
            content = file.read()
        self.assertIn("./bin/incrementVersion.sh", content)
        self.assertIn("./bin/formatPythonCode.sh", content)
        self.assertTrue(
            os.access(
                os.path.join(self.name, ".git", "hooks", "pre-commit"),
                os.X_OK,
            )
        )

    def test_create_with_gui_true_creates_gui(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        configuration.options["gui"] = True
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        gui_path = os.path.join(self.name, self.name, "gui")
        self.assertTrue(os.path.exists(gui_path))

    def test_create_with_gui_true_modifies_prospector_profile(self):
        configuration = pymetacode.configuration.Configuration()
        configuration.package["name"] = self.name
        configuration.options["gui"] = True
        self.creator.configuration = configuration
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, ".prospector.yaml")) as file:
            content = file.read()
        self.assertIn("extension-pkg-allow-list: PySide6", content)

    def test_create_creates_pyproject_toml_file(self):
        self.creator.create(name=self.name)
        self.assertTrue(
            os.path.exists(os.path.join(self.name, "pyproject.toml"))
        )

    def test_create_fills_pyproject_toml_file(self):
        self.creator.create(name=self.name)
        with open(os.path.join(self.name, "pyproject.toml")) as file:
            contents = file.read()
        self.assertIn("[build-system]", contents)


class TestModuleCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.ModuleCreator()
        self.package = "bar"
        self.name = "foo"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])
        if os.path.exists("tests"):
            shutil.rmtree("tests")
        if os.path.exists("docs"):
            shutil.rmtree("docs")

    def create_package_structure(self):
        os.mkdir(self.configuration.package["name"])
        os.mkdir("tests")
        os.makedirs(os.path.join("docs", "api"))

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_with_name_property_set(self):
        self.creator.name = self.name
        self.creator.create()

    def test_create_with_name_sets_name_property(self):
        self.creator.create(name=self.name)
        self.assertEqual(self.name, self.creator.name)

    def test_create_creates_module(self):
        self.creator.create(name=self.name)
        path = os.path.join(self.package, self.name + ".py")
        self.assertTrue(os.path.exists(path))

    def test_create_with_name_property_set_creates_module(self):
        self.creator.name = self.name
        self.creator.create()
        path = os.path.join(self.package, self.name + ".py")
        self.assertTrue(os.path.exists(path))

    def test_create_does_not_change_existing_file(self):
        filename = os.path.join(self.package, self.name + ".py")
        with open(filename, "a") as file:
            file.write("foo bar")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.creator.create(name=self.name)
        with open(filename) as file:
            file_content = file.read()
        self.assertEqual("foo bar", file_content)

    def test_create_warns_if_module_exists(self):
        filename = os.path.join(self.package, self.name + ".py")
        with open(filename, "a") as file:
            file.write("foo bar")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)

    def test_create_replaces_placeholders_in_module_file(self):
        filename = os.path.join(self.package, self.name + ".py")
        self.creator.create(name=self.name)
        with open(filename) as file:
            contents = file.read()
        content_line = "{} module of the {} package.".format(
            self.name, self.package
        )
        self.assertIn(content_line, contents)

    def test_create_with_logging_adds_logger(self):
        self.creator.configuration.options["logging"] = True
        filename = os.path.join(self.package, self.name + ".py")
        self.creator.create(name=self.name)
        with open(filename) as file:
            contents = file.read()
        self.assertIn("import logging", contents)
        self.assertIn("logger = logging.getLogger(__name__)", contents)

    def test_create_creates_test_module(self):
        self.creator.create(name=self.name)
        path = os.path.join("tests", "test_{}.py".format(self.name))
        self.assertTrue(os.path.exists(path))

    def test_create_with_name_property_set_creates_test_module(self):
        self.creator.name = self.name
        self.creator.create()
        path = os.path.join("tests", "test_{}.py".format(self.name))
        self.assertTrue(os.path.exists(path))

    def test_create_does_not_change_existing_test_file(self):
        filename = os.path.join(self.package, "test_{}.py".format(self.name))
        with open(filename, "a") as file:
            file.write("foo bar")
        self.creator.create(name=self.name)
        with open(filename) as file:
            file_content = file.read()
        self.assertEqual("foo bar", file_content)

    def test_create_warns_if_test_module_exists(self):
        filename = os.path.join("tests", "test_{}.py".format(self.name))
        with open(filename, "a") as file:
            file.write("foo bar")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)

    def test_create_replaces_placeholders_in_test_module_file(self):
        filename = os.path.join("tests", "test_{}.py".format(self.name))
        self.creator.create(name=self.name)
        with open(filename) as file:
            contents = file.read()
        content_line = "from {} import {}".format(self.package, self.name)
        self.assertIn(content_line, contents)

    def test_create_creates_api_documentation(self):
        self.creator.create(name=self.name)
        path = os.path.join(
            "docs", "api", "{}.{}.rst".format(self.package, self.name)
        )
        self.assertTrue(os.path.exists(path), f"{path} does not exist")

    def test_create_warns_if_api_documentation_exists(self):
        filename = os.path.join(
            "docs", "api", "{}.{}.rst".format(self.package, self.name)
        )
        with open(filename, "a") as file:
            file.write("foo bar")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)

    def test_create_replaces_placeholders_in_api_documentation(self):
        filename = os.path.join(
            "docs", "api", "{}.{}.rst".format(self.package, self.name)
        )
        self.creator.create(name=self.name)
        with open(filename) as file:
            contents = file.read()
        content_line = "{}.{} module".format(self.package, self.name)
        self.assertIn(content_line, contents)

    def test_create_adds_documentation_to_api_toctree(self):
        index_filename = os.path.join("docs", "api", "index.rst")
        index_contents = """

        .. toctree::
            :maxdepth: 1
            


        Index
        -----
        """.replace(
            "        ", ""
        )
        with open(index_filename, "w+") as file:
            file.write(index_contents)
        self.creator.create(name=self.name)
        toctree_entry = "{}.{}".format(self.package, self.name)
        with open(index_filename) as file:
            contents = file.read()
        self.assertIn(toctree_entry, contents)

    def test_create_sorts_api_toctree_alphabetically(self):
        index_filename = os.path.join("docs", "api", "index.rst")
        index_contents = """

        .. toctree::
            :maxdepth: 1
            

        Index
        -----
        """.replace(
            "        ", ""
        )
        with open(index_filename, "w+") as file:
            file.write(index_contents)
        self.creator.create(name="zzz")
        self.creator.create(name=self.name)
        new_toctree_entry = "    {}.{}".format(self.package, self.name)
        old_toctree_entry = "    {}.{}".format(self.package, "zzz")
        with open(index_filename) as file:
            contents = file.read()
        self.assertLess(
            contents.index(new_toctree_entry),
            contents.index(old_toctree_entry),
        )

    def test_create_with_dot_creates_module_in_subpackage(self):
        subpackage = "foobar"
        os.mkdir(os.path.join(self.configuration.package["name"], subpackage))
        os.mkdir(os.path.join("tests", subpackage))
        os.mkdir(os.path.join("docs", "api", subpackage))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join(self.package, subpackage, self.name + ".py")
        self.assertTrue(os.path.exists(path), f"{path} does not exist")

    def test_create_with_dot_creates_test_module_in_subpackage(self):
        subpackage = "foobar"
        os.mkdir(os.path.join(self.configuration.package["name"], subpackage))
        os.mkdir(os.path.join("tests", subpackage))
        os.mkdir(os.path.join("docs", "api", subpackage))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join("tests", subpackage, f"test_{self.name}.py")
        self.assertTrue(os.path.exists(path), f"{path} does not exist")

    def test_create_with_dot_adds_subpackage_to_import_in_test_module(self):
        subpackage = "foobar"
        os.mkdir(os.path.join(self.configuration.package["name"], subpackage))
        os.mkdir(os.path.join("tests", subpackage))
        os.mkdir(os.path.join("docs", "api", subpackage))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join("tests", subpackage, f"test_{self.name}.py")
        with open(path) as file:
            contents = file.read()
        self.assertIn(
            ".".join([self.configuration.package["name"], subpackage]),
            contents,
        )

    def test_create_with_dot_and_missing_subpackage_issues_warning(self):
        subpackage = "foobar"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=".".join([subpackage, self.name]))
            self.assertTrue(w)

    def test_create_with_subpackage_creates_api_documentation(self):
        subpackage = "foobar"
        os.mkdir(os.path.join(self.configuration.package["name"], subpackage))
        os.mkdir(os.path.join("tests", subpackage))
        os.mkdir(os.path.join("docs", "api", subpackage))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join(
            "docs",
            "api",
            subpackage,
            ".".join([self.package, subpackage, f"{self.name}.rst"]),
        )
        self.assertTrue(os.path.exists(path), f"{path} does not exist")

    def test_create_with_subpackage_adds_subpackage_name_to_api_doc(self):
        subpackage = "foobar"
        os.mkdir(os.path.join(self.configuration.package["name"], subpackage))
        os.mkdir(os.path.join("tests", subpackage))
        os.mkdir(os.path.join("docs", "api", subpackage))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join(
            "docs",
            "api",
            subpackage,
            ".".join([self.package, subpackage, f"{self.name}.rst"]),
        )
        with open(path, "r", encoding="utf8") as file:
            contents = file.read()
        self.assertIn(".".join([subpackage, self.name]), contents)

    def test_create_with_subpackage_adds_documentation_to_api_toctree(self):
        subpackage = "foobar"
        os.mkdir(os.path.join(self.configuration.package["name"], subpackage))
        os.mkdir(os.path.join("tests", subpackage))
        os.mkdir(os.path.join("docs", "api", subpackage))
        index_filename = os.path.join("docs", "api", subpackage, "index.rst")
        index_contents = """

        .. toctree::
            :maxdepth: 1



        Index
        -----
        """.replace(
            "        ", ""
        )
        with open(index_filename, "w+") as file:
            file.write(index_contents)
        self.creator.create(name=".".join([subpackage, self.name]))
        toctree_entry = f"{self.package}.{subpackage}.{self.name}"
        with open(index_filename) as file:
            contents = file.read()
        self.assertIn(toctree_entry, contents)

    def test_create_with_two_dots_creates_module_in_subsubpackage(self):
        subpackage = "subpkga.subpkgb"
        subpkg_path = os.path.join(*subpackage.split("."))
        os.makedirs(
            os.path.join(self.configuration.package["name"], subpkg_path)
        )
        os.makedirs(os.path.join("tests", subpkg_path))
        os.makedirs(os.path.join("docs", "api", subpkg_path))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join(self.package, subpkg_path, self.name + ".py")
        self.assertTrue(os.path.exists(path), f"{path} does not exist")

    def test_create_with_subsubpackage_creates_api_documentation(self):
        subpackage = "subpkga.subpkgb"
        subpkg_path = os.path.join(*subpackage.split("."))
        os.makedirs(
            os.path.join(self.configuration.package["name"], subpkg_path)
        )
        os.makedirs(os.path.join("tests", subpkg_path))
        os.makedirs(os.path.join("docs", "api", subpkg_path))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join(
            "docs",
            "api",
            subpkg_path,
            ".".join([self.package, subpackage, f"{self.name}.rst"]),
        )
        self.assertTrue(os.path.exists(path), f"{path} does not exist")

    def test_create_with_subsubpackage_adds_subpackage_name_to_api_doc(self):
        subpackage = "subpkga.subpkgb"
        subpkg_path = os.path.join(*subpackage.split("."))
        os.makedirs(
            os.path.join(self.configuration.package["name"], subpkg_path)
        )
        os.makedirs(os.path.join("tests", subpkg_path))
        os.makedirs(os.path.join("docs", "api", subpkg_path))
        self.creator.create(name=".".join([subpackage, self.name]))
        path = os.path.join(
            "docs",
            "api",
            subpkg_path,
            ".".join([self.package, subpackage, f"{self.name}.rst"]),
        )
        with open(path, "r", encoding="utf8") as file:
            contents = file.read()
        self.assertIn(".".join([subpackage, self.name]), contents)

    def test_create_with_subsubpackage_adds_documentation_to_api_toctree(
        self,
    ):
        subpackage = "subpkga.subpkgb"
        subpkg_path = os.path.join(*subpackage.split("."))
        os.makedirs(
            os.path.join(self.configuration.package["name"], subpkg_path)
        )
        os.makedirs(os.path.join("tests", subpkg_path))
        os.makedirs(os.path.join("docs", "api", subpkg_path))
        index_filename = os.path.join("docs", "api", subpkg_path, "index.rst")
        index_contents = """

        .. toctree::
            :maxdepth: 1



        Index
        -----
        """.replace(
            "        ", ""
        )
        with open(index_filename, "w+") as file:
            file.write(index_contents)
        self.creator.create(name=".".join([subpackage, self.name]))
        toctree_entry = f"{self.package}.{subpackage}.{self.name}"
        with open(index_filename) as file:
            contents = file.read()
        self.assertIn(toctree_entry, contents)


class TestClassCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.ClassCreator()
        with utils.change_working_dir(".."):
            self.creator._package_version = utils.package_version_from_file()
        self.package = "bar"
        self.subpackage = ""
        self.module = "foo"
        self.name = "FooBar"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()
        self.create_module()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])
        if os.path.exists("tests"):
            shutil.rmtree("tests")
        if os.path.exists("docs"):
            shutil.rmtree("docs")
        if self.subpackage and os.path.exists(self.subpackage):
            shutil.rmtree(self.subpackage)

    def create_package_structure(self):
        os.mkdir(self.configuration.package["name"])
        os.mkdir("tests")
        os.makedirs(os.path.join("docs", "api"))

    def create_module(self, module=""):
        creator = coding.ModuleCreator()
        creator.name = module or self.module
        creator.configuration = self.configuration
        creator.create()

    def create_subpackage(self):
        creator = coding.SubpackageCreator()
        if "." in self.subpackage:
            creator.name = ".".join(self.subpackage.split(".")[:-1])
            creator.configuration = self.configuration
            creator.create()
        creator.name = self.subpackage
        creator.configuration = self.configuration
        creator.create()

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_without_module_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create(name="foo")

    def test_create_with_nonexisting_module_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create(name="foo", module="foofoofoofoofoo")

    def test_create_creates_class_in_module(self):
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join(self.package, self.module + ".py")
        with open(path) as file:
            contents = file.read()
        self.assertIn('class {}:\n    """'.format(self.name), contents)

    def test_create_adds_version_added(self):
        self.creator._package_version = "0.2"
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join(self.package, self.module + ".py")
        with open(path) as file:
            contents = file.read()
        self.assertIn(".. versionadded:: 0.2", contents)

    def test_create_adds_version_added_only_if_not_initial_version(self):
        self.creator._package_version = "0.1"
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join(self.package, self.module + ".py")
        with open(path) as file:
            contents = file.read()
        self.assertNotIn(".. versionadded:: ", contents)

    def test_create_creates_test_class_in_test_module(self):
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join("tests", "test_{}.py".format(self.module))
        with open(path) as file:
            contents = file.read()
        self.assertIn(
            "class Test{}(unittest.TestCase):".format(self.name), contents
        )

    def test_create_existing_class_in_module_issues_warning(self):
        self.creator.create(name=self.name, module=self.module)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name, module=self.module)
            self.assertIn(
                f"Class {self.name} exists already in " f"{self.module}.",
                str(w[0].message),
            )

    def test_create_checks_for_exact_class_name_not_only_prefix(self):
        self.creator.create(name=f"{self.name}Foo", module=self.module)
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.creator.create(name=self.name, module=self.module)
            self.assertFalse(warning)

    def test_create_checks_for_exact_class_name_with_bracket(self):
        module_name = os.path.join(self.package, f"{self.module}.py")
        with open(module_name, "w") as file:
            file.write(f"class {self.name}(foo):")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name, module=self.module)
            self.assertIn(
                f"Class {self.name} exists already in " f"{self.module}.",
                str(w[0].message),
            )

    def test_create_with_subpackage_creates_class_in_module(self):
        self.subpackage = "foobar"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            self.package, self.subpackage, self.module + ".py"
        )
        with open(path) as file:
            contents = file.read()
        self.assertIn('class {}:\n    """'.format(self.name), contents)

    def test_create_with_subpackage_creates_test_class_in_test_module(self):
        self.subpackage = "foobar"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            "tests", self.subpackage, "test_{}.py".format(self.module)
        )
        with open(path) as file:
            contents = file.read()
        self.assertIn(
            "class Test{}(unittest.TestCase):".format(self.name), contents
        )

    def test_create_with_subsubpackage_creates_class_in_module(self):
        self.subpackage = "subpkga.subpkgb"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            self.package, *self.subpackage.split("."), self.module + ".py"
        )
        with open(path) as file:
            contents = file.read()
        self.assertIn('class {}:\n    """'.format(self.name), contents)

    def test_create_with_subsubpackage_creates_test_class_in_test_module(
        self,
    ):
        self.subpackage = "subpkga.subpkgb"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            "tests",
            *self.subpackage.split("."),
            "test_{}.py".format(self.module),
        )
        with open(path) as file:
            contents = file.read()
        self.assertIn(
            "class Test{}(unittest.TestCase):".format(self.name), contents
        )


class TestFunctionCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.FunctionCreator()
        with utils.change_working_dir(".."):
            self.creator._package_version = utils.package_version_from_file()
        self.package = "bar"
        self.module = "foo"
        self.name = "foo_bar"
        self.subpackage = ""
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()
        self.create_module()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])
        if os.path.exists("tests"):
            shutil.rmtree("tests")
        if os.path.exists("docs"):
            shutil.rmtree("docs")

    def create_package_structure(self):
        os.mkdir(self.configuration.package["name"])
        os.mkdir("tests")
        os.makedirs(os.path.join("docs", "api"))

    def create_module(self, module=""):
        creator = coding.ModuleCreator()
        creator.name = module or self.module
        creator.configuration = self.configuration
        creator.create()

    def create_subpackage(self):
        creator = coding.SubpackageCreator()
        if "." in self.subpackage:
            creator.name = ".".join(self.subpackage.split(".")[:-1])
            creator.configuration = self.configuration
            creator.create()
        creator.name = self.subpackage
        creator.configuration = self.configuration
        creator.create()

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_without_module_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create(name="foo")

    def test_create_with_nonexisting_module_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create(name="foo", module="foofoofoofoofoo")

    def test_create_creates_function_in_module(self):
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join(self.package, self.module + ".py")
        with open(path) as file:
            contents = file.read()
        self.assertIn('def {}():\n    """'.format(self.name), contents)

    def test_create_adds_version_added(self):
        self.creator._package_version = "0.2"
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join(self.package, self.module + ".py")
        with open(path) as file:
            contents = file.read()
        self.assertIn(".. versionadded:: 0.2", contents)

    def test_create_adds_version_added_only_if_not_initial_version(self):
        self.creator._package_version = "0.1"
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join(self.package, self.module + ".py")
        with open(path) as file:
            contents = file.read()
        self.assertNotIn(".. versionadded:: ", contents)

    def test_create_creates_test_class_in_test_module(self):
        self.creator.create(name=self.name, module=self.module)
        path = os.path.join("tests", "test_{}.py".format(self.module))
        with open(path) as file:
            contents = file.read()
        camel = utils.underscore_to_camel_case(self.name)
        self.assertIn(
            "class Test{}(unittest.TestCase):".format(camel), contents
        )

    def test_create_existing_function_in_module_issues_warning(self):
        self.creator.create(name=self.name, module=self.module)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name, module=self.module)
            self.assertIn(
                f"Function {self.name} exists already in " f"{self.module}.",
                str(w[0].message),
            )

    def test_create_checks_for_exact_function_name_not_only_prefix(self):
        self.creator.create(name=f"{self.name}Foo", module=self.module)
        with warnings.catch_warnings(record=True) as warning:
            warnings.simplefilter("always")
            self.creator.create(name=self.name, module=self.module)
            self.assertFalse(warning)

    def test_create_checks_for_exact_function_name_with_bracket(self):
        module_name = os.path.join(self.package, f"{self.module}.py")
        with open(module_name, "w") as file:
            file.write(f"def {self.name}(foo):")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name, module=self.module)
            self.assertIn(
                f"Function {self.name} exists already in " f"{self.module}.",
                str(w[0].message),
            )

    def test_create_with_subpackage_creates_function_in_module(self):
        self.subpackage = "foobar"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            self.package, self.subpackage, self.module + ".py"
        )
        with open(path) as file:
            contents = file.read()
        self.assertIn('def {}():\n    """'.format(self.name), contents)

    def test_create_with_subpackage_creates_test_class_in_test_module(self):
        self.subpackage = "foobar"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            "tests", self.subpackage, "test_{}.py".format(self.module)
        )
        with open(path) as file:
            contents = file.read()
        camel = utils.underscore_to_camel_case(self.name)
        self.assertIn(
            "class Test{}(unittest.TestCase):".format(camel), contents
        )

    def test_create_with_subsubpackage_creates_function_in_module(self):
        self.subpackage = "subpkga.subpkgb"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            self.package, *self.subpackage.split("."), self.module + ".py"
        )
        with open(path) as file:
            contents = file.read()
        self.assertIn('def {}():\n    """'.format(self.name), contents)

    def test_create_with_subsubpackage_creates_test_class_in_test_module(
        self,
    ):
        self.subpackage = "subpkga.subpkgb"
        self.create_subpackage()
        self.create_module(module=".".join([self.subpackage, self.module]))
        self.creator.create(
            name=self.name, module=".".join([self.subpackage, self.module])
        )
        path = os.path.join(
            "tests",
            *self.subpackage.split("."),
            "test_{}.py".format(self.module),
        )
        with open(path) as file:
            contents = file.read()
        camel = utils.underscore_to_camel_case(self.name)
        self.assertIn(
            "class Test{}(unittest.TestCase):".format(camel), contents
        )


class TestGuiCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.GuiCreator()
        self.package = "bar"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])

    def create_package_structure(self):
        pkg = coding.PackageCreator()
        pkg.name = self.package
        pkg.configuration = self.configuration
        pkg.create()

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_creates_gui_directory(self):
        path = os.path.join(self.package, "gui")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(path))
            self.assertTrue(os.path.isdir(path))

    def test_create_with_existing_gui_directory_issues_warning(self):
        path = os.path.join(self.package, "gui")
        with utils.change_working_dir(self.package):
            self.creator.create()
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create()
                self.assertTrue(w)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(os.path.isdir(path))

    def test_create_with_existing_gui_dir_warns_and_does_nothing(self):
        path = os.path.join(self.package, "gui")
        with utils.change_working_dir(self.package):
            os.mkdir(path)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create()
                self.assertTrue(w)
            self.assertFalse(os.path.exists(os.path.join(path, "ui")))

    def test_create_creates_subdirectories(self):
        directories = [
            os.path.join(self.package, "gui", "images"),
            os.path.join(self.package, "gui", "ui"),
        ]
        with utils.change_working_dir(self.package):
            self.creator.create()
            for directory in directories:
                with self.subTest(directory=directory):
                    self.assertTrue(os.path.exists(directory))
                    self.assertTrue(os.path.isdir(directory))

    def test_create_creates_init_files(self):
        directories = [
            os.path.join(self.package, "gui"),
            os.path.join(self.package, "gui", "ui"),
        ]
        with utils.change_working_dir(self.package):
            self.creator.create()
            for directory in directories:
                with self.subTest(directory=directory):
                    filename = os.path.join(directory, "__init__.py")
                    self.assertTrue(os.path.exists(filename))

    def test_create_creates_test_subdirectory(self):
        directory = os.path.join("tests", "gui")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(directory))
            self.assertTrue(os.path.isdir(directory))

    def test_create_creates_init_file_in_test_subdirectory(self):
        directory = os.path.join("tests", "gui")
        with utils.change_working_dir(self.package):
            self.creator.create()
            filename = os.path.join(directory, "__init__.py")
            self.assertTrue(os.path.exists(filename))

    def test_create_copies_makefile(self):
        filepath = os.path.join(self.package, "gui", "Makefile")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(filepath))

    def test_create_copies_app_module(self):
        filepath = os.path.join(self.package, "gui", "app.py")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(filepath))

    def test_create_replaces_variables_in_app_module(self):
        filepath = os.path.join(self.package, "gui", "app.py")
        with utils.change_working_dir(self.package):
            self.creator.create()
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(self.package + ".gui import mainwindow", contents)

    def test_create_with_splash_adds_splash_in_app_module(self):
        filepath = os.path.join(self.package, "gui", "app.py")
        self.configuration.gui["splash"] = True
        with utils.change_working_dir(self.package):
            self.creator.create()
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("splash_screen()", contents)

    def test_create_without_splash_does_not_add_splash_in_app_module(self):
        filepath = os.path.join(self.package, "gui", "app.py")
        self.configuration.gui["splash"] = False
        self.creator.configuration = self.configuration
        with utils.change_working_dir(self.package):
            self.creator.create()
            with open(filepath) as file:
                contents = file.read()
            self.assertNotIn("splash_screen()", contents)

    def test_create_with_splash_adds_splash_image(self):
        filepath = os.path.join(self.package, "gui", "images", "splash.svg")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(filepath))

    def test_create_with_splash_adds_project_name_to_splash_image(self):
        filepath = os.path.join(self.package, "gui", "images", "splash.svg")
        with utils.change_working_dir(self.package):
            self.creator.create()
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(self.package, contents)

    def test_create_without_splash_does_not_add_splash_image(self):
        filepath = os.path.join(self.package, "gui", "images", "splash.svg")
        self.configuration.gui["splash"] = False
        self.creator.configuration = self.configuration
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertFalse(os.path.exists(filepath))

    def test_create_adds_icon_image(self):
        filepath = os.path.join(self.package, "gui", "images", "icon.svg")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(filepath))

    def test_create_creates_mainwindow_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepaths = [
                os.path.join(self.package, "gui", "mainwindow.py"),
                os.path.join("tests", "gui", "test_mainwindow.py"),
            ]
            for filepath in filepaths:
                with self.subTest(filepath=filepath):
                    self.assertTrue(
                        os.path.exists(filepath),
                        f"File {filepath} does not exist.",
                    )

    def test_create_fills_mainwindow_module(self):
        filepath = os.path.join(self.package, "gui", "mainwindow.py")
        with utils.change_working_dir(self.package):
            self.creator.create()
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("class MainWindow", contents)

    def test_create_fills_mainwindow_unittest_file(self):
        filepath = os.path.join("tests", "gui", "test_mainwindow.py")
        with utils.change_working_dir(self.package):
            self.creator.create()
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"from {self.package}.gui import mainwindow", contents
            )
            self.assertIn(
                f"class TestMainWindow(unittest.TestCase)", contents
            )

    def test_create_creates_docs_subdirectory(self):
        directory = os.path.join("docs", "api", "gui")
        with utils.change_working_dir(self.package):
            self.creator.create()
            self.assertTrue(os.path.exists(directory))
            self.assertTrue(os.path.isdir(directory))

    def test_create_populates_docs_api_gui_subdirectory(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            files = [
                "index.rst",
                f"{self.package}.gui.app.rst",
                f"{self.package}.gui.mainwindow.rst",
            ]
            for file in files:
                with self.subTest(file=file):
                    filename = os.path.join("docs", "api", "gui", file)
                    self.assertTrue(
                        os.path.exists(filename),
                        f'"{filename}" has not been created',
                    )

    def test_api_gui_docs_do_not_show_inherited_members(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            files = [
                "index.rst",
                f"{self.package}.gui.app.rst",
                f"{self.package}.gui.mainwindow.rst",
            ]
            for file in files:
                with self.subTest(file=file):
                    filename = os.path.join("docs", "api", "gui", file)
                    with open(filename, "r", encoding="utf8") as doc:
                        content = doc.read()
                    self.assertNotIn(":inherited-members:", content)

    def test_create_replaces_variables_in_docs_api_gui_index(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = os.path.join("docs", "api", "gui", "index.rst")
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(f"{self.package}.gui subpackage", contents)
            self.assertIn(f".. automodule:: {self.package}.gui", contents)

    def test_create_sets_correct_header_length_in_docs_api_gui_index(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = os.path.join("docs", "api", "gui", "index.rst")
            with open(filepath) as file:
                contents = file.read()
            header_underline = (
                len(self.package) + 5 + len("subpackage")
            ) * "="
            self.assertIn(header_underline, contents)

    def test_create_adds_subpackages_block_in_docs_api_index(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = os.path.join("docs", "api", "index.rst")
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("Subpackages", contents)
            self.assertIn(
                f"subpackages available within the {self.package}", contents
            )

    def test_create_adds_gui_subpackage_to_toc_in_docs_api_index(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = os.path.join("docs", "api", "index.rst")
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("gui/index", contents)

    def test_create_adds_to_subpackages_toc_in_docs_api_index(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = os.path.join("docs", "api", "index.rst")
            with open(filepath) as file:
                contents = file.read()
            contents = contents.split("\n")
            self.assertGreater(
                contents.index("    gui/index"), contents.index("Subpackages")
            )

    def test_create_adds_submodules_to_toc_in_docs_api_gui_index(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = os.path.join("docs", "api", "gui", "index.rst")
            with open(filepath) as file:
                contents = file.read()
            modules = ["app", "mainwindow"]
            for module in modules:
                with self.subTest(module=module):
                    self.assertIn(module, contents)

    def test_create_adds_block_to_manifest_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = "MANIFEST.in"
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("# Include the README", contents)
            self.assertIn(
                f"recursive-include {self.package}/gui/images *", contents
            )

    def test_create_adds_requirements_to_setup_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = "setup.py"
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("setuptools.setup(", contents)
            self.assertIn("PySide6", contents)
            self.assertIn("qtbricks", contents)

    def test_create_does_not_add_already_existing_requirements(self):
        self.tearDown()
        self.configuration.options["gui"] = True
        self.creator.configuration = self.configuration
        self.create_package_structure()
        with utils.change_working_dir(self.package):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.creator.create()
            filepath = "setup.py"
            with open(filepath) as file:
                contents = file.read()
            self.assertEqual(1, contents.split().count('"PySide6",'))
            self.assertEqual(1, contents.split().count('"qtbricks",'))

    def test_create_adds_entry_points_to_setup_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create()
            filepath = "setup.py"
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("setuptools.setup(", contents)
            self.assertIn("gui_scripts", contents)

    def test_create_does_not_add_already_existing_entry_point(self):
        self.tearDown()
        self.configuration.options["gui"] = True
        self.creator.configuration = self.configuration
        self.create_package_structure()
        with utils.change_working_dir(self.package):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.creator.create()
            filepath = "setup.py"
            with open(filepath) as file:
                contents = file.read()
            self.assertEqual(1, contents.split().count('"gui_scripts":'))


class TestGuiWindowCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.GuiWindowCreator()
        self.package = "bar"
        self.name = "test"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])

    def create_package_structure(self):
        pkg = coding.PackageCreator()
        pkg.name = self.package
        pkg.create()
        with utils.change_working_dir(self.package):
            gui = coding.GuiCreator()
            gui.configuration = self.configuration
            gui.create()

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaisesRegex(ValueError, "No window name given"):
            self.creator.create()

    def test_setting_name_property_adds_window_suffix(self):
        self.creator.name = self.name
        self.assertEqual(f"{self.name}window", self.creator.name)

    def test_setting_name_property_with_window_suffix(self):
        self.creator.name = f"{self.name}window"
        self.assertEqual(f"{self.name}window", self.creator.name)

    def test_create_with_name_sets_name_property(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            self.assertEqual(f"{self.name}window", self.creator.name)

    def test_setting_name_sets_lowercase_name(self):
        self.creator.name = "CamelCase"
        self.assertEqual(f"{self.creator.name}".lower(), self.creator.name)

    def test_setting_empty_name(self):
        self.creator.name = "CamelCase"
        self.creator.name = ""
        self.assertEqual("", self.creator.name)

    def test_setting_name_property_with_window_suffix_sets_lowercase(self):
        self.creator.name = "CamelCaseWindow"
        self.assertEqual("camelcasewindow", self.creator.name)

    def test_set_class_name_from_window_name(self):
        self.creator.name = f"{self.name}"
        self.assertEqual(
            f"{self.name.capitalize()}Window", self.creator.class_name
        )

    def test_set_class_name_from_window_name_with_suffix(self):
        self.creator.name = f"{self.name}window"
        self.assertEqual(
            f"{self.name.capitalize()}Window", self.creator.class_name
        )

    def test_set_empty_class_name_from_empty_name(self):
        self.creator.name = "foo"
        self.creator.name = ""
        self.assertEqual("", self.creator.class_name)

    def test_create_creates_window_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            gui_path = os.path.join(self.package, "gui")
            filepaths = [
                os.path.join(gui_path, self.creator.name + ".py"),
                os.path.join(gui_path, "ui", self.creator.name + ".ui"),
                # os.path.join(gui_path, 'ui', self.name + '.py'),
                os.path.join(
                    "tests", "gui", "test_" + self.creator.name + ".py"
                ),
            ]
            for filepath in filepaths:
                with self.subTest(filepath=filepath):
                    self.assertTrue(os.path.exists(filepath))

    def test_create_fills_window_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("class ", contents)

    def test_create_replaces_variables_in_window_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"from .ui.{self.creator.name} import Ui_"
                f"{self.creator.class_name}",
                contents,
            )
            self.assertIn(
                f"class {self.creator.class_name}(QMainWindow, "
                f"Ui_{self.creator.class_name}",
                contents,
            )

    def test_create_fills_window_ui_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", "ui", self.creator.name + ".ui"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("<ui version=", contents)

    def test_create_replaces_variables_in_window_ui_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", "ui", self.creator.name + ".ui"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"<class>{self.creator.class_name}</class>", contents
            )
            self.assertIn(
                f'<widget class="QMainWindow" name="{self.creator.class_name}">',
                contents,
            )
            self.assertIn(
                f"<string>{self.creator.class_name}</string>", contents
            )

    def test_create_fills_window_unittest_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                "tests", "gui", "test_" + self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"from {self.package}.gui import {self.creator.name}",
                contents,
            )
            self.assertIn(
                f"class Test{self.creator.class_name}(unittest.TestCase)",
                contents,
            )

    def test_create_creates_api_documentation(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            self.assertTrue(os.path.exists(filename))

    def test_create_warns_if_api_documentation_exists(self):
        with utils.change_working_dir(self.package):
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.name}window.rst",
            )
            with open(filename, "a") as file:
                file.write("foo bar")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create(name=self.name)
                self.assertTrue(w)

    def test_create_replaces_placeholders_in_api_documentation(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            with open(filename) as file:
                contents = file.read()
            content_line = f"{self.package}.gui.{self.creator.name}"
            self.assertIn(content_line, contents)

    def test_create_adds_documentation_to_api_toctree(self):
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            toctree_entry = f"{self.package}.gui.{self.creator.name}"
            with open(index_filename) as file:
                contents = file.read()
            self.assertIn(toctree_entry, contents)

    def test_create_already_existing_window_warns_and_does_nothing(self):
        gui_path = os.path.join(self.package, "gui")
        window_module = os.path.join(gui_path, self.name + "window.py")
        ui_file = os.path.join(gui_path, "ui", self.name + "window.ui")
        with utils.change_working_dir(self.package):
            with open(window_module, "w+", encoding="utf8") as file:
                file.write("")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create(name=self.name)
                self.assertTrue(w)
            self.assertFalse(os.path.exists(ui_file))


class TestSubpackageCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.SubpackageCreator()
        self.package = "pkg"
        self.name = "subpkg"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])
        if os.path.exists("tests"):
            shutil.rmtree("tests")
        if os.path.exists("docs"):
            shutil.rmtree("docs")

    def create_package_structure(self):
        os.mkdir(self.configuration.package["name"])
        os.mkdir("tests")
        os.makedirs(os.path.join("docs", "api"))

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_with_name_property_set(self):
        self.creator.name = self.name
        self.creator.create()

    def test_create_with_name_sets_name_property(self):
        self.creator.create(name=self.name)
        self.assertEqual(self.name, self.creator.name)

    def test_create_creates_subpackage(self):
        self.creator.create(name=self.name)
        path = os.path.join(self.package, self.name)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

    def test_create_with_name_property_set_creates_subpackage(self):
        self.creator.name = self.name
        self.creator.create()
        path = os.path.join(self.package, self.name)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

    def test_create_creates_init_in_subpackage(self):
        self.creator.create(name=self.name)
        path = os.path.join(self.package, self.name, "__init__.py")
        self.assertTrue(os.path.exists(path))

    def test_create_with_name_property_set_creates_tests_subpackage(self):
        self.creator.name = self.name
        self.creator.create()
        path = os.path.join("tests", self.name)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

    def test_create_creates_init_in_tests_subpackage(self):
        self.creator.create(name=self.name)
        path = os.path.join("tests", self.name, "__init__.py")
        self.assertTrue(os.path.exists(path))

    def test_create_does_not_change_existing_file(self):
        directory = os.path.join(self.package, self.name)
        os.mkdir(directory)
        filename = os.path.join(directory, "__init__.py")
        with open(filename, "a") as file:
            file.write("foo bar")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.creator.create(name=self.name)
        with open(filename) as file:
            file_content = file.read()
        self.assertEqual("foo bar", file_content)

    def test_create_warns_if_subpackage_exists(self):
        directory = os.path.join(self.package, self.name)
        os.mkdir(directory)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)

    def test_create_creates_docs_subdirectory(self):
        directory = os.path.join("docs", "api", self.name)
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(directory))
        self.assertTrue(os.path.isdir(directory))

    def test_create_populates_docs_api_subdirectory(self):
        self.creator.create(name=self.name)
        filename = os.path.join("docs", "api", self.name, "index.rst")
        self.assertTrue(
            os.path.exists(filename), f"'{filename}' has not been created"
        )

    def test_subpackage_api_documentation_has_correct_markup(self):
        self.creator.create(name=self.name)
        filename = os.path.join("docs", "api", self.name, "index.rst")
        with open(filename) as file:
            contents = file.readlines()
        self.assertEqual(len(contents[0]), len(contents[1]))

    def test_create_adds_subpackages_section_to_api_doc_index(self):
        self.creator.create(name=self.name)
        filename = os.path.join("docs", "api", "index.rst")
        with open(filename, encoding="utf8") as file:
            contents = file.read()
        self.assertIn("Subpackages", contents)

    def test_create_doesnt_add_subpackages_section_twice(self):
        self.creator.create(name="foo")
        self.creator.create(name="bar")
        filename = os.path.join("docs", "api", "index.rst")
        with open(filename, encoding="utf8") as file:
            contents = file.read().split()
        self.assertEqual(1, contents.count("Subpackages"))

    def test_create_adds_subpackage_to_api_doc_index_toctree(self):
        self.creator.create(name=self.name)
        filename = os.path.join("docs", "api", "index.rst")
        with open(filename, encoding="utf8") as file:
            contents = file.read()
        self.assertIn(f"{self.name}/index", contents)

    def test_create_cascaded_subpackage_creates_subpackage(self):
        self.name = "subpkga.subpkgb"
        self.creator.create(name=".".join(self.name.split(".")[:-1]))
        self.creator.create(name=self.name)
        path = os.path.join(self.package, *self.name.split("."))
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

    def test_create_cascaded_subpackage_warns_if_subpackage_exists(self):
        self.name = "subpkga.subpkgb"
        directory = os.path.join(self.package, *self.name.split("."))
        os.makedirs(directory)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)

    def test_create_cascaded_subpkg_warns_if_missing_intermediate_dirs(self):
        self.name = "subpkga.subpkgb"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.creator.create(name=self.name)
            self.assertTrue(w)

    def test_create_cascaded_subpackage_creates_docs_subdirectory(self):
        self.name = "subpkga.subpkgb"
        directory = os.path.join("docs", "api", *self.name.split("."))
        self.creator.create(name=".".join(self.name.split(".")[:-1]))
        self.creator.create(name=self.name)
        self.assertTrue(os.path.exists(directory))
        self.assertTrue(os.path.isdir(directory))

    def test_create_cascaded_subpkg_adds_subpkg_to_api_doc_toctree(self):
        self.name = "subpkga.subpkgb"
        self.creator.create(name=".".join(self.name.split(".")[:-1]))
        self.creator.create(name=self.name)
        filename = os.path.join(
            "docs", "api", ".".join(self.name.split(".")[:-1]), "index.rst"
        )
        with open(filename, encoding="utf8") as file:
            contents = file.read()
        path_to_docs = ".".join(self.name.split(".")[1:]).replace(".", "/")
        self.assertIn(f"{path_to_docs}/index", contents)


class TestGuiWidgetCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.GuiWidgetCreator()
        self.package = "bar"
        self.name = "foo_bar"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])

    def create_package_structure(self):
        pkg = coding.PackageCreator()
        pkg.name = self.package
        pkg.create()
        with utils.change_working_dir(self.package):
            gui = coding.GuiCreator()
            gui.configuration = self.configuration
            gui.create()

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_with_name_property_set(self):
        self.creator.name = self.name
        with utils.change_working_dir(self.package):
            self.creator.create()

    def test_setting_name_property_adds_widget_suffix(self):
        self.creator.name = self.name
        self.assertEqual(f"{self.name}_widget", self.creator.name)

    def test_setting_name_property_with_window_suffix(self):
        self.creator.name = f"{self.name}_widget"
        self.assertEqual(f"{self.name}_widget", self.creator.name)

    def test_create_with_name_sets_name_property(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            self.assertEqual(f"{self.name}_widget", self.creator.name)

    def test_setting_name_sets_lowercase_name(self):
        self.creator.name = "CamelCase"
        self.assertEqual(f"{self.creator.name}".lower(), self.creator.name)

    def test_setting_empty_name(self):
        self.creator.name = "CamelCase"
        self.creator.name = ""
        self.assertEqual("", self.creator.name)

    def test_setting_name_property_with_widget_suffix_sets_lowercase(self):
        self.creator.name = "CamelCaseWidget"
        self.assertEqual("camelcasewidget", self.creator.name)

    def test_set_class_name_from_widget_name(self):
        self.creator.name = f"{self.name}"
        self.assertEqual(
            f"{utils.underscore_to_camel_case(self.name)}Widget",
            self.creator.class_name,
        )

    def test_set_class_name_from_widget_name_with_suffix(self):
        self.creator.name = f"{self.name}_widget"
        self.assertEqual(
            f"{utils.underscore_to_camel_case(self.name)}Widget",
            self.creator.class_name,
        )

    def test_set_empty_class_name_from_empty_name(self):
        self.creator.name = "foo"
        self.creator.name = ""
        self.assertEqual("", self.creator.class_name)

    def test_create_creates_widget_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            gui_path = os.path.join(self.package, "gui")
            filepaths = [
                os.path.join(gui_path, self.creator.name + ".py"),
                os.path.join(
                    "tests", "gui", "test_" + self.creator.name + ".py"
                ),
            ]
            for filepath in filepaths:
                with self.subTest(filepath=filepath):
                    self.assertTrue(os.path.exists(filepath))

    def test_create_fills_widget_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("class ", contents)

    def test_create_replaces_variables_in_widget_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"class {self.creator.class_name}(QtWidgets.QWidget)",
                contents,
            )

    def test_create_fills_widget_unittest_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                "tests", "gui", "test_" + self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"from {self.package}.gui import {self.creator.name}",
                contents,
            )
            self.assertIn(
                f"class Test{self.creator.class_name}(unittest.TestCase)",
                contents,
            )

    def test_create_creates_api_documentation(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            self.assertTrue(os.path.exists(filename))

    def test_api_documentation_does_not_show_inherited_members(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            with open(filename) as file:
                contents = file.read()
            self.assertNotIn("inherited-members", contents)

    def test_create_warns_if_api_documentation_exists(self):
        with utils.change_working_dir(self.package):
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.name}_widget.rst",
            )
            with open(filename, "a") as file:
                file.write("foo bar")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create(name=self.name)
                self.assertTrue(w)

    def test_create_replaces_placeholders_in_api_documentation(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            with open(filename) as file:
                contents = file.read()
            content_line = f"{self.package}.gui.{self.creator.name}"
            self.assertIn(content_line, contents)

    def test_create_adds_documentation_to_api_toctree(self):
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            toctree_entry = f"{self.package}.gui.{self.creator.name}"
            with open(index_filename) as file:
                contents = file.read()
            self.assertIn(toctree_entry, contents)

    def test_create_already_existing_widget_warns_and_does_nothing(self):
        gui_path = os.path.join(self.package, "gui")
        widget_module = os.path.join(gui_path, self.name + "_widget.py")
        with utils.change_working_dir(self.package):
            with open(widget_module, "w+", encoding="utf8") as file:
                file.write("")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create(name=self.name)
                self.assertTrue(w)


class TestGuiDialogCreator(unittest.TestCase):
    def setUp(self):
        self.creator = coding.GuiDialogCreator()
        self.package = "bar"
        self.name = "foo_bar"
        self.configuration = pymetacode.configuration.Configuration()
        self.configuration.package["name"] = self.package
        self.creator.configuration = self.configuration
        self.create_package_structure()

    def tearDown(self):
        if os.path.exists(self.configuration.package["name"]):
            shutil.rmtree(self.configuration.package["name"])

    def create_package_structure(self):
        pkg = coding.PackageCreator()
        pkg.name = self.package
        pkg.create()
        with utils.change_working_dir(self.package):
            gui = coding.GuiCreator()
            gui.configuration = self.configuration
            gui.create()

    def test_instantiate_class(self):
        pass

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.creator, "create"))
        self.assertTrue(callable(self.creator.create))

    def test_create_without_name_raises(self):
        with self.assertRaises(ValueError):
            self.creator.create()

    def test_create_with_name_property_set(self):
        self.creator.name = self.name
        with utils.change_working_dir(self.package):
            self.creator.create()

    def test_setting_name_property_adds_dialog_suffix(self):
        self.creator.name = self.name
        self.assertEqual(f"{self.name}_dialog", self.creator.name)

    def test_setting_name_property_with_dialog_suffix(self):
        self.creator.name = f"{self.name}_dialog"
        self.assertEqual(f"{self.name}_dialog", self.creator.name)

    def test_create_with_name_sets_name_property(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            self.assertEqual(f"{self.name}_dialog", self.creator.name)

    def test_setting_name_sets_lowercase_name(self):
        self.creator.name = "CamelCase"
        self.assertEqual(f"{self.creator.name}".lower(), self.creator.name)

    def test_setting_empty_name(self):
        self.creator.name = "CamelCase"
        self.creator.name = ""
        self.assertEqual("", self.creator.name)

    def test_setting_name_property_with_dialog_suffix_sets_lowercase(self):
        self.creator.name = "CamelCaseDialog"
        self.assertEqual("camelcasedialog", self.creator.name)

    def test_set_class_name_from_dialog_name(self):
        self.creator.name = f"{self.name}"
        self.assertEqual(
            f"{utils.underscore_to_camel_case(self.name)}Dialog",
            self.creator.class_name,
        )

    def test_set_class_name_from_dialog_name_with_suffix(self):
        self.creator.name = f"{self.name}_dialog"
        self.assertEqual(
            f"{utils.underscore_to_camel_case(self.name)}Dialog",
            self.creator.class_name,
        )

    def test_set_empty_class_name_from_empty_name(self):
        self.creator.name = "foo"
        self.creator.name = ""
        self.assertEqual("", self.creator.class_name)

    def test_create_creates_widget_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            gui_path = os.path.join(self.package, "gui")
            filepaths = [
                os.path.join(gui_path, self.creator.name + ".py"),
                os.path.join(
                    "tests", "gui", "test_" + self.creator.name + ".py"
                ),
            ]
            for filepath in filepaths:
                with self.subTest(filepath=filepath):
                    self.assertTrue(os.path.exists(filepath))

    def test_create_fills_widget_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn("class ", contents)

    def test_create_replaces_variables_in_widget_module(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                self.package, "gui", self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"class {self.creator.class_name}(QtWidgets.QDialog)",
                contents,
            )

    def test_create_fills_widget_unittest_file(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filepath = os.path.join(
                "tests", "gui", "test_" + self.creator.name + ".py"
            )
            with open(filepath) as file:
                contents = file.read()
            self.assertIn(
                f"from {self.package}.gui import {self.creator.name}",
                contents,
            )
            self.assertIn(
                f"class Test{self.creator.class_name}(unittest.TestCase)",
                contents,
            )

    def test_create_creates_api_documentation(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            self.assertTrue(os.path.exists(filename))

    def test_api_documentation_does_not_show_inherited_members(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            with open(filename) as file:
                contents = file.read()
            self.assertNotIn("inherited-members", contents)

    def test_create_warns_if_api_documentation_exists(self):
        with utils.change_working_dir(self.package):
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.name}_dialog.rst",
            )
            with open(filename, "a") as file:
                file.write("foo bar")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create(name=self.name)
                self.assertTrue(w)

    def test_create_replaces_placeholders_in_api_documentation(self):
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            filename = os.path.join(
                "docs",
                "api",
                "gui",
                f"{self.package}.gui.{self.creator.name}.rst",
            )
            with open(filename) as file:
                contents = file.read()
            content_line = f"{self.package}.gui.{self.creator.name}"
            self.assertIn(content_line, contents)

    def test_create_adds_documentation_to_api_toctree(self):
        index_filename = os.path.join("docs", "api", "gui", "index.rst")
        with utils.change_working_dir(self.package):
            self.creator.create(name=self.name)
            toctree_entry = f"{self.package}.gui.{self.creator.name}"
            with open(index_filename) as file:
                contents = file.read()
            self.assertIn(toctree_entry, contents)

    def test_create_already_existing_widget_warns_and_does_nothing(self):
        gui_path = os.path.join(self.package, "gui")
        widget_module = os.path.join(gui_path, self.name + "_dialog.py")
        with utils.change_working_dir(self.package):
            with open(widget_module, "w+", encoding="utf8") as file:
                file.write("")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.creator.create(name=self.name)
                self.assertTrue(w)
