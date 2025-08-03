import collections
import copy
import datetime
import os
import shutil
import unittest
from unittest.mock import patch

from pymetacode import utils


class TestEnsureFileExists(unittest.TestCase):
    def setUp(self):
        self.filename = "foo"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_ensure_file_exists_without_name_raises(self):
        with self.assertRaises(ValueError):
            utils.ensure_file_exists()

    def test_ensure_file_exists_creates_file(self):
        utils.ensure_file_exists(self.filename)
        self.assertTrue(os.path.exists(self.filename))

    def test_ensure_file_exists_does_not_change_existing_file(self):
        with open(self.filename, "a") as file:
            file.write("foo bar")
        utils.ensure_file_exists(self.filename)
        with open(self.filename) as file:
            file_content = file.read()
        self.assertEqual("foo bar", file_content)


class TestGetPackageData(unittest.TestCase):
    def setUp(self):
        self.filename = "bar"
        self.data_dir = "foo"

    def tearDown(self):
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)

    def create_data_dir_and_contents(self):
        data_dir = os.path.join(self.data_dir, "pymetacode")
        os.makedirs(data_dir)
        with open(
            os.path.join(data_dir, self.filename), "w+", encoding="utf8"
        ) as file:
            file.write("foo")

    def test_get_package_data_without_name_raises(self):
        with self.assertRaises(ValueError):
            utils.get_package_data()

    def test_get_package_data_returns_content(self):
        with patch("pkgutil.get_data", return_value="foo".encode()):
            content = utils.get_package_data(self.filename)
        self.assertTrue(content)

    def test_get_package_data_with_prefixed_package_returns_content(self):
        content = utils.get_package_data("pymetacode@gitignore")
        self.assertTrue(content)

    def test_get_package_data_with_foreign_package_returns_content(self):
        content = utils.get_package_data("pip@__main__.py", directory="")
        self.assertTrue(content)

    def test_get_package_data_with_user_data_returns_content(self):
        self.create_data_dir_and_contents()
        with patch("platformdirs.user_data_dir", return_value=self.data_dir):
            content = utils.get_package_data(self.filename, directory="")
        self.assertTrue(content)

    def test_get_package_data_with_site_data_returns_content(self):
        self.create_data_dir_and_contents()
        with patch("platformdirs.site_data_dir", return_value=self.data_dir):
            content = utils.get_package_data(self.filename, directory="")
        self.assertTrue(content)


class TestToDictMixin(unittest.TestCase):
    def setUp(self):
        class MixedIn(utils.ToDictMixin):
            pass

        self.mixed_in = MixedIn()

    @staticmethod
    def set_properties_from_dict(obj=None, dict_=None):
        dict_ = copy.deepcopy(dict_)
        for key in dict_:
            setattr(obj, key, dict_[key])

    def test_instantiate_class(self):
        pass

    def test_string_property(self):
        orig_dict = {"foo": "bar"}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_only_public_properties(self):
        orig_dict = {"foo": "bar"}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        self.mixed_in._protected_property = None
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_dict_property(self):
        orig_dict = {"foo": {"bar": "baz"}}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_cascaded_dict_property(self):
        orig_dict = {"foo": {"bar": {"baz": "baf"}}}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_ordered_dict_property(self):
        orig_dict = {"foo": collections.OrderedDict({"bar": "baz"})}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_mixed_in_object_property(self):
        orig_dict = {"foo": "bar"}
        mixed_in = utils.ToDictMixin()
        self.set_properties_from_dict(obj=mixed_in, dict_=orig_dict)
        self.mixed_in.object = mixed_in
        full_dict = {"object": {"foo": "bar"}}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(full_dict, obj_dict)

    def test_generic_object_property(self):
        orig_dict = {"foo": "bar"}

        class DummyClass:
            pass

        obj = DummyClass()
        self.set_properties_from_dict(obj=obj, dict_=orig_dict)
        self.mixed_in.object = obj
        full_dict = {"object": {"foo": "bar"}}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(full_dict, obj_dict)

    def test_list_of_dicts_property(self):
        orig_dict = {"foo": [{"foo": "bar"}, {"bar": "baz"}]}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_list_of_dicts_containing_dicts_property(self):
        orig_dict = {"foo": [{"foo": {"foobar": "bar"}}, {"bar": "baz"}]}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_list_of_objects_property(self):
        toobj_dict = {"foo": "bar"}
        obj1 = utils.ToDictMixin()
        obj2 = utils.ToDictMixin()
        self.set_properties_from_dict(obj=obj1, dict_=toobj_dict)
        self.set_properties_from_dict(obj=obj2, dict_=toobj_dict)
        self.mixed_in.objects = [obj1, obj2]
        orig_dict = {"objects": [toobj_dict, toobj_dict]}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_list_of_dicts_containing_objects_property(self):
        toobj_dict = {"foo": "bar"}
        obj1 = utils.ToDictMixin()
        obj2 = utils.ToDictMixin()
        self.set_properties_from_dict(obj=obj1, dict_=toobj_dict)
        self.set_properties_from_dict(obj=obj2, dict_=toobj_dict)
        orig_dict = {"foo": [{"foo": toobj_dict}, {"bar": toobj_dict}]}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        # noinspection PyUnresolvedReferences
        self.mixed_in.foo[0]["foo"] = obj1
        # noinspection PyUnresolvedReferences
        self.mixed_in.foo[1]["bar"] = obj2
        obj_dict = self.mixed_in.to_dict()
        self.assertEqual(orig_dict["foo"], obj_dict["foo"])

    def test_datetime_property(self):
        date = datetime.datetime.now()
        toobj_dict = {"date": date}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=toobj_dict)
        orig_dict = {"date": str(date)}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_date_property(self):
        date = datetime.date.today()
        toobj_dict = {"date": date}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=toobj_dict)
        orig_dict = {"date": str(date)}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_time_property(self):
        date = datetime.time(12, 10, 30)
        toobj_dict = {"date": date}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=toobj_dict)
        orig_dict = {"date": str(date)}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_dict_preserves_argument_definition_order(self):
        arguments = ["purpose", "operator", "labbook"]

        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ""
                self.operator = ""
                self.labbook = ""

        obj = Test()
        self.assertEqual(arguments, list(obj.to_dict().keys()))

    def test_with_properties_to_exclude(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ""
                self.operator = ""
                self._exclude_from_to_dict = ["operator"]

        obj = Test()
        self.assertEqual(["purpose"], list(obj.to_dict().keys()))

    def test_with_property_to_include(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ""
                self._foo = None
                self._include_in_to_dict = ["_foo"]

        obj = Test()
        self.assertEqual(["purpose", "_foo"], list(obj.to_dict().keys()))

    def test_with_properties_to_include(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ""
                self._foo = None
                self._bar = None
                self._include_in_to_dict = ["_foo", "_bar"]

        obj = Test()
        self.assertEqual(
            ["purpose", "_foo", "_bar"], list(obj.to_dict().keys())
        )


class TestChangeWorkingDir(unittest.TestCase):
    def test_change_working_dir_returns_to_original_dir(self):
        oldpwd = os.getcwd()
        with utils.change_working_dir(".."):
            pass
        self.assertEqual(oldpwd, os.getcwd())


class TestCamelCaseToUnderscore(unittest.TestCase):
    def test_camel_case_to_underscore_converts_correctly(self):
        result = utils.camel_case_to_underscore("FooBar")
        self.assertEqual("foo_bar", result)


class TestUnderscoreToCamelCase(unittest.TestCase):
    def test_underscore_to_camel_case_converts_correctly(self):
        result = utils.underscore_to_camel_case("foo_bar")
        self.assertEqual("FooBar", result)


class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.template = utils.Template()
        self.destination = "foo.txt"

    def tearDown(self):
        if os.path.exists(self.destination):
            os.remove(self.destination)

    def test_instantiate_class(self):
        pass

    def test_render_renders_template(self):
        self.template.path = "licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe"}
        }
        rendered_template = self.template.render()
        self.assertIn("Copyright (c) 2021 John Doe", rendered_template)

    def test_render_with_package_prefix_renders_template(self):
        self.template.path = "pymetacode@licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe"}
        }
        rendered_template = self.template.render()
        self.assertIn("Copyright (c) 2021 John Doe", rendered_template)

    def test_render_adds_rst_header_markup_to_context(self):
        self.template.path = "licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe", "name": "foo"}
        }
        self.template.render()
        self.assertIn("rst_markup", self.template.context.keys())

    def test_create_creates_file_at_destination(self):
        self.template.path = "licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe"}
        }
        self.template.destination = self.destination
        self.template.create()
        self.assertTrue(os.path.exists(self.destination))

    def test_create_fills_destination(self):
        self.template.path = "licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe"}
        }
        self.template.destination = self.destination
        self.template.create()
        with open(self.destination) as file:
            content = file.read()
        self.assertIn("Copyright (c) 2021 John Doe", content)

    def test_append_appends_template_content_to_destination(self):
        test_content = "foo bar bla blub\n\n"
        with open(self.destination, "w+") as file:
            file.write(test_content)
        self.template.path = "licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe"}
        }
        self.template.destination = self.destination
        self.template.append()
        with open(self.destination) as file:
            content = file.read()
        self.assertIn(test_content, content)

    def test_append_appends_parsed_template_to_destination(self):
        test_content = "foo bar bla blub\n\n"
        with open(self.destination, "w+") as file:
            file.write(test_content)
        self.template.path = "licenses"
        self.template.template = "bsd-2clause.j2.txt"
        self.template.context = {
            "package": {"year": "2021", "author": "John Doe"}
        }
        self.template.destination = self.destination
        self.template.append()
        with open(self.destination) as file:
            content = file.read()
        self.assertIn("Copyright (c) 2021 John Doe", content)

    def test_create_with_properties_set_on_instantiation(self):
        template = utils.Template(
            path="licenses",
            template="bsd-2clause.j2.txt",
            context={"package": {"year": "2021", "author": "John Doe"}},
            destination=self.destination,
        )
        template.create()
        with open(self.destination) as file:
            content = file.read()
        self.assertIn("Copyright (c) 2021 John Doe", content)


class TestPackageVersionFromFile(unittest.TestCase):
    def test_package_version_from_file_returns_version(self):
        with utils.change_working_dir(".."):
            result = utils.package_version_from_file()
        with open(os.path.join("..", "VERSION")) as file:
            version = file.read()
        self.assertEqual(version, result)


class TestMakeExecutable(unittest.TestCase):
    def setUp(self):
        self.filename = "foo.txt"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_set_executable_makes_file_executable(self):
        with open(self.filename, "w+", encoding="utf8") as file:
            file.write("")
        utils.make_executable(self.filename)
        self.assertTrue(os.access(self.filename, os.X_OK))


class TestAddToToctree(unittest.TestCase):
    def setUp(self):
        self.filename = "test.rst"
        self.content = [
            ".. toctree::",
            "    :maxdepth: 1",
            "",
            "additional text",
        ]

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def write_file(self):
        with open(self.filename, "w+", encoding="utf8") as file:
            for line in self.content:
                file.write(line + "\n")

    def get_file_contents(self):
        with open(self.filename, "r", encoding="utf8") as file:
            content = file.read()
        return content

    def test_add_to_toctree_adds_line(self):
        self.write_file()
        utils.add_to_toctree(filename=self.filename, entries=["foo"])
        self.assertIn("foo", self.get_file_contents())

    def test_add_to_toctree_adds_line_in_actual_toctree(self):
        self.write_file()
        utils.add_to_toctree(filename=self.filename, entries=["foo"])
        self.assertLess(
            self.get_file_contents().index("foo"),
            self.get_file_contents().index("additional"),
        )

    def test_add_to_toctree_adds_empty_line_after_toctree(self):
        self.write_file()
        utils.add_to_toctree(filename=self.filename, entries=["foo"])
        file_contents = self.get_file_contents().split("\n")
        index = file_contents.index("additional text") - 1
        self.assertFalse(file_contents[index])

    def test_add_to_toctree_with_trailing_whitespace(self):
        self.content[0] = ".. toctree:: "
        self.write_file()
        utils.add_to_toctree(filename=self.filename, entries=["foo"])
        self.assertLess(
            self.get_file_contents().index("foo"),
            self.get_file_contents().index("additional"),
        )

    def test_add_to_toctree_adds_multiple_lines(self):
        self.write_file()
        entries = ["foo", "bar"]
        utils.add_to_toctree(filename=self.filename, entries=entries)
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertIn(entry, self.get_file_contents())

    def test_add_to_toctree_adds_line_at_the_bottom_of_the_toctree(self):
        self.write_file()
        utils.add_to_toctree(filename=self.filename, entries=["foo"])
        utils.add_to_toctree(filename=self.filename, entries=["bar"])
        file_contents = self.get_file_contents().split("\n")
        self.assertGreater(
            file_contents.index("    bar"), file_contents.index("    foo")
        )

    def test_add_to_toctree_sorts_entries_if_told_so(self):
        self.write_file()
        entries = ["foo", "bar"]
        utils.add_to_toctree(
            filename=self.filename, entries=entries, sort=True
        )
        file_contents = self.get_file_contents().split("\n")
        self.assertLess(
            file_contents.index("    bar"), file_contents.index("    foo")
        )

    def test_add_to_toctree_sorts_all_entries(self):
        self.write_file()
        entries = ["foo", "bar"]
        utils.add_to_toctree(filename=self.filename, entries=["bla"])
        utils.add_to_toctree(
            filename=self.filename, entries=entries, sort=True
        )
        file_contents = self.get_file_contents().split("\n")
        self.assertLess(
            file_contents.index("    bar"), file_contents.index("    bla")
        )
        self.assertLess(
            file_contents.index("    bla"), file_contents.index("    foo")
        )

    def test_add_to_toctree_appearing_after_string_in_file(self):
        content = self.content
        self.content = content + ["", "Lorem ipsum", ""] + content
        self.write_file()
        utils.add_to_toctree(
            filename=self.filename, entries=["bla"], after="Lorem"
        )
        file_contents = self.get_file_contents().split("\n")
        self.assertGreater(
            file_contents.index("    bla"), file_contents.index("Lorem ipsum")
        )
