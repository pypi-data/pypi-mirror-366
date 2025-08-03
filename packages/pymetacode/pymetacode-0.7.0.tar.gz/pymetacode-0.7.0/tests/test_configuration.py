import datetime
import os
import unittest

import pymetacode.configuration


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.configuration = pymetacode.configuration.Configuration()
        self.filename = "foo.yaml"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_package_property(self):
        self.assertTrue(hasattr(self.configuration, "package"))

    def test_package_property_has_keys(self):
        self.assertListEqual(
            [
                "name",
                "author",
                "author_email",
                "year",
                "description",
                "urls",
                "keywords",
                "install_requires",
                "license",
            ],
            list(self.configuration.package.keys()),
        )

    def test_package_property_year_is_set_to_current_year(self):
        current_year = datetime.date.strftime(datetime.date.today(), "%Y")
        self.assertEqual(current_year, self.configuration.package["year"])

    def test_has_documentation_property(self):
        self.assertTrue(hasattr(self.configuration, "documentation"))

    def test_documentation_property_has_keys(self):
        self.assertListEqual(
            ["logo", "favicon", "language"],
            list(self.configuration.documentation.keys()),
        )

    def test_default_documentation_language_is_en(self):
        self.assertEqual("en", self.configuration.documentation["language"])

    def test_has_options_property(self):
        self.assertTrue(hasattr(self.configuration, "options"))

    def test_options_property_has_keys(self):
        self.assertListEqual(
            ["logging", "git", "gui"], list(self.configuration.options.keys())
        )

    def test_has_gui_property(self):
        self.assertTrue(hasattr(self.configuration, "gui"))

    def test_options_gui_has_keys(self):
        self.assertListEqual(
            ["splash", "organisation", "domain"],
            list(self.configuration.gui.keys()),
        )

    def test_to_dict_returns_dict(self):
        result = self.configuration.to_dict()
        self.assertTrue(isinstance(result, dict))

    def test_to_dict_with_unknown_license_raises(self):
        self.configuration.package["license"] = "foo"
        with self.assertRaises(ValueError):
            self.configuration.to_dict()

    def test_to_file_writes_yaml_file(self):
        self.configuration.to_file(name=self.filename)
        self.assertTrue(os.path.exists(self.filename))

    def test_to_file_writes_contents_to_yaml_file(self):
        self.configuration.to_file(name=self.filename)
        with open(self.filename) as file:
            contents = file.read()
        self.assertIn("package:", contents)

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(ValueError):
            self.configuration.from_dict()

    def test_from_dict_sets_properties(self):
        dict_ = {
            "package": {
                "name": "foo",
                "urls": {
                    "main": "https://foo.local/",
                },
            },
        }
        self.configuration.from_dict(dict_)
        self.assertEqual(
            dict_["package"]["name"], self.configuration.package["name"]
        )

    def test_from_dict_does_not_set_unknown_attribute(self):
        attribute = "foo"
        dict_ = dict()
        dict_[attribute] = "foo"
        self.configuration.from_dict(dict_)
        self.assertFalse(hasattr(self.configuration, attribute))

    def test_from_dict_updates_dicts(self):
        dict_ = self.configuration.to_dict()
        dict_["package"].pop("license")
        self.configuration.from_dict(dict_)
        self.assertIn("license", self.configuration.package)

    def test_from_file_sets_properties(self):
        self.configuration.package["name"] = "foo"
        self.configuration.package["author"] = "John Doe"
        self.configuration.to_file(self.filename)
        new_config = pymetacode.configuration.Configuration()
        new_config.from_file(self.filename)
        self.assertEqual(
            new_config.package["name"], self.configuration.package["name"]
        )
        self.assertEqual(
            new_config.package["author"], self.configuration.package["author"]
        )

    def test_from_dict_with_unknown_license_raises(self):
        dict_ = self.configuration.to_dict()
        dict_["package"]["license"] = "foo"
        with self.assertRaises(ValueError):
            self.configuration.from_dict(dict_)
